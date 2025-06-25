#!/usr/bin/env python3
"""
Solana API Validator - Cross-validate and augment SOL transaction data using Solana RPC
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional

class SolanaAPIValidator:
    def __init__(self, rpc_url="https://api.mainnet-beta.solana.com"):
        self.rpc_url = rpc_url
        self.session = requests.Session()
        
    def get_account_info(self, wallet_address: str) -> Dict:
        """Get basic account information"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [
                wallet_address,
                {"encoding": "base64"}
            ]
        }
        
        response = self.session.post(self.rpc_url, json=payload)
        return response.json()
    
    def get_confirmed_signatures(self, wallet_address: str, limit: int = 1000, before: str = None) -> List[Dict]:
        """Get all confirmed transaction signatures for a wallet"""
        params = [wallet_address, {"limit": limit}]
        if before:
            params[1]["before"] = before
            
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": params
        }
        
        response = self.session.post(self.rpc_url, json=payload)
        result = response.json()
        
        if 'result' in result:
            return result['result']
        else:
            print(f"Error getting signatures: {result}")
            return []
    
    def get_transaction_details(self, signature: str) -> Optional[Dict]:
        """Get detailed transaction information"""
        payload = {
            "jsonrpc": "2.0", 
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "json",
                    "maxSupportedTransactionVersion": 0,
                    "commitment": "confirmed"
                }
            ]
        }
        
        response = self.session.post(self.rpc_url, json=payload)
        result = response.json()
        
        if 'result' in result and result['result']:
            return result['result']
        return None
    
    def parse_transaction(self, tx_data: Dict, wallet_address: str) -> Dict:
        """Parse raw transaction data into structured format"""
        if not tx_data:
            return None
            
        meta = tx_data.get('meta', {})
        transaction = tx_data.get('transaction', {})
        
        # Basic transaction info
        parsed_tx = {
            'signature': transaction.get('signatures', [''])[0],
            'slot': tx_data.get('slot'),
            'block_time': tx_data.get('blockTime'),
            'fee': meta.get('fee', 0),
            'status': 'success' if meta.get('err') is None else 'failed',
            'wallet_address': wallet_address
        }
        
        # Convert timestamp
        if parsed_tx['block_time']:
            parsed_tx['timestamp'] = datetime.fromtimestamp(
                parsed_tx['block_time'], 
                tz=timezone.utc
            ).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Parse account keys and instructions
        message = transaction.get('message', {})
        account_keys = message.get('accountKeys', [])
        instructions = message.get('instructions', [])
        
        # Try to identify the transaction type and involved tokens
        parsed_tx['instructions'] = []
        parsed_tx['token_transfers'] = []
        
        for instruction in instructions:
            program_id_index = instruction.get('programId')
            if isinstance(program_id_index, int) and program_id_index < len(account_keys):
                program_id = account_keys[program_id_index]
                
                parsed_instruction = {
                    'program_id': program_id,
                    'accounts': [account_keys[i] for i in instruction.get('accounts', []) if i < len(account_keys)],
                    'data': instruction.get('data', '')
                }
                
                # Identify known programs
                parsed_instruction['program_name'] = self.identify_program(program_id)
                parsed_tx['instructions'].append(parsed_instruction)
        
        # Parse token balance changes
        pre_balances = meta.get('preBalances', [])
        post_balances = meta.get('postBalances', [])
        
        for i, account in enumerate(account_keys):
            if i < len(pre_balances) and i < len(post_balances):
                balance_change = post_balances[i] - pre_balances[i]
                if balance_change != 0:
                    parsed_tx['token_transfers'].append({
                        'account': account,
                        'balance_change': balance_change,
                        'is_main_wallet': account == wallet_address
                    })
        
        # Parse SPL token transfers
        if 'preTokenBalances' in meta and 'postTokenBalances' in meta:
            parsed_tx['spl_transfers'] = self.parse_spl_transfers(
                meta['preTokenBalances'], 
                meta['postTokenBalances'],
                wallet_address
            )
        
        return parsed_tx
    
    def identify_program(self, program_id: str) -> str:
        """Identify known Solana programs"""
        known_programs = {
            '11111111111111111111111111111111': 'System Program',
            'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA': 'SPL Token',
            'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL': 'Associated Token',
            'ComputeBudget111111111111111111111111111111': 'Compute Budget',
            '9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP': 'Orca',
            'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc': 'Orca Whirlpools',
            'RVKd61ztZW9GUwhRbbLoYVRE5Xf1B2tVscKqwZqXgEr': 'Raydium AMM',
            'CAMMCzo5YL8w4VFF8KVHrK22GGUQpMkFr654shPq32i3': 'Raydium CLMM',
            'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4': 'Jupiter',
            'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB': 'Jupiter V4',
        }
        
        return known_programs.get(program_id, f'Unknown ({program_id[:8]}...)')
    
    def parse_spl_transfers(self, pre_balances: List, post_balances: List, wallet_address: str) -> List[Dict]:
        """Parse SPL token transfers"""
        transfers = []
        
        # Create lookup by account
        pre_lookup = {balance['accountIndex']: balance for balance in pre_balances}
        post_lookup = {balance['accountIndex']: balance for balance in post_balances}
        
        # Find all account indices involved
        all_indices = set(pre_lookup.keys()) | set(post_lookup.keys())
        
        for account_index in all_indices:
            pre_balance = pre_lookup.get(account_index, {})
            post_balance = post_lookup.get(account_index, {})
            
            pre_amount = float(pre_balance.get('uiTokenAmount', {}).get('uiAmount', 0))
            post_amount = float(post_balance.get('uiTokenAmount', {}).get('uiAmount', 0))
            
            if pre_amount != post_amount:
                mint = post_balance.get('mint') or pre_balance.get('mint')
                owner = post_balance.get('owner') or pre_balance.get('owner')
                
                transfers.append({
                    'mint': mint,
                    'owner': owner,
                    'amount_change': post_amount - pre_amount,
                    'decimals': post_balance.get('uiTokenAmount', {}).get('decimals', 0),
                    'is_main_wallet': owner == wallet_address
                })
        
        return transfers

