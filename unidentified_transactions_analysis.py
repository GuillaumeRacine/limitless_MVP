#!/usr/bin/env python3
"""
Comprehensive analysis of remaining unidentified and unmatched transactions
"""

from clm_data import CLMDataManager
from views.transactions import TransactionsView
import pandas as pd

def analyze_unidentified_transactions():
    print("🔍 COMPREHENSIVE UNIDENTIFIED TRANSACTIONS ANALYSIS")
    print("="*80)
    
    # Initialize data manager
    data_manager = CLMDataManager()
    
    # Load current transaction data
    transactions = data_manager.load_transactions()
    df = pd.DataFrame(transactions)
    
    print(f"📊 OVERALL TRANSACTION STATUS")
    print("-" * 50)
    print(f"Total transactions in database: {len(df):,}")
    
    # Chain distribution
    chain_counts = df['chain'].value_counts()
    print(f"\n⛓️  Chain Distribution:")
    for chain, count in chain_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {chain:<12} {count:>6,} ({percentage:>5.1f}%)")
    
    # Check for remaining unknown/unidentified transactions
    print(f"\n🔍 UNIDENTIFIED TRANSACTION ANALYSIS")
    print("-" * 60)
    
    # 1. Unknown chain transactions
    unknown_chain = df[df['chain'] == 'Unknown']
    print(f"❌ Unknown chain: {len(unknown_chain):,} transactions")
    
    # 2. Missing wallet addresses
    missing_wallets = df[(df['wallet'].isna()) | (df['wallet'] == '') | (df['wallet'].str.strip() == '')]
    print(f"👤 Missing wallet addresses: {len(missing_wallets):,} transactions")
    
    # 3. Unknown platforms
    unknown_platforms = df[df['platform'] == 'Unknown']
    print(f"🏪 Unknown platforms: {len(unknown_platforms):,} transactions")
    
    # 4. Check wallet coverage by chain
    print(f"\n👛 WALLET ADDRESS COVERAGE BY CHAIN")
    print("-" * 50)
    
    wallet_coverage_summary = {}
    
    for chain in chain_counts.index:
        chain_txs = df[df['chain'] == chain]
        with_wallets = len(chain_txs[chain_txs['wallet'].notna() & (chain_txs['wallet'] != '') & (chain_txs['wallet'].str.strip() != '')])
        without_wallets = len(chain_txs) - with_wallets
        coverage_pct = (with_wallets / len(chain_txs)) * 100 if len(chain_txs) > 0 else 0
        
        wallet_coverage_summary[chain] = {
            'total': len(chain_txs),
            'with_wallets': with_wallets,
            'without_wallets': without_wallets,
            'coverage_pct': coverage_pct
        }
        
        print(f"  {chain:<12} {with_wallets:>6,}/{len(chain_txs):,} ({coverage_pct:>5.1f}% coverage) | Missing: {without_wallets:,}")
    
    # 5. Strategy mapping analysis
    print(f"\n🗺️  STRATEGY MAPPING ANALYSIS")
    print("-" * 50)
    
    tx_view = TransactionsView(data_manager)
    wallet_strategies = tx_view._create_wallet_strategy_mapping()
    
    strategy_counts = {}
    unmapped_count = 0
    
    for _, tx in df.iterrows():
        wallet = tx.get('wallet', '').strip()
        if wallet and wallet != '':
            strategy = wallet_strategies.get(wallet, 'Unknown')
            if strategy not in strategy_counts:
                strategy_counts[strategy] = 0
            strategy_counts[strategy] += 1
        else:
            unmapped_count += 1
    
    print(f"Strategy distribution:")
    for strategy, count in sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(df)) * 100
        print(f"  {strategy:<15} {count:>6,} ({percentage:>5.1f}%)")
    
    print(f"  {'No Wallet':<15} {unmapped_count:>6,} ({(unmapped_count/len(df))*100:>5.1f}%)")
    
    # 6. Detailed analysis of problematic transactions
    print(f"\n🔬 DETAILED ANALYSIS OF UNMATCHED TRANSACTIONS")
    print("-" * 60)
    
    # Find transactions with multiple issues
    problematic_txs = df[
        (df['chain'] == 'Unknown') | 
        (df['wallet'].isna() | (df['wallet'] == '') | (df['wallet'].str.strip() == '')) |
        (df['platform'] == 'Unknown')
    ].copy()
    
    print(f"Transactions with identification issues: {len(problematic_txs):,}")
    
    if len(problematic_txs) > 0:
        # Analyze by issue type
        issue_analysis = {}
        for _, tx in problematic_txs.iterrows():
            issues = []
            
            if tx.get('chain') == 'Unknown':
                issues.append('Unknown Chain')
            
            wallet = tx.get('wallet', '').strip()
            if not wallet or wallet == '':
                issues.append('Missing Wallet')
            
            if tx.get('platform') == 'Unknown':
                issues.append('Unknown Platform')
            
            issue_key = ' + '.join(issues)
            if issue_key not in issue_analysis:
                issue_analysis[issue_key] = 0
            issue_analysis[issue_key] += 1
        
        print(f"\nIssue breakdown:")
        for issue, count in sorted(issue_analysis.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(problematic_txs)) * 100
            print(f"  {issue:<25} {count:>6,} ({percentage:>5.1f}%)")
        
        # Sample problematic transactions
        print(f"\n🔬 Sample problematic transactions:")
        sample_problematic = problematic_txs.head(5)
        
        for i, (_, tx) in enumerate(sample_problematic.iterrows(), 1):
            chain = tx.get('chain', 'Unknown')
            wallet = tx.get('wallet', 'Missing')[:20] if tx.get('wallet') else 'Missing'
            platform = tx.get('platform', 'Unknown')
            timestamp = tx.get('timestamp', 'Unknown')
            
            print(f"  #{i}: {chain} | {wallet} | {platform} | {timestamp}")
            
            # Show raw_data snippet
            raw_data = tx.get('raw_data', {})
            if raw_data:
                key_fields = ['Portfolio', 'Coin Symbol', 'Type', 'Amount']
                raw_snippet = []
                for field in key_fields:
                    if field in raw_data:
                        value = str(raw_data[field])[:20]
                        raw_snippet.append(f"{field}={value}")
                if raw_snippet:
                    print(f"      Raw: {' | '.join(raw_snippet)}")
    
    # 7. Enhancement recommendations
    print(f"\n💡 ENHANCEMENT RECOMMENDATIONS")
    print("-" * 50)
    
    total_unidentified = len(unknown_chain) + len(missing_wallets) + len(unknown_platforms)
    
    recommendations = []
    
    if len(unknown_chain) > 0:
        recommendations.append(f"🔍 Investigate {len(unknown_chain)} unknown chain transactions")
    
    if len(missing_wallets) > 0:
        recommendations.append(f"👤 Enhance wallet inference for {len(missing_wallets)} transactions")
    
    if len(unknown_platforms) > 0:
        recommendations.append(f"🏪 Improve platform detection for {len(unknown_platforms)} transactions")
    
    # Check coverage gaps
    for chain, stats in wallet_coverage_summary.items():
        if stats['coverage_pct'] < 70 and stats['without_wallets'] > 100:
            recommendations.append(f"⛓️  Improve {chain} wallet coverage ({stats['without_wallets']:,} missing)")
    
    if not recommendations:
        recommendations.append("✅ Data quality is excellent - minimal unidentified transactions")
    
    for rec in recommendations:
        print(f"  {rec}")
    
    # 8. Overall assessment
    print(f"\n🎯 OVERALL ASSESSMENT")
    print("="*50)
    
    identified_txs = len(df) - len(problematic_txs)
    identification_rate = (identified_txs / len(df)) * 100 if len(df) > 0 else 0
    
    print(f"✅ Successfully identified: {identified_txs:,}/{len(df):,} transactions ({identification_rate:.1f}%)")
    print(f"❌ Remaining unidentified: {len(problematic_txs):,} transactions ({100-identification_rate:.1f}%)")
    
    if identification_rate >= 95:
        print(f"🏆 EXCELLENT: Very high identification rate!")
    elif identification_rate >= 85:
        print(f"🟢 GOOD: High identification rate")
    elif identification_rate >= 70:
        print(f"🟡 FAIR: Decent identification rate, room for improvement")
    else:
        print(f"🔴 NEEDS WORK: Low identification rate, requires attention")
    
    # Compare to original state
    print(f"\n📈 IMPROVEMENT FROM ORIGINAL STATE")
    print("-" * 40)
    print(f"Original unknown transactions: 1,095")
    print(f"Current unidentified transactions: {len(problematic_txs):,}")
    print(f"Improvement: {1095 - len(problematic_txs):,} transactions identified ({((1095 - len(problematic_txs))/1095)*100:.1f}%)")
    
    return {
        'total_transactions': len(df),
        'unidentified_count': len(problematic_txs),
        'identification_rate': identification_rate,
        'unknown_chain': len(unknown_chain),
        'missing_wallets': len(missing_wallets),
        'unknown_platforms': len(unknown_platforms)
    }

if __name__ == "__main__":
    results = analyze_unidentified_transactions()
    
    print(f"\n🎯 SUMMARY")
    print(f"Total transactions: {results['total_transactions']:,}")
    print(f"Unidentified: {results['unidentified_count']:,}")
    print(f"Identification rate: {results['identification_rate']:.1f}%")