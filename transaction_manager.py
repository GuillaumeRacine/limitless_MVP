"""
Transaction Manager - CSV Import and Transaction Matching System
Handles multi-chain transaction data import and matching to positions
"""

import pandas as pd
import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import hashlib
import os
from pathlib import Path

@dataclass
class UnifiedTransaction:
    """Unified transaction format across all chains"""
    tx_id: str
    chain: str
    wallet_address: str
    timestamp: datetime
    type: str  # deposit, withdraw, swap, claim, fee, received, sent
    token_in: Optional[str]
    token_out: Optional[str] 
    amount_in: Optional[float]
    amount_out: Optional[float]
    gas_fee: Optional[float]
    platform: Optional[str]
    notes: Optional[str]
    raw_data: dict
    confidence_score: float = 0.0
    matched_position_id: Optional[str] = None

class TransactionDatabase:
    """SQLite database for storing transactions and matches"""
    
    def __init__(self, db_path: str = "data/transactions.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                tx_id TEXT PRIMARY KEY,
                chain TEXT NOT NULL,
                wallet_address TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                token_in TEXT,
                token_out TEXT,
                amount_in REAL,
                amount_out REAL,
                gas_fee REAL,
                platform TEXT,
                notes TEXT,
                raw_data TEXT,
                confidence_score REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Transaction matches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT NOT NULL,
                position_id TEXT,
                match_type TEXT, -- position, fee, yield, other
                confidence_score REAL,
                matched_by TEXT, -- auto, manual
                matched_at TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (tx_id) REFERENCES transactions(tx_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_transaction(self, transaction: UnifiedTransaction):
        """Insert a transaction into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO transactions 
            (tx_id, chain, wallet_address, timestamp, type, token_in, token_out,
             amount_in, amount_out, gas_fee, platform, notes, raw_data, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction.tx_id,
            transaction.chain,
            transaction.wallet_address,
            transaction.timestamp.isoformat(),
            transaction.type,
            transaction.token_in,
            transaction.token_out,
            transaction.amount_in,
            transaction.amount_out,
            transaction.gas_fee,
            transaction.platform,
            transaction.notes,
            json.dumps(transaction.raw_data),
            transaction.confidence_score
        ))
        
        conn.commit()
        conn.close()
    
    def get_transactions(self, wallet_address: str = None, chain: str = None) -> List[UnifiedTransaction]:
        """Retrieve transactions with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if wallet_address:
            query += " AND wallet_address = ?"
            params.append(wallet_address)
        
        if chain:
            query += " AND chain = ?"
            params.append(chain)
            
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            tx = UnifiedTransaction(
                tx_id=row[0],
                chain=row[1], 
                wallet_address=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                type=row[4],
                token_in=row[5],
                token_out=row[6],
                amount_in=row[7],
                amount_out=row[8],
                gas_fee=row[9],
                platform=row[10],
                notes=row[11],
                raw_data=json.loads(row[12]) if row[12] else {},
                confidence_score=row[13] or 0.0
            )
            transactions.append(tx)
        
        return transactions

class CSVImporter:
    """Import transactions from various CSV formats"""
    
    def __init__(self, db: TransactionDatabase):
        self.db = db
    
    def import_coinstats_csv(self, csv_path: str, wallet_address: str, chain: str = "SOL") -> List[UnifiedTransaction]:
        """Import CoinStats format CSV (Solana transactions)"""
        df = pd.read_csv(csv_path)
        transactions = []
        
        for _, row in df.iterrows():
            # Generate unique transaction ID from row data
            tx_id = self._generate_tx_id(row, wallet_address)
            
            # Parse timestamp
            timestamp = pd.to_datetime(row['Date'])
            
            # Determine transaction type and tokens
            tx_type = row['Type'].lower()
            token_symbol = row['Coin Symbol']
            amount = float(row['Amount']) if pd.notna(row['Amount']) else 0.0
            
            # Parse fee information
            gas_fee = None
            if pd.notna(row['Fee Amount']) and row['Fee Amount'] != '':
                try:
                    gas_fee = float(row['Fee Amount'])
                except (ValueError, TypeError):
                    gas_fee = 0.0
            
            # Create unified transaction
            transaction = UnifiedTransaction(
                tx_id=tx_id,
                chain=chain,
                wallet_address=wallet_address,
                timestamp=timestamp,
                type=tx_type,
                token_in=token_symbol if tx_type in ['buy', 'received'] else None,
                token_out=token_symbol if tx_type in ['sell', 'sent'] else None,
                amount_in=amount if tx_type in ['buy', 'received'] else None,
                amount_out=amount if tx_type in ['sell', 'sent'] else None,
                gas_fee=gas_fee,
                platform=row['Exchange'] if pd.notna(row['Exchange']) else None,
                notes=row['Notes'] if pd.notna(row['Notes']) else None,
                raw_data={
                    'portfolio': row['Portfolio'],
                    'coin_name': row['Coin Name'],
                    'pair': row.get('Pair', ''),
                    'price': row.get('Price', ''),
                    'price_usd': row.get('Price USD', ''),
                    'fee_percent': row.get('Fee Percent', ''),
                    'fee_currency': row.get('Fee Currency', '')
                }
            )
            
            transactions.append(transaction)
            self.db.insert_transaction(transaction)
        
        print(f"Imported {len(transactions)} transactions from {csv_path}")
        return transactions
    
    def import_zerion_csv(self, csv_path: str, wallet_address: str, chain: str) -> List[UnifiedTransaction]:
        """Import Zerion format CSV (placeholder - need actual format)"""
        # TODO: Implement once we have actual Zerion CSV format
        print(f"Zerion CSV import not yet implemented for {csv_path}")
        return []
    
    def _generate_tx_id(self, row, wallet_address: str) -> str:
        """Generate unique transaction ID from row data"""
        # Combine key fields to create unique hash
        unique_string = f"{wallet_address}_{row['Date']}_{row['Type']}_{row['Amount']}_{row['Coin Symbol']}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]

class WalletConfig:
    """Wallet configuration management"""
    
    def __init__(self, config_path: str = "data/wallet_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load wallet configuration from JSON file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "SOL": {
                    "long_strategy": "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k",
                    "neutral_strategy": "Djrzp7SyiTsDre41hgaUCh99Aw7PrchetGDbdm3GfHo6",
                    "yield_wallet": ""
                },
                "ETH": {
                    "long_strategy": "",
                    "neutral_strategy": "",
                    "yield_wallet": ""
                },
                "SUI": {
                    "long_strategy": "",
                    "neutral_strategy": "",
                    "yield_wallet": ""
                }
            }
    
    def save_config(self):
        """Save wallet configuration to JSON file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_wallet_strategy(self, wallet_address: str) -> Optional[str]:
        """Determine strategy type for a wallet address"""
        for chain, wallets in self.config.items():
            for strategy, address in wallets.items():
                if address == wallet_address:
                    return strategy
        return None
    
    def get_chain_wallets(self, chain: str) -> Dict[str, str]:
        """Get all wallets for a specific chain"""
        return self.config.get(chain, {})

class TransactionMatcher:
    """Match transactions to positions using various strategies"""
    
    def __init__(self, db: TransactionDatabase):
        self.db = db
    
    def match_transactions_to_positions(self, positions: List[Dict]) -> Dict:
        """Match all transactions to positions and return match results"""
        results = {
            'high_confidence': [],
            'medium_confidence': [],
            'low_confidence': [],
            'unmatched': []
        }
        
        transactions = self.db.get_transactions()
        
        for transaction in transactions:
            matches = self._find_position_matches(transaction, positions)
            
            if not matches:
                results['unmatched'].append(transaction)
            else:
                best_match = max(matches, key=lambda x: x['confidence'])
                
                if best_match['confidence'] >= 0.8:
                    results['high_confidence'].append({
                        'transaction': transaction,
                        'position': best_match['position'],
                        'confidence': best_match['confidence']
                    })
                elif best_match['confidence'] >= 0.5:
                    results['medium_confidence'].append({
                        'transaction': transaction,
                        'position': best_match['position'], 
                        'confidence': best_match['confidence']
                    })
                else:
                    results['low_confidence'].append({
                        'transaction': transaction,
                        'position': best_match['position'],
                        'confidence': best_match['confidence']
                    })
        
        return results
    
    def _find_position_matches(self, transaction: UnifiedTransaction, positions: List[Dict]) -> List[Dict]:
        """Find potential position matches for a transaction"""
        matches = []
        
        for position in positions:
            confidence = 0.0
            
            # Wallet address match (high weight)
            if transaction.wallet_address == position.get('wallet'):
                confidence += 0.4
            
            # Chain match
            if transaction.chain.upper() == position.get('chain', '').upper():
                confidence += 0.2
            
            # Token pair matching
            position_tokens = self._extract_tokens_from_pair(position.get('token_pair', ''))
            tx_tokens = [transaction.token_in, transaction.token_out]
            
            if any(token in position_tokens for token in tx_tokens if token):
                confidence += 0.2
            
            # Platform match
            if transaction.platform and transaction.platform.lower() == position.get('platform', '').lower():
                confidence += 0.1
            
            # Amount proximity (for entry transactions)
            if transaction.amount_in and position.get('entry_value'):
                amount_diff = abs(transaction.amount_in - position['entry_value']) / position['entry_value']
                if amount_diff < 0.05:  # Within 5%
                    confidence += 0.1
            
            if confidence > 0.3:  # Minimum threshold
                matches.append({
                    'position': position,
                    'confidence': confidence
                })
        
        return matches
    
    def _extract_tokens_from_pair(self, token_pair: str) -> List[str]:
        """Extract individual tokens from token pair string"""
        if not token_pair:
            return []
        
        # Handle different formats: "SOL/USDC", "SOL + USD", "JLP / SOL"
        separators = ['/', '+', '-']
        for sep in separators:
            if sep in token_pair:
                tokens = [token.strip() for token in token_pair.split(sep)]
                return tokens
        
        return [token_pair.strip()]

class TransactionManager:
    """Main transaction management interface"""
    
    def __init__(self):
        self.db = TransactionDatabase()
        self.csv_importer = CSVImporter(self.db)
        self.wallet_config = WalletConfig()
        self.matcher = TransactionMatcher(self.db)
    
    def import_csv_file(self, csv_path: str, format_type: str, wallet_address: str, chain: str):
        """Import CSV file with specified format"""
        if format_type.lower() == 'coinstats':
            return self.csv_importer.import_coinstats_csv(csv_path, wallet_address, chain)
        elif format_type.lower() == 'zerion':
            return self.csv_importer.import_zerion_csv(csv_path, wallet_address, chain)
        else:
            raise ValueError(f"Unsupported CSV format: {format_type}")
    
    def get_transaction_summary(self) -> Dict:
        """Get summary of all transactions"""
        transactions = self.db.get_transactions()
        
        summary = {
            'total_transactions': len(transactions),
            'by_chain': {},
            'by_type': {},
            'by_wallet': {}
        }
        
        for tx in transactions:
            # By chain
            summary['by_chain'][tx.chain] = summary['by_chain'].get(tx.chain, 0) + 1
            
            # By type
            summary['by_type'][tx.type] = summary['by_type'].get(tx.type, 0) + 1
            
            # By wallet
            summary['by_wallet'][tx.wallet_address] = summary['by_wallet'].get(tx.wallet_address, 0) + 1
        
        return summary
    
    def run_matching_analysis(self, positions: List[Dict]) -> Dict:
        """Run transaction matching analysis against positions"""
        return self.matcher.match_transactions_to_positions(positions)