def validate_sol_wallets():
    """Main function to validate SOL wallet data"""
    print("🔍 SOLANA WALLET VALIDATION")
    print("="*70)
    
    # Your SOL wallets from .env
    sol_wallets = {
        "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k": "Long",
        "Djrzp7SyiTsDre41hgaUCh99Aw7PrchetGDbdm3GfHo6": "Neutral", 
        "GKvUys93yYe4U1a82u2k4VDvsxQLeCtaGyeggfh1hoBk": "Yield"
    }
    
    validator = SolanaAPIValidator()
    
    for wallet_address, strategy in sol_wallets.items():
        print(f"\n🔗 Validating {strategy} Strategy Wallet")
        print(f"📧 Address: {wallet_address}")
        print("-" * 60)
        
        # Get account info
        account_info = validator.get_account_info(wallet_address)
        if 'result' in account_info and account_info['result']:
            lamports = account_info['result']['value']['lamports']
            sol_balance = lamports / 1_000_000_000  # Convert lamports to SOL
            print(f"💰 Current SOL Balance: {sol_balance:.6f} SOL")
        else:
            print("⚠️  Could not fetch account info")
            continue
        
        # Get transaction signatures (limit to 50 for initial test)
        print(f"📊 Fetching recent transactions...")
        signatures = validator.get_confirmed_signatures(wallet_address, limit=50)
        
        if not signatures:
            print("❌ No transactions found")
            continue
            
        print(f"✅ Found {len(signatures)} recent transactions")
        
        # Parse first 10 transactions in detail
        print(f"\n🔬 Analyzing first 10 transactions:")
        print("-" * 60)
        
        parsed_transactions = []
        
        for i, sig_info in enumerate(signatures[:10]):
            signature = sig_info['signature']
            print(f"\nTransaction #{i+1}: {signature[:16]}...")
            
            # Add delay to respect rate limits
            time.sleep(0.2)
            
            tx_details = validator.get_transaction_details(signature)
            
            if tx_details:
                parsed_tx = validator.parse_transaction(tx_details, wallet_address)
                
                if parsed_tx:
                    parsed_transactions.append(parsed_tx)
                    
                    # Display key info
                    print(f"  📅 Time: {parsed_tx['timestamp']}")
                    print(f"  ⛽ Fee: {parsed_tx['fee']/1_000_000_000:.6f} SOL")
                    print(f"  ✅ Status: {parsed_tx['status']}")
                    print(f"  🔧 Programs: {[inst['program_name'] for inst in parsed_tx['instructions']]}")
                    
                    # Show token transfers
                    if parsed_tx['spl_transfers']:
                        print(f"  🪙 SPL Transfers:")
                        for transfer in parsed_tx['spl_transfers']:
                            if transfer['is_main_wallet']:
                                sign = "+" if transfer['amount_change'] > 0 else ""
                                print(f"     {sign}{transfer['amount_change']:.6f} {transfer['mint'][:8]}...")
                else:
                    print(f"  ❌ Failed to parse transaction")
            else:
                print(f"  ❌ Failed to fetch transaction details")
        
        print(f"\n📈 Summary for {strategy} wallet:")
        print(f"  💰 Current Balance: {sol_balance:.6f} SOL")
        print(f"  📊 Recent Transactions: {len(signatures)}")
        print(f"  ✅ Successfully Parsed: {len(parsed_transactions)}")
        
        # Identify common platforms
        platforms = []
        for tx in parsed_transactions:
            for instruction in tx['instructions']:
                program_name = instruction['program_name']
                if 'Unknown' not in program_name and program_name not in platforms:
                    platforms.append(program_name)
        
        if platforms:
            print(f"  🏪 Platforms Used: {', '.join(platforms)}")
    
    print(f"\n✅ SOL validation completed!")
    print(f"\n💡 Next Steps:")
    print(f"  1. Compare with existing CSV data")
    print(f"  2. Identify missing transactions")
    print(f"  3. Extract wallet addresses from unknown transactions")
    print(f"  4. Implement automatic data augmentation")

if __name__ == "__main__":
    validate_sol_wallets()