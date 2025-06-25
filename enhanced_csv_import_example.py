#!/usr/bin/env python3
"""
Enhanced CSV Import Example
Demonstrates how to use the new multi-chain CSV import functionality
"""

from clm_data import CLMDataManager

def main():
    # Initialize the data manager
    manager = CLMDataManager()
    
    # Example 1: Import multiple CSV files from different sources
    print("=== Example 1: Multi-chain CSV Import ===")
    
    csv_configs = [
        # Solana transaction export
        {
            'path': 'data/solana_transactions.csv',
            'chain': 'SOL',
            'type': 'transactions'
        },
        # Ethereum balance snapshot
        {
            'path': 'data/ethereum_balances.csv',
            'chain': 'ETH',
            'type': 'balances'
        },
        # Sui positions (existing format)
        {
            'path': 'data/sui_positions.csv',
            'chain': 'SUI',
            'type': 'positions',
            'strategy': 'long'
        },
        # Arbitrum positions
        {
            'path': 'data/arbitrum_positions.csv',
            'chain': 'ARB',
            'type': 'positions',
            'strategy': 'neutral'
        }
    ]
    
    # Import all CSV files
    results = manager.import_multi_chain_csvs(csv_configs)
    
    # Save the imported data
    if results['transactions']:
        manager.save_transactions(results['transactions'])
        print(f"💾 Saved {len(results['transactions'])} transactions")
    
    if results['balances']:
        manager.save_balances(results['balances'])
        print(f"💾 Saved {len(results['balances'])} balance records")
    
    if results['positions']['long'] or results['positions']['neutral']:
        # Merge with existing positions
        manager.long_positions.extend(results['positions']['long'])
        manager.neutral_positions.extend(results['positions']['neutral'])
        manager.save_positions()
        print(f"💾 Saved enhanced position data")
    
    # Example 2: Import specific transaction CSV
    print("\n=== Example 2: Import Specific Transaction CSV ===")
    
    # Transaction CSV with columns: Tx Hash, Wallet Address, Timestamp, Gas Fees, Block Number
    transactions = manager.import_transaction_csv('data/solana_dex_transactions.csv', 'SOL')
    if transactions:
        manager.save_transactions(transactions)
    
    # Example 3: Import balance snapshot CSV
    print("\n=== Example 3: Import Balance Snapshot ===")
    
    # Balance CSV with columns: Wallet Address, Token Pair, Current Balance, Contract Address
    balances = manager.import_balance_csv('data/portfolio_snapshot.csv', 'ETH')
    if balances:
        manager.save_balances(balances)
    
    # Example 4: Load and display imported data
    print("\n=== Example 4: View Imported Data ===")
    
    # Load transactions
    transactions = manager.load_transactions()
    print(f"📊 Loaded {len(transactions)} transactions")
    
    # Load balances
    balances = manager.load_balances()
    print(f"💰 Loaded {len(balances)} balance records")
    
    # Display sample transaction data
    if transactions:
        print("\n📋 Sample Transaction:")
        tx = transactions[0]
        print(f"   Tx Hash: {tx['tx_hash']}")
        print(f"   Wallet: {tx['wallet']}")
        print(f"   Chain: {tx['chain']}")
        print(f"   Gas Fees: ${tx['gas_fees']}")
        print(f"   Block: {tx['block_number']}")
    
    # Display sample balance data
    if balances:
        print("\n📋 Sample Balance:")
        balance = balances[0]
        print(f"   Wallet: {balance['wallet']}")
        print(f"   Chain: {balance['chain']}")
        print(f"   Token Pair: {balance['token_pair']}")
        print(f"   LP Balance: {balance['lp_balance']}")
        print(f"   Contract: {balance['contract_address']}")

def create_sample_csvs():
    """Create sample CSV files for testing"""
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Sample transaction CSV (Solana format)
    solana_tx_csv = """Transaction ID,Wallet Address,Timestamp,Gas Fees,Block Number,Platform,Chain
7kj9dHJ2k3H4J5K6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0,DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k,2024-06-20 10:30:00,0.0025,245678901,Orca,SOL
8lm0eIK3l4I5K6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0J1,DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k,2024-06-20 11:15:00,0.0018,245678902,Raydium,SOL
9no1fJL4m5J6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0J1K2,DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k,2024-06-20 12:45:00,0.0032,245678903,Orca,SOL"""
    
    with open('data/solana_transactions.csv', 'w') as f:
        f.write(solana_tx_csv)
    
    # Sample balance CSV (Ethereum format)
    eth_balance_csv = """Wallet Address,Token Pair,Current Balance,Token A Balance,Token B Balance,Contract Address,Chain
0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a,ETH/USDC,1250.75,0.534,1245.30,0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640,ETH
0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a,WBTC/ETH,0.0145,0.0145,0.0,0x4585fe77225b41b697c938b018e2ac67ac5a20c0,ETH
0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a,USDC/USDT,2500.00,1250.00,1250.00,0x3041cbd36888becc7bbcbc0045e3b1f144466f5f,ETH"""
    
    with open('data/ethereum_balances.csv', 'w') as f:
        f.write(eth_balance_csv)
    
    print("✅ Created sample CSV files in data/ directory")

if __name__ == "__main__":
    # Create sample CSV files for testing
    create_sample_csvs()
    
    # Run the main example
    main()