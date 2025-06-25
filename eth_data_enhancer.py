#!/usr/bin/env python3
"""
ETH Data Enhancer - Classify unknown ETH transactions and backfill missing data using APIs
"""

from clm_data import CLMDataManager
from eth_api_validator import EthereumAPIValidator
import pandas as pd
import json
import time
from datetime import datetime, timezone
import uuid

class ETHDataEnhancer:
    def __init__(self):
        self.data_manager = CLMDataManager()
        self.validator = EthereumAPIValidator()
        
        # ETH wallets from .env with strategies
        self.eth_wallets = {
            "0x862f26238d773Fde4E29156f3Bb7CF58eA4cD1af": "Long",
            "0x52Ad60E77D2CAb7EdDCafC1f169Af354f2b1508a": "Neutral",
            "0xaa9650695251fd56Aaea2B0A5FB91573849E1a3d": "Yield"
        }
        
        # Supported chains
        self.supported_chains = ['ethereum', 'base', 'arbitrum', 'optimism', 'polygon']
        
        # Chain name mappings
        self.chain_mappings = {
            'ethereum': 'ethereum',
            'base': 'base', 
            'arbitrum': 'arbitrum',
            'optimism': 'optimism',
            'polygon': 'polygon'
        }
    
    def classify_unknown_eth_transactions(self):
        """Classify unknown transactions that are actually ETH/L2 transactions"""
        print("🔍 CLASSIFYING UNKNOWN ETH/L2 TRANSACTIONS")
        print("="*60)
        
        # Load existing transactions
        transactions = self.data_manager.load_transactions()
        df = pd.DataFrame(transactions)
        
        # Filter for known ETH chains first to see current state
        eth_chains = ['ethereum', 'base', 'arbitrum', 'optimism', 'polygon']
        current_eth_txs = df[df['chain'].isin(eth_chains)]
        
        print(f"📊 Current ETH/L2 transactions in database: {len(current_eth_txs)}")
        for chain in eth_chains:
            count = len(df[df['chain'] == chain])
            if count > 0:
                print(f"  {chain}: {count}")
        
        # Look for ETH indicators in remaining transactions
        # After SOL enhancement, we shouldn't have 'Unknown' chain, but let's check other chains
        potential_eth_txs = df[~df['chain'].isin(eth_chains + ['SOL'])].copy()
        
        print(f"📊 Analyzing {len(potential_eth_txs)} transactions for ETH indicators...")
        
        eth_candidates = []
        
        for idx, tx in potential_eth_txs.iterrows():
            raw_data = tx.get('raw_data', {})
            
            # Check for ETH indicators
            is_eth = False
            eth_indicators = []
            chain_detected = None
            
            # Check for direct chain indicators
            for field in ['Chain', 'Network', 'Blockchain']:
                if field in raw_data:
                    value = str(raw_data[field]).lower()
                    if 'ethereum' in value or 'eth' in value:
                        is_eth = True
                        chain_detected = 'ethereum'
                        eth_indicators.append(f'{field}={value}')
                    elif 'base' in value:
                        is_eth = True
                        chain_detected = 'base'
                        eth_indicators.append(f'{field}={value}')
                    elif 'arbitrum' in value or 'arb' in value:
                        is_eth = True
                        chain_detected = 'arbitrum'
                        eth_indicators.append(f'{field}={value}')
                    elif 'optimism' in value or 'op' in value:
                        is_eth = True
                        chain_detected = 'optimism'
                        eth_indicators.append(f'{field}={value}')
                    elif 'polygon' in value or 'matic' in value:
                        is_eth = True
                        chain_detected = 'polygon'
                        eth_indicators.append(f'{field}={value}')
            
            # Check for ETH token indicators
            coin_symbol = raw_data.get('Coin Symbol', '').upper()
            if coin_symbol in ['ETH', 'WETH', 'USDC', 'USDT', 'WBTC', 'DAI']:
                is_eth = True
                if not chain_detected:
                    chain_detected = 'ethereum'  # Default to mainnet
                eth_indicators.append(f'Token={coin_symbol}')
            
            # Check for currency indicators
            for field in ['Buy Currency', 'Sell Currency', 'Fee Currency']:
                if field in raw_data:
                    value = str(raw_data[field]).upper()
                    if value in ['ETH', 'ETHEREUM']:
                        is_eth = True
                        if not chain_detected:
                            chain_detected = 'ethereum'
                        eth_indicators.append(f'{field}={value}')
            
            # Check for platform indicators
            platform = raw_data.get('Platform', '').lower()
            exchange = raw_data.get('Exchange', '').lower()
            
            if any(p in platform for p in ['uniswap', 'aero', 'curve', 'sushiswap']):
                is_eth = True
                if 'aero' in platform:
                    chain_detected = 'base'
                elif not chain_detected:
                    chain_detected = 'ethereum'
                eth_indicators.append(f'Platform={platform}')
            
            if any(e in exchange for e in ['uniswap', 'coinbase', 'binance']):
                is_eth = True
                if not chain_detected:
                    chain_detected = 'ethereum'
                eth_indicators.append(f'Exchange={exchange}')
            
            if is_eth:
                eth_candidates.append({
                    'index': idx,
                    'transaction': tx,
                    'indicators': eth_indicators,
                    'detected_chain': chain_detected or 'ethereum',
                    'coin_symbol': coin_symbol
                })
        
        print(f"✅ Found {len(eth_candidates)} transactions with ETH/L2 indicators")
        
        if len(eth_candidates) == 0:
            print("❌ No ETH candidates found in remaining transactions")
            return 0
        
        # Show sample of candidates
        print(f"\n🔬 Sample ETH candidates:")
        for i, candidate in enumerate(eth_candidates[:5]):
            tx = candidate['transaction']
            raw_data = tx.get('raw_data', {})
            print(f"  #{i+1}: {candidate['detected_chain']} | {candidate['coin_symbol']} | {' | '.join(candidate['indicators'])}")
            print(f"       Type: {raw_data.get('Type', 'N/A')}, Amount: {raw_data.get('Amount', 'N/A')}")
        
        # Classify and update transactions
        updated_count = 0
        
        for candidate in eth_candidates:
            idx = candidate['index']
            tx = candidate['transaction']
            raw_data = tx.get('raw_data', {})
            detected_chain = candidate['detected_chain']
            
            # Update the transaction
            df.at[idx, 'chain'] = detected_chain
            
            # Try to infer platform from token/type
            platform = self.infer_eth_platform(raw_data, detected_chain)
            df.at[idx, 'platform'] = platform
            
            # Try to infer wallet address
            wallet = self.infer_eth_wallet(raw_data, platform, detected_chain)
            if wallet:
                df.at[idx, 'wallet'] = wallet
            
            # Update gas fees if available
            fee_amount = raw_data.get('Fee Amount')
            if fee_amount and str(fee_amount).lower() != 'nan':
                try:
                    # Convert various fee formats
                    fee_float = float(str(fee_amount).replace('$', '').replace(',', ''))
                    df.at[idx, 'gas_fees'] = fee_float
                except:
                    pass
            
            updated_count += 1
        
        # Save updated transactions
        updated_transactions = df.to_dict('records')
        self.data_manager.save_transactions(updated_transactions)
        
        print(f"\n✅ Successfully classified {updated_count} transactions as ETH/L2")
        print(f"📊 Updated chain distribution:")
        
        chain_counts = df['chain'].value_counts()
        for chain, count in chain_counts.items():
            print(f"  {chain}: {count:,} transactions")
        
        return updated_count
    
    def infer_eth_platform(self, raw_data, chain):
        """Infer ETH platform from transaction data"""
        coin_symbol = raw_data.get('Coin Symbol', '').upper()
        tx_type = raw_data.get('Type', '').lower()
        platform = raw_data.get('Platform', '').lower()
        exchange = raw_data.get('Exchange', '').lower()
        
        # Platform mapping based on chain and indicators
        if chain == 'base':
            if 'aero' in platform or coin_symbol == 'AERO':
                return 'Aerodrome'
            else:
                return 'Base'
        
        elif chain == 'arbitrum':
            return 'Arbitrum'
        
        elif chain == 'optimism':
            return 'Optimism'
        
        elif chain == 'polygon':
            return 'Polygon'
        
        else:  # ethereum mainnet
            if 'uniswap' in platform or 'uniswap' in exchange:
                return 'Uniswap'
            elif 'curve' in platform:
                return 'Curve'
            elif 'sushiswap' in platform:
                return 'SushiSwap'
            elif tx_type in ['received', 'sent']:
                return 'Transfer'
            elif tx_type in ['sell', 'buy']:
                return 'DEX'
            else:
                return 'Ethereum'
    
    def infer_eth_wallet(self, raw_data, platform, chain):
        """Infer ETH wallet based on platform, chain, and strategy patterns"""
        
        # Check if wallet address is in raw_data
        for field in ['Wallet Address', 'From', 'To', 'Address']:
            if field in raw_data and raw_data[field]:
                addr = str(raw_data[field]).strip()
                # Normalize case for comparison
                for wallet_addr in self.eth_wallets.keys():
                    if addr.lower() == wallet_addr.lower():
                        return wallet_addr
        
        # Infer based on chain and platform patterns
        coin_symbol = raw_data.get('Coin Symbol', '').upper()
        tx_type = raw_data.get('Type', '').lower()
        amount = raw_data.get('Amount', 0)
        
        # Try to extract numeric amount for analysis
        try:
            if isinstance(amount, str):
                amount_val = float(amount.replace('$', '').replace(',', ''))
            else:
                amount_val = float(amount)
        except:
            amount_val = 0
        
        # Strategy inference based on patterns
        
        # Long strategy: Usually active trading, DEX usage, larger amounts
        if (platform in ['Uniswap', 'Aerodrome', 'DEX'] or 
            coin_symbol in ['WETH', 'WBTC'] or
            (amount_val > 1000 and tx_type in ['buy', 'sell'])):
            return "0x862f26238d773Fde4E29156f3Bb7CF58eA4cD1af"  # Long wallet
        
        # Neutral strategy: Stable trading, USDC focus
        elif (coin_symbol in ['USDC', 'USDT', 'DAI'] and 
              tx_type in ['received', 'sent'] and 
              amount_val < 10000):
            return "0x52Ad60E77D2CAb7EdDCafC1f169Af354f2b1508a"  # Neutral wallet
        
        # Yield strategy: Small amounts, transfers, yield claiming
        elif (tx_type == 'received' and amount_val < 1000) or 'yield' in str(raw_data).lower():
            return "0xaa9650695251fd56Aaea2B0A5FB91573849E1a3d"  # Yield wallet
        
        # Base chain often used for Long strategy
        elif chain == 'base':
            return "0x862f26238d773Fde4E29156f3Bb7CF58eA4cD1af"  # Long wallet
        
        return None  # Let the system infer later
    
    def backfill_eth_transactions(self, limit_per_wallet_chain=10):
        """Backfill missing ETH transactions using API data (limited due to rate limits)"""
        print(f"\n🔄 BACKFILLING MISSING ETH TRANSACTIONS")
        print("="*60)
        
        # Load existing transactions to avoid duplicates
        existing_transactions = self.data_manager.load_transactions()
        existing_hashes = set()
        
        for tx in existing_transactions:
            if tx.get('tx_hash'):
                existing_hashes.add(tx['tx_hash'].lower())
        
        print(f"📊 Existing transaction hashes in database: {len(existing_hashes)}")
        
        new_transactions = []
        total_found = 0
        
        # Process each wallet on each chain
        for wallet_address, strategy in self.eth_wallets.items():
            print(f"\n🔗 Backfilling {strategy} wallet: {wallet_address[:16]}...")
            
            for chain in self.supported_chains[:2]:  # Limit to ETH and Base for now due to API limits
                print(f"  ⛓️  {chain.upper()}:")
                
                try:
                    # Get transfers from API (limited count due to rate limits)
                    transfers = self.validator.get_asset_transfers(
                        wallet_address, 
                        chain, 
                        category=["external", "erc20"],  # Simplified categories
                        max_count=limit_per_wallet_chain
                    )
                    
                    if not transfers:
                        print(f"    ❌ No transfers found or rate limited")
                        continue
                    
                    print(f"    📊 Found {len(transfers)} transfers from API")
                    
                    # Filter out existing transactions
                    new_transfers = []
                    for transfer in transfers:
                        tx_hash = transfer.get('hash', '').lower()
                        if tx_hash and tx_hash not in existing_hashes:
                            new_transfers.append(transfer)
                    
                    print(f"    ✨ New transfers to process: {len(new_transfers)}")
                    
                    # Process new transactions
                    processed = 0
                    for transfer in new_transfers:
                        try:
                            parsed_transfer = self.validator.parse_transfer(transfer, wallet_address, chain)
                            
                            if parsed_transfer and parsed_transfer.get('hash'):
                                # Convert to our transaction format
                                new_tx = self.convert_api_to_transaction_format(
                                    parsed_transfer, strategy, chain
                                )
                                new_transactions.append(new_tx)
                                existing_hashes.add(parsed_transfer['hash'].lower())  # Avoid duplicates
                                processed += 1
                                
                                if processed % 3 == 0:
                                    print(f"      Processed {processed} transactions...")
                        except Exception as e:
                            print(f"      ⚠️ Error processing transfer: {e}")
                    
                    print(f"    ✅ Successfully processed {processed} new transactions")
                    total_found += processed
                    
                except Exception as e:
                    print(f"    ❌ Error fetching transfers for {chain}: {e}")
                
                # Add delay between chains to respect rate limits
                time.sleep(1)
            
            # Add delay between wallets
            time.sleep(2)
        
        if new_transactions:
            # Add new transactions to existing data
            all_transactions = existing_transactions + new_transactions
            self.data_manager.save_transactions(all_transactions)
            
            print(f"\n✅ BACKFILL COMPLETE")
            print(f"📊 Added {len(new_transactions)} new ETH/L2 transactions")
            print(f"📊 Total transactions now: {len(all_transactions)}")
        else:
            print(f"\n📊 No new transactions found to backfill (may be rate limited)")
        
        return len(new_transactions)
    
    def convert_api_to_transaction_format(self, parsed_transfer, strategy, chain):
        """Convert API transfer format to our standard transaction format"""
        
        # Create transaction record
        transaction = {
            'id': str(uuid.uuid4())[:12],
            'tx_hash': parsed_transfer['hash'],
            'wallet': parsed_transfer['wallet_address'],
            'chain': chain,
            'platform': parsed_transfer.get('platform', 'Ethereum'),
            'timestamp': parsed_transfer.get('block_timestamp', ''),
            'gas_fees': 0,  # Would need separate API call to get exact gas fees
            'block_number': parsed_transfer.get('block_num', ''),
            'contract_address': '',
            'imported_at': datetime.now().isoformat(),
            'raw_data': {
                'Strategy': strategy,
                'Hash': parsed_transfer['hash'],
                'From': parsed_transfer.get('from', ''),
                'To': parsed_transfer.get('to', ''),
                'Asset': parsed_transfer.get('asset', ''),
                'Value': parsed_transfer.get('value_numeric', 0),
                'Category': parsed_transfer.get('category', ''),
                'Type': parsed_transfer.get('tx_type', ''),
                'Chain': chain,
                'Source': 'Ethereum API'
            }
        }
        
        return transaction

