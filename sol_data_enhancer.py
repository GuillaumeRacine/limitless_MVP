#!/usr/bin/env python3
"""
SOL Data Enhancer - Classify unknown SOL transactions and backfill missing data using API
"""

from clm_data import CLMDataManager
from sol_api_validator import SolanaAPIValidator
import pandas as pd
import json
import time
from datetime import datetime, timezone
import uuid

class SOLDataEnhancer:
    def __init__(self):
        self.data_manager = CLMDataManager()
        self.validator = SolanaAPIValidator()
        
        # SOL wallets from .env with strategies
        self.sol_wallets = {
            "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k": "Long",
            "Djrzp7SyiTsDre41hgaUCh99Aw7PrchetGDbdm3GfHo6": "Neutral", 
            "GKvUys93yYe4U1a82u2k4VDvsxQLeCtaGyeggfh1hoBk": "Yield"
        }
    
    def classify_unknown_sol_transactions(self):
        """Classify unknown transactions that are actually SOL transactions"""
        print("🔍 CLASSIFYING UNKNOWN SOL TRANSACTIONS")
        print("="*60)
        
        # Load existing transactions
        transactions = self.data_manager.load_transactions()
        df = pd.DataFrame(transactions)
        
        # Filter for unknown transactions
        unknown_txs = df[df['chain'] == 'Unknown'].copy()
        
        print(f"📊 Total unknown transactions: {len(unknown_txs)}")
        
        # Identify SOL indicators
        sol_candidates = []
        
        for idx, tx in unknown_txs.iterrows():
            raw_data = tx.get('raw_data', {})
            
            # Check for SOL indicators
            is_sol = False
            sol_indicators = []
            
            if raw_data.get('Portfolio') == 'Solana':
                is_sol = True
                sol_indicators.append('Portfolio=Solana')
            
            if raw_data.get('Fee Currency') == 'solana':
                is_sol = True
                sol_indicators.append('Fee Currency=solana')
            
            coin_symbol = raw_data.get('Coin Symbol', '')
            if coin_symbol in ['SOL', 'RAY', 'ORCA', 'JLP', 'USDC']:  # Common SOL tokens
                is_sol = True
                sol_indicators.append(f'Token={coin_symbol}')
            
            if is_sol:
                sol_candidates.append({
                    'index': idx,
                    'transaction': tx,
                    'indicators': sol_indicators,
                    'coin_symbol': coin_symbol
                })
        
        print(f"✅ Found {len(sol_candidates)} transactions with SOL indicators")
        
        if len(sol_candidates) == 0:
            print("❌ No SOL candidates found")
            return 0
        
        # Show sample of candidates
        print(f"\n🔬 Sample SOL candidates:")
        for i, candidate in enumerate(sol_candidates[:5]):
            tx = candidate['transaction']
            raw_data = tx.get('raw_data', {})
            print(f"  #{i+1}: {candidate['coin_symbol']} | {' | '.join(candidate['indicators'])}")
            print(f"       Amount: {raw_data.get('Amount', 'N/A')}, Type: {raw_data.get('Type', 'N/A')}")
        
        # Classify and update transactions
        updated_count = 0
        
        for candidate in sol_candidates:
            idx = candidate['index']
            tx = candidate['transaction']
            raw_data = tx.get('raw_data', {})
            
            # Update the transaction
            df.at[idx, 'chain'] = 'SOL'
            
            # Try to infer platform from token/type
            platform = self.infer_sol_platform(raw_data)
            df.at[idx, 'platform'] = platform
            
            # Try to infer wallet address
            wallet = self.infer_sol_wallet(raw_data, platform)
            if wallet:
                df.at[idx, 'wallet'] = wallet
            
            # Update gas fees if available
            fee_amount = raw_data.get('Fee Amount')
            if fee_amount and str(fee_amount).lower() != 'nan':
                try:
                    df.at[idx, 'gas_fees'] = float(fee_amount)
                except:
                    pass
            
            updated_count += 1
        
        # Save updated transactions
        updated_transactions = df.to_dict('records')
        self.data_manager.save_transactions(updated_transactions)
        
        print(f"\n✅ Successfully classified {updated_count} transactions as SOL")
        print(f"📊 Updated chain distribution:")
        
        chain_counts = df['chain'].value_counts()
        for chain, count in chain_counts.items():
            print(f"  {chain}: {count:,} transactions")
        
        return updated_count
    
    def infer_sol_platform(self, raw_data):
        """Infer SOL platform from transaction data"""
        coin_symbol = raw_data.get('Coin Symbol', '')
        tx_type = raw_data.get('Type', '')
        
        # Platform mapping based on tokens and patterns
        if coin_symbol == 'RAY':
            return 'Raydium'
        elif coin_symbol == 'ORCA':
            return 'Orca'
        elif coin_symbol == 'JLP':
            return 'Jupiter'
        elif tx_type in ['Received', 'Sent']:
            return 'Transfer'
        elif tx_type in ['Sell', 'Buy']:
            return 'DEX'
        else:
            return 'Solana'
    
    def infer_sol_wallet(self, raw_data, platform):
        """Infer SOL wallet based on platform and strategy patterns"""
        
        # Check if wallet address is in raw_data
        for field in ['Wallet Address', 'From', 'To', 'Address']:
            if field in raw_data and raw_data[field]:
                addr = str(raw_data[field]).strip()
                if addr in self.sol_wallets:
                    return addr
        
        # Infer based on platform patterns
        coin_symbol = raw_data.get('Coin Symbol', '')
        tx_type = raw_data.get('Type', '')
        
        # Long strategy platforms/tokens
        if platform in ['Orca', 'Raydium', 'Jupiter'] or coin_symbol in ['RAY', 'ORCA', 'JLP']:
            return "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k"  # Long wallet
        
        # Neutral strategy indicators
        elif coin_symbol == 'USDC' and tx_type in ['Received', 'Sent']:
            return "Djrzp7SyiTsDre41hgaUCh99Aw7PrchetGDbdm3GfHo6"  # Neutral wallet
        
        # Yield wallet for transfers
        elif tx_type == 'Received' and coin_symbol == 'SOL':
            return "GKvUys93yYe4U1a82u2k4VDvsxQLeCtaGyeggfh1hoBk"  # Yield wallet
        
        return None  # Let the system infer later
    
    def backfill_api_transactions(self, limit_per_wallet=50):
        """Backfill missing transactions using API data"""
        print(f"\n🔄 BACKFILLING MISSING SOL TRANSACTIONS")
        print("="*60)
        
        # Load existing transactions to avoid duplicates
        existing_transactions = self.data_manager.load_transactions()
        existing_signatures = set()
        
        for tx in existing_transactions:
            if tx.get('tx_hash'):
                existing_signatures.add(tx['tx_hash'])
        
        print(f"📊 Existing signatures in database: {len(existing_signatures)}")
        
        new_transactions = []
        total_found = 0
        
        for wallet_address, strategy in self.sol_wallets.items():
            print(f"\n🔗 Backfilling {strategy} wallet: {wallet_address[:16]}...")
            
            # Get signatures from API
            signatures = self.validator.get_confirmed_signatures(wallet_address, limit=limit_per_wallet)
            
            if not signatures:
                print(f"  ❌ No signatures found")
                continue
            
            print(f"  📊 Found {len(signatures)} signatures from API")
            
            # Filter out existing signatures
            new_signatures = [sig for sig in signatures if sig['signature'] not in existing_signatures]
            print(f"  ✨ New signatures to process: {len(new_signatures)}")
            
            # Process new transactions (limit to avoid rate limits)
            processed = 0
            for sig_info in new_signatures[:20]:  # Limit to 20 new transactions per wallet
                signature = sig_info['signature']
                
                # Add delay to respect rate limits
                time.sleep(0.3)
                
                # Get transaction details
                tx_details = self.validator.get_transaction_details(signature)
                
                if tx_details:
                    parsed_tx = self.validator.parse_transaction(tx_details, wallet_address)
                    
                    if parsed_tx:
                        # Convert to our transaction format
                        new_tx = self.convert_api_to_transaction_format(parsed_tx, strategy)
                        new_transactions.append(new_tx)
                        processed += 1
                        
                        if processed % 5 == 0:
                            print(f"    Processed {processed} transactions...")
                else:
                    print(f"    ⚠️ Failed to fetch details for {signature[:16]}...")
            
            print(f"  ✅ Successfully processed {processed} new transactions")
            total_found += processed
            
            # Add delay between wallets
            time.sleep(1)
        
        if new_transactions:
            # Add new transactions to existing data
            all_transactions = existing_transactions + new_transactions
            self.data_manager.save_transactions(all_transactions)
            
            print(f"\n✅ BACKFILL COMPLETE")
            print(f"📊 Added {len(new_transactions)} new SOL transactions")
            print(f"📊 Total transactions now: {len(all_transactions)}")
        else:
            print(f"\n📊 No new transactions found to backfill")
        
        return len(new_transactions)
    
    def convert_api_to_transaction_format(self, parsed_tx, strategy):
        """Convert API transaction format to our standard format"""
        
        # Determine platform from instructions
        platform = 'Solana'
        for instruction in parsed_tx.get('instructions', []):
            program_name = instruction.get('program_name', '')
            if 'Orca' in program_name:
                platform = 'Orca'
                break
            elif 'Raydium' in program_name:
                platform = 'Raydium'
                break
            elif 'Jupiter' in program_name:
                platform = 'Jupiter'
                break
        
        # Create transaction record
        transaction = {
            'id': str(uuid.uuid4())[:12],
            'tx_hash': parsed_tx['signature'],
            'wallet': parsed_tx['wallet_address'],
            'chain': 'SOL',
            'platform': platform,
            'timestamp': parsed_tx.get('timestamp', ''),
            'gas_fees': parsed_tx.get('fee', 0) / 1_000_000_000,  # Convert lamports to SOL
            'block_number': parsed_tx.get('slot', ''),
            'contract_address': '',
            'imported_at': datetime.now().isoformat(),
            'raw_data': {
                'Strategy': strategy,
                'Signature': parsed_tx['signature'],
                'Slot': parsed_tx.get('slot'),
                'Status': parsed_tx.get('status', 'success'),
                'Instructions': len(parsed_tx.get('instructions', [])),
                'Programs': [inst.get('program_name', '') for inst in parsed_tx.get('instructions', [])],
                'SPL_Transfers': len(parsed_tx.get('spl_transfers', [])),
                'Source': 'Solana API'
            }
        }
        
        return transaction

def main():
    """Main enhancement process"""
    print("🚀 SOL DATA ENHANCEMENT PROCESS")
    print("="*80)
    
    enhancer = SOLDataEnhancer()
    
    # Phase 1: Classify unknown SOL transactions
    print("PHASE 1: Classifying Unknown SOL Transactions")
    classified_count = enhancer.classify_unknown_sol_transactions()
    
    # Phase 2: Backfill missing transactions from API
    print("\nPHASE 2: Backfilling Missing Transactions")
    backfilled_count = enhancer.backfill_api_transactions(limit_per_wallet=25)
    
    # Summary
    print(f"\n🎯 ENHANCEMENT SUMMARY")
    print("="*50)
    print(f"✅ Classified unknown transactions: {classified_count}")
    print(f"✅ Backfilled from API: {backfilled_count}")
    print(f"🚀 Total SOL data improvements: {classified_count + backfilled_count}")
    
    if classified_count > 0 or backfilled_count > 0:
        print(f"\n💡 Your SOL transaction data is now significantly more complete!")
        print(f"🔍 Recommend running the transaction view to see the improvements")
    
    print(f"\n✅ SOL enhancement completed!")

if __name__ == "__main__":
    main()