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
        self.transactions_json = "data/JSON_out/clm_transactions.json"
        self.balances_json = "data/JSON_out/clm_balances.json"
        self.csv_tracking_json = "data/JSON_out/csv_tracking.json"
        
        # Data folder for automatic scanning
        self.data_folder = "data"
        
        # Enhanced CSV column mappings for different sources
        self.column_mappings = {
            'default': {
                'position': ['Position Details', 'Position', 'Token Pair'],
                'wallet': ['Wallet', 'Wallet Address', 'Address'],
                'chain': ['Chain', 'Blockchain', 'Network'],
                'platform': ['Platform', 'Protocol', 'Exchange'],
                'entry_value': ['Total Entry Value', 'Entry Value (cash in)', 'Entry Amount'],
                'entry_date': ['Entry Date', 'Date', 'Timestamp'],
                'transaction_id': ['Transaction ID', 'Tx Hash', 'Hash', 'Entry Tx'],
                'exit_transaction_id': ['Exit Transaction ID', 'Exit Tx Hash', 'Exit Hash'],
                'gas_fees': ['Gas Fees', 'Network Fees', 'Transaction Fees Total'],
                'contract_address': ['Contract Address', 'Pool Address', 'Token Address'],
                'current_balance': ['Current Balance', 'Balance', 'LP Tokens'],
                'token_a_balance': ['Token A Balance', 'Base Token Balance'],
                'token_b_balance': ['Token B Balance', 'Quote Token Balance'],
                'block_number': ['Block Number', 'Block', 'Entry Block']
            },
            'transaction_export': {
                'position': ['Transaction ID', 'Tx Hash', 'Hash'],
                'wallet': ['Wallet Address', 'Address', 'Wallet'],
                'chain': ['Chain', 'Blockchain', 'Network'],
                'platform': ['Platform', 'Protocol', 'Exchange'],
                'entry_date': ['Timestamp', 'Date', 'Entry Date'],
                'transaction_id': ['Transaction ID', 'Tx Hash', 'Hash'],
                'gas_fees': ['Gas Fees', 'Network Fees'],
                'contract_address': ['Contract Address', 'Pool Address'],
                'block_number': ['Block Number', 'Block']
            },
            'balance_export': {
                'position': ['Token Pair', 'Position', 'Position Details'],
                'wallet': ['Wallet Address', 'Address', 'Wallet'],
                'chain': ['Chain', 'Blockchain', 'Network'],
                'platform': ['Platform', 'Protocol', 'Exchange'],
                'contract_address': ['Contract Address', 'Pool Address', 'Token Address'],
                'current_balance': ['Current Balance', 'Balance', 'LP Tokens'],
                'token_a_balance': ['Token A Balance', 'Base Token Balance'],
                'token_b_balance': ['Token B Balance', 'Quote Token Balance']
            }
        }
        
    def get_file_hash(self, filepath: str) -> str:
        """Get MD5 hash of file to detect changes"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except FileNotFoundError:
            return ""
    
    def discover_csv_files(self) -> dict:
        """Discover all CSV files in data folder and classify them"""
        import glob
        
        csv_files = glob.glob(os.path.join(self.data_folder, "*.csv"))
        classified_files = {
            'positions': {'long': [], 'neutral': []},
            'transactions': [],
            'balances': [],
            'unknown': []
        }
        
        for csv_file in csv_files:
            file_name = os.path.basename(csv_file).lower()
            
            # Skip files that look like they contain format instructions
            if any(skip in file_name for skip in ['sample', 'example', 'template', 'format']):
                continue
            
            # Classify based on filename patterns
            if 'long' in file_name and 'position' in file_name:
                classified_files['positions']['long'].append(csv_file)
            elif 'neutral' in file_name and 'position' in file_name:
                classified_files['positions']['neutral'].append(csv_file)
            elif any(keyword in file_name for keyword in ['transaction', 'tx', 'trade']):
                classified_files['transactions'].append(csv_file)
            elif any(keyword in file_name for keyword in ['balance', 'portfolio', 'holding']):
                classified_files['balances'].append(csv_file)
            else:
                # Try to classify by analyzing file content
                classified_files['unknown'].append(csv_file)
        
        return classified_files
    
    def classify_unknown_csv(self, csv_path: str) -> str:
        """Analyze CSV content to determine its type"""
        try:
            # Read just the header to classify
            df = pd.read_csv(csv_path, nrows=0)
            columns = [col.lower() for col in df.columns]
            
            # Look for position-related columns
            position_indicators = ['position', 'token pair', 'platform', 'entry value', 'min range', 'max range']
            if any(indicator in ' '.join(columns) for indicator in position_indicators):
                return 'positions'
            
            # Look for transaction-related columns
            transaction_indicators = ['transaction id', 'tx hash', 'hash', 'block number', 'gas fees']
            if any(indicator in ' '.join(columns) for indicator in transaction_indicators):
                return 'transactions'
            
            # Look for balance-related columns
            balance_indicators = ['balance', 'lp tokens', 'token a balance', 'token b balance']
            if any(indicator in ' '.join(columns) for indicator in balance_indicators):
                return 'balances'
            
            return 'unknown'
            
        except Exception as e:
            print(f"⚠️  Error analyzing {csv_path}: {e}")
            return 'unknown'
    
    def load_csv_tracking(self) -> dict:
        """Load CSV file tracking metadata"""
        try:
            with open(self.csv_tracking_json, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'processed_files': {}, 'last_scan': ''}
    
    def save_csv_tracking(self, tracking_data: dict):
        """Save CSV file tracking metadata"""
        os.makedirs(os.path.dirname(self.csv_tracking_json), exist_ok=True)
        with open(self.csv_tracking_json, 'w') as f:
            json.dump(tracking_data, f, indent=2)
    
    def auto_detect_and_process_csvs(self) -> dict:
        """Automatically detect and process new/changed CSV files"""
        print("🔍 Scanning for CSV files in data folder...")
        
        # Load tracking data
        tracking_data = self.load_csv_tracking()
        processed_files = tracking_data.get('processed_files', {})
        
        # Discover all CSV files
        classified_files = self.discover_csv_files()
        
        # Classify unknown files
        for unknown_file in classified_files['unknown']:
            file_type = self.classify_unknown_csv(unknown_file)
            if file_type == 'positions':
                # Default to neutral if we can't determine strategy from filename
                classified_files['positions']['neutral'].append(unknown_file)
            elif file_type in ['transactions', 'balances']:
                classified_files[file_type].append(unknown_file)
        
        # Process results
        results = {
            'new_files': [],
            'updated_files': [],
            'unchanged_files': [],
            'processed_data': {
                'positions': {'long': [], 'neutral': []},
                'transactions': [],
                'balances': []
            },
            'errors': []
        }
        
        # Check each file for changes
        all_files = (
            classified_files['positions']['long'] + 
            classified_files['positions']['neutral'] + 
            classified_files['transactions'] + 
            classified_files['balances']
        )
        
        for csv_file in all_files:
            current_hash = self.get_file_hash(csv_file)
            file_info = processed_files.get(csv_file, {})
            stored_hash = file_info.get('hash', '')
            
            if not current_hash:
                continue  # File doesn't exist or can't be read
            
            if current_hash != stored_hash:
                # File is new or changed
                if stored_hash:
                    results['updated_files'].append(csv_file)
                    print(f"📝 Updated: {os.path.basename(csv_file)}")
                else:
                    results['new_files'].append(csv_file)
                    print(f"✨ New: {os.path.basename(csv_file)}")
                
                # Process the file
                try:
                    processed_data = self._process_single_csv(csv_file, classified_files)
                    if processed_data:
                        # Merge processed data
                        for category in processed_data:
                            if category in results['processed_data']:
                                if isinstance(results['processed_data'][category], dict):
                                    for subcategory in processed_data[category]:
                                        results['processed_data'][category][subcategory].extend(
                                            processed_data[category][subcategory]
                                        )
                                else:
                                    results['processed_data'][category].extend(processed_data[category])
                    
                    # Update tracking
                    processed_files[csv_file] = {
                        'hash': current_hash,
                        'last_processed': datetime.now().isoformat(),
                        'file_type': self._get_file_type_from_classified(csv_file, classified_files)
                    }
                    
                except Exception as e:
                    error_msg = f"Error processing {csv_file}: {e}"
                    results['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
            else:
                results['unchanged_files'].append(csv_file)
        
        # Update tracking data
        tracking_data['processed_files'] = processed_files
        tracking_data['last_scan'] = datetime.now().isoformat()
        self.save_csv_tracking(tracking_data)
        
        # Print summary
        total_new = len(results['new_files']) + len(results['updated_files'])
        if total_new > 0:
            print(f"\n📊 Processing complete:")
            print(f"   🆕 {len(results['new_files'])} new files")
            print(f"   📝 {len(results['updated_files'])} updated files")
            print(f"   ➡️  {len(results['unchanged_files'])} unchanged files")
            if results['errors']:
                print(f"   ❌ {len(results['errors'])} errors")
        else:
            print("✅ No new or updated CSV files found")
        
        return results
    
    def _get_file_type_from_classified(self, csv_file: str, classified_files: dict) -> str:
        """Helper to determine file type from classified files dict"""
        if csv_file in classified_files['positions']['long']:
            return 'positions_long'
        elif csv_file in classified_files['positions']['neutral']:
            return 'positions_neutral'
        elif csv_file in classified_files['transactions']:
            return 'transactions'
        elif csv_file in classified_files['balances']:
            return 'balances'
        return 'unknown'
    
    def _process_single_csv(self, csv_file: str, classified_files: dict) -> dict:
        """Process a single CSV file based on its classification"""
        results = {'positions': {'long': [], 'neutral': []}, 'transactions': [], 'balances': []}
        
        try:
            if csv_file in classified_files['positions']['long']:
                # Process as long positions
                df = pd.read_csv(csv_file)
                df = self.clean_csv_data(df)
                csv_format = self.detect_csv_format(df)
                
                for _, row in df.iterrows():
                    position = self.parse_position(row, 'long', csv_format)
                    results['positions']['long'].append(position)
            
            elif csv_file in classified_files['positions']['neutral']:
                # Process as neutral positions
                df = pd.read_csv(csv_file)
                df = self.clean_csv_data(df)
                csv_format = self.detect_csv_format(df)
                
                for _, row in df.iterrows():
                    position = self.parse_position(row, 'neutral', csv_format)
                    results['positions']['neutral'].append(position)
            
            elif csv_file in classified_files['transactions']:
                # Process as transactions
                transactions = self.import_transaction_csv(csv_file)
                results['transactions'] = transactions
            
            elif csv_file in classified_files['balances']:
                # Process as balances
                balances = self.import_balance_csv(csv_file)
                results['balances'] = balances
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing {csv_file}: {e}")
            return None
    
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
    
    def detect_csv_format(self, df):
        """Detect CSV format and return appropriate column mapping"""
        columns = df.columns.tolist()
        
        # Check for transaction-focused format (wallet exports)
        if any(col in columns for col in ['Transaction ID', 'Tx Hash', 'Hash']):
            return 'transaction_export'
        
        # Check for balance-focused format (portfolio snapshots)
        elif any(col in columns for col in ['Current Balance', 'LP Tokens']):
            return 'balance_export'
        
        # Default to existing position format
        else:
            return 'default'
    
    def get_column_value(self, row, field_type, csv_format='default'):
        """Get value from row using flexible column mapping"""
        possible_columns = self.column_mappings.get(csv_format, {}).get(field_type, [])
        
        for col_name in possible_columns:
            if col_name in row.index and pd.notna(row[col_name]):
                return row[col_name]
        return None
    
    def clean_csv_data(self, df):
        """Remove format/instruction rows from CSV"""
        # Handle both 'Position Details' and 'Position' column names
        position_col = 'Position Details' if 'Position Details' in df.columns else 'Position'
        
        # If no position column found, try to find the main identifier column
        if position_col not in df.columns:
            for possible_col in ['Transaction ID', 'Tx Hash', 'Address', 'Token']:
                if possible_col in df.columns:
                    position_col = possible_col
                    break
        
        if position_col in df.columns:
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
    
    def parse_position(self, row: pd.Series, strategy: str, csv_format: str = 'default') -> dict:
        """Parse a single position row into standardized format with enhanced fields"""
        # Get position details using flexible column mapping
        position_details = self.get_column_value(row, 'position', csv_format)
        if not position_details:
            position_details = str(next(iter([v for v in row.values if pd.notna(v)]), 'Unknown'))
        else:
            position_details = str(position_details)
        
        # Extract platform and token pair
        if '|' in position_details:
            platform, pair = position_details.split('|', 1)
            platform = platform.strip()
            pair = pair.strip()
        else:
            platform_val = self.get_column_value(row, 'platform', csv_format)
            platform = str(platform_val) if platform_val else 'Unknown'
            pair = position_details
        
        # Normalize token pair format for pricing
        pair = self._normalize_token_pair(pair)
        
        # Get entry value using flexible mapping
        entry_value = None
        entry_value_raw = self.get_column_value(row, 'entry_value', csv_format)
        if entry_value_raw:
            entry_value = self.parse_currency(entry_value_raw)
        
        # Check if position is closed
        status = str(row.get('Status', '')).lower().strip()
        exit_date = row.get('Exit Date')
        is_closed = (status in ['closed', 'close', 'exit', 'exited'] or 
                    (pd.notna(exit_date) and str(exit_date).strip() != ''))
        
        # Enhanced position data structure
        position = {
            'id': self.create_position_id(row, strategy),
            'position_details': position_details,
            'strategy': strategy,
            'platform': platform,
            'token_pair': pair,
            'chain': str(self.get_column_value(row, 'chain', csv_format) or 'Unknown'),
            'wallet': str(self.get_column_value(row, 'wallet', csv_format) or 'Unknown'),
            'entry_value': entry_value,
            'entry_date': str(self.get_column_value(row, 'entry_date', csv_format) or ''),
            'days_active': float(row.get('Days #')) if pd.notna(row.get('Days #')) else None,
            'min_range': float(row['Min Range']) if pd.notna(row.get('Min Range')) else None,
            'max_range': float(row['Max Range']) if pd.notna(row.get('Max Range')) else None,
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
            'last_updated': datetime.now().isoformat(),
            
            # Enhanced transaction and balance tracking
            'transaction_data': {
                'entry_tx_id': str(self.get_column_value(row, 'transaction_id', csv_format) or ''),
                'exit_tx_id': str(self.get_column_value(row, 'exit_transaction_id', csv_format) or ''),
                'gas_fees_paid': self.parse_currency(self.get_column_value(row, 'gas_fees', csv_format)),
                'block_number': str(self.get_column_value(row, 'block_number', csv_format) or '')
            },
            'contract_data': {
                'contract_address': str(self.get_column_value(row, 'contract_address', csv_format) or ''),
                'pool_address': str(self.get_column_value(row, 'contract_address', csv_format) or '')
            },
            'balance_data': {
                'current_lp_balance': self.parse_currency(self.get_column_value(row, 'current_balance', csv_format)),
                'token_a_balance': self.parse_currency(self.get_column_value(row, 'token_a_balance', csv_format)),
                'token_b_balance': self.parse_currency(self.get_column_value(row, 'token_b_balance', csv_format))
            }
        }
        
        return position
    
    def import_transaction_csv(self, csv_path: str, chain: str = None) -> list:
        """Import transactions from wallet/DEX export CSV"""
        try:
            df = pd.read_csv(csv_path)
            df = self.clean_csv_data(df)
            
            csv_format = self.detect_csv_format(df)
            transactions = []
            
            for _, row in df.iterrows():
                transaction = {
                    'id': hashlib.md5(str(row.to_dict()).encode()).hexdigest()[:12],
                    'tx_hash': str(self.get_column_value(row, 'transaction_id', csv_format) or ''),
                    'wallet': str(self.get_column_value(row, 'wallet', csv_format) or ''),
                    'chain': chain or str(self.get_column_value(row, 'chain', csv_format) or 'Unknown'),
                    'platform': str(self.get_column_value(row, 'platform', csv_format) or 'Unknown'),
                    'timestamp': str(self.get_column_value(row, 'entry_date', csv_format) or ''),
                    'gas_fees': self.parse_currency(self.get_column_value(row, 'gas_fees', csv_format)),
                    'block_number': str(self.get_column_value(row, 'block_number', csv_format) or ''),
                    'contract_address': str(self.get_column_value(row, 'contract_address', csv_format) or ''),
                    'imported_at': datetime.now().isoformat(),
                    'raw_data': row.to_dict()  # Keep original data for reference
                }
                transactions.append(transaction)
            
            print(f"✅ Imported {len(transactions)} transactions from {csv_path}")
            return transactions
            
        except Exception as e:
            print(f"❌ Error importing {csv_path}: {e}")
            return []
    
    def import_balance_csv(self, csv_path: str, chain: str = None) -> list:
        """Import current balances from portfolio snapshot CSV"""
        try:
            df = pd.read_csv(csv_path)
            df = self.clean_csv_data(df)
            
            csv_format = self.detect_csv_format(df)
            balances = []
            
            for _, row in df.iterrows():
                balance = {
                    'id': hashlib.md5(str(row.to_dict()).encode()).hexdigest()[:12],
                    'wallet': str(self.get_column_value(row, 'wallet', csv_format) or ''),
                    'chain': chain or str(self.get_column_value(row, 'chain', csv_format) or 'Unknown'),
                    'platform': str(self.get_column_value(row, 'platform', csv_format) or 'Unknown'),
                    'token_pair': str(self.get_column_value(row, 'position', csv_format) or ''),
                    'lp_balance': self.parse_currency(self.get_column_value(row, 'current_balance', csv_format)),
                    'token_a_balance': self.parse_currency(self.get_column_value(row, 'token_a_balance', csv_format)),
                    'token_b_balance': self.parse_currency(self.get_column_value(row, 'token_b_balance', csv_format)),
                    'contract_address': str(self.get_column_value(row, 'contract_address', csv_format) or ''),
                    'snapshot_date': datetime.now().isoformat(),
                    'raw_data': row.to_dict()
                }
                balances.append(balance)
            
            print(f"✅ Imported {len(balances)} balance records from {csv_path}")
            return balances
            
        except Exception as e:
            print(f"❌ Error importing {csv_path}: {e}")
            return []
    
    def import_multi_chain_csvs(self, csv_configs: list) -> dict:
        """Import multiple CSV files from different chains and sources
        
        Args:
            csv_configs: List of dicts with format:
            [
                {'path': 'sol_transactions.csv', 'chain': 'SOL', 'type': 'transactions'},
                {'path': 'eth_balances.csv', 'chain': 'ETH', 'type': 'balances'},
                {'path': 'sui_positions.csv', 'chain': 'SUI', 'type': 'positions', 'strategy': 'long'}
            ]
        """
        results = {
            'transactions': [],
            'balances': [],
            'positions': {'long': [], 'neutral': []},
            'errors': []
        }
        
        for config in csv_configs:
            csv_path = config.get('path')
            chain = config.get('chain', 'Unknown')
            import_type = config.get('type', 'positions')
            
            if not os.path.exists(csv_path):
                results['errors'].append(f"File not found: {csv_path}")
                continue
            
            try:
                if import_type == 'transactions':
                    transactions = self.import_transaction_csv(csv_path, chain)
                    results['transactions'].extend(transactions)
                    
                elif import_type == 'balances':
                    balances = self.import_balance_csv(csv_path, chain)
                    results['balances'].extend(balances)
                    
                elif import_type == 'positions':
                    strategy = config.get('strategy', 'neutral')
                    df = pd.read_csv(csv_path)
                    df = self.clean_csv_data(df)
                    csv_format = self.detect_csv_format(df)
                    
                    for _, row in df.iterrows():
                        position = self.parse_position(row, strategy, csv_format)
                        # Override chain if specified in config
                        if chain != 'Unknown':
                            position['chain'] = chain
                        results['positions'][strategy].append(position)
                        
            except Exception as e:
                results['errors'].append(f"Error processing {csv_path}: {e}")
        
        print(f"🔄 Multi-chain import complete:")
        print(f"   📊 {len(results['positions']['long'])} long positions")
        print(f"   ⚖️  {len(results['positions']['neutral'])} neutral positions")
        print(f"   💰 {len(results['balances'])} balance records")
        print(f"   🔗 {len(results['transactions'])} transactions")
        if results['errors']:
            print(f"   ❌ {len(results['errors'])} errors")
        
        return results
    
    def merge_incremental_data(self, processed_data: dict):
        """Merge new processed data with existing data, avoiding duplicates"""
        print("🔄 Merging new data with existing positions...")
        
        # Load existing data
        self.load_existing_positions()
        existing_transactions = self.load_transactions()
        existing_balances = self.load_balances()
        
        # Track changes
        stats = {
            'positions': {'new': 0, 'updated': 0, 'moved_to_closed': 0},
            'transactions': {'new': 0, 'duplicates': 0},
            'balances': {'new': 0, 'updated': 0}
        }
        
        # Create lookup dictionaries for existing data
        existing_long = {pos['id']: pos for pos in self.long_positions}
        existing_neutral = {pos['id']: pos for pos in self.neutral_positions}
        existing_closed = {pos['id']: pos for pos in self.closed_positions}
        existing_tx_ids = {tx['id'] for tx in existing_transactions}
        existing_balance_ids = {bal['id'] for bal in existing_balances}
        
        # Process new positions
        for strategy in ['long', 'neutral']:
            for new_position in processed_data['positions'][strategy]:
                position_id = new_position['id']
                existing_dict = existing_long if strategy == 'long' else existing_neutral
                
                if not new_position['is_active']:
                    # Move to closed positions
                    if position_id not in existing_closed:
                        stats['positions']['moved_to_closed'] += 1
                        print(f"📁 Moving to closed: {new_position['position_details']}")
                    
                    # Remove from active lists and add to closed
                    self.long_positions = [p for p in self.long_positions if p['id'] != position_id]
                    self.neutral_positions = [p for p in self.neutral_positions if p['id'] != position_id]
                    self.closed_positions = [p for p in self.closed_positions if p['id'] != position_id]
                    self.closed_positions.append(new_position)
                    
                else:
                    # Active position
                    if position_id in existing_dict:
                        # Update existing position, preserve price data
                        existing_pos = existing_dict[position_id]
                        new_position['current_price'] = existing_pos.get('current_price')
                        new_position['range_status'] = existing_pos.get('range_status', 'unknown')
                        stats['positions']['updated'] += 1
                    else:
                        stats['positions']['new'] += 1
                        print(f"✨ New {strategy} position: {new_position['position_details']}")
                    
                    # Update the appropriate list
                    if strategy == 'long':
                        self.long_positions = [p for p in self.long_positions if p['id'] != position_id]
                        self.long_positions.append(new_position)
                    else:
                        self.neutral_positions = [p for p in self.neutral_positions if p['id'] != position_id]
                        self.neutral_positions.append(new_position)
        
        # Process new transactions (avoid duplicates)
        new_transactions = []
        for transaction in processed_data['transactions']:
            if transaction['id'] not in existing_tx_ids:
                new_transactions.append(transaction)
                stats['transactions']['new'] += 1
            else:
                stats['transactions']['duplicates'] += 1
        
        if new_transactions:
            print(f"💰 {len(new_transactions)} new transactions")
            existing_transactions.extend(new_transactions)
            self.save_transactions(existing_transactions)
        
        # Process new balances (update or add)
        updated_balances = existing_balances.copy()
        for balance in processed_data['balances']:
            if balance['id'] not in existing_balance_ids:
                updated_balances.append(balance)
                stats['balances']['new'] += 1
                print(f"💼 New balance record: {balance['token_pair']}")
            else:
                # Update existing balance
                for i, existing_bal in enumerate(updated_balances):
                    if existing_bal['id'] == balance['id']:
                        updated_balances[i] = balance
                        stats['balances']['updated'] += 1
                        break
        
        if stats['balances']['new'] > 0 or stats['balances']['updated'] > 0:
            self.save_balances(updated_balances)
        
        # Save updated positions
        self.save_positions()
        
        # Print summary
        print(f"\\n✅ Merge complete:")
        print(f"   📊 Positions: {stats['positions']['new']} new, {stats['positions']['updated']} updated, {stats['positions']['moved_to_closed']} moved to closed")
        print(f"   💰 Transactions: {stats['transactions']['new']} new, {stats['transactions']['duplicates']} duplicates skipped")
        print(f"   💼 Balances: {stats['balances']['new']} new, {stats['balances']['updated']} updated")
        print(f"   📈 Total active: {len(self.long_positions)} long + {len(self.neutral_positions)} neutral = {len(self.long_positions) + len(self.neutral_positions)}")
    
    def update_positions(self, neutral_csv: str, long_csv: str):
        """Update positions with incremental changes (legacy method - use auto_detect_and_process_csvs instead)"""
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
            
            # Detect CSV format for flexible parsing
            csv_format = self.detect_csv_format(df)
            if csv_format != 'default':
                print(f"📊 Detected {csv_format} format for {csv_path}")
            
            for _, row in df.iterrows():
                position = self.parse_position(row, strategy, csv_format)
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
    
    def save_transactions(self, transactions: list):
        """Save transaction data to JSON"""
        os.makedirs(os.path.dirname(self.transactions_json), exist_ok=True)
        with open(self.transactions_json, 'w') as f:
            json.dump(transactions, f, indent=2)
    
    def save_balances(self, balances: list):
        """Save balance data to JSON"""
        os.makedirs(os.path.dirname(self.balances_json), exist_ok=True)
        with open(self.balances_json, 'w') as f:
            json.dump(balances, f, indent=2)
    
    def load_transactions(self) -> list:
        """Load transaction data from JSON"""
        try:
            with open(self.transactions_json, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def load_balances(self) -> list:
        """Load balance data from JSON"""
        try:
            with open(self.balances_json, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
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