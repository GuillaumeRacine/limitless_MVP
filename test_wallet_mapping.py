#!/usr/bin/env python3
"""
Quick test to verify wallet-to-strategy mapping is working
"""

from clm_data import CLMDataManager
from views.transactions import TransactionsView
import pandas as pd

def test_wallet_mapping():
    print("🧪 Testing Wallet-to-Strategy Mapping System")
    print("="*60)
    
    # Initialize data manager
    data_manager = CLMDataManager()
    
    # Load transaction data
    transactions = data_manager.load_transactions()
    
    if not transactions:
        print("❌ No transaction data found")
        return
    
    print(f"📊 Loaded {len(transactions)} transactions")
    
    # Initialize transactions view
    tx_view = TransactionsView(data_manager)
    
    # Test wallet mapping
    wallet_strategies = tx_view._create_wallet_strategy_mapping()
    
    print(f"\n🗺️ Wallet-to-Strategy Mapping ({len(wallet_strategies)} wallets):")
    print("-" * 80)
    
    for wallet, strategy in wallet_strategies.items():
        chain = "Unknown"
        # Determine chain based on wallet format
        if wallet.startswith("0x") and len(wallet) == 42:
            chain = "ETH"
        elif wallet.startswith("0x") and len(wallet) == 66:
            chain = "SUI"
        elif not wallet.startswith("0x"):
            chain = "SOL"
        
        print(f"{chain:<5} {wallet:<20} → {strategy}")
    
    # Test transaction wallet identification
    print(f"\n🔍 Testing Transaction Wallet Identification:")
    print("-" * 80)
    
    df = pd.DataFrame(transactions)
    
    # Sample a few transactions to test
    sample_size = min(10, len(df))
    sample_txs = df.head(sample_size)
    
    print(f"{'Chain':<8} {'Original Wallet':<20} {'Inferred Wallet':<20} {'Strategy':<12}")
    print("-" * 70)
    
    for _, tx in sample_txs.iterrows():
        original_wallet = tx.get('wallet', '')
        
        # Test inference if wallet is empty
        if not original_wallet or original_wallet.strip() == '':
            inferred_wallet = tx_view._infer_wallet_from_transaction(tx)
        else:
            inferred_wallet = original_wallet
        
        strategy = wallet_strategies.get(inferred_wallet, 'Unknown')
        chain = tx.get('chain', 'Unknown')
        
        print(f"{chain:<8} {original_wallet[:19]:<20} {inferred_wallet[:19]:<20} {strategy:<12}")
    
    # Count transactions by chain
    print(f"\n📈 Transaction Distribution by Chain:")
    print("-" * 40)
    
    chain_counts = df['chain'].value_counts()
    for chain, count in chain_counts.items():
        print(f"{chain:<8} {count:>8,} transactions")
    
    print(f"\n✅ Wallet mapping test completed!")

if __name__ == "__main__":
    test_wallet_mapping()