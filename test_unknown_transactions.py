#!/usr/bin/env python3
"""
Investigate transactions with Unknown chain to improve chain detection
"""

from clm_data import CLMDataManager
import pandas as pd

def investigate_unknown_chains():
    print("🔍 Investigating Unknown Chain Transactions")
    print("="*60)
    
    # Initialize data manager
    data_manager = CLMDataManager()
    
    # Load transaction data
    transactions = data_manager.load_transactions()
    
    if not transactions:
        print("❌ No transaction data found")
        return
    
    df = pd.DataFrame(transactions)
    
    # Filter for unknown chain transactions
    unknown_txs = df[df['chain'] == 'Unknown'].head(10)
    
    print(f"📊 Found {len(df[df['chain'] == 'Unknown'])} transactions with Unknown chain")
    print(f"🔬 Examining first 10 transactions:\n")
    
    for i, (_, tx) in enumerate(unknown_txs.iterrows(), 1):
        print(f"Transaction #{i}:")
        print(f"  Wallet: {tx.get('wallet', 'Not set')}")
        print(f"  Platform: {tx.get('platform', 'Not set')}")
        print(f"  Timestamp: {tx.get('timestamp', 'Not set')}")
        print(f"  Gas Fees: {tx.get('gas_fees', 'Not set')}")
        
        # Check raw_data for clues
        raw_data = tx.get('raw_data', {})
        if raw_data:
            print(f"  Raw Data Keys: {list(raw_data.keys())}")
            # Show a few key fields if they exist
            for key in ['Chain', 'Network', 'Blockchain', 'Token Symbol', 'Buy Currency', 'Sell Currency']:
                if key in raw_data:
                    print(f"    {key}: {raw_data[key]}")
        
        print()
    
    # Check platforms for unknown transactions to see if we can infer chain
    print("🏪 Platform distribution for Unknown chain transactions:")
    platform_counts = df[df['chain'] == 'Unknown']['platform'].value_counts().head(10)
    for platform, count in platform_counts.items():
        print(f"  {platform}: {count} transactions")

if __name__ == "__main__":
    investigate_unknown_chains()