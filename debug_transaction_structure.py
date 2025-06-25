#!/usr/bin/env python3
"""
Debug transaction data structure to understand available fields
"""

from clm_data import CLMDataManager
import pandas as pd
import json

def debug_transaction_structure():
    print("🔍 Debugging Transaction Data Structure")
    print("="*70)
    
    # Initialize data manager
    data_manager = CLMDataManager()
    
    # Load transaction data
    transactions = data_manager.load_transactions()
    
    if not transactions:
        print("❌ No transaction data found")
        return
    
    df = pd.DataFrame(transactions)
    
    print(f"📊 Loaded {len(transactions)} transactions")
    print(f"📊 Available columns: {list(df.columns)}")
    print()
    
    # Check first few transactions in detail
    print("🔬 DETAILED INSPECTION OF FIRST 3 TRANSACTIONS")
    print("="*70)
    
    for i in range(min(3, len(transactions))):
        tx = transactions[i]
        print(f"\nTransaction #{i+1}:")
        print("-" * 40)
        
        for key, value in tx.items():
            if key == 'raw_data' and isinstance(value, dict):
                print(f"  {key}:")
                for subkey, subvalue in value.items():
                    print(f"    {subkey}: {subvalue}")
            else:
                print(f"  {key}: {value}")
    
    # Check chain distribution
    print(f"\n📈 CHAIN DISTRIBUTION")
    print("-" * 40)
    chain_counts = df['chain'].value_counts()
    for chain, count in chain_counts.items():
        print(f"  {chain}: {count:,} transactions")
    
    # Check platform distribution
    print(f"\n🏪 PLATFORM DISTRIBUTION")
    print("-" * 40)
    platform_counts = df['platform'].value_counts()
    for platform, count in platform_counts.head(10).items():
        print(f"  {platform}: {count:,} transactions")
    
    # Check for source file information
    print(f"\n📁 SOURCE FILE INFORMATION")
    print("-" * 40)
    
    if 'source_file' in df.columns:
        source_files = df['source_file'].value_counts()
        print(f"Found {len(source_files)} unique source files:")
        for file, count in source_files.head(10).items():
            print(f"  {file}: {count:,} transactions")
    else:
        print("  No source_file column found")
    
    # Check raw_data fields across all transactions
    print(f"\n📋 RAW_DATA FIELD ANALYSIS")
    print("-" * 40)
    
    all_raw_fields = set()
    for tx in transactions[:100]:  # Sample first 100
        raw_data = tx.get('raw_data', {})
        if isinstance(raw_data, dict):
            all_raw_fields.update(raw_data.keys())
    
    print(f"Found {len(all_raw_fields)} unique raw_data fields:")
    for field in sorted(all_raw_fields):
        print(f"  {field}")
    
    # Check for wallet-like fields in raw_data
    print(f"\n🔍 POTENTIAL WALLET FIELDS IN RAW_DATA")
    print("-" * 40)
    
    wallet_like_fields = []
    for field in all_raw_fields:
        if any(keyword in field.lower() for keyword in ['wallet', 'address', 'from', 'to', 'account', 'user']):
            wallet_like_fields.append(field)
    
    if wallet_like_fields:
        print("Found potential wallet fields:")
        for field in wallet_like_fields:
            print(f"  {field}")
            
            # Show sample values
            sample_values = []
            for tx in transactions[:50]:
                raw_data = tx.get('raw_data', {})
                if field in raw_data and raw_data[field]:
                    value = str(raw_data[field]).strip()
                    if value and value not in sample_values and len(sample_values) < 3:
                        sample_values.append(value)
            
            if sample_values:
                print(f"    Sample values: {sample_values}")
    else:
        print("No obvious wallet fields found in raw_data")

if __name__ == "__main__":
    debug_transaction_structure()