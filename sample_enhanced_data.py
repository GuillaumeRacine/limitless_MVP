#!/usr/bin/env python3
"""
Create and test enhanced CSV files with transaction IDs, gas fees, and balance data
"""

import os
import pandas as pd
from clm_data import CLMDataManager

def create_enhanced_csv_samples():
    """Create sample CSV files with enhanced fields"""
    
    # Create enhanced long positions CSV with transaction data
    enhanced_long_data = {
        'Position Details': ['SOL/USDC | Orca', 'ETH/USDC | Uniswap', 'WBTC/SOL | Orca'],
        'Strategy': ['Long', 'Long', 'Long'],
        'Wallet': [
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k',
            '0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a',
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k'
        ],
        'Chain': ['SOL', 'ETH', 'SOL'],
        'Platform': ['Orca', 'Uniswap', 'Orca'],
        'Total Entry Value': ['$25,000', '$30,000', '$20,000'],
        'Entry Date': ['June 20', 'June 21', 'June 22'],
        'Min Range': [90.0, 1800.0, 600.0],
        'Max Range': [120.0, 2500.0, 800.0],
        'Transaction ID': [
            '7kj9dHJ2k3H4J5K6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0',
            '0x8lm0eIK3l4I5K6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0J1',
            '9no1fJL4m5J6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0J1K2'
        ],
        'Gas Fees': ['$0.003', '$15.50', '$0.005'],
        'Contract Address': [
            '9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP',
            '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
            '4585fe77225b41b697c938b018e2ac67ac5a20c0'
        ],
        'Block Number': ['245678901', '18920345', '245678902'],
        'Current Balance': ['1250.75', '12.5', '0.025'],
        'Token A Balance': ['625.00', '6.25', '0.0125'],
        'Token B Balance': ['625.75', '1245.30', '600.25']
    }
    
    enhanced_long_df = pd.DataFrame(enhanced_long_data)
    enhanced_long_df.to_csv('data/enhanced_long_positions.csv', index=False)
    
    # Create transaction-only CSV (for wallet exports)
    transaction_data = {
        'Transaction ID': [
            '7kj9dHJ2k3H4J5K6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0',
            '8lm0eIK3l4I5K6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0J1',
            '9no1fJL4m5J6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0J1K2'
        ],
        'Wallet Address': [
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k',
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k',
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k'
        ],
        'Chain': ['SOL', 'SOL', 'SOL'],
        'Platform': ['Orca', 'Raydium', 'Orca'],
        'Timestamp': ['2024-06-20 10:30:00', '2024-06-20 11:15:00', '2024-06-20 12:45:00'],
        'Gas Fees': ['$0.003', '$0.002', '$0.005'],
        'Block Number': ['245678901', '245678902', '245678903'],
        'Contract Address': [
            '9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP',
            'AVs9TA4nWDzfPJE9gqub6T2b5s4w3XP9VUj8Xa6u8MaY',
            'H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG'
        ]
    }
    
    transaction_df = pd.DataFrame(transaction_data)
    transaction_df.to_csv('data/solana_transactions.csv', index=False)
    
    # Create balance-only CSV (portfolio snapshot)
    balance_data = {
        'Wallet Address': [
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k',
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k',
            'DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k'
        ],
        'Chain': ['SOL', 'SOL', 'SOL'],
        'Platform': ['Orca', 'Raydium', 'Jupiter'],
        'Token Pair': ['SOL/USDC', 'RAY/USDC', 'JLP/SOL'],
        'Current Balance': ['1250.75', '500.25', '25.5'],
        'Token A Balance': ['625.00', '250.00', '12.75'],
        'Token B Balance': ['625.75', '250.25', '12.75'],
        'Contract Address': [
            '9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP',
            'AVs9TA4nWDzfPJE9gqub6T2b5s4w3XP9VUj8Xa6u8MaY',
            '27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4'
        ]
    }
    
    balance_df = pd.DataFrame(balance_data)
    balance_df.to_csv('data/portfolio_balances.csv', index=False)
    
    print("✅ Created enhanced CSV samples:")
    print("   - data/enhanced_long_positions.csv (positions with tx data)")
    print("   - data/solana_transactions.csv (transaction records)")
    print("   - data/portfolio_balances.csv (balance snapshot)")

def test_enhanced_import():
    """Test importing the enhanced CSV data"""
    
    manager = CLMDataManager()
    
    print("\n=== Testing Enhanced CSV Import ===")
    
    # Test 1: Enhanced position CSV
    print("\n1. Testing enhanced position CSV...")
    csv_configs = [{
        'path': 'data/enhanced_long_positions.csv',
        'chain': 'Mixed',
        'type': 'positions',
        'strategy': 'long'
    }]
    
    results1 = manager.import_multi_chain_csvs(csv_configs)
    
    if results1['positions']['long']:
        pos = results1['positions']['long'][0]
        print(f"   ✅ Enhanced position imported:")
        print(f"      Position: {pos['position_details']}")
        print(f"      Wallet: {pos['wallet']}")
        print(f"      Transaction: {pos['transaction_data']['entry_tx_id']}")
        print(f"      Gas Fees: ${pos['transaction_data']['gas_fees_paid']}")
        print(f"      Contract: {pos['contract_data']['contract_address']}")
        print(f"      LP Balance: {pos['balance_data']['current_lp_balance']}")
    
    # Test 2: Transaction CSV
    print("\n2. Testing transaction CSV...")
    transactions = manager.import_transaction_csv('data/solana_transactions.csv', 'SOL')
    
    if transactions:
        tx = transactions[0]
        print(f"   ✅ Transaction imported:")
        print(f"      Tx Hash: {tx['tx_hash']}")
        print(f"      Wallet: {tx['wallet']}")
        print(f"      Platform: {tx['platform']}")
        print(f"      Gas Fees: ${tx['gas_fees']}")
        print(f"      Block: {tx['block_number']}")
    
    # Test 3: Balance CSV
    print("\n3. Testing balance CSV...")
    balances = manager.import_balance_csv('data/portfolio_balances.csv', 'SOL')
    
    if balances:
        bal = balances[0]
        print(f"   ✅ Balance imported:")
        print(f"      Wallet: {bal['wallet']}")
        print(f"      Token Pair: {bal['token_pair']}")
        print(f"      LP Balance: {bal['lp_balance']}")
        print(f"      Token A: {bal['token_a_balance']}")
        print(f"      Token B: {bal['token_b_balance']}")
        print(f"      Contract: {bal['contract_address']}")
    
    # Save all imported data
    if transactions:
        manager.save_transactions(transactions)
        print(f"\n💾 Saved {len(transactions)} transactions to JSON")
    
    if balances:
        manager.save_balances(balances)
        print(f"💾 Saved {len(balances)} balance records to JSON")
    
    # Show JSON files created
    print(f"\n📁 JSON files created:")
    if os.path.exists(manager.transactions_json):
        print(f"   ✅ {manager.transactions_json}")
    if os.path.exists(manager.balances_json):
        print(f"   ✅ {manager.balances_json}")

def main():
    # Create sample files
    create_enhanced_csv_samples()
    
    # Test importing them
    test_enhanced_import()

if __name__ == "__main__":
    main()