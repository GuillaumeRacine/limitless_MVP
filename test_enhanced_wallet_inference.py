#!/usr/bin/env python3
"""
Test the enhanced wallet inference system
"""

from clm_data import CLMDataManager
from views.transactions import TransactionsView
import pandas as pd

def test_enhanced_inference():
    print("🧪 Testing Enhanced Wallet Inference System")
    print("="*70)
    
    # Initialize data manager and view
    data_manager = CLMDataManager()
    tx_view = TransactionsView(data_manager)
    
    # Load transaction data
    transactions = data_manager.load_transactions()
    
    if not transactions:
        print("❌ No transaction data found")
        return
    
    df = pd.DataFrame(transactions)
    
    # Filter transactions with missing wallets
    missing_wallet_txs = df[(df['wallet'].isna()) | (df['wallet'] == '') | (df['wallet'].str.strip() == '')]
    
    print(f"📊 Found {len(missing_wallet_txs)} transactions with missing wallet addresses")
    print(f"📊 Testing inference on sample of {min(20, len(missing_wallet_txs))} transactions")
    print()
    
    # Test inference on sample
    inference_results = {
        'successful': 0,
        'failed': 0,
        'by_method': {
            'raw_data': 0,
            'filename': 0, 
            'platform_chain': 0,
            'failed': 0
        },
        'by_strategy': {
            'Long': 0,
            'Neutral': 0,
            'Yield': 0,
            'Unknown': 0
        }
    }
    
    wallet_strategies = tx_view._create_wallet_strategy_mapping()
    
    print(f"{'#':<3} {'Chain':<8} {'Platform':<12} {'Original':<15} {'Inferred':<25} {'Strategy':<10} {'Method':<12}")
    print("-" * 95)
    
    sample_txs = missing_wallet_txs.head(20)
    
    for i, (_, tx) in enumerate(sample_txs.iterrows(), 1):
        original_wallet = tx.get('wallet', '')
        chain = tx.get('chain', 'Unknown')
        platform = tx.get('platform', 'Unknown')
        
        # Test our inference
        inferred_wallet = tx_view._infer_wallet_from_transaction(tx)
        
        # Determine which method worked
        method = 'failed'
        if inferred_wallet:
            inference_results['successful'] += 1
            
            # Check if from raw_data fields
            raw_data = tx.get('raw_data', {})
            found_in_raw = False
            for field in ['From', 'To', 'Address', 'Wallet', 'Account', 'User Address', 'Interacted with']:
                if field in raw_data and str(raw_data[field]).strip() == inferred_wallet:
                    method = 'raw_data'
                    found_in_raw = True
                    break
            
            if not found_in_raw:
                # Check if from filename
                source_file = tx.get('source_file', '')
                if source_file and inferred_wallet in source_file:
                    method = 'filename'
                else:
                    method = 'platform_chain'
        else:
            inference_results['failed'] += 1
            method = 'failed'
        
        inference_results['by_method'][method] += 1
        
        # Get strategy
        strategy = wallet_strategies.get(inferred_wallet, 'Unknown')
        inference_results['by_strategy'][strategy] += 1
        
        # Display result
        inferred_display = inferred_wallet[:24] if inferred_wallet else 'None'
        print(f"{i:<3} {chain:<8} {platform:<12} {original_wallet:<15} {inferred_display:<25} {strategy:<10} {method:<12}")
    
    print()
    print("📈 INFERENCE RESULTS SUMMARY")
    print("-" * 50)
    print(f"✅ Successful inferences: {inference_results['successful']}/{len(sample_txs)} ({inference_results['successful']/len(sample_txs)*100:.1f}%)")
    print(f"❌ Failed inferences: {inference_results['failed']}/{len(sample_txs)} ({inference_results['failed']/len(sample_txs)*100:.1f}%)")
    
    print(f"\n🔧 Inference Methods Used:")
    for method, count in inference_results['by_method'].items():
        if count > 0:
            print(f"  {method:<15} {count:>3} transactions")
    
    print(f"\n🎯 Strategies Identified:")
    for strategy, count in inference_results['by_strategy'].items():
        if count > 0:
            print(f"  {strategy:<15} {count:>3} transactions")
    
    # Test on full dataset
    print(f"\n🔍 FULL DATASET PROJECTION")
    print("-" * 50)
    
    total_missing = len(missing_wallet_txs)
    if inference_results['successful'] > 0:
        success_rate = inference_results['successful'] / len(sample_txs)
        projected_recoverable = int(total_missing * success_rate)
        print(f"📊 Projected recoverable wallets: ~{projected_recoverable:,} out of {total_missing:,} missing")
        print(f"📈 This would reduce missing wallets from {total_missing:,} to ~{total_missing - projected_recoverable:,}")
    
    print(f"\n✅ Enhanced wallet inference testing completed!")

if __name__ == "__main__":
    test_enhanced_inference()