def main():
    """Main ETH enhancement process"""
    print("🚀 ETH DATA ENHANCEMENT PROCESS")
    print("="*80)
    
    enhancer = ETHDataEnhancer()
    
    # Phase 1: Classify unknown ETH transactions
    print("PHASE 1: Classifying Unknown ETH/L2 Transactions")
    classified_count = enhancer.classify_unknown_eth_transactions()
    
    # Phase 2: Backfill missing transactions from API (limited)
    print("\nPHASE 2: Backfilling Missing Transactions (Limited)")
    backfilled_count = enhancer.backfill_eth_transactions(limit_per_wallet_chain=15)
    
    # Summary
    print(f"\n🎯 ETH ENHANCEMENT SUMMARY")
    print("="*50)
    print(f"✅ Classified unknown transactions: {classified_count}")
    print(f"✅ Backfilled from API: {backfilled_count}")
    print(f"🚀 Total ETH data improvements: {classified_count + backfilled_count}")
    
    if classified_count > 0 or backfilled_count > 0:
        print(f"\n💡 Your ETH transaction data is now significantly more complete!")
        print(f"🔍 ETH/L2 transactions should now be properly classified and enhanced")
    
    print(f"\n✅ ETH enhancement completed!")
    print(f"📊 Note: API rate limits restrict full backfill - upgrade to paid tier for complete data")

if __name__ == "__main__":
    main()