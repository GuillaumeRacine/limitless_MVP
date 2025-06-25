#!/usr/bin/env python3
"""
SUI Data Enhancer - Enhance SUI transaction data with blockchain validation and additional metadata
"""

import pandas as pd
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
from sui_api_validator import SuiAPIValidator
import requests

class SuiDataEnhancer:
    def __init__(self):
        self.validator = SuiAPIValidator()
        self.coin_metadata_cache = {}
        self.price_cache = {}
        
    def get_coin_metadata(self, coin_type: str) -> Dict:
        """Get and cache coin metadata"""
        if coin_type in self.coin_metadata_cache:
            return self.coin_metadata_cache[coin_type]
        
        metadata = self.validator.get_coin_metadata(coin_type)
        if metadata:
            self.coin_metadata_cache[coin_type] = metadata
        return metadata
    
    def get_historical_price(self, symbol: str, timestamp_ms: int) -> Optional[float]:
        """Get historical price from CoinGecko or other sources"""
        # For now, return current price as placeholder
        # In production, would use historical price APIs
        symbol_map = {
            'SUI': 'sui',
            'USDC': 'usd-coin',
            'USDT': 'tether',
            'WETH': 'ethereum',
            'LBTC': 'bitcoin',
            'CETUS': 'cetus-protocol'
        }
        
        coingecko_id = symbol_map.get(symbol.upper())
        if not coingecko_id:
            return None
        
        cache_key = f"{coingecko_id}_{timestamp_ms}"
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]
        
        try:
            # Get current price as approximation
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if coingecko_id in data:
                price = data[coingecko_id]['usd']
                self.price_cache[cache_key] = price
                return price
        except:
            pass
        
        return None
    
    def parse_asset_string(self, asset_str: str) -> Dict:
        """Parse asset string like '-5SUI' or '1245.582512USDC'"""
        if not asset_str or pd.isna(asset_str):
            return {'amount': 0, 'symbol': '', 'direction': ''}
        
        asset_str = str(asset_str).strip()
        
        # Handle negative amounts
        direction = 'out' if asset_str.startswith('-') else 'in'
        asset_str = asset_str.lstrip('-')
        
        # Split number and symbol
        import re
        match = re.match(r'^([\d.]+)([A-Za-z\-]+)$', asset_str)
        if match:
            amount = float(match.group(1))
            symbol = match.group(2)
            return {
                'amount': amount,
                'symbol': symbol,
                'direction': direction
            }
        
        return {'amount': 0, 'symbol': '', 'direction': ''}
    
    def enhance_transaction(self, row: Dict) -> Dict:
        """Enhance a single transaction with blockchain data"""
        enhanced = row.copy()
        
        # Get transaction from blockchain
        digest = row.get('Digest', '')
        if digest:
            tx_data = self.validator.get_transaction(digest)
            if tx_data:
                parsed = self.validator.parse_transaction_data(tx_data)
                if parsed:
                    # Add blockchain data
                    enhanced['block_number'] = parsed.get('checkpoint')
                    enhanced['tx_status'] = parsed.get('status')
                    enhanced['sender'] = parsed.get('sender')
                    enhanced['gas_used_sui'] = parsed.get('gas_used')
                    
                    # Process balance changes
                    total_usd_value = 0
                    for change in parsed.get('balance_changes', []):
                        coin_type = change.get('coin_type', '')
                        amount = change.get('amount', 0)
                        
                        # Get coin metadata
                        metadata = self.get_coin_metadata(coin_type)
                        if metadata:
                            decimals = metadata.get('decimals', 9)
                            symbol = metadata.get('symbol', 'Unknown')
                            
                            # Convert to human readable amount
                            human_amount = amount / (10 ** decimals)
                            
                            # Get USD value
                            price = self.get_historical_price(symbol, parsed.get('timestamp_ms'))
                            if price:
                                usd_value = abs(human_amount * price)
                                total_usd_value += usd_value
                    
                    enhanced['total_usd_value'] = total_usd_value
                    enhanced['validation_status'] = 'verified'
        
        # Parse asset string
        asset_info = self.parse_asset_string(row.get('Asset', ''))
        enhanced['parsed_amount'] = asset_info['amount']
        enhanced['parsed_symbol'] = asset_info['symbol']
        enhanced['parsed_direction'] = asset_info['direction']
        
        # Calculate USD value from parsed asset if not from blockchain
        if 'total_usd_value' not in enhanced and asset_info['symbol']:
            price = self.get_historical_price(asset_info['symbol'], int(row.get('Time', 0)))
            if price:
                enhanced['estimated_usd_value'] = asset_info['amount'] * price
        
        # Classify transaction type
        tx_type = row.get('Type', '').lower()
        enhanced['tx_category'] = self.classify_transaction(tx_type, asset_info)
        
        # Extract platform from interacted addresses
        interacted = row.get('Interacted with', '')
        enhanced['platforms'] = self.extract_platforms(interacted)
        
        return enhanced
    
    def classify_transaction(self, tx_type: str, asset_info: Dict) -> str:
        """Classify transaction into categories"""
        tx_type = tx_type.lower()
        
        if 'swap' in tx_type:
            return 'swap'
        elif 'liquidity' in tx_type or 'lp' in tx_type:
            return 'liquidity'
        elif 'harvest' in tx_type or 'collect' in tx_type:
            return 'farming'
        elif 'stake' in tx_type:
            return 'staking'
        elif 'send' in tx_type or 'receive' in tx_type:
            return 'transfer'
        elif 'mint' in tx_type or 'burn' in tx_type:
            return 'mint_burn'
        else:
            return 'other'
    
    def extract_platforms(self, interacted_str: str) -> List[str]:
        """Extract platform names from interacted addresses"""
        if not interacted_str:
            return []
        
        platforms = []
        # Look for names in parentheses
        import re
        matches = re.findall(r'\(([^)]+)\)', interacted_str)
        
        for match in matches:
            # Clean up platform name
            platform = match.strip()
            if platform and platform.lower() not in ['sui', 'unknown']:
                platforms.append(platform)
        
        return list(set(platforms))  # Remove duplicates
    
    def enhance_csv_file(self, input_path: str, output_path: str = None):
        """Enhance entire CSV file with blockchain data"""
        print(f"Reading CSV file: {input_path}")
        df = pd.read_csv(input_path)
        
        if output_path is None:
            output_path = input_path.replace('.csv', '_enhanced.csv')
        
        enhanced_rows = []
        total = len(df)
        
        print(f"Enhancing {total} transactions...")
        
        for idx, row in df.iterrows():
            print(f"Processing transaction {idx+1}/{total}: {row.get('Digest', 'Unknown')[:8]}...")
            
            try:
                enhanced_row = self.enhance_transaction(row.to_dict())
                enhanced_rows.append(enhanced_row)
            except Exception as e:
                print(f"Error enhancing transaction: {e}")
                enhanced_row = row.to_dict()
                enhanced_row['enhancement_error'] = str(e)
                enhanced_rows.append(enhanced_row)
            
            # Rate limiting
            time.sleep(0.1)
            
            # Save progress every 50 transactions
            if (idx + 1) % 50 == 0:
                temp_df = pd.DataFrame(enhanced_rows)
                temp_df.to_csv(output_path.replace('.csv', '_temp.csv'), index=False)
                print(f"Progress saved: {idx+1}/{total}")
        
        # Create final enhanced dataframe
        enhanced_df = pd.DataFrame(enhanced_rows)
        
        # Add additional calculated columns
        enhanced_df['timestamp_utc'] = pd.to_datetime(enhanced_df['Time'].astype(int), unit='ms', utc=True)
        enhanced_df['date'] = enhanced_df['timestamp_utc'].dt.date
        
        # Sort by timestamp
        enhanced_df = enhanced_df.sort_values('timestamp_utc', ascending=False)
        
        # Save enhanced data
        enhanced_df.to_csv(output_path, index=False)
        print(f"\nEnhanced data saved to: {output_path}")
        
        # Print summary statistics
        self.print_summary(enhanced_df)
        
        return enhanced_df
    
    def print_summary(self, df: pd.DataFrame):
        """Print summary statistics of enhanced data"""
        print("\n" + "="*60)
        print("ENHANCEMENT SUMMARY")
        print("="*60)
        
        print(f"Total transactions: {len(df)}")
        
        # Validation status
        if 'validation_status' in df.columns:
            verified = len(df[df['validation_status'] == 'verified'])
            print(f"Verified transactions: {verified} ({verified/len(df)*100:.1f}%)")
        
        # Transaction categories
        if 'tx_category' in df.columns:
            print("\nTransaction Categories:")
            for category, count in df['tx_category'].value_counts().items():
                print(f"  {category}: {count}")
        
        # Platform distribution
        if 'platforms' in df.columns:
            all_platforms = []
            for platforms in df['platforms'].dropna():
                if isinstance(platforms, list):
                    all_platforms.extend(platforms)
            
            if all_platforms:
                print("\nTop Platforms:")
                platform_counts = pd.Series(all_platforms).value_counts().head(10)
                for platform, count in platform_counts.items():
                    print(f"  {platform}: {count}")
        
        # Value statistics
        if 'total_usd_value' in df.columns or 'estimated_usd_value' in df.columns:
            usd_col = 'total_usd_value' if 'total_usd_value' in df.columns else 'estimated_usd_value'
            total_volume = df[usd_col].sum()
            avg_tx_size = df[usd_col].mean()
            
            print(f"\nValue Statistics:")
            print(f"  Total Volume: ${total_volume:,.2f}")
            print(f"  Average Transaction: ${avg_tx_size:,.2f}")
        
        # Gas statistics
        if 'gas_used_sui' in df.columns:
            total_gas = df['gas_used_sui'].sum()
            avg_gas = df['gas_used_sui'].mean()
            
            print(f"\nGas Statistics:")
            print(f"  Total Gas Used: {total_gas:.6f} SUI")
            print(f"  Average Gas/Tx: {avg_gas:.6f} SUI")

def main():
    """Process all SUI CSV files"""
    enhancer = SuiDataEnhancer()
    
    # Define wallet mappings
    wallets = {
        'long': '0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a',
        'neutral': '0x1df6f74ae73e453bc276d84512f1cd8387b643432163221df4f4c76112bfaf66',
        'yield': '0xa1c48a832320557655096e4fb475df116f9b0215fea51ef1b189e346325b9e2d'
    }
    
    # Process each wallet's transactions
    for strategy, wallet in wallets.items():
        csv_pattern = f"data/sui_{wallet}_activities_*.csv"
        
        # Find matching files
        import glob
        csv_files = glob.glob(csv_pattern)
        
        if csv_files:
            for csv_file in csv_files:
                print(f"\nProcessing {strategy} wallet transactions: {csv_file}")
                output_file = csv_file.replace('.csv', '_enhanced.csv')
                
                try:
                    enhancer.enhance_csv_file(csv_file, output_file)
                except Exception as e:
                    print(f"Error processing {csv_file}: {e}")
        else:
            print(f"No CSV files found for {strategy} wallet")

if __name__ == "__main__":
    main()