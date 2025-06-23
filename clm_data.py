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
        self.fx_rates = {}
        
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
        position_col = 'Position Details' if 'Position Details' in row.index else 'Position'
        position_details = str(row.get(position_col, ''))
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
        # Handle both 'Position Details' and 'Position' column names
        position_col = 'Position Details' if 'Position Details' in df.columns else 'Position'
        
        df = df[~df[position_col].str.contains('Data format|How to get', na=False)]
        df = df.dropna(subset=[position_col])
        df = df[df[position_col].str.strip() != '']
        return df
    
    def _normalize_token_pair(self, pair):
        """Normalize token pair format for consistent pricing"""
        if not pair:
            return pair
            
        # Handle different formats:
        # "SOL + USD" -> "SOL/USDC" 
        # "SUI + USD" -> "SUI/USDC"
        # "SOL short" -> "SOL" (for perpetuals)
        # "SUI short" -> "SUI" (for perpetuals)
        
        pair = pair.strip()
        
        # Handle perpetual positions (show as token/USDC for pricing)
        if 'short' in pair.lower():
            token = pair.replace('short', '').strip().upper()
            return f"{token}/USDC"  # Return as token/USDC for price display
        
        # Handle CLM positions with "TOKEN + USD" format
        if '+' in pair and 'USD' in pair.upper():
            token = pair.split('+')[0].strip().upper()
            # Convert USD to USDC for pricing
            return f"{token}/USDC"
        
        # Handle standard "TOKEN/TOKEN" format (keep as-is)
        if '/' in pair:
            return pair
            
        return pair
    
    def parse_position(self, row: pd.Series, strategy: str) -> dict:
        """Parse a single position row into standardized format"""
        # Handle both 'Position Details' and 'Position' column names
        position_col = 'Position Details' if 'Position Details' in row.index else 'Position'
        position_details = str(row[position_col])
        
        # Extract platform and token pair
        if '|' in position_details:
            platform, pair = position_details.split('|', 1)
            platform = platform.strip()
            pair = pair.strip()
        else:
            platform = str(row.get('Platform', 'Unknown'))
            pair = position_details
        
        # Normalize token pair format for pricing
        pair = self._normalize_token_pair(pair)
        
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
        """Fetch current prices for tokens using DefiLlama + CoinGecko"""
        tokens = set()
        all_positions = self.long_positions + self.neutral_positions
        
        for position in all_positions:
            if position['token_pair']:
                pair = position['token_pair'].replace(' ', '')
                if '/' in pair:
                    token_a, token_b = pair.split('/')
                    tokens.add(token_a.upper())
                    tokens.add(token_b.upper())
        
        # Add base tokens for wrapped tokens to enable ratio calculations
        if any(token in ['WBTC', 'CBBTC'] for token in tokens):
            tokens.add('BTC')
        if any(token in ['WETH', 'WHETH'] for token in tokens):
            tokens.add('ETH')
        
        # Try DefiLlama first for DeFi tokens
        self._fetch_defillama_prices(tokens)
        
        # Fill gaps with CoinGecko
        self._fetch_coingecko_prices(tokens)
        
        # Fetch FX rates
        self._fetch_fx_rates()
        
        # Demo prices if all APIs fail
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
            print("🔄 Using demo prices (APIs unavailable)")
        
        # Demo FX rates if API fails
        if not self.fx_rates:
            self.fx_rates = {
                'USD_CAD': 1.43,
                'CAD_USD': 0.70
            }
            print("🔄 Using demo FX rates (API unavailable)")
        
        # Store timestamp for display
        self.last_price_update = datetime.now()
    
    def _fetch_defillama_prices(self, tokens):
        """Fetch prices from DefiLlama API"""
        # DefiLlama coin IDs for your tokens
        defillama_map = {
            'SOL': 'coingecko:solana',
            'ORCA': 'coingecko:orca', 
            'RAY': 'coingecko:raydium',
            'JLP': 'solana:27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4',  # JLP token address
            'USDC': 'coingecko:usd-coin',
            'ETH': 'coingecko:ethereum',
            'BTC': 'coingecko:bitcoin',
            'SUI': 'coingecko:sui',
            'WETH': 'coingecko:ethereum',
            'WBTC': 'coingecko:wrapped-bitcoin',
            'CBBTC': 'coingecko:coinbase-wrapped-btc',
            'WHETH': 'coingecko:ethereum',  # Wrapped ETH on Solana
            'USDT': 'coingecko:tether'
        }
        
        try:
            # Get coins that we have DefiLlama IDs for
            available_tokens = [token for token in tokens if token in defillama_map]
            if not available_tokens:
                return
                
            # Build coin IDs string
            coin_ids = ','.join([defillama_map[token] for token in available_tokens])
            
            url = f"https://coins.llama.fi/prices/current/{coin_ids}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                price_data = response.json()
                
                if 'coins' in price_data:
                    for token in available_tokens:
                        coin_id = defillama_map[token]
                        if coin_id in price_data['coins']:
                            coin_data = price_data['coins'][coin_id]
                            if 'price' in coin_data:
                                self.prices[token] = coin_data['price']
                    
                    defillama_count = len([t for t in available_tokens if t in self.prices])
                    if defillama_count > 0:
                        print(f"🦙 DefiLlama: {defillama_count} tokens")
                        
        except Exception as e:
            print(f"⚠️  DefiLlama API error: {e}")
    
    def _fetch_coingecko_prices(self, tokens):
        """Fetch prices from CoinGecko API for missing tokens"""
        # CoinGecko mapping
        coingecko_map = {
            'SOL': 'solana',
            'USDC': 'usd-coin',
            'ETH': 'ethereum',
            'BTC': 'bitcoin',
            'SUI': 'sui',
            'ORCA': 'orca',
            'RAY': 'raydium',
            'JLP': 'jupiter-exchange-solana',
            'WETH': 'ethereum',
            'USDT': 'tether'
        }
        
        try:
            # Only fetch tokens we don't already have
            missing_tokens = [token for token in tokens if token not in self.prices and token in coingecko_map]
            if not missing_tokens:
                return
                
            coingecko_ids = ','.join([coingecko_map[token] for token in missing_tokens])
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_ids}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                price_data = response.json()
                
                for token in missing_tokens:
                    gecko_id = coingecko_map[token]
                    if gecko_id in price_data:
                        self.prices[token] = price_data[gecko_id]['usd']
                
                coingecko_count = len([t for t in missing_tokens if t in self.prices])
                if coingecko_count > 0:
                    print(f"🦎 CoinGecko: {coingecko_count} tokens")
                    
        except Exception as e:
            print(f"⚠️  CoinGecko API error: {e}")
        
        total_fetched = len(self.prices)
        if total_fetched > 0:
            print(f"📈 Total prices fetched: {total_fetched} tokens")
    
    def _fetch_fx_rates(self):
        """Fetch FX rates from exchangerate-api.io (free, no API key)"""
        try:
            # Get USD to CAD rate (since this API uses USD as base)
            url = "https://open.er-api.com/v6/latest/USD"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                fx_data = response.json()
                
                if fx_data.get('result') == 'success' and 'rates' in fx_data:
                    usd_cad = fx_data['rates'].get('CAD')
                    if usd_cad:
                        self.fx_rates['USD_CAD'] = usd_cad
                        self.fx_rates['CAD_USD'] = 1.0 / usd_cad
                        print(f"💱 FX rates: 1 USD = ${usd_cad:.4f} CAD")
                        
        except Exception as e:
            print(f"⚠️  FX API error: {e}")
    
    def update_position_status(self):
        """Update current price and range status for positions"""
        all_positions = self.long_positions + self.neutral_positions
        
        for position in all_positions:
            if not position['token_pair']:
                continue
                
            pair = position['token_pair'].replace(' ', '')
            if '/' in pair:
                current_price = self._calculate_pair_price(pair)
                
                if current_price is not None:
                    position['current_price'] = current_price
                    
                    # Handle different position types
                    if not position['min_range'] and position['max_range']:
                        # Perpetual position: only has max range (liquidation/close level)
                        if current_price > position['max_range']:
                            position['range_status'] = 'perp_closed'  # Price above liquidation
                        else:
                            position['range_status'] = 'perp_active'  # Price within acceptable range
                    elif not position['min_range'] or not position['max_range']:
                        # Position without valid ranges
                        position['range_status'] = 'no_range'
                    else:
                        # Normal CLM position with both min and max ranges
                        if current_price < position['min_range']:
                            position['range_status'] = 'out_of_range_low'
                        elif current_price > position['max_range']:
                            position['range_status'] = 'out_of_range_high'
                        else:
                            position['range_status'] = 'in_range'
    
    def _calculate_pair_price(self, pair):
        """Calculate the appropriate price for a token pair"""
        if not pair:
            return None
            
        # Handle single tokens (for perpetuals)
        if '/' not in pair:
            token = pair.upper()
            return self.prices.get(token)
        
        tokens = pair.split('/')
        if len(tokens) != 2:
            return None
            
        base_token = tokens[0].upper()
        quote_token = tokens[1].upper()
        
        # Special handling for specific pairs
        if pair.upper() == 'JLP/SOL':
            # JLP/SOL needs special calculation - JLP is a pool token with different pricing
            jlp_price = self.prices.get('JLP')
            sol_price = self.prices.get('SOL')
            
            if jlp_price and sol_price and sol_price > 0:
                # JLP price is in USD, we want SOL per JLP
                # So: JLP_USD_price / SOL_USD_price = SOL per JLP
                sol_per_jlp = jlp_price / sol_price
                return sol_per_jlp
        
        elif pair.upper() in ['WBTC/SOL', 'CBBTC/SOL', 'WHETH/SOL']:
            # For BTC/SOL and ETH/SOL pairs, calculate ratio
            btc_tokens = ['WBTC', 'CBBTC']
            eth_tokens = ['WHETH', 'WHETF']
            
            if base_token in btc_tokens:
                # Use BTC price for wrapped BTC tokens
                btc_price = self.prices.get('BTC')
                sol_price = self.prices.get('SOL')
                if btc_price and sol_price and sol_price > 0:
                    return btc_price / sol_price
            elif base_token in eth_tokens:
                # Use ETH price for wrapped ETH tokens
                eth_price = self.prices.get('ETH')
                sol_price = self.prices.get('SOL')
                if eth_price and sol_price and sol_price > 0:
                    return eth_price / sol_price
        
        # Default behavior: use base token price directly
        if base_token in self.prices:
            return self.prices[base_token]
            
        return None
    
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