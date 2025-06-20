#!/usr/bin/env python3
"""
CLM Data Manager - Handles all data operations
"""

import pandas as pd
import json
import os
from datetime import datetime
import hashlib
import requests

class CLMDataManager:
    def __init__(self):
        self.long_positions = []
        self.neutral_positions = []
        self.closed_positions = []
        self.prices = {}
        
        # File paths
        self.long_json = "data/JSON_out/clm_long.json"
        self.neutral_json = "data/JSON_out/clm_neutral.json"
        self.closed_json = "data/JSON_out/clm_closed.json"
        self.metadata_json = "data/JSON_out/clm_metadata.json"
        
    def get_file_hash(self, filepath: str) -> str:
        """Get MD5 hash of file to detect changes"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except FileNotFoundError:
            return ""
    
    def load_metadata(self) -> dict:
        """Load metadata about last conversion"""
        try:
            with open(self.metadata_json, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "last_update": "",
                "neutral_csv_hash": "",
                "long_csv_hash": "",
                "neutral_csv_path": "",
                "long_csv_path": ""
            }
    
    def save_metadata(self, metadata: dict):
        """Save metadata about conversion"""
        with open(self.metadata_json, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def check_for_updates(self, neutral_csv: str, long_csv: str) -> bool:
        """Check if CSV files have changed since last conversion"""
        metadata = self.load_metadata()
        
        current_neutral_hash = self.get_file_hash(neutral_csv)
        current_long_hash = self.get_file_hash(long_csv)
        
        return (current_neutral_hash != metadata.get("neutral_csv_hash") or
                current_long_hash != metadata.get("long_csv_hash") or
                not os.path.exists(self.long_json) or
                not os.path.exists(self.neutral_json))
    
    def load_existing_positions(self):
        """Load existing position data"""
        try:
            with open(self.long_json, 'r') as f:
                self.long_positions = json.load(f)
        except FileNotFoundError:
            self.long_positions = []
            
        try:
            with open(self.neutral_json, 'r') as f:
                self.neutral_positions = json.load(f)
        except FileNotFoundError:
            self.neutral_positions = []
            
        try:
            with open(self.closed_json, 'r') as f:
                self.closed_positions = json.load(f)
        except FileNotFoundError:
            self.closed_positions = []
    
    def create_position_id(self, row: pd.Series, strategy: str) -> str:
        """Create unique ID for position"""
        position_details = str(row.get('Position Details', ''))
        entry_date = str(row.get('Entry Date', ''))
        entry_value_col = 'Total Entry Value' if strategy == 'long' else 'Entry Value (cash in)'
        entry_value = str(row.get(entry_value_col, ''))
        
        id_string = f"{position_details}_{entry_date}_{entry_value}_{strategy}"
        return hashlib.md5(id_string.encode()).hexdigest()[:12]
    
    def parse_currency(self, value):
        """Parse currency values like '$24,427' to float"""
        if pd.isna(value) or value == '':
            return None
        if isinstance(value, str):
            cleaned = value.replace('$', '').replace(',', '').strip()
            if cleaned == '' or cleaned == 'N/A':
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return float(value)
    
    def parse_percentage(self, value):
        """Parse percentage values like '12.20%' to float"""
        if pd.isna(value) or value == '':
            return None
        if isinstance(value, str):
            cleaned = value.replace('%', '').strip()
            if cleaned == '' or cleaned == 'N/A':
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return float(value)
    
    def clean_csv_data(self, df):
        """Remove format/instruction rows from CSV"""
        df = df[~df['Position Details'].str.contains('Data format|How to get', na=False)]
        df = df.dropna(subset=['Position Details'])
        df = df[df['Position Details'].str.strip() != '']
        return df
    
    def parse_position(self, row: pd.Series, strategy: str) -> dict:
        """Parse a single position row into standardized format"""
        position_details = str(row['Position Details'])
        
        # Extract platform and token pair
        if '|' in position_details:
            platform, pair = position_details.split('|', 1)
            platform = platform.strip()
            pair = pair.strip()
        else:
            platform = str(row.get('Platform', 'Unknown'))
            pair = position_details
        
        # Get entry value (different column names)
        entry_value_col = 'Total Entry Value' if strategy == 'long' else 'Entry Value (cash in)'
        entry_value = self.parse_currency(row.get(entry_value_col))
        
        # Check if position is closed
        status = str(row.get('Status', '')).lower().strip()
        exit_date = row.get('Exit Date')
        is_closed = (status in ['closed', 'close', 'exit', 'exited'] or 
                    (pd.notna(exit_date) and str(exit_date).strip() != ''))
        
        position = {
            'id': self.create_position_id(row, strategy),
            'position_details': position_details,
            'strategy': strategy,
            'platform': platform,
            'token_pair': pair,
            'chain': str(row.get('Chain', 'Unknown')),
            'wallet': str(row.get('Wallet', 'Unknown')),
            'entry_value': entry_value,
            'entry_date': str(row.get('Entry Date', '')),
            'days_active': float(row.get('Days #')) if pd.notna(row.get('Days #')) else None,
            'min_range': float(row['Min Range']) if pd.notna(row['Min Range']) else None,
            'max_range': float(row['Max Range']) if pd.notna(row['Max Range']) else None,
            'exit_date': str(exit_date) if pd.notna(exit_date) and str(exit_date).strip() != '' else None,
            'exit_value': self.parse_currency(row.get('Exit Value')),
            'claimed_yield_value': self.parse_currency(row.get('Claimed Yield Value')),
            'claimed_yield_return': self.parse_percentage(row.get('Claimed Yield Return')),
            'price_return': self.parse_percentage(row.get('Price Return')),
            'impermanent_loss': self.parse_percentage(row.get('IL')),
            'transaction_fees': self.parse_percentage(row.get('Transaction Fees')),
            'slippage': self.parse_percentage(row.get('Slippage')),
            'yield_apr': self.parse_percentage(row.get('Yield APR')),
            'net_return': self.parse_percentage(row.get('Net Return')),
            'status': status if status else ('closed' if is_closed else 'open'),
            'is_active': not is_closed,
            'current_price': None,
            'range_status': 'unknown',
            'last_updated': datetime.now().isoformat()
        }
        
        return position
    
    def update_positions(self, neutral_csv: str, long_csv: str):
        """Update positions with incremental changes"""
        print("🔄 Checking for position updates...")
        
        self.load_existing_positions()
        
        existing_long = {pos['id']: pos for pos in self.long_positions}
        existing_neutral = {pos['id']: pos for pos in self.neutral_positions}
        existing_closed = {pos['id']: pos for pos in self.closed_positions}
        
        new_positions = {'long': [], 'neutral': [], 'closed': []}
        updated_count = 0
        new_count = 0
        moved_to_closed = 0
        
        # Process both CSV files
        for csv_path, strategy in [(neutral_csv, 'neutral'), (long_csv, 'long')]:
            if not os.path.exists(csv_path):
                print(f"⚠️  {csv_path} not found, skipping...")
                continue
                
            df = pd.read_csv(csv_path)
            df = self.clean_csv_data(df)
            
            for _, row in df.iterrows():
                position = self.parse_position(row, strategy)
                position_id = position['id']
                
                if not position['is_active']:
                    # Move to closed positions
                    if position_id not in existing_closed:
                        moved_to_closed += 1
                        print(f"📁 Moving to closed: {position['position_details']}")
                    new_positions['closed'].append(position)
                    
                    # Remove from active lists
                    if position_id in existing_long:
                        self.long_positions = [p for p in self.long_positions if p['id'] != position_id]
                    if position_id in existing_neutral:
                        self.neutral_positions = [p for p in self.neutral_positions if p['id'] != position_id]
                    
                else:
                    # Active position
                    existing_dict = existing_long if strategy == 'long' else existing_neutral
                    
                    if position_id in existing_dict:
                        # Update existing position
                        existing_pos = existing_dict[position_id]
                        position['current_price'] = existing_pos.get('current_price')
                        position['range_status'] = existing_pos.get('range_status', 'unknown')
                        updated_count += 1
                    else:
                        new_count += 1
                        print(f"✨ New position: {position['position_details']}")
                    
                    new_positions[strategy].append(position)
        
        # Update position lists
        self.long_positions = new_positions['long']
        self.neutral_positions = new_positions['neutral']
        
        # Update closed positions
        for new_closed in new_positions['closed']:
            self.closed_positions = [p for p in self.closed_positions if p['id'] != new_closed['id']]
            self.closed_positions.append(new_closed)
        
        # Save updated data
        self.save_positions()
        
        # Update metadata
        metadata = {
            "last_update": datetime.now().isoformat(),
            "neutral_csv_hash": self.get_file_hash(neutral_csv),
            "long_csv_hash": self.get_file_hash(long_csv),
            "neutral_csv_path": neutral_csv,
            "long_csv_path": long_csv
        }
        self.save_metadata(metadata)
        
        print(f"✅ Update complete:")
        print(f"   📊 {len(self.long_positions)} long positions")
        print(f"   ⚖️  {len(self.neutral_positions)} neutral positions") 
        print(f"   📁 {len(self.closed_positions)} closed positions")
        print(f"   🆕 {new_count} new, 🔄 {updated_count} updated, 📁 {moved_to_closed} moved to closed")
    
    def save_positions(self):
        """Save positions to separate JSON files"""
        with open(self.long_json, 'w') as f:
            json.dump(self.long_positions, f, indent=2)
        
        with open(self.neutral_json, 'w') as f:
            json.dump(self.neutral_positions, f, indent=2)
            
        with open(self.closed_json, 'w') as f:
            json.dump(self.closed_positions, f, indent=2)
    
    def load_positions(self):
        """Load all position data"""
        self.load_existing_positions()
        total_active = len(self.long_positions) + len(self.neutral_positions)
        print(f"📊 Loaded {total_active} active positions ({len(self.long_positions)} long, {len(self.neutral_positions)} neutral) + {len(self.closed_positions)} closed")
    
    def get_token_prices(self):
        """Fetch current prices for tokens"""
        tokens = set()
        all_positions = self.long_positions + self.neutral_positions
        
        for position in all_positions:
            if position['token_pair']:
                pair = position['token_pair'].replace(' ', '')
                if '/' in pair:
                    token_a, token_b = pair.split('/')
                    tokens.add(token_a.upper())
                    tokens.add(token_b.upper())
        
        token_map = {
            'SOL': 'solana',
            'USDC': 'usd-coin',
            'ETH': 'ethereum',
            'BTC': 'bitcoin',
            'ORCA': 'orca',
            'RAY': 'raydium',
            'JLP': 'jupiter-exchange-solana',
            'WETH': 'ethereum',
            'USDT': 'tether'
        }
        
        try:
            coingecko_ids = ','.join([token_map.get(token, token.lower()) for token in tokens if token in token_map])
            
            if coingecko_ids:
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_ids}&vs_currencies=usd"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    price_data = response.json()
                    
                    for token, gecko_id in token_map.items():
                        if gecko_id in price_data:
                            self.prices[token] = price_data[gecko_id]['usd']
                    
                    print(f"📈 Fetched prices for {len(self.prices)} tokens")
                else:
                    print(f"⚠️  Price API error: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Could not fetch prices: {e}")
            
        # Demo prices if API fails
        if not self.prices:
            self.prices = {
                'SOL': 98.50,
                'USDC': 1.00,
                'ETH': 2340.00,
                'BTC': 43200.00,
                'ORCA': 3.25,
                'RAY': 0.85,
                'JLP': 0.032
            }
            print("🔄 Using demo prices (API unavailable)")
    
    def update_position_status(self):
        """Update current price and range status for positions"""
        all_positions = self.long_positions + self.neutral_positions
        
        for position in all_positions:
            if not position['token_pair'] or not position['min_range'] or not position['max_range']:
                continue
                
            pair = position['token_pair'].replace(' ', '')
            if '/' in pair:
                base_token = pair.split('/')[0].upper()
                
                if base_token in self.prices:
                    current_price = self.prices[base_token]
                    position['current_price'] = current_price
                    
                    if current_price < position['min_range']:
                        position['range_status'] = 'out_of_range_low'
                    elif current_price > position['max_range']:
                        position['range_status'] = 'out_of_range_high'
                    else:
                        position['range_status'] = 'in_range'
    
    def refresh_prices_and_status(self):
        """Convenience method to refresh all price data"""
        self.get_token_prices()
        self.update_position_status()
    
    def get_all_active_positions(self):
        """Get all active positions combined"""
        return self.long_positions + self.neutral_positions
    
    def get_positions_by_strategy(self, strategy: str):
        """Get positions by strategy type"""
        if strategy == 'long':
            return self.long_positions
        elif strategy == 'neutral':
            return self.neutral_positions
        elif strategy == 'closed':
            return self.closed_positions
        else:
            return []