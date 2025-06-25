#!/usr/bin/env python3
"""
Import Your Full Transaction CSV
Simple script to import your complete transaction history
"""

from clm_data import CLMDataManager
import os

def import_my_transactions():
    """Import your transaction CSV file"""
    
    manager = CLMDataManager()
    
    print("📥 Transaction CSV Import Tool")
    print("=" * 40)
    
    # Option 1: Place your CSV in the data folder
    csv_options = [
        'data/my_sol_transactions.csv',
        'data/sol_transaction_history.csv', 
        'data/wallet_export.csv',
        'data/dex_transactions.csv'
    ]
    
    print("🔍 Looking for transaction CSV files...")
    
    found_files = []
    for csv_path in csv_options:
        if os.path.exists(csv_path):
            found_files.append(csv_path)
            print(f"   ✅ Found: {csv_path}")
    
    # Check for any CSV files in data directory
    if os.path.exists('data'):
        all_csvs = [f for f in os.listdir('data') if f.endswith('.csv') and 'transaction' in f.lower()]
        for csv_file in all_csvs:
            csv_path = f'data/{csv_file}'
            if csv_path not in found_files:
                found_files.append(csv_path)
                print(f"   ✅ Found: {csv_path}")
    
    if not found_files:
        print("❌ No transaction CSV files found!")
        print("\n📋 To import your transactions:")
        print("   1. Copy your transaction CSV to the data/ folder")
        print("   2. Name it something like 'my_sol_transactions.csv'")
        print("   3. Run this script again")
        print("\n💡 Expected CSV columns:")
        print("   - Transaction ID / Tx Hash")
        print("   - Wallet Address")
        print("   - Platform / Exchange")
        print("   - Timestamp / Date")
        print("   - Gas Fees")
        print("   - Contract Address (optional)")
        print("   - Block Number (optional)")
        return
    
    # Import each found file
    all_transactions = []
    
    for csv_path in found_files:
        print(f"\n📤 Importing: {csv_path}")
        
        # Detect chain from filename or ask user
        chain = 'SOL'  # Default to SOL, you can modify this
        if 'eth' in csv_path.lower():
            chain = 'ETH'
        elif 'sui' in csv_path.lower():
            chain = 'SUI'
        elif 'base' in csv_path.lower():
            chain = 'BASE'
        elif 'arb' in csv_path.lower():
            chain = 'ARB'
        
        # Import the transactions
        transactions = manager.import_transaction_csv(csv_path, chain)
        
        if transactions:
            all_transactions.extend(transactions)
            print(f"   ✅ Imported {len(transactions)} transactions from {chain}")
            
            # Show sample
            tx = transactions[0]
            print(f"   📋 Sample: {tx['tx_hash'][:10]}... on {tx['platform']} (Gas: ${tx['gas_fees']})")
        else:
            print(f"   ❌ No transactions imported from {csv_path}")
    
    if all_transactions:
        # Save all transactions
        manager.save_transactions(all_transactions)
        
        print(f"\n✅ Import Complete!")
        print(f"   📊 Total transactions: {len(all_transactions)}")
        
        # Analysis
        chains = set(tx['chain'] for tx in all_transactions)
        platforms = set(tx['platform'] for tx in all_transactions)
        total_gas = sum(tx.get('gas_fees', 0) or 0 for tx in all_transactions)
        
        print(f"   ⛓️  Chains: {', '.join(chains)}")
        print(f"   🏪 Platforms: {', '.join(list(platforms)[:5])}{'...' if len(platforms) > 5 else ''}")
        print(f"   ⛽ Total Gas: ${total_gas:.6f}")
        
        print(f"\n💾 Saved to: data/JSON_out/clm_transactions.json")
        
        # Integration check
        print(f"\n🔗 Checking integration with positions...")
        manager.update_positions(
            'data/Tokens_Trade_Sheet - Neutral Positions.csv',
            'data/Tokens_Trade_Sheet - Long Positions.csv'
        )
        
        # Find matches
        matches = 0
        for position in manager.long_positions + manager.neutral_positions:
            pos_wallet = position.get('wallet', '')
            for tx in all_transactions:
                if tx.get('wallet') == pos_wallet:
                    matches += 1
                    break
        
        print(f"   🎯 Found {matches} positions with matching transaction data")

if __name__ == "__main__":
    import_my_transactions()