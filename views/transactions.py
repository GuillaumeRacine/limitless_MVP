#!/usr/bin/env python3
"""
Enhanced Transactions View - Comprehensive transaction analysis with fee breakdown, MEV estimation, and strategy insights
"""

from datetime import datetime, timedelta
import statistics
import pandas as pd

class TransactionsView:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def display(self):
        """Display comprehensive transactions analysis with bank statement view"""
        print("\n" + "="*150)
        print("💰 COMPREHENSIVE TRANSACTION ANALYSIS")
        print("="*150)
        
        # Load all transaction data
        transactions = self.data_manager.load_transactions()
        positions = self.data_manager.get_all_active_positions() + self.data_manager.get_positions_by_strategy('closed')
        
        if not transactions:
            print("📊 No imported transaction data available.")
            print("💡 Use [A]sk → Import transactions to load transaction CSV files.")
            return
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(transactions)
        
        # Show menu options
        print("\n📋 Transaction Analysis Options:")
        print("  [1] Bank Statement View (Chronological)")
        print("  [2] Comprehensive Analysis Dashboard")
        print("  [3] Quick Summary Only")
        
        choice = input("\nSelect view (1-3) [default: 1]: ").strip() or "1"
        
        if choice == "1":
            self._display_bank_statement_view(df)
        elif choice == "2":
            # Display comprehensive analysis
            self._display_overview_summary(df)
            self._display_chain_platform_breakdown(df)
            self._display_fee_analysis(df, positions)
            self._display_strategy_breakdown(df, positions)
            self._display_wallet_analysis(df)
            self._display_time_analysis(df)
            self._display_cost_efficiency_analysis(df, positions)
        elif choice == "3":
            self._display_overview_summary(df)
        else:
            print("❌ Invalid choice, showing bank statement view")
            self._display_bank_statement_view(df)
    
    def _display_overview_summary(self, df):
        """Display high-level transaction overview"""
        print(f"\n📊 TRANSACTION DATABASE OVERVIEW")
        print("-" * 80)
        
        total_txns = len(df)
        total_gas = df['gas_fees'].fillna(0).sum()
        unique_wallets = df['wallet'].nunique()
        unique_platforms = df['platform'].nunique()
        unique_chains = df['chain'].nunique()
        
        # Date range
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        valid_dates = df.dropna(subset=['timestamp'])
        if len(valid_dates) > 0:
            date_range = f"{valid_dates['timestamp'].min().strftime('%Y-%m-%d')} to {valid_dates['timestamp'].max().strftime('%Y-%m-%d')}"
            days_span = (valid_dates['timestamp'].max() - valid_dates['timestamp'].min()).days
        else:
            date_range = "No valid dates"
            days_span = 0
        
        print(f"📈 Total Transactions: {total_txns:,}")
        print(f"⛽ Total Gas Fees: ${total_gas:.6f}")
        print(f"👛 Unique Wallets: {unique_wallets}")
        print(f"🏪 Platforms: {unique_platforms}")
        print(f"⛓️  Chains: {unique_chains}")
        print(f"📅 Date Range: {date_range} ({days_span} days)")
        if days_span > 0:
            print(f"📊 Avg Transactions/Day: {total_txns / days_span:.1f}")
    
    def _display_chain_platform_breakdown(self, df):
        """Display detailed chain and platform breakdown with transaction counts and values"""
        print(f"\n🌐 CHAIN & PLATFORM BREAKDOWN")
        print("-" * 120)
        
        # Chain breakdown
        chain_stats = df.groupby('chain').agg({
            'tx_hash': 'count',
            'gas_fees': ['sum', 'mean'],
            'platform': 'nunique',
            'wallet': 'nunique'
        }).round(6)
        
        chain_stats.columns = ['tx_count', 'total_gas', 'avg_gas', 'platforms', 'wallets']
        chain_stats = chain_stats.sort_values('tx_count', ascending=False)
        
        print(f"{'Chain':<8} {'Transactions':<12} {'Total Gas':<12} {'Avg Gas':<12} {'Platforms':<10} {'Wallets':<8}")
        print("-" * 70)
        
        for chain, stats in chain_stats.iterrows():
            print(f"{chain:<8} {stats['tx_count']:>11,} ${stats['total_gas']:>10.6f} "
                  f"${stats['avg_gas']:>10.6f} {stats['platforms']:>9} {stats['wallets']:>7}")
        
        # Platform breakdown (top 10)
        print(f"\n🏪 TOP PLATFORMS BY TRANSACTION COUNT")
        print("-" * 100)
        
        platform_stats = df.groupby('platform').agg({
            'tx_hash': 'count',
            'gas_fees': ['sum', 'mean'],
            'chain': lambda x: ', '.join(x.unique()[:3]),  # Show up to 3 chains
            'wallet': 'nunique'
        }).round(6)
        
        platform_stats.columns = ['tx_count', 'total_gas', 'avg_gas', 'chains', 'wallets']
        platform_stats = platform_stats.sort_values('tx_count', ascending=False).head(10)
        
        print(f"{'Platform':<15} {'Transactions':<12} {'Total Gas':<12} {'Avg Gas':<12} {'Chains':<15} {'Wallets':<8}")
        print("-" * 90)
        
        for platform, stats in platform_stats.iterrows():
            chains_str = stats['chains'][:13] + "..." if len(stats['chains']) > 13 else stats['chains']
            print(f"{platform[:14]:<15} {stats['tx_count']:>11,} ${stats['total_gas']:>10.6f} "
                  f"${stats['avg_gas']:>10.6f} {chains_str:<15} {stats['wallets']:>7}")
    
    def _display_fee_analysis(self, df, positions):
        """Analyze transaction fees, MEV, and slippage costs"""
        print(f"\n💸 TRANSACTION COST ANALYSIS")
        print("-" * 120)
        
        # Calculate actual costs from transactions
        total_gas = df['gas_fees'].fillna(0).sum()
        avg_gas = df['gas_fees'].fillna(0).mean()
        median_gas = df['gas_fees'].fillna(0).median()
        max_gas = df['gas_fees'].fillna(0).max()
        
        # Estimate other costs from position data
        total_entry_value = sum([p.get('entry_value', 0) or 0 for p in positions])
        
        # Estimate MEV (typically 0.01-0.05% of transaction value for DEX trades)
        estimated_mev = total_entry_value * 0.0003  # Conservative 0.03% estimate
        
        # Calculate slippage and fees from position data
        total_slippage = 0
        total_tx_fees = 0
        
        for pos in positions:
            if pos.get('slippage') and pos.get('entry_value'):
                total_slippage += pos['entry_value'] * (pos['slippage'] / 100)
            if pos.get('transaction_fees') and pos.get('entry_value'):
                total_tx_fees += pos['entry_value'] * (pos['transaction_fees'] / 100)
        
        print(f"⛽ GAS FEES ANALYSIS")
        print(f"   Total Gas Paid: ${total_gas:.6f}")
        print(f"   Average per Tx: ${avg_gas:.6f}")
        print(f"   Median per Tx: ${median_gas:.6f}")
        print(f"   Highest Gas Tx: ${max_gas:.6f}")
        
        print(f"\n💰 ESTIMATED TRADING COSTS")
        print(f"   🔄 Protocol Fees: ${total_tx_fees:.2f} (from position data)")
        print(f"   📉 Slippage Costs: ${total_slippage:.2f} (from position data)")
        print(f"   🤖 MEV/Frontrunning: ${estimated_mev:.2f} (estimated)")
        print(f"   ⛽ Network Gas: ${total_gas:.6f}")
        
        total_costs = total_tx_fees + total_slippage + estimated_mev + total_gas
        print(f"   💸 TOTAL ESTIMATED COSTS: ${total_costs:.2f}")
        
        if total_entry_value > 0:
            cost_percentage = (total_costs / total_entry_value) * 100
            print(f"   📊 Cost as % of Capital: {cost_percentage:.3f}%")
        
        # Cost efficiency by platform
        print(f"\n🏪 COST EFFICIENCY BY PLATFORM")
        print("-" * 80)
        
        platform_efficiency = df.groupby('platform').agg({
            'gas_fees': ['sum', 'mean', 'count']
        }).round(6)
        
        platform_efficiency.columns = ['total_gas', 'avg_gas', 'tx_count']
        platform_efficiency = platform_efficiency[platform_efficiency['tx_count'] >= 1].sort_values('avg_gas')
        
        print(f"{'Platform':<15} {'Transactions':<12} {'Total Gas':<12} {'Avg Gas/Tx':<12} {'Efficiency':<10}")
        print("-" * 70)
        
        for platform, stats in platform_efficiency.head(10).iterrows():
            if stats['avg_gas'] <= 0.001:
                efficiency = "🟢 Low"
            elif stats['avg_gas'] <= 0.005:
                efficiency = "🟡 Medium"
            else:
                efficiency = "🔴 High"
            
            print(f"{platform[:14]:<15} {stats['tx_count']:>11,} ${stats['total_gas']:>10.6f} "
                  f"${stats['avg_gas']:>10.6f} {efficiency:<10}")
    
    def _display_strategy_breakdown(self, df, positions):
        """Analyze transactions by trading strategy"""
        print(f"\n📈 STRATEGY-SPECIFIC ANALYSIS")
        print("-" * 120)
        
        # Map transactions to strategies using position data
        position_strategies = {pos['id']: pos['strategy'] for pos in positions}
        
        # Create strategy breakdown from positions since tx data doesn't have strategy info
        long_positions = [p for p in positions if p['strategy'] == 'long']
        neutral_positions = [p for p in positions if p['strategy'] == 'neutral']
        
        # Calculate strategy metrics
        long_entry_value = sum([p.get('entry_value', 0) or 0 for p in long_positions])
        neutral_entry_value = sum([p.get('entry_value', 0) or 0 for p in neutral_positions])
        total_entry_value = long_entry_value + neutral_entry_value
        
        long_platforms = set([p['platform'] for p in long_positions])
        neutral_platforms = set([p['platform'] for p in neutral_positions])
        
        # Estimate transaction distribution based on entry values
        total_gas = df['gas_fees'].fillna(0).sum()
        total_txns = len(df)
        
        if total_entry_value > 0:
            long_gas_estimate = total_gas * (long_entry_value / total_entry_value)
            neutral_gas_estimate = total_gas * (neutral_entry_value / total_entry_value)
            
            long_txn_estimate = int(total_txns * (long_entry_value / total_entry_value))
            neutral_txn_estimate = total_txns - long_txn_estimate
        else:
            long_gas_estimate = neutral_gas_estimate = 0
            long_txn_estimate = neutral_txn_estimate = 0
        
        print(f"📊 STRATEGY COMPARISON")
        print("-" * 80)
        print(f"{'Strategy':<15} {'Positions':<10} {'Entry Value':<15} {'Est. Gas':<12} {'Est. Txns':<10} {'Platforms':<15}")
        print("-" * 80)
        
        print(f"{'📈 Long':<15} {len(long_positions):>9} ${long_entry_value:>13,.0f} "
              f"${long_gas_estimate:>10.6f} {long_txn_estimate:>9} {len(long_platforms):>9}")
        
        print(f"{'⚖️  Neutral':<15} {len(neutral_positions):>9} ${neutral_entry_value:>13,.0f} "
              f"${neutral_gas_estimate:>10.6f} {neutral_txn_estimate:>9} {len(neutral_platforms):>9}")
        
        # Strategy efficiency analysis
        print(f"\n💡 STRATEGY INSIGHTS")
        print("-" * 60)
        
        if len(long_positions) > 0:
            avg_long_position = long_entry_value / len(long_positions)
            long_gas_per_dollar = long_gas_estimate / long_entry_value if long_entry_value > 0 else 0
            print(f"📈 Long Strategy:")
            print(f"   Average Position Size: ${avg_long_position:,.0f}")
            print(f"   Gas Cost per $1000: ${long_gas_per_dollar * 1000:.6f}")
            print(f"   Most Used Platforms: {', '.join(list(long_platforms)[:3])}")
        
        if len(neutral_positions) > 0:
            avg_neutral_position = neutral_entry_value / len(neutral_positions)
            neutral_gas_per_dollar = neutral_gas_estimate / neutral_entry_value if neutral_entry_value > 0 else 0
            print(f"\n⚖️  Neutral Strategy:")
            print(f"   Average Position Size: ${avg_neutral_position:,.0f}")
            print(f"   Gas Cost per $1000: ${neutral_gas_per_dollar * 1000:.6f}")
            print(f"   Most Used Platforms: {', '.join(list(neutral_platforms)[:3])}")
    
    def _display_wallet_analysis(self, df):
        """Analyze activity and costs by wallet"""
        print(f"\n👛 WALLET-LEVEL ANALYSIS")
        print("-" * 100)
        
        wallet_stats = df.groupby('wallet').agg({
            'tx_hash': 'count',
            'gas_fees': ['sum', 'mean'],
            'platform': lambda x: len(x.unique()),
            'chain': lambda x: ', '.join(x.unique()[:3])
        }).round(6)
        
        wallet_stats.columns = ['tx_count', 'total_gas', 'avg_gas', 'platforms', 'chains']
        wallet_stats = wallet_stats.sort_values('total_gas', ascending=False)
        
        print(f"{'Wallet (Truncated)':<20} {'Txns':<6} {'Total Gas':<12} {'Avg Gas':<12} {'Platforms':<10} {'Chains':<15}")
        print("-" * 85)
        
        for wallet, stats in wallet_stats.head(10).iterrows():
            wallet_short = wallet[:8] + "..." + wallet[-8:] if len(wallet) > 16 else wallet
            chains_str = stats['chains'][:13] + "..." if len(stats['chains']) > 13 else stats['chains']
            
            print(f"{wallet_short:<20} {stats['tx_count']:>5,} ${stats['total_gas']:>10.6f} "
                  f"${stats['avg_gas']:>10.6f} {stats['platforms']:>9} {chains_str:<15}")
        
        # Wallet efficiency rankings
        if len(wallet_stats) > 1:
            print(f"\n🏆 WALLET EFFICIENCY RANKINGS")
            print("-" * 60)
            
            # Rank by lowest average gas (most efficient)
            efficient_wallets = wallet_stats[wallet_stats['tx_count'] >= 2].sort_values('avg_gas').head(5)
            
            print(f"⭐ Most Gas Efficient Wallets:")
            for i, (wallet, stats) in enumerate(efficient_wallets.iterrows(), 1):
                wallet_short = wallet[:12] + "..." if len(wallet) > 12 else wallet
                print(f"   {i}. {wallet_short} - ${stats['avg_gas']:.6f}/tx ({stats['tx_count']} txns)")
    
    def _display_time_analysis(self, df):
        """Analyze transaction patterns over time"""
        print(f"\n📅 TRANSACTION TIME ANALYSIS")
        print("-" * 100)
        
        # Convert timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        valid_df = df.dropna(subset=['timestamp'])
        
        if len(valid_df) == 0:
            print("⚠️  No valid timestamps available for time analysis")
            return
        
        # Daily activity analysis
        daily_stats = valid_df.groupby(valid_df['timestamp'].dt.date).agg({
            'tx_hash': 'count',
            'gas_fees': 'sum'
        }).round(6)
        
        daily_stats.columns = ['tx_count', 'daily_gas']
        daily_stats = daily_stats.sort_index(ascending=False).head(10)
        
        print(f"📊 DAILY ACTIVITY (Last 10 Days with Transactions)")
        print("-" * 60)
        print(f"{'Date':<12} {'Transactions':<12} {'Gas Fees':<12} {'Avg Gas/Tx':<12}")
        print("-" * 50)
        
        for date, stats in daily_stats.iterrows():
            avg_gas = stats['daily_gas'] / stats['tx_count'] if stats['tx_count'] > 0 else 0
            print(f"{str(date):<12} {stats['tx_count']:>11,} ${stats['daily_gas']:>10.6f} ${avg_gas:>10.6f}")
        
        # Peak activity analysis
        if len(daily_stats) > 0:
            peak_day = daily_stats.loc[daily_stats['tx_count'].idxmax()]
            high_gas_day = daily_stats.loc[daily_stats['daily_gas'].idxmax()]
            
            print(f"\n🔥 ACTIVITY PEAKS")
            print("-" * 40)
            print(f"📈 Highest Transaction Day: {daily_stats['tx_count'].idxmax()} ({peak_day['tx_count']} txns)")
            print(f"💸 Highest Gas Day: {daily_stats['daily_gas'].idxmax()} (${high_gas_day['daily_gas']:.6f})")
    
    def _display_cost_efficiency_analysis(self, df, positions):
        """Analyze cost efficiency and provide recommendations"""
        print(f"\n💡 COST EFFICIENCY INSIGHTS & RECOMMENDATIONS")
        print("-" * 120)
        
        total_gas = df['gas_fees'].fillna(0).sum()
        total_txns = len(df)
        total_entry_value = sum([p.get('entry_value', 0) or 0 for p in positions])
        
        print(f"📊 EFFICIENCY METRICS")
        print("-" * 50)
        print(f"💰 Capital Deployed: ${total_entry_value:,.0f}")
        print(f"⛽ Total Gas Costs: ${total_gas:.6f}")
        print(f"📊 Gas per $1000 Deployed: ${(total_gas / total_entry_value * 1000) if total_entry_value > 0 else 0:.6f}")
        print(f"🔢 Average Gas per Transaction: ${total_gas / total_txns if total_txns > 0 else 0:.6f}")
        
        # Platform recommendations
        platform_efficiency = df.groupby('platform')['gas_fees'].agg(['mean', 'count']).round(6)
        platform_efficiency = platform_efficiency[platform_efficiency['count'] >= 2].sort_values('mean')
        
        print(f"\n🏆 PLATFORM EFFICIENCY RANKINGS")
        print("-" * 60)
        print(f"{'Rank':<5} {'Platform':<15} {'Avg Gas/Tx':<12} {'Transactions':<12} {'Rating':<10}")
        print("-" * 55)
        
        for i, (platform, stats) in enumerate(platform_efficiency.head(10).iterrows(), 1):
            if stats['mean'] <= 0.001:
                rating = "🟢 Excellent"
            elif stats['mean'] <= 0.003:
                rating = "🟡 Good"
            elif stats['mean'] <= 0.005:
                rating = "🟠 Fair"
            else:
                rating = "🔴 Expensive"
            
            print(f"{i:<5} {platform[:14]:<15} ${stats['mean']:>10.6f} {stats['count']:>11,} {rating:<10}")
        
        # Recommendations
        print(f"\n💡 OPTIMIZATION RECOMMENDATIONS")
        print("-" * 60)
        
        if len(platform_efficiency) > 0:
            best_platform = platform_efficiency.index[0]
            worst_platform = platform_efficiency.index[-1]
            
            print(f"✅ Most Efficient Platform: {best_platform} (${platform_efficiency.loc[best_platform, 'mean']:.6f}/tx)")
            print(f"⚠️  Least Efficient Platform: {worst_platform} (${platform_efficiency.loc[worst_platform, 'mean']:.6f}/tx)")
        
        # Chain efficiency
        chain_efficiency = df.groupby('chain')['gas_fees'].agg(['mean', 'count']).round(6)
        chain_efficiency = chain_efficiency[chain_efficiency['count'] >= 2].sort_values('mean')
        
        if len(chain_efficiency) > 1:
            best_chain = chain_efficiency.index[0]
            print(f"⛓️  Most Efficient Chain: {best_chain} (${chain_efficiency.loc[best_chain, 'mean']:.6f}/tx)")
        
        # Cost optimization suggestions
        avg_gas = df['gas_fees'].fillna(0).mean()
        if avg_gas > 0.005:
            print(f"💸 High gas costs detected. Consider:")
            print(f"   • Batching transactions when possible")
            print(f"   • Using more efficient chains/platforms")
            print(f"   • Timing transactions during low network activity")
        
        print(f"\n🎯 STRATEGY OPTIMIZATION")
        print("-" * 40)
        print(f"📊 Current average gas cost represents {(avg_gas / (total_entry_value / total_txns) * 100) if total_entry_value > 0 and total_txns > 0 else 0:.4f}% of average position size")
        print(f"💡 Focus on platforms with gas costs < $0.003 per transaction for optimal efficiency")
    
    def _display_bank_statement_view(self, df):
        """Display chronological bank statement view of all transactions"""
        print("\n" + "="*150)
        print("🏦 TRANSACTION BANK STATEMENT - CHRONOLOGICAL VIEW")
        print("="*150)
        
        # Convert to DataFrame if needed
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        
        # Convert timestamps to datetime with multiple format support
        df['timestamp'] = self._parse_timestamps_flexible(df['timestamp'])
        
        # Filter out rows with invalid timestamps and sort by date (newest first)
        valid_df = df.dropna(subset=['timestamp']).sort_values('timestamp', ascending=False)
        
        # Filter out approve transactions
        valid_df = self._filter_approve_transactions(valid_df)
        
        if len(valid_df) == 0:
            print("⚠️  No transactions with valid timestamps found")
            return
        
        # Quick summary
        total_txns = len(valid_df)
        total_gas = valid_df['gas_fees'].fillna(0).sum()
        date_range = f"{valid_df['timestamp'].min().strftime('%Y-%m-%d')} to {valid_df['timestamp'].max().strftime('%Y-%m-%d')}"
        unique_chains = valid_df['chain'].nunique()
        unique_platforms = valid_df['platform'].nunique()
        
        print(f"📊 STATEMENT SUMMARY")
        print("-" * 80)
        print(f"📈 Total Transactions: {total_txns:,}")
        print(f"📅 Date Range: {date_range}")
        print(f"⛓️  Chains Covered: {unique_chains}")
        print(f"🏪 Platforms Used: {unique_platforms}")
        print(f"⛽ Total Gas Fees: ${total_gas:.6f}")
        
        # Pagination setup
        page_size = 50
        total_pages = (len(valid_df) + page_size - 1) // page_size
        
        print(f"\n📋 TRANSACTION HISTORY ({total_txns:,} transactions, {total_pages} pages)")
        print("-" * 150)
        
        # Ask for page or show first page
        try:
            page_input = input(f"Enter page number (1-{total_pages}) or 'all' for all transactions [default: 1]: ").strip()
            if page_input.lower() == 'all':
                show_all = True
                page = 1
            else:
                show_all = False
                page = int(page_input) if page_input else 1
                page = max(1, min(page, total_pages))
        except:
            show_all = False
            page = 1
        
        # Create wallet-to-strategy mapping from position data
        wallet_strategies = self._create_wallet_strategy_mapping()
        
        # Display enhanced header
        print(f"{'Date':<12} {'Strategy':<10} {'Action':<15} {'Token Units':<15} {'USD Value':<10} {'Token Pair':<15} {'Platform':<12} {'Chain':<8} {'Contract':<12}")
        print("-" * 170)
        
        if show_all:
            # Show all transactions
            for _, tx in valid_df.iterrows():
                self._print_enhanced_transaction_row(tx, wallet_strategies)
        else:
            # Show specific page
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_df = valid_df.iloc[start_idx:end_idx]
            
            for _, tx in page_df.iterrows():
                self._print_enhanced_transaction_row(tx, wallet_strategies)
            
            print("-" * 150)
            print(f"📄 Page {page} of {total_pages} | Showing {len(page_df)} transactions")
            if page < total_pages:
                print(f"💡 To see more: Re-run transactions view and select page {page + 1}")
        
        # Monthly summary
        self._display_monthly_summary(valid_df)
        
        # Chain and platform quick stats
        print(f"\n⛓️  CHAIN DISTRIBUTION")
        print("-" * 60)
        chain_counts = valid_df['chain'].value_counts()
        for chain, count in chain_counts.head(10).items():
            percentage = (count / len(valid_df)) * 100
            gas_total = valid_df[valid_df['chain'] == chain]['gas_fees'].fillna(0).sum()
            print(f"{chain:<12} {count:>8,} txns ({percentage:>5.1f}%) | Gas: ${gas_total:.6f}")
        
        print(f"\n🏪 TOP PLATFORMS")
        print("-" * 60)
        platform_counts = valid_df['platform'].value_counts()
        for platform, count in platform_counts.head(10).items():
            percentage = (count / len(valid_df)) * 100
            gas_total = valid_df[valid_df['platform'] == platform]['gas_fees'].fillna(0).sum()
            print(f"{platform[:11]:<12} {count:>8,} txns ({percentage:>5.1f}%) | Gas: ${gas_total:.6f}")
        
        print(f"\n💡 Bank Statement View shows all {total_txns:,} transactions in chronological order")
        print(f"📈 Most recent transaction: {valid_df.iloc[0]['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 Oldest transaction: {valid_df.iloc[-1]['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _create_wallet_strategy_mapping(self):
        """Create comprehensive mapping from wallet addresses to their strategies"""
        
        # Define wallet-to-strategy mapping based on .env file configuration
        wallet_strategies = {
            # LONG STRATEGY WALLETS
            # SOL Chain
            "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k": "Long",
            # ETH L1 and L2s
            "0x862f26238d773Fde4E29156f3Bb7CF58eA4cD1af": "Long",
            "0x862f26238d773fde4e29156f3bb7cf58ea4cd1af": "Long",  # lowercase variant
            # SUI Chain
            "0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a": "Long",
            
            # NEUTRAL STRATEGY WALLETS
            # SOL Chain
            "Djrzp7SyiTsDre41hgaUCh99Aw7PrchetGDbdm3GfHo6": "Neutral",
            # ETH L1 and L2s
            "0x52Ad60E77D2CAb7EdDCafC1f169Af354f2b1508a": "Neutral",
            "0x52ad60e77d2cab7eddcafc1f169af354f2b1508a": "Neutral",  # lowercase variant
            # SUI Chain
            "0x1df6f74ae73e453bc276d84512f1cd8387b643432163221df4f4c76112bfaf66": "Neutral",
            
            # YIELD WALLETS (off-chain yield destinations)
            # SOL Chain
            "GKvUys93yYe4U1a82u2k4VDvsxQLeCtaGyeggfh1hoBk": "Yield",
            # ETH L1 and L2s
            "0xaa9650695251fd56Aaea2B0A5FB91573849E1a3d": "Yield",
            "0xaa9650695251fd56aaea2b0a5fb91573849e1a3d": "Yield",  # lowercase variant
            # SUI Chain
            "0xa1c48a832320557655096e4fb475df116f9b0215fea51ef1b189e346325b9e2d": "Yield",
        }
        
        # Also get strategies from position data for any additional wallets
        positions = self.data_manager.get_all_active_positions() + self.data_manager.get_positions_by_strategy('closed')
        
        position_strategies = {}
        for pos in positions:
            wallet = pos.get('wallet', 'Unknown')
            strategy = pos.get('strategy', 'Unknown')
            
            if wallet not in position_strategies:
                position_strategies[wallet] = {}
            
            if strategy not in position_strategies[wallet]:
                position_strategies[wallet][strategy] = 0
            position_strategies[wallet][strategy] += 1
        
        # Add position-based strategies to our mapping
        for wallet, strategies in position_strategies.items():
            if wallet not in wallet_strategies and strategies:
                primary_strategy = max(strategies.items(), key=lambda x: x[1])[0]
                if len(strategies) > 1:
                    strategy_list = list(strategies.keys())
                    if 'long' in strategy_list and 'neutral' in strategy_list:
                        wallet_strategies[wallet] = "Multi (L+N)"
                    else:
                        wallet_strategies[wallet] = "Multi"
                else:
                    wallet_strategies[wallet] = primary_strategy.title()
        
        return wallet_strategies
    
    def _print_enhanced_transaction_row(self, tx, wallet_strategies):
        """Print enhanced transaction row with strategy, amounts, and token pairs"""
        date_str = tx['timestamp'].strftime('%Y-%m-%d')
        
        # Get wallet strategy - handle missing wallet addresses
        wallet = tx.get('wallet', '')
        
        # If wallet is empty, try to infer from chain and other data
        if not wallet or wallet.strip() == '':
            wallet = self._infer_wallet_from_transaction(tx)
        
        strategy = wallet_strategies.get(wallet, 'Unknown')
        strategy_display = strategy[:9]
        
        # Extract data from raw_data if available
        raw_data = tx.get('raw_data', {})
        
        # Get action - handle different formats
        action = self._extract_action(raw_data)
        action_display = action[:14]
        
        # Get token units and USD value separately
        token_units = self._extract_token_units(raw_data)
        usd_value = self._extract_usd_value(raw_data)
        
        # Get token pair and format it
        token_display = self._extract_token_pair(raw_data)
        
        # Enhanced platform detection
        platform = self._enhance_platform_detection(tx, raw_data)[:11]
        
        # Chain
        chain = tx.get('chain', 'Unknown')[:7]
        
        # Contract (shortened)
        contract = tx.get('contract_address', '')
        if contract and contract != '':
            if len(contract) > 11:
                contract_display = contract[:6] + "..." + contract[-2:]
            else:
                contract_display = contract[:11]
        else:
            contract_display = "N/A"
        
        print(f"{date_str:<12} {strategy_display:<10} {action_display:<15} {token_units:<15} {usd_value:<10} {token_display:<15} {platform:<12} {chain:<8} {contract_display:<12}")
    
    def _extract_action(self, raw_data):
        """Extract transaction action from various data formats"""
        # SOL format
        if 'Action' in raw_data:
            return raw_data['Action']
        
        # ETH/SUI format 
        if 'Transaction Type' in raw_data:
            tx_type = raw_data['Transaction Type']
            # Map common transaction types to readable actions
            type_mapping = {
                'execute': 'Execute',
                'swap': 'Swap',
                'trade': 'Trade',
                'send': 'Send',
                'receive': 'Receive',
                'approve': 'Approve',
                'deposit': 'Deposit',
                'withdraw': 'Withdraw',
                'mint': 'Mint',
                'burn': 'Burn',
                'add liquidity': 'Add Liquidity',
                'remove liquidity': 'Remove Liquidity'
            }
            return type_mapping.get(tx_type.lower(), tx_type.title())
        
        # Other possible fields
        for field in ['Type', 'Activity', 'Operation']:
            if field in raw_data:
                return str(raw_data[field])
        
        return 'Unknown'
    
    def _extract_amount(self, raw_data):
        """Extract transaction amount from various data formats with both token and USD values"""
        # SOL format
        if 'Amount' in raw_data:
            amount_raw = raw_data['Amount']
            return self._format_amount(amount_raw)
        
        # ETH/SUI format - try to get both token amount and USD value
        buy_amount = raw_data.get('Buy Amount')
        buy_currency = raw_data.get('Buy Currency')
        buy_fiat = raw_data.get('Buy Fiat Amount')
        
        sell_amount = raw_data.get('Sell Amount')
        sell_currency = raw_data.get('Sell Currency')
        sell_fiat = raw_data.get('Sell Fiat Amount')
        
        # Build comprehensive amount display
        amount_parts = []
        
        # Handle buy side
        try:
            if buy_amount and str(buy_amount).lower() != 'nan' and float(buy_amount) > 0:
                token_str = self._format_token_amount(buy_amount, buy_currency)
                if buy_fiat and str(buy_fiat).lower() != 'nan' and float(buy_fiat) > 0:
                    amount_parts.append(f"{token_str} (${float(buy_fiat):,.2f})")
                else:
                    amount_parts.append(token_str)
        except (ValueError, TypeError):
            pass
        
        # Handle sell side (if no buy side or if it's a swap)
        try:
            if not amount_parts and sell_amount and str(sell_amount).lower() != 'nan' and float(sell_amount) > 0:
                token_str = self._format_token_amount(sell_amount, sell_currency)
                if sell_fiat and str(sell_fiat).lower() != 'nan' and float(sell_fiat) > 0:
                    amount_parts.append(f"{token_str} (${float(sell_fiat):,.2f})")
                else:
                    amount_parts.append(token_str)
        except (ValueError, TypeError):
            pass
        
        # If we have amount parts, return them
        if amount_parts:
            return amount_parts[0][:20]  # Limit length for display
        
        # Fallback to any fiat amount
        if buy_fiat and str(buy_fiat).lower() != 'nan':
            return self._format_amount(buy_fiat)
        elif sell_fiat and str(sell_fiat).lower() != 'nan':
            return self._format_amount(sell_fiat)
        
        return '$0.00'
    
    def _extract_token_units(self, raw_data):
        """Extract token units for separate display"""
        # Check SUI enhanced data first
        if 'parsed_amount' in raw_data and 'parsed_symbol' in raw_data:
            amount = raw_data.get('parsed_amount', 0)
            symbol = raw_data.get('parsed_symbol', '')
            if amount and float(amount) > 0.00:
                return self._format_token_units_only(amount, symbol)
        
        # SOL format
        if 'Amount' in raw_data:
            amount_raw = raw_data['Amount']
            # Try to extract token amount from string like "5.23 SOL"
            return self._parse_token_from_amount_string(amount_raw)
        
        # ETH/SUI format - prioritize the larger amount
        buy_amount = raw_data.get('Buy Amount')
        buy_currency = raw_data.get('Buy Currency')
        sell_amount = raw_data.get('Sell Amount')
        sell_currency = raw_data.get('Sell Currency')
        
        try:
            # Check buy side
            if buy_amount and str(buy_amount).lower() != 'nan' and float(buy_amount) > 0.00:
                return self._format_token_units_only(buy_amount, buy_currency)
            
            # Check sell side
            if sell_amount and str(sell_amount).lower() != 'nan' and float(sell_amount) > 0.00:
                return self._format_token_units_only(sell_amount, sell_currency)
        except (ValueError, TypeError):
            pass
        
        return ""
    
    def _extract_usd_value(self, raw_data):
        """Extract USD value as integer when token units > 0.00"""
        # Check SUI enhanced data first
        if 'total_usd_value' in raw_data:
            usd_value = raw_data.get('total_usd_value', 0)
            if usd_value and float(usd_value) > 0:
                return f"${int(float(usd_value)):,}"
        
        # ETH/SUI format fiat amounts
        buy_fiat = raw_data.get('Buy Fiat Amount')
        sell_fiat = raw_data.get('Sell Fiat Amount')
        
        # Check if we have token units first
        token_units = self._extract_token_units(raw_data)
        if not token_units:
            return ""
        
        try:
            # Use fiat amount if available
            if buy_fiat and str(buy_fiat).lower() != 'nan' and float(buy_fiat) > 0:
                return f"${int(float(buy_fiat)):,}"
            elif sell_fiat and str(sell_fiat).lower() != 'nan' and float(sell_fiat) > 0:
                return f"${int(float(sell_fiat)):,}"
        except (ValueError, TypeError):
            pass
        
        return ""
    
    def _format_token_units_only(self, amount, currency):
        """Format token amount without USD value"""
        if not amount or not currency or str(amount).lower() == 'nan':
            return ""
        
        try:
            amount_float = float(amount)
            if amount_float <= 0.00:
                return ""
            
            currency_clean = str(currency)[:6]  # Limit currency length
            
            # Format based on amount size
            if amount_float >= 1000000:
                return f"{amount_float/1000000:.2f}M {currency_clean}"
            elif amount_float >= 1000:
                return f"{amount_float/1000:.2f}K {currency_clean}"
            elif amount_float >= 1:
                return f"{amount_float:.2f} {currency_clean}"
            else:
                # For small amounts, show appropriate decimals
                if amount_float >= 0.01:
                    return f"{amount_float:.4f} {currency_clean}"
                else:
                    return f"{amount_float:.6f} {currency_clean}"
        except (ValueError, TypeError):
            return ""
    
    def _parse_token_from_amount_string(self, amount_str):
        """Parse token amount from strings like '$1,234' or '5.23 SOL'"""
        if not amount_str or str(amount_str).lower() == 'nan':
            return ""
        
        amount_str = str(amount_str).strip()
        
        # If it's a USD amount (starts with $), skip it for token units
        if amount_str.startswith('$'):
            return ""
        
        # Try to extract number and currency
        import re
        # Pattern for "123.45 TOKEN" or "123.45TOKEN"
        match = re.match(r'^([\d,.]+)\s*([A-Za-z]+)', amount_str)
        if match:
            amount = match.group(1).replace(',', '')
            currency = match.group(2)
            try:
                amount_float = float(amount)
                if amount_float > 0.00:
                    return self._format_token_units_only(amount_float, currency)
            except:
                pass
        
        return ""
    
    def _format_token_amount(self, amount, currency):
        """Format token amount with currency"""
        if not amount or not currency or str(amount).lower() == 'nan':
            return ""
        
        try:
            amount_float = float(amount)
            # Format based on amount size
            if amount_float >= 1000000:
                return f"{amount_float/1000000:.2f}M {currency[:4]}"
            elif amount_float >= 1000:
                return f"{amount_float/1000:.2f}K {currency[:4]}"
            elif amount_float >= 1:
                return f"{amount_float:.2f} {currency[:4]}"
            else:
                # For small amounts, show more decimals
                return f"{amount_float:.6f} {currency[:4]}"
        except:
            return str(amount)[:10]
    
    def _format_amount(self, amount_raw, is_token=False):
        """Format amount consistently"""
        if not amount_raw or str(amount_raw).lower() == 'nan':
            return '$0.00' if not is_token else '0'
        
        if isinstance(amount_raw, str):
            # Clean up amount string: "$25,000" -> "25000"
            amount_clean = amount_raw.replace('$', '').replace(',', '').strip()
            try:
                amount_float = float(amount_clean)
                if is_token:
                    if amount_float >= 1000:
                        return f"{amount_float:,.0f}"
                    else:
                        return f"{amount_float:.2f}"
                else:
                    if amount_float >= 1000:
                        return f"${amount_float:,.0f}"
                    else:
                        return f"${amount_float:.2f}"
            except:
                return str(amount_raw)[:11]
        else:
            try:
                amount_float = float(amount_raw)
                if is_token:
                    if amount_float >= 1000:
                        return f"{amount_float:,.0f}"
                    else:
                        return f"{amount_float:.2f}"
                else:
                    if amount_float >= 1000:
                        return f"${amount_float:,.0f}"
                    else:
                        return f"${amount_float:.2f}"
            except:
                return str(amount_raw)[:11]
    
    def _extract_token_pair(self, raw_data):
        """Extract token pair information from various data formats"""
        # SOL format
        if 'Token Pair' in raw_data:
            token_pair = raw_data['Token Pair']
            if token_pair:
                # Handle different formats: "SOL/USDC", "SOL→USDC", etc.
                if '→' in token_pair:
                    # Swap format: SOL→USDC becomes "SOL → USDC"
                    parts = token_pair.split('→')
                    if len(parts) == 2:
                        return f"{parts[0].strip()} → {parts[1].strip()}"[:14]
                elif '/' in token_pair:
                    # LP format: SOL/USDC
                    return token_pair[:14]
                else:
                    return token_pair[:14]
        
        # ETH/SUI format - construct from buy/sell currencies
        buy_currency = raw_data.get('Buy Currency', '')
        sell_currency = raw_data.get('Sell Currency', '')
        
        if buy_currency and sell_currency and str(buy_currency).lower() != 'nan' and str(sell_currency).lower() != 'nan':
            # This is a swap: sold X for Y
            return f"{sell_currency[:6]} → {buy_currency[:6]}"[:14]
        elif buy_currency and str(buy_currency).lower() != 'nan':
            # Only bought something
            return f"Buy {buy_currency[:8]}"[:14]
        elif sell_currency and str(sell_currency).lower() != 'nan':
            # Only sold something  
            return f"Sell {sell_currency[:8]}"[:14]
        
        return "Unknown"[:14]
    
    def _print_transaction_row(self, tx):
        """Legacy transaction row printing method (kept for compatibility)"""
        date_str = tx['timestamp'].strftime('%Y-%m-%d')
        time_str = tx['timestamp'].strftime('%H:%M:%S')
        chain = tx['chain'][:7]
        platform = tx['platform'][:11]
        
        # Truncate wallet address
        wallet = tx['wallet']
        if len(wallet) > 15:
            wallet_display = wallet[:6] + "..." + wallet[-6:]
        else:
            wallet_display = wallet[:15]
        
        # Format gas fee
        gas_fee = tx.get('gas_fees', 0) or 0
        gas_str = f"${gas_fee:.6f}" if gas_fee > 0 else "$0.000000"
        
        # Truncate transaction hash
        tx_hash = tx.get('tx_hash', '')
        hash_display = tx_hash[:10] + "..." if len(tx_hash) > 10 else tx_hash[:10]
        
        # Block number
        block = str(tx.get('block_number', ''))[:9]
        
        print(f"{date_str:<12} {time_str:<8} {chain:<8} {platform:<12} {wallet_display:<16} {gas_str:<12} {hash_display:<12} {block:<10}")
    
    def _display_monthly_summary(self, df):
        """Display monthly transaction summary"""
        print(f"\n📅 MONTHLY ACTIVITY SUMMARY")
        print("-" * 80)
        
        # Group by year-month
        df['year_month'] = df['timestamp'].dt.strftime('%Y-%m')
        monthly_stats = df.groupby('year_month').agg({
            'tx_hash': 'count',
            'gas_fees': 'sum',
            'chain': 'nunique',
            'platform': 'nunique'
        }).round(6)
        
        monthly_stats.columns = ['transactions', 'total_gas', 'chains', 'platforms']
        monthly_stats = monthly_stats.sort_index(ascending=False)
        
        print(f"{'Month':<10} {'Transactions':<12} {'Gas Fees':<12} {'Chains':<8} {'Platforms':<10}")
        print("-" * 60)
        
        for month, stats in monthly_stats.head(12).iterrows():
            print(f"{month:<10} {stats['transactions']:>11,} ${stats['total_gas']:>10.6f} {stats['chains']:>7} {stats['platforms']:>9}")
        
        if len(monthly_stats) > 12:
            print(f"... and {len(monthly_stats) - 12} more months")
    
    def _filter_approve_transactions(self, df):
        """Filter out approve transactions and other non-value transactions"""
        # Keep original count for reporting
        original_count = len(df)
        
        # Filter based on transaction type in raw_data
        def is_value_transaction(row):
            raw_data = row.get('raw_data', {})
            
            # Check transaction type field
            tx_type = raw_data.get('Transaction Type', '').lower()
            if tx_type == 'approve':
                return False
            
            # Check action field
            action = raw_data.get('Action', '').lower()
            if action == 'approve':
                return False
            
            # For ETH/EVM transactions, check if there's actual value transfer
            # Approve transactions typically have no buy/sell amounts
            buy_amount = raw_data.get('Buy Amount')
            sell_amount = raw_data.get('Sell Amount')
            
            # If both amounts are zero or nan, likely not a value transfer
            has_buy = buy_amount and str(buy_amount).lower() != 'nan' and float(buy_amount) > 0
            has_sell = sell_amount and str(sell_amount).lower() != 'nan' and float(sell_amount) > 0
            
            # If transaction type exists and no amounts, filter out
            if tx_type and not has_buy and not has_sell:
                return False
            
            return True
        
        # Apply filter
        filtered_df = df[df.apply(is_value_transaction, axis=1)]
        
        # Report filtering results
        filtered_count = original_count - len(filtered_df)
        if filtered_count > 0:
            print(f"ℹ️  Filtered out {filtered_count} approve/non-value transactions")
        
        return filtered_df
    
    def _parse_timestamps_flexible(self, timestamps):
        """Parse timestamps with multiple format support"""
        import pandas as pd
        from datetime import datetime
        
        def parse_single_timestamp(ts):
            if pd.isna(ts) or ts == '':
                return pd.NaT
            
            ts_str = str(ts).strip()
            
            # List of common timestamp formats to try
            formats = [
                '%Y-%m-%d %H:%M:%S',           # 2024-06-20 10:30:15
                '%m/%d/%Y, %I:%M:%S %p',       # 6/21/2025, 2:17:01 AM
                '%m/%d/%Y %I:%M:%S %p',        # 6/21/2025 2:17:01 AM
                '%Y-%m-%d',                    # 2024-06-20
                '%m/%d/%Y',                    # 6/21/2025
                '%Y-%m-%dT%H:%M:%S',           # 2024-06-20T10:30:15
                '%Y-%m-%dT%H:%M:%S.%f',        # 2024-06-20T10:30:15.123456
                '%Y-%m-%d %H:%M',              # 2024-06-20 10:30
                '%m/%d/%y %H:%M:%S',           # 6/21/25 14:17:01
                '%d/%m/%Y %H:%M:%S',           # 21/06/2024 14:17:01
            ]
            
            # Try each format
            for fmt in formats:
                try:
                    parsed = datetime.strptime(ts_str, fmt)
                    # Convert to timezone-naive to avoid comparison issues
                    return pd.Timestamp(parsed).tz_localize(None)
                except ValueError:
                    continue
            
            # If all formats fail, try pandas to_datetime which is more flexible
            try:
                parsed = pd.to_datetime(ts_str)
                # Ensure timezone-naive
                if hasattr(parsed, 'tz_localize'):
                    return parsed.tz_localize(None) if parsed.tz is not None else parsed
                return parsed
            except:
                return pd.NaT
        
        # Apply the parsing function to all timestamps
        return timestamps.apply(parse_single_timestamp)
    
    def _infer_wallet_from_transaction(self, tx):
        """Infer wallet address from transaction data when wallet field is empty"""
        
        # Try to extract wallet from various fields
        raw_data = tx.get('raw_data', {})
        chain = tx.get('chain', '').upper()
        
        # Check common wallet fields in raw_data
        wallet_fields = ['From', 'To', 'Address', 'Wallet', 'Account', 'User Address', 'Interacted with']
        for field in wallet_fields:
            if field in raw_data and raw_data[field]:
                wallet_addr = str(raw_data[field]).strip()
                if wallet_addr and wallet_addr.lower() != 'nan':
                    # Validate wallet format before returning
                    if self._is_valid_wallet_format(wallet_addr, chain):
                        return wallet_addr
        
        # Try to infer from filename pattern if source file info is available
        source_file = tx.get('source_file', '')
        if source_file:
            extracted_wallet = self._extract_wallet_from_filename(source_file)
            if extracted_wallet:
                return extracted_wallet
        
        # Try to infer from platform and chain combination
        platform = tx.get('platform', '')
        if platform and chain:
            inferred_wallet = self._infer_wallet_from_platform_chain(platform, chain)
            if inferred_wallet:
                return inferred_wallet
        
        return ""
    
    def _is_valid_wallet_format(self, wallet_addr, chain):
        """Validate wallet address format for given chain"""
        if not wallet_addr or len(wallet_addr) < 10:
            return False
            
        chain_upper = chain.upper()
        
        # ETH/EVM chains: 0x + 40 hex chars
        if chain_upper in ['ETH', 'ETHEREUM', 'BASE', 'ARBITRUM', 'OPTIMISM', 'POLYGON']:
            return wallet_addr.startswith('0x') and len(wallet_addr) == 42
        
        # SOL: Base58, typically 32-44 chars, no 0x prefix
        elif chain_upper in ['SOL', 'SOLANA']:
            return not wallet_addr.startswith('0x') and 32 <= len(wallet_addr) <= 44
        
        # SUI: 0x + 64 hex chars
        elif chain_upper == 'SUI':
            return wallet_addr.startswith('0x') and len(wallet_addr) == 66
        
        return True  # Default to allowing unknown formats
    
    def _extract_wallet_from_filename(self, filename):
        """Extract wallet address from CSV filename patterns"""
        import re
        
        # Pattern for ETH addresses in filename: 0x + 40 hex chars
        eth_pattern = r'0x[a-fA-F0-9]{40}'
        
        # Pattern for SUI addresses in filename: 0x + 64 hex chars  
        sui_pattern = r'0x[a-fA-F0-9]{64}'
        
        # Pattern for SOL addresses: Base58 string, typically 32-44 chars
        sol_pattern = r'[A-Za-z0-9]{32,44}'
        
        # Try SUI first (longer), then ETH, then SOL
        for pattern in [sui_pattern, eth_pattern]:
            match = re.search(pattern, filename)
            if match:
                return match.group(0)
        
        # For SOL, be more selective to avoid false positives
        sol_matches = re.findall(sol_pattern, filename)
        for match in sol_matches:
            # Additional validation for SOL addresses
            if not match.startswith('0x') and not match.isdigit():
                # Check if it matches known SOL wallet pattern
                if any(match == wallet for wallet in [
                    "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k",
                    "Djrzp7SyiTsDre41hgaUCh99Aw7PrchetGDbdm3GfHo6", 
                    "GKvUys93yYe4U1a82u2k4VDvsxQLeCtaGyeggfh1hoBk"
                ]):
                    return match
        
        return None
    
    def _infer_wallet_from_platform_chain(self, platform, chain):
        """Infer most likely wallet based on platform and chain combination"""
        
        # Define platform preferences for each strategy
        long_platforms = ['orca', 'cetus', 'aero', 'ray', 'uniswap']
        neutral_platforms = ['clm', 'perp']
        
        platform_lower = platform.lower()
        chain_upper = chain.upper()
        
        # Map known platform/chain combinations to our wallet addresses
        platform_chain_mapping = {
            # Long strategy wallets
            ('SOL', 'long'): "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k",
            ('ETH', 'long'): "0x862f26238d773Fde4E29156f3Bb7CF58eA4cD1af", 
            ('SUI', 'long'): "0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a",
            
            # Neutral strategy wallets
            ('SOL', 'neutral'): "Djrzp7SyiTsDre41hgaUCh99Aw7PrchetGDbdm3GfHo6",
            ('ETH', 'neutral'): "0x52Ad60E77D2CAb7EdDCafC1f169Af354f2b1508a",
            ('SUI', 'neutral'): "0x1df6f74ae73e453bc276d84512f1cd8387b643432163221df4f4c76112bfaf66",
        }
        
        # Determine strategy from platform
        strategy = None
        if any(plat in platform_lower for plat in long_platforms):
            strategy = 'long'
        elif any(plat in platform_lower for plat in neutral_platforms):
            strategy = 'neutral'
        
        if strategy:
            return platform_chain_mapping.get((chain_upper, strategy))
        
        return None
    
    def _enhance_platform_detection(self, tx, raw_data):
        """Enhanced platform detection using multiple sources"""
        # First try the existing platform field
        platform = tx.get('platform', '')
        if platform and platform.lower() not in ['unknown', 'transfer', 'send', 'receive']:
            return platform
        
        # Try protocol field from raw data
        protocol = raw_data.get('Protocol', '')
        if protocol and str(protocol).lower() != 'nan':
            return protocol
        
        # Try exchange field
        exchange = raw_data.get('Exchange', '')
        if exchange and str(exchange).lower() != 'nan':
            return exchange
        
        # Contract-based detection for known DEX contracts
        contract = tx.get('contract_address', '').lower()
        chain = tx.get('chain', '').upper()
        
        # Known DEX contract patterns
        dex_contracts = {
            # Solana
            ('SOL', '675kpx9mhtjfud3hyg3e8afrawfmxb'): 'Orca',
            ('SOL', 'whirldsbimxwxubjuhpkjzstwl'): 'Orca Whirlpool',
            ('SOL', 'raydium'): 'Raydium',
            ('SOL', 'meteoraxn2h'): 'Meteora',
            ('SOL', 'jupyweamzm'): 'Jupiter',
            
            # Ethereum/Base/Arbitrum
            ('ETH', '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45'): 'Uniswap V3',
            ('BASE', '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45'): 'Uniswap V3',
            ('BASE', '0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24'): 'BaseSwap',
            ('BASE', '0x827922686190790b37229fd06084350e74485b72'): 'Aerodrome',
            
            # SUI
            ('SUI', 'cetus'): 'Cetus',
            ('SUI', 'turbos'): 'Turbos',
        }
        
        # Check contract patterns
        for (check_chain, pattern), dex_name in dex_contracts.items():
            if chain == check_chain and pattern in contract:
                return dex_name
        
        # Token pair based inference
        token_pair = self._extract_token_pair(raw_data)
        action = self._extract_action(raw_data)
        
        # If it's a swap/trade with known patterns
        if action.lower() in ['swap', 'trade', 'exchange']:
            if 'JLP' in token_pair:
                return 'Jupiter'
            elif 'RAY' in token_pair:
                return 'Raydium'
            elif chain == 'SOL' and any(token in token_pair for token in ['SOL', 'USDC']):
                return 'DEX'  # Generic Solana DEX
            elif chain in ['ETH', 'BASE', 'ARB'] and '→' in token_pair:
                return 'DEX'  # Generic EVM DEX
        
        # Platform inference from action patterns
        if action.lower() in ['add liquidity', 'remove liquidity']:
            if chain == 'SOL':
                return 'LP Pool'
            else:
                return 'LP Pool'
        
        # If still unknown but has value transfer
        if action.lower() in ['send', 'receive', 'transfer']:
            return 'Transfer'
        
        return platform if platform else 'Unknown'