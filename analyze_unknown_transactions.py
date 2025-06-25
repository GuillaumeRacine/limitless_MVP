#!/usr/bin/env python3
"""
Comprehensive analysis of unknown transactions to understand available data
"""

from clm_data import CLMDataManager
import pandas as pd
import json

def analyze_unknown_transactions():
    print("🔍 COMPREHENSIVE ANALYSIS OF UNKNOWN TRANSACTIONS")
    print("="*80)
    
    # Initialize data manager
    data_manager = CLMDataManager()
    
    # Load transaction data
    transactions = data_manager.load_transactions()
    
    if not transactions:
        print("❌ No transaction data found")
        return
    
    df = pd.DataFrame(transactions)
    
    # Filter for unknown transactions
    unknown_txs = df[df['chain'] == 'Unknown']
    
    print(f"📊 Total transactions: {len(df):,}")
    print(f"📊 Unknown chain transactions: {len(unknown_txs):,}")
    print(f"📊 Analysis sample: First 10 unknown transactions")
    print()
    
    print("🔬 DETAILED FIELD ANALYSIS")
    print("="*80)
    
    # Show structure of first few unknown transactions
    sample_unknown = unknown_txs.head(10)
    
    for i, (_, tx) in enumerate(sample_unknown.iterrows(), 1):
        print(f"\n📋 Unknown Transaction #{i}")
        print("-" * 60)
        
        # Show all top-level fields
        print("TOP-LEVEL FIELDS:")
        for key, value in tx.items():
            if key != 'raw_data':
                print(f"  {key:<18}: {value}")
        
        # Show raw_data in detail
        raw_data = tx.get('raw_data', {})
        if raw_data:
            print(f"\nRAW_DATA FIELDS ({len(raw_data)} fields):")
            for key, value in raw_data.items():
                # Truncate long values
                value_str = str(value)
                if len(value_str) > 80:
                    value_str = value_str[:77] + "..."
                print(f"  {key:<20}: {value_str}")
        
        if i >= 3:  # Show detailed view for first 3 only
            break
    
    print(f"\n" + "="*80)
    print("📊 STATISTICAL ANALYSIS OF UNKNOWN TRANSACTIONS")
    print("="*80)
    
    # Analyze raw_data fields across all unknown transactions
    all_raw_fields = {}
    field_value_samples = {}
    
    for _, tx in unknown_txs.iterrows():
        raw_data = tx.get('raw_data', {})
        if isinstance(raw_data, dict):
            for field, value in raw_data.items():
                if field not in all_raw_fields:
                    all_raw_fields[field] = 0
                    field_value_samples[field] = set()
                
                all_raw_fields[field] += 1
                
                # Collect sample values (limit to avoid memory issues)
                value_str = str(value).strip()
                if value_str and value_str.lower() not in ['nan', 'none', ''] and len(field_value_samples[field]) < 10:
                    field_value_samples[field].add(value_str[:50])  # Truncate long values
    
    print(f"\n📋 RAW_DATA FIELD FREQUENCY ANALYSIS")
    print(f"Found {len(all_raw_fields)} unique fields across {len(unknown_txs)} unknown transactions")
    print("-" * 80)
    print(f"{'Field Name':<25} {'Frequency':<12} {'Sample Values'}")
    print("-" * 80)
    
    # Sort by frequency
    sorted_fields = sorted(all_raw_fields.items(), key=lambda x: x[1], reverse=True)
    
    for field, count in sorted_fields:
        percentage = (count / len(unknown_txs)) * 100
        samples = list(field_value_samples[field])[:3]  # Show up to 3 samples
        samples_str = " | ".join(samples) if samples else "No valid samples"
        if len(samples_str) > 50:
            samples_str = samples_str[:47] + "..."
        
        print(f"{field:<25} {count:>6} ({percentage:>5.1f}%) {samples_str}")
    
    print(f"\n🔍 CHAIN DETECTION ANALYSIS")
    print("-" * 60)
    
    # Look for chain indicators in raw_data
    chain_indicators = {
        'ethereum': ['ethereum', 'eth', 'mainnet', 'erc-20', 'erc20'],
        'base': ['base', 'base mainnet', 'base chain'],
        'arbitrum': ['arbitrum', 'arb', 'arbitrum one'],
        'optimism': ['optimism', 'op', 'op mainnet'],
        'polygon': ['polygon', 'matic', 'polygon pos'],
        'solana': ['solana', 'sol', 'spl'],
        'sui': ['sui', 'sui mainnet']
    }
    
    chain_detection_results = {}
    
    for _, tx in unknown_txs.head(100).iterrows():  # Sample first 100
        raw_data = tx.get('raw_data', {})
        
        # Check various fields for chain indicators
        search_fields = ['Chain', 'Network', 'Blockchain', 'Token Symbol', 'Buy Currency', 'Sell Currency', 'Platform', 'Exchange']
        
        detected_chains = set()
        for field in search_fields:
            if field in raw_data:
                value = str(raw_data[field]).lower()
                for chain, indicators in chain_indicators.items():
                    if any(indicator in value for indicator in indicators):
                        detected_chains.add(chain)
        
        if detected_chains:
            key = ', '.join(sorted(detected_chains))
            if key not in chain_detection_results:
                chain_detection_results[key] = 0
            chain_detection_results[key] += 1
    
    if chain_detection_results:
        print("Potential chain detection from raw_data (sample of 100):")
        for chains, count in sorted(chain_detection_results.items(), key=lambda x: x[1], reverse=True):
            print(f"  {chains}: {count} transactions")
    else:
        print("No clear chain indicators found in raw_data fields")
    
    print(f"\n🏪 PLATFORM DETECTION ANALYSIS")
    print("-" * 60)
    
    # Look for platform indicators
    platform_fields = ['Platform', 'Exchange', 'Venue', 'Protocol', 'App Name', 'Application']
    platform_values = {}
    
    for _, tx in unknown_txs.head(100).iterrows():
        raw_data = tx.get('raw_data', {})
        
        for field in platform_fields:
            if field in raw_data and raw_data[field]:
                value = str(raw_data[field]).strip()
                if value and value.lower() not in ['nan', 'none', 'unknown']:
                    if value not in platform_values:
                        platform_values[value] = 0
                    platform_values[value] += 1
    
    if platform_values:
        print("Potential platforms found (sample of 100):")
        sorted_platforms = sorted(platform_values.items(), key=lambda x: x[1], reverse=True)
        for platform, count in sorted_platforms[:10]:
            print(f"  {platform}: {count} transactions")
    else:
        print("No clear platform indicators found")
    
    print(f"\n💡 ENHANCEMENT RECOMMENDATIONS")
    print("="*80)
    
    # Provide specific enhancement strategies
    enhancement_strategies = []
    
    if 'Buy Currency' in all_raw_fields or 'Sell Currency' in all_raw_fields:
        enhancement_strategies.append("✅ Currency-based chain detection (ETH→ethereum, SOL→solana, etc.)")
    
    if 'Exchange' in all_raw_fields or 'Platform' in all_raw_fields:
        enhancement_strategies.append("✅ Platform-based chain mapping (Uniswap→ethereum, Orca→solana, etc.)")
    
    if 'Transaction Type' in all_raw_fields:
        enhancement_strategies.append("✅ Transaction type analysis for platform classification")
    
    if 'Buy Fiat Amount' in all_raw_fields:
        enhancement_strategies.append("✅ Fiat amount analysis for transaction value extraction")
    
    enhancement_strategies.extend([
        "✅ Token symbol standardization (WETH→ETH, USDC.e→USDC)",
        "✅ Cross-reference with known wallet addresses for chain inference",
        "✅ Timestamp pattern analysis for exchange-specific formats",
        "✅ Fee pattern analysis (gas fees vs trading fees)"
    ])
    
    for strategy in enhancement_strategies:
        print(f"  {strategy}")
    
    print(f"\n🎯 PRIORITY ENHANCEMENT AREAS:")
    print(f"  1. Currency symbol → Chain mapping")
    print(f"  2. Platform/Exchange → Chain mapping") 
    print(f"  3. Wallet address inference from transaction context")
    print(f"  4. Transaction amount and fee normalization")

if __name__ == "__main__":
    analyze_unknown_transactions()