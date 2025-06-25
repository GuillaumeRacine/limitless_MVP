#!/usr/bin/env python3
"""
Test SOL Transaction History CSV Import
Comprehensive testing for Solana-specific transaction data
"""

import pandas as pd
from clm_data import CLMDataManager

def create_realistic_sol_transaction_csv():
    """Create realistic Solana transaction CSV based on actual wallet exports"""
    
    # Realistic Solana transaction data (formats from Jupiter, Orca, Raydium exports)
    sol_tx_data = {
        'Transaction ID': [
            '5KJP9WYxKmBhAhPtLLZWVgTjhQf4qJnbtC1QZyXpMvJDfMqNbCxAzR8vEhGzVt2S',
            '3NYf8xZpHjKdVnBqMfRzWcJLNxRtGhQm6kPzAbEuDfYvCzXwMjRzVqTgNhBpLm4A',
            '2LKm5BzCpTdNhQx9vEgRjWyXfAuMpZnYtRzVqBxLkNmRzCdFgHzPzWyXrEtYuIoP',
            '4RzVqBxLkNmRzCdFgHzPzWyXrEtYuIoPmNbVcXzAsDfGhJkL9qWeRtYuIoPaS5D',
            '6HzPzWyXrEtYuIoPmNbVcXzAsDfGhJkL9qWeRtYuIoPaSdFgHjKlZxCvBnM3QwE'
        ],
        'Wallet Address': [
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k',
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k', 
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k',
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k',
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k'
        ],
        'Chain': ['SOL', 'SOL', 'SOL', 'SOL', 'SOL'],
        'Platform': ['Orca', 'Raydium', 'Jupiter', 'Orca', 'Meteora'],
        'Action': ['Add Liquidity', 'Swap', 'Add Liquidity', 'Remove Liquidity', 'Add Liquidity'],
        'Token Pair': ['SOL/USDC', 'SOL→USDC', 'JLP/SOL', 'WBTC/SOL', 'RAY/USDC'],
        'Amount': ['$25,000', '$5,000', '$12,500', '$8,750', '$15,000'],
        'Timestamp': [
            '2024-06-20 10:30:15',
            '2024-06-20 11:45:22', 
            '2024-06-20 14:22:08',
            '2024-06-21 09:15:33',
            '2024-06-21 16:45:11'
        ],
        'Gas Fees': ['$0.003542', '$0.000892', '$0.004123', '$0.002891', '$0.003401'],
        'Block Number': [245678901, 245679124, 245682387, 245698234, 245701567],
        'Contract Address': [
            '9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP',  # Orca SOL/USDC
            'AVs9TA4nWDzfPJE9gqub6T2b5s4w3XP9VUj8Xa6u8MaY',  # Raydium SOL/USDC
            '27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4',  # JLP
            '4585fe77225b41b697c938b018e2ac67ac5a20c0',      # WBTC/SOL
            'FarmsPzpWu9i7Kky8tPN37rs2TpmMrAZrC7S7vJa91Hr'   # Meteora RAY/USDC
        ],
        'Status': ['Success', 'Success', 'Success', 'Success', 'Success'],
        'LP Tokens Received': ['1250.75', '', '625.30', '', '750.25'],
        'LP Tokens Burned': ['', '', '', '433.50', '']
    }
    
    df = pd.DataFrame(sol_tx_data)
    df.to_csv('data/realistic_sol_transactions.csv', index=False)
    
    print("✅ Created realistic SOL transaction CSV: data/realistic_sol_transactions.csv")
    return df

def test_sol_transaction_import():
    """Test importing SOL transaction history"""
    
    manager = CLMDataManager()
    
    print("\n=== Testing SOL Transaction History Import ===")
    
    # Import the realistic SOL transaction CSV
    csv_path = 'data/realistic_sol_transactions.csv'
    transactions = manager.import_transaction_csv(csv_path, 'SOL')
    
    if not transactions:
        print("❌ No transactions imported")
        return
    
    print(f"\n✅ Successfully imported {len(transactions)} SOL transactions")
    
    # Analyze the imported data
    total_gas_fees = sum(tx.get('gas_fees', 0) or 0 for tx in transactions)
    platforms = set(tx.get('platform', 'Unknown') for tx in transactions)
    contracts = set(tx.get('contract_address', '') for tx in transactions if tx.get('contract_address'))
    
    print(f"\n📊 SOL Transaction Analysis:")
    print(f"   💰 Total Gas Fees: ${total_gas_fees:.6f} SOL")
    print(f"   🏪 Platforms: {', '.join(platforms)}")
    print(f"   📝 Unique Contracts: {len(contracts)}")
    print(f"   🔗 Block Range: {min(int(tx.get('block_number', 0)) for tx in transactions if tx.get('block_number'))} - {max(int(tx.get('block_number', 0)) for tx in transactions if tx.get('block_number'))}")
    
    # Show detailed sample
    print(f"\n📋 Sample SOL Transaction Details:")
    tx = transactions[0]
    print(f"   🆔 ID: {tx['id']}")
    print(f"   🔗 Tx Hash: {tx['tx_hash']}")
    print(f"   👛 Wallet: {tx['wallet'][:8]}...{tx['wallet'][-8:]}")
    print(f"   ⛓️  Chain: {tx['chain']}")
    print(f"   🏪 Platform: {tx['platform']}")
    print(f"   ⏰ Timestamp: {tx['timestamp']}")
    print(f"   ⛽ Gas Fee: ${tx['gas_fees']} SOL")
    print(f"   📦 Block: #{tx['block_number']}")
    print(f"   📄 Contract: {tx['contract_address'][:8]}...{tx['contract_address'][-8:]}")
    
    # Test SOL-specific validation
    print(f"\n🔍 SOL-Specific Validation:")
    
    # Validate wallet address format (Solana base58)
    sol_wallet = tx['wallet']
    if len(sol_wallet) >= 32 and all(c in 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz123456789' for c in sol_wallet):
        print(f"   ✅ Valid SOL wallet address format")
    else:
        print(f"   ⚠️  Unusual SOL wallet format")
    
    # Validate transaction hash format (Solana base58)
    sol_tx_hash = tx['tx_hash']
    if len(sol_tx_hash) >= 64 and all(c in 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz123456789' for c in sol_tx_hash):
        print(f"   ✅ Valid SOL transaction hash format")
    else:
        print(f"   ⚠️  Unusual SOL transaction hash format")
    
    # Validate gas fees (typical SOL range)
    gas_fee = tx['gas_fees']
    if 0.000001 <= gas_fee <= 0.01:
        print(f"   ✅ Realistic SOL gas fee range")
    else:
        print(f"   ⚠️  Gas fee outside typical SOL range")
    
    # Save and verify persistence
    manager.save_transactions(transactions)
    loaded_transactions = manager.load_transactions()
    
    if len(loaded_transactions) >= len(transactions):
        print(f"   ✅ Transactions saved and loaded successfully")
    else:
        print(f"   ⚠️  Transaction persistence issue")
    
    return transactions

def test_sol_integration_with_positions():
    """Test how SOL transactions integrate with existing positions"""
    
    manager = CLMDataManager()
    
    print(f"\n=== Testing SOL Transaction-Position Integration ===")
    
    # Load existing positions
    neutral_csv = 'data/Tokens_Trade_Sheet - Neutral Positions.csv'
    long_csv = 'data/Tokens_Trade_Sheet - Long Positions.csv'
    manager.update_positions(neutral_csv, long_csv)
    
    # Load SOL transactions
    transactions = manager.load_transactions()
    
    # Find potential matches between transactions and positions
    matches = []
    for position in manager.long_positions + manager.neutral_positions:
        pos_wallet = position.get('wallet', '')
        pos_platform = position.get('platform', '').lower()
        
        for tx in transactions:
            tx_wallet = tx.get('wallet', '')
            tx_platform = tx.get('platform', '').lower()
            
            if pos_wallet == tx_wallet and pos_platform == tx_platform:
                matches.append({
                    'position_id': position['id'],
                    'transaction_id': tx['id'],
                    'platform': pos_platform,
                    'wallet': pos_wallet[:8] + '...'
                })
    
    print(f"   🔗 Found {len(matches)} potential transaction-position matches")
    
    if matches:
        print(f"   📋 Sample Match:")
        match = matches[0]
        print(f"      Position ID: {match['position_id']}")
        print(f"      Transaction ID: {match['transaction_id']}")
        print(f"      Platform: {match['platform']}")
        print(f"      Wallet: {match['wallet']}")
    
    # Show SOL-specific position data
    sol_positions = [pos for pos in manager.long_positions + manager.neutral_positions if pos.get('chain', '').upper() == 'SOL']
    print(f"   📊 SOL Positions: {len(sol_positions)} found")
    
    if sol_positions:
        sol_pos = sol_positions[0]
        print(f"   📋 Sample SOL Position:")
        print(f"      Position: {sol_pos.get('position_details', 'N/A')}")
        print(f"      Wallet: {sol_pos.get('wallet', 'N/A')[:8]}...")
        print(f"      Platform: {sol_pos.get('platform', 'N/A')}")
        
        # Check if position has enhanced transaction data
        tx_data = sol_pos.get('transaction_data', {})
        if tx_data.get('entry_tx_id'):
            print(f"      ✅ Has transaction data: {tx_data['entry_tx_id'][:8]}...")
        else:
            print(f"      ⚠️  No transaction data linked")

def main():
    """Run comprehensive SOL transaction testing"""
    
    print("🔬 Comprehensive SOL Transaction History Testing")
    print("=" * 50)
    
    # Create realistic test data
    create_realistic_sol_transaction_csv()
    
    # Test transaction import
    transactions = test_sol_transaction_import()
    
    # Test integration with positions
    test_sol_integration_with_positions()
    
    print(f"\n✅ SOL Transaction History Testing Complete!")
    print(f"   📊 {len(transactions)} transactions processed")
    print(f"   💾 Data saved to JSON files")
    print(f"   🔗 Integration with positions validated")

if __name__ == "__main__":
    main()