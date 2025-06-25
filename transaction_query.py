#!/usr/bin/env python3
"""
Transaction Query Tool - Analyze transaction data with filters and aggregations
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os

class TransactionQueryTool:
    def __init__(self, json_path: str = "data/JSON_out/clm_transactions.json"):
        self.json_path = json_path
        self.transactions = []
        self.df = None
        self.load_transactions()
    
    def load_transactions(self):
        """Load transactions from JSON file"""
        try:
            with open(self.json_path, 'r') as f:
                self.transactions = json.load(f)
            
            if self.transactions:
                self.df = pd.DataFrame(self.transactions)
                # Convert timestamp to datetime if it exists
                if 'timestamp' in self.df.columns:
                    self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], errors='coerce')
                # Convert gas_fees to numeric
                if 'gas_fees' in self.df.columns:
                    self.df['gas_fees'] = pd.to_numeric(self.df['gas_fees'], errors='coerce').fillna(0)
                
                print(f"📊 Loaded {len(self.transactions)} transactions")
            else:
                print("⚠️  No transactions found")
                
        except FileNotFoundError:
            print(f"❌ Transaction file not found: {self.json_path}")
        except Exception as e:
            print(f"❌ Error loading transactions: {e}")
    
    def query(self, 
              chain: Optional[str] = None,
              platform: Optional[str] = None,
              wallet: Optional[str] = None,
              start_date: Optional[str] = None,
              end_date: Optional[str] = None,
              min_gas: Optional[float] = None,
              max_gas: Optional[float] = None,
              limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Query transactions with filters
        
        Args:
            chain: Filter by blockchain (SOL, ETH, SUI, etc.)
            platform: Filter by platform (Orca, Jupiter, etc.)
            wallet: Filter by wallet address
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            min_gas: Minimum gas fees
            max_gas: Maximum gas fees
            limit: Limit number of results
        
        Returns:
            Dictionary with filtered transactions and analytics
        """
        if self.df is None or len(self.df) == 0:
            return {"error": "No transaction data available"}
        
        # Start with all transactions
        filtered_df = self.df.copy()
        
        # Apply filters
        filters_applied = []
        
        if chain:
            filtered_df = filtered_df[filtered_df['chain'].str.upper() == chain.upper()]
            filters_applied.append(f"chain={chain}")
        
        if platform:
            filtered_df = filtered_df[filtered_df['platform'].str.contains(platform, case=False, na=False)]
            filters_applied.append(f"platform={platform}")
        
        if wallet:
            filtered_df = filtered_df[filtered_df['wallet'].str.contains(wallet, case=False, na=False)]
            filters_applied.append(f"wallet={wallet[:10]}...")
        
        if start_date:
            try:
                start_dt = pd.to_datetime(start_date)
                filtered_df = filtered_df[filtered_df['timestamp'] >= start_dt]
                filters_applied.append(f"start_date={start_date}")
            except:
                pass
        
        if end_date:
            try:
                end_dt = pd.to_datetime(end_date)
                filtered_df = filtered_df[filtered_df['timestamp'] <= end_dt]
                filters_applied.append(f"end_date={end_date}")
            except:
                pass
        
        if min_gas is not None:
            filtered_df = filtered_df[filtered_df['gas_fees'] >= min_gas]
            filters_applied.append(f"min_gas={min_gas}")
        
        if max_gas is not None:
            filtered_df = filtered_df[filtered_df['gas_fees'] <= max_gas]
            filters_applied.append(f"max_gas={max_gas}")
        
        # Apply limit
        if limit:
            filtered_df = filtered_df.head(limit)
            filters_applied.append(f"limit={limit}")
        
        # Calculate analytics
        analytics = self._calculate_analytics(filtered_df)
        
        return {
            "filters_applied": filters_applied,
            "total_transactions": len(filtered_df),
            "analytics": analytics,
            "transactions": filtered_df.to_dict('records') if len(filtered_df) <= 100 else "Too many results (use limit parameter)"
        }
    
    def _calculate_analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate analytics for filtered transactions"""
        if len(df) == 0:
            return {"error": "No transactions match filters"}
        
        analytics = {
            "count": len(df),
            "gas_fees": {
                "total": float(df['gas_fees'].sum()),
                "average": float(df['gas_fees'].mean()),
                "median": float(df['gas_fees'].median()),
                "min": float(df['gas_fees'].min()),
                "max": float(df['gas_fees'].max())
            },
            "chains": df['chain'].value_counts().to_dict(),
            "platforms": df['platform'].value_counts().to_dict(),
            "unique_wallets": df['wallet'].nunique()
        }
        
        # Time analysis if timestamps available
        if 'timestamp' in df.columns and not df['timestamp'].isna().all():
            valid_timestamps = df.dropna(subset=['timestamp'])
            if len(valid_timestamps) > 0:
                analytics["time_window"] = {
                    "earliest": valid_timestamps['timestamp'].min().isoformat(),
                    "latest": valid_timestamps['timestamp'].max().isoformat(),
                    "span_days": (valid_timestamps['timestamp'].max() - valid_timestamps['timestamp'].min()).days
                }
                
                # Daily transaction counts
                daily_counts = valid_timestamps.groupby(valid_timestamps['timestamp'].dt.date).size()
                analytics["daily_activity"] = {
                    "avg_per_day": float(daily_counts.mean()),
                    "max_per_day": int(daily_counts.max()),
                    "min_per_day": int(daily_counts.min()),
                    "most_active_day": str(daily_counts.idxmax()),
                    "transactions_on_most_active": int(daily_counts.max())
                }
        
        return analytics
    
    def quick_stats(self) -> Dict[str, Any]:
        """Get quick overview stats"""
        if self.df is None or len(self.df) == 0:
            return {"error": "No transaction data available"}
        
        return {
            "total_transactions": len(self.df),
            "total_gas_fees": float(self.df['gas_fees'].sum()),
            "chains": list(self.df['chain'].unique()),
            "platforms": list(self.df['platform'].unique()),
            "unique_wallets": self.df['wallet'].nunique(),
            "date_range": self._get_date_range()
        }
    
    def _get_date_range(self) -> Dict[str, str]:
        """Get date range of transactions"""
        if 'timestamp' in self.df.columns:
            valid_timestamps = self.df.dropna(subset=['timestamp'])
            if len(valid_timestamps) > 0:
                return {
                    "earliest": valid_timestamps['timestamp'].min().strftime('%Y-%m-%d'),
                    "latest": valid_timestamps['timestamp'].max().strftime('%Y-%m-%d')
                }
        return {"earliest": "N/A", "latest": "N/A"}
    
    def top_gas_spenders(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find wallets that spent the most on gas"""
        if self.df is None or len(self.df) == 0:
            return []
        
        gas_by_wallet = self.df.groupby('wallet')['gas_fees'].agg(['sum', 'count', 'mean']).round(6)
        gas_by_wallet = gas_by_wallet.sort_values('sum', ascending=False).head(top_n)
        
        result = []
        for wallet, row in gas_by_wallet.iterrows():
            result.append({
                "wallet": wallet[:10] + "..." if len(wallet) > 10 else wallet,
                "total_gas": float(row['sum']),
                "tx_count": int(row['count']),
                "avg_gas": float(row['mean'])
            })
        
        return result
    
    def platform_analysis(self) -> Dict[str, Any]:
        """Analyze activity by platform"""
        if self.df is None or len(self.df) == 0:
            return {}
        
        platform_stats = self.df.groupby('platform').agg({
            'tx_hash': 'count',
            'gas_fees': ['sum', 'mean'],
            'wallet': 'nunique'
        }).round(6)
        
        platform_stats.columns = ['tx_count', 'total_gas', 'avg_gas', 'unique_wallets']
        
        result = {}
        for platform, row in platform_stats.iterrows():
            result[platform] = {
                "transactions": int(row['tx_count']),
                "total_gas": float(row['total_gas']),
                "avg_gas_per_tx": float(row['avg_gas']),
                "unique_wallets": int(row['unique_wallets'])
            }
        
        return result

def main():
    """Interactive CLI for transaction queries"""
    query_tool = TransactionQueryTool()
    
    if not query_tool.transactions:
        print("❌ No transaction data available. Make sure to import transactions first.")
        return
    
    print("🔍 Transaction Query Tool")
    print("=" * 50)
    
    while True:
        print("\n📊 Query Options:")
        print("  [1] Quick Stats Overview")
        print("  [2] Custom Query with Filters")
        print("  [3] Top Gas Spenders")
        print("  [4] Platform Analysis")
        print("  [5] Chain Analysis")
        print("  [q] Quit")
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice in ['q', 'quit', 'exit']:
            break
        
        elif choice == '1':
            print("\n📈 Quick Stats:")
            stats = query_tool.quick_stats()
            print(f"  📊 Total Transactions: {stats['total_transactions']:,}")
            print(f"  ⛽ Total Gas Fees: ${stats['total_gas_fees']:.6f}")
            print(f"  ⛓️  Chains: {', '.join(stats['chains'])}")
            print(f"  🏪 Platforms: {len(stats['platforms'])} different")
            print(f"  👛 Unique Wallets: {stats['unique_wallets']}")
            print(f"  📅 Date Range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
        elif choice == '2':
            print("\n🔍 Custom Query Builder:")
            chain = input("Chain (SOL/ETH/SUI/BASE/ARB) [Enter for all]: ").strip() or None
            platform = input("Platform (Orca/Jupiter/etc.) [Enter for all]: ").strip() or None
            start_date = input("Start date (YYYY-MM-DD) [Enter for all]: ").strip() or None
            end_date = input("End date (YYYY-MM-DD) [Enter for all]: ").strip() or None
            
            try:
                min_gas = input("Min gas fees [Enter for all]: ").strip()
                min_gas = float(min_gas) if min_gas else None
            except:
                min_gas = None
            
            try:
                limit = input("Limit results [Enter for no limit]: ").strip()
                limit = int(limit) if limit else None
            except:
                limit = None
            
            result = query_tool.query(
                chain=chain, platform=platform, 
                start_date=start_date, end_date=end_date,
                min_gas=min_gas, limit=limit
            )
            
            print(f"\n🎯 Query Results:")
            print(f"  🔍 Filters: {', '.join(result['filters_applied'])}")
            print(f"  📊 Matching Transactions: {result['total_transactions']:,}")
            
            if 'analytics' in result:
                analytics = result['analytics']
                print(f"  ⛽ Total Gas: ${analytics['gas_fees']['total']:.6f}")
                print(f"  ⛽ Avg Gas: ${analytics['gas_fees']['average']:.6f}")
                print(f"  ⛓️  Chains: {analytics['chains']}")
                print(f"  🏪 Platforms: {analytics['platforms']}")
                
                if 'time_window' in analytics:
                    tw = analytics['time_window']
                    print(f"  📅 Time Span: {tw['span_days']} days ({tw['earliest'][:10]} to {tw['latest'][:10]})")
        
        elif choice == '3':
            print("\n🔥 Top 10 Gas Spenders:")
            spenders = query_tool.top_gas_spenders(10)
            for i, spender in enumerate(spenders, 1):
                print(f"  {i:2}. {spender['wallet']} - ${spender['total_gas']:.6f} ({spender['tx_count']} txs)")
        
        elif choice == '4':
            print("\n🏪 Platform Analysis:")
            platforms = query_tool.platform_analysis()
            for platform, stats in platforms.items():
                print(f"  {platform}:")
                print(f"    📊 {stats['transactions']:,} transactions")
                print(f"    ⛽ ${stats['total_gas']:.6f} total gas")
                print(f"    👛 {stats['unique_wallets']} unique wallets")
        
        elif choice == '5':
            print("\n⛓️  Chain Analysis:")
            result = query_tool.query()
            if 'analytics' in result:
                chains = result['analytics']['chains']
                for chain, count in chains.items():
                    print(f"  {chain}: {count:,} transactions")
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()