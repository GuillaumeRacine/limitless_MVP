#!/usr/bin/env python3
"""
CLM Data Manager - Simplified version
"""

import pandas as pd
import json
import os
from datetime import datetime
import hashlib
import requests
from typing import Dict, List, Any

class CLMDataManager:
    def __init__(self):
        self.long_positions = []
        self.neutral_positions = []
        self.closed_positions = []
        self.prices = {}
        self.price_changes = {}
        self.fx_rates = {}
        
        # File paths
        self.long_json = "data/JSON_out/clm_long.json"
        self.neutral_json = "data/JSON_out/clm_neutral.json"
        self.closed_json = "data/JSON_out/clm_closed.json"
        self.transactions_json = "data/JSON_out/clm_transactions.json"
        
    def parse_value(self, value, value_type='currency'):
        """Universal value parser"""
        if pd.isna(value) or value == '' or value == 'N/A':
            return None
        
        if isinstance(value, str):
            if value_type == 'currency':
                value = value.replace('$', '').replace(',', '').strip()
            elif value_type == 'percentage':
                value = value.replace('%', '').strip()
            
            # Remove any quotes that might be in the value
            value = value.replace('"', '').replace("'", '')
            
            try:
                return float(value)
            except ValueError:
                return None
        
        return float(value)
    
    def get_column_value(self, row, field_type):
        """Get value from row using simple column mapping"""
        column_map = {
            'position': ['Position Details', 'Position', 'Token Pair'],
            'platform': ['Platform', 'Protocol'],
            'chain': ['Chain', 'Blockchain'],
            'entry_value': ['Total Entry Value', 'Entry Value (cash in)'],
            'entry_date': ['Entry Date', 'Date'],
            'wallet': ['Wallet', 'Address']
        }
        
        for col_name in column_map.get(field_type, []):
            if col_name in row.index and pd.notna(row[col_name]):
                return row[col_name]
        return None
    
    def clean_csv_data(self, df):
        """Remove format/instruction rows from CSV"""
        position_col = 'Position Details' if 'Position Details' in df.columns else 'Position'
        
        if position_col in df.columns:
            df = df[~df[position_col].str.contains('Data format|How to get', na=False)]
            df = df.dropna(subset=[position_col])
            df = df[df[position_col].str.strip() != '']
        
        return df
    
    def _normalize_token_pair(self, pair):
        """Normalize token pair format for consistent pricing"""
        if not pair:
            return pair
            
        pair = pair.strip()
        
        # Handle perpetual positions (show as token/USDC for pricing)
        if 'short' in pair.lower():
            token = pair.replace('short', '').strip().upper()
            return f"{token}/USDC"
        
        # Handle CLM positions with "TOKEN + USD" format
        if '+' in pair and 'USD' in pair.upper():
            token = pair.split('+')[0].strip().upper()
            return f"{token}/USDC"
        
        # Handle standard "TOKEN/TOKEN" format (keep as-is)
        if '/' in pair:
            return pair
            
        return pair
    
    def create_position_id(self, row: pd.Series, strategy: str) -> str:
        """Create unique ID for position"""
        position_col = 'Position Details' if 'Position Details' in row.index else 'Position'
        position_details = str(row.get(position_col, ''))
        entry_date = str(row.get('Entry Date', ''))
        entry_value_col = 'Total Entry Value' if strategy == 'long' else 'Entry Value (cash in)'
        entry_value = str(row.get(entry_value_col, ''))
        
        id_string = f"{position_details}_{entry_date}_{entry_value}_{strategy}"
        return hashlib.md5(id_string.encode()).hexdigest()[:12]
    
    def parse_position(self, row: pd.Series, strategy: str) -> dict:
        """Parse a single position row into standardized format"""
        # Get position details
        position_details = self.get_column_value(row, 'position')
        if not position_details:
            position_details = str(next(iter([v for v in row.values if pd.notna(v)]), 'Unknown'))
        else:
            position_details = str(position_details)
        
        # Extract token pair from position details
        if '|' in position_details:
            _, pair = position_details.split('|', 1)
            pair = pair.strip()
        else:
            pair = position_details
        
        # Get basic fields
        platform = str(self.get_column_value(row, 'platform') or 'Unknown')
        
        # Override strategy if specified in row
        if 'Strategy' in row.index and pd.notna(row['Strategy']):
            strategy = str(row['Strategy']).lower().strip()
        
        # Normalize token pair format for pricing
        pair = self._normalize_token_pair(pair)
        
        # Get entry value
        entry_value = None
        entry_value_raw = self.get_column_value(row, 'entry_value')
        if entry_value_raw:
            entry_value = self.parse_value(entry_value_raw, 'currency')
        
        # Check if position is closed
        status = str(row.get('Status', '')).lower().strip()
        exit_date = row.get('Exit Date')
        is_closed = (status in ['closed', 'close', 'exit', 'exited'] or 
                    (pd.notna(exit_date) and str(exit_date).strip() != ''))
        
        # Create position object
        position = {
            'id': self.create_position_id(row, strategy),
            'position_details': position_details,
            'strategy': strategy,
            'platform': platform,
            'token_pair': pair,
            'chain': str(self.get_column_value(row, 'chain') or 'Unknown'),
            'wallet': str(self.get_column_value(row, 'wallet') or 'Unknown'),
            'entry_value': entry_value,
            'entry_date': str(self.get_column_value(row, 'entry_date') or ''),
            'days_active': float(row.get('Days #')) if pd.notna(row.get('Days #')) else None,
            'min_range': self.parse_value(row.get('Min Range'), 'currency'),
            'max_range': self.parse_value(row.get('Max Range'), 'currency'),
            'exit_date': str(exit_date) if pd.notna(exit_date) and str(exit_date).strip() != '' else None,
            'exit_value': self.parse_value(row.get('Exit Value'), 'currency'),
            'claimed_yield_value': self.parse_value(row.get('Claimed Yield Value'), 'currency'),
            'claimed_yield_return': self.parse_value(row.get('Claimed Yield Return'), 'percentage'),
            'price_return': self.parse_value(row.get('Price Return'), 'percentage'),
            'impermanent_loss': self.parse_value(row.get('IL'), 'percentage'),
            'transaction_fees': self.parse_value(row.get('Transaction Fees'), 'percentage'),
            'slippage': self.parse_value(row.get('Slippage'), 'percentage'),
            'yield_apr': self.parse_value(row.get('Yield APR'), 'percentage'),
            'net_return': self.parse_value(row.get('Net Return'), 'percentage'),
            'status': status if status else ('closed' if is_closed else 'open'),
            'is_active': not is_closed,
            'current_price': None,
            'range_status': 'unknown',
            'last_updated': datetime.now().isoformat()
        }
        
        return position
    
    def save_positions(self):
        """Save positions to separate JSON files"""
        os.makedirs(os.path.dirname(self.long_json), exist_ok=True)
        
        with open(self.long_json, 'w') as f:
            json.dump(self.long_positions, f, indent=2)
        
        with open(self.neutral_json, 'w') as f:
            json.dump(self.neutral_positions, f, indent=2)
            
        with open(self.closed_json, 'w') as f:
            json.dump(self.closed_positions, f, indent=2)
    
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
    
    def load_positions(self) -> bool:
        """Load all position data"""
        self.load_existing_positions()
        total_active = len(self.long_positions) + len(self.neutral_positions)
        if total_active > 0:
            print(f"📊 Loaded {total_active} active positions ({len(self.long_positions)} long, {len(self.neutral_positions)} neutral) + {len(self.closed_positions)} closed")
            return True
        return False
    
    def load_from_csv(self, neutral_csv: str, long_csv: str):
        """Load positions from CSV files"""
        import pandas as pd
        
        # Load neutral positions
        if os.path.exists(neutral_csv):
            neutral_df = pd.read_csv(neutral_csv)
            neutral_df = self.clean_csv_data(neutral_df)
            for _, row in neutral_df.iterrows():
                position = self.parse_position(row, 'neutral')
                if position['is_active']:
                    self.neutral_positions.append(position)
                else:
                    self.closed_positions.append(position)
        
        # Load long positions
        if os.path.exists(long_csv):
            long_df = pd.read_csv(long_csv)
            long_df = self.clean_csv_data(long_df)
            for _, row in long_df.iterrows():
                position = self.parse_position(row, 'long')
                if position['is_active']:
                    self.long_positions.append(position)
                else:
                    self.closed_positions.append(position)
        
        # Save to JSON
        self.save_positions()
        
        total_active = len(self.long_positions) + len(self.neutral_positions)
        print(f"📊 Loaded {total_active} active positions ({len(self.long_positions)} long, {len(self.neutral_positions)} neutral) + {len(self.closed_positions)} closed")
    
    def load_from_combined_csv(self, csv_path: str):
        """Load positions from a single combined CSV file with Strategy column"""
        import pandas as pd
        
        if not os.path.exists(csv_path):
            print(f"❌ File not found: {csv_path}")
            return
        
        print(f"📄 Loading combined CSV: {csv_path}")
        
        # Clear existing positions
        self.long_positions = []
        self.neutral_positions = []
        self.closed_positions = []
        
        try:
            df = pd.read_csv(csv_path)
            df = self.clean_csv_data(df)
            
            for _, row in df.iterrows():
                # Parse position - strategy will be determined from the Strategy column
                position = self.parse_position(row, 'unknown')
                
                if position['is_active']:
                    if position['strategy'] == 'long':
                        self.long_positions.append(position)
                    elif position['strategy'] == 'neutral':
                        self.neutral_positions.append(position)
                    else:
                        print(f"⚠️  Unknown strategy '{position['strategy']}' for position: {position['position_details']}")
                else:
                    self.closed_positions.append(position)
            
            # Save to JSON
            self.save_positions()
            
            total_active = len(self.long_positions) + len(self.neutral_positions)
            print(f"📊 Loaded {total_active} active positions ({len(self.long_positions)} long, {len(self.neutral_positions)} neutral) + {len(self.closed_positions)} closed")
            
        except Exception as e:
            print(f"❌ Error loading combined CSV: {e}")
            return
    
    def load_transactions(self) -> list:
        """Load transaction data from JSON"""
        try:
            with open(self.transactions_json, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_transactions(self, transactions: list):
        """Save transaction data to JSON"""
        os.makedirs(os.path.dirname(self.transactions_json), exist_ok=True)
        with open(self.transactions_json, 'w') as f:
            json.dump(transactions, f, indent=2)
    
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
        
        # Add base tokens for wrapped tokens
        if any(token in ['WBTC', 'CBBTC'] for token in tokens):
            tokens.add('BTC')
        if any(token in ['WETH', 'WHETH'] for token in tokens):
            tokens.add('ETH')
        
        # Try DefiLlama first
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
            self.price_changes = {
                'BTC': 2.3,
                'ETH': 3.1,
                'SOL': 5.2,
                'SUI': 12.5,
                'JLP': 1.1,
                'ORCA': -2.4,
                'RAY': 4.7,
                'USDC': 0.0,
                'USDT': -0.1
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
        defillama_map = {
            'SOL': 'coingecko:solana',
            'ORCA': 'coingecko:orca', 
            'RAY': 'coingecko:raydium',
            'JLP': 'solana:27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4',
            'USDC': 'coingecko:usd-coin',
            'ETH': 'coingecko:ethereum',
            'BTC': 'coingecko:bitcoin',
            'SUI': 'coingecko:sui',
            'WETH': 'coingecko:ethereum',
            'WBTC': 'coingecko:wrapped-bitcoin',
            'CBBTC': 'coingecko:coinbase-wrapped-btc',
            'WHETH': 'coingecko:ethereum',
            'USDT': 'coingecko:tether'
        }
        
        try:
            available_tokens = [token for token in tokens if token in defillama_map]
            if not available_tokens:
                return
                
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
            missing_tokens = [token for token in tokens if token not in self.prices and token in coingecko_map]
            if not missing_tokens:
                return
                
            coingecko_ids = ','.join([coingecko_map[token] for token in missing_tokens])
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_ids}&vs_currencies=usd&include_24hr_change=true"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                price_data = response.json()
                
                for token in missing_tokens:
                    gecko_id = coingecko_map[token]
                    if gecko_id in price_data:
                        self.prices[token] = price_data[gecko_id]['usd']
                        if 'usd_24h_change' in price_data[gecko_id]:
                            self.price_changes[token] = price_data[gecko_id]['usd_24h_change']
                
                coingecko_count = len([t for t in missing_tokens if t in self.prices])
                if coingecko_count > 0:
                    print(f"🦎 CoinGecko: {coingecko_count} tokens")
                    
        except Exception as e:
            print(f"⚠️  CoinGecko API error: {e}")
        
        total_fetched = len(self.prices)
        if total_fetched > 0:
            print(f"📈 Total prices fetched: {total_fetched} tokens")
    
    def _fetch_fx_rates(self):
        """Fetch FX rates from exchangerate-api.io"""
        try:
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
                        # Perpetual position
                        if current_price > position['max_range']:
                            position['range_status'] = 'perp_closed'
                        else:
                            position['range_status'] = 'perp_active'
                    elif not position['min_range'] or not position['max_range']:
                        # Position without valid ranges
                        position['range_status'] = 'no_range'
                    else:
                        # Normal CLM position
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
            jlp_price = self.prices.get('JLP')
            sol_price = self.prices.get('SOL')
            
            if jlp_price and sol_price and sol_price > 0:
                return jlp_price / sol_price
        
        elif pair.upper() in ['WBTC/SOL', 'CBBTC/SOL', 'WHETH/SOL']:
            btc_tokens = ['WBTC', 'CBBTC']
            eth_tokens = ['WHETH', 'WHETF']
            
            if base_token in btc_tokens:
                btc_price = self.prices.get('BTC')
                sol_price = self.prices.get('SOL')
                if btc_price and sol_price and sol_price > 0:
                    return btc_price / sol_price
            elif base_token in eth_tokens:
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