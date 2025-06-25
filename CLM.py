#!/usr/bin/env python3
"""
CLM Portfolio Tracker - Main CLI Controller
"""

import sys
import os
from time import sleep
from datetime import datetime, timedelta
from clm_data import CLMDataManager
from views.active_positions import ActivePositionsView
from views.transactions import TransactionsView
from views.historical_returns import HistoricalReturnsView
from views.allocation_breakdown import AllocationBreakdownView
from views.prices import PricesView
from views.historical_performance import HistoricalPerformanceView

class CLMTracker:
    def __init__(self):
        self.data_manager = CLMDataManager()
        self.active_view = ActivePositionsView(self.data_manager)
        self.transactions_view = TransactionsView(self.data_manager)
        self.historical_view = HistoricalReturnsView(self.data_manager)
        self.breakdown_view = AllocationBreakdownView(self.data_manager)
        self.prices_view = PricesView(self.data_manager)
        self.historical_performance_view = HistoricalPerformanceView(self.data_manager)
        
    def run_cli(self):
        """Main CLI loop"""
        while True:
            # Update data
            self.data_manager.refresh_prices_and_status()
            
            # Clear screen and show main view
            print("\033[2J\033[H")
            self.active_view.display()
            
            # Show menu
            print(f"\n{'='*120}")
            print("📋 Main Views: [1] Active Positions  [2] Transactions  [3] Historical Returns  [4] Allocation Breakdown  [5] Prices  [6] Token Performance")
            print("🔍 Strategy Details: [L] Long Strategy  [N] Neutral Strategy")
            print("🔧 Actions: [r]efresh | [i]mport transactions | [A]sk about transactions | [q]uit")
            print("="*120)
            
            try:
                choice = input("\nSelect view or action: ").lower().strip()
                
                if choice in ['q', 'quit', 'exit']:
                    print("👋 Goodbye!")
                    break
                elif choice in ['1', 'active', 'positions']:
                    continue  # Stay on home view
                elif choice in ['l', 'long']:
                    print("\033[2J\033[H")
                    self.active_view.display_strategy_detail('long')
                    input("\nPress Enter to return...")
                elif choice in ['n', 'neutral']:
                    print("\033[2J\033[H")
                    self.active_view.display_strategy_detail('neutral')
                    input("\nPress Enter to return...")
                elif choice in ['2', 'transactions']:
                    print("\033[2J\033[H")
                    self.transactions_view.display()
                    input("\nPress Enter to return...")
                elif choice in ['3', 'historical', 'returns']:
                    print("\033[2J\033[H")
                    self.historical_view.display()
                    input("\nPress Enter to return...")
                elif choice in ['4', 'allocation', 'breakdown']:
                    print("\033[2J\033[H")
                    self.breakdown_view.display()
                    input("\nPress Enter to return...")
                elif choice in ['5', 'prices', 'pricing']:
                    print("\033[2J\033[H")
                    self.prices_view.display()
                    input("\nPress Enter to return...")
                elif choice in ['6', 'performance', 'token performance', 'historical performance']:
                    print("\033[2J\033[H")
                    self.historical_performance_view.display()
                    input("\nPress Enter to return...")
                elif choice in ['r', 'refresh']:
                    print("🔄 Refreshing data...")
                    continue
                elif choice in ['i', 'import']:
                    print("\033[2J\033[H")
                    self.import_transactions_menu()
                    input("\nPress Enter to return...")
                elif choice in ['a', 'ask']:
                    print("\033[2J\033[H")
                    self.transaction_query_menu()
                    input("\nPress Enter to return...")
                else:
                    print("❌ Invalid choice. Use 1, 2, 3, 4, 5, 6, L, N, i, A, r, or q")
                    sleep(1)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    
    def import_transactions_menu(self):
        """Interactive transaction import menu"""
        print("📥 Transaction Import Menu")
        print("=" * 50)
        
        # Check for CSV files in data directory
        import os
        csv_files = []
        if os.path.exists('data'):
            csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]
        
        print("\n🔍 Available CSV files in data/ directory:")
        if not csv_files:
            print("   ❌ No CSV files found in data/ directory")
            print("\n📋 To import transactions:")
            print("   1. Copy your transaction CSV to the data/ folder")
            print("   2. Supported formats: wallet exports, DEX transaction history")
            print("   3. Required columns: Transaction ID, Wallet Address, Platform")
            print("   4. Optional: Gas Fees, Block Number, Contract Address")
            return
        
        # Show available files
        transaction_csvs = []
        for i, csv_file in enumerate(csv_files, 1):
            print(f"   [{i}] {csv_file}")
            if any(word in csv_file.lower() for word in ['transaction', 'tx', 'wallet', 'dex']):
                transaction_csvs.append(csv_file)
        
        if not transaction_csvs:
            print("\n💡 No obvious transaction files found.")
            print("   Transaction files usually contain: 'transaction', 'tx', 'wallet', or 'dex' in the name")
        
        print(f"\n🔧 Import Options:")
        print(f"   [a] Auto-import all transaction-like CSV files")
        print(f"   [s] Select specific file by number")
        print(f"   [c] Cancel")
        
        choice = input("\nChoice: ").lower().strip()
        
        if choice == 'c':
            return
        elif choice == 'a':
            # Auto-import transaction files
            if not transaction_csvs:
                print("❌ No transaction CSV files detected")
                return
            
            print(f"📤 Auto-importing {len(transaction_csvs)} transaction files...")
            self.batch_import_transactions(transaction_csvs)
            
        elif choice == 's':
            # Select specific file
            try:
                file_num = int(input("Enter file number: "))
                if 1 <= file_num <= len(csv_files):
                    selected_file = csv_files[file_num - 1]
                    print(f"📤 Importing: {selected_file}")
                    
                    # Ask for chain
                    chain = input("Enter chain (SOL/ETH/SUI/BASE/ARB) [default: SOL]: ").upper().strip()
                    if not chain:
                        chain = 'SOL'
                    
                    csv_path = f'data/{selected_file}'
                    transactions = self.data_manager.import_transaction_csv(csv_path, chain)
                    
                    if transactions:
                        self.data_manager.save_transactions(transactions)
                        print(f"✅ Imported {len(transactions)} transactions")
                        
                        # Show summary
                        total_gas = sum(tx.get('gas_fees', 0) or 0 for tx in transactions)
                        platforms = set(tx.get('platform') for tx in transactions)
                        print(f"   ⛓️  Chain: {chain}")
                        print(f"   🏪 Platforms: {len(platforms)} different")
                        print(f"   ⛽ Total Gas: ${total_gas:.6f}")
                    else:
                        print("❌ No transactions imported")
                else:
                    print("❌ Invalid file number")
            except ValueError:
                print("❌ Please enter a valid number")
        else:
            print("❌ Invalid choice")
    
    def batch_import_transactions(self, csv_files):
        """Import multiple transaction CSV files"""
        all_transactions = []
        
        for csv_file in csv_files:
            csv_path = f'data/{csv_file}'
            
            # Auto-detect chain from filename
            chain = 'SOL'  # Default
            filename_lower = csv_file.lower()
            if 'eth' in filename_lower:
                chain = 'ETH'
            elif 'sui' in filename_lower:
                chain = 'SUI'
            elif 'base' in filename_lower:
                chain = 'BASE'
            elif 'arb' in filename_lower:
                chain = 'ARB'
            
            print(f"   📂 {csv_file} ({chain})")
            transactions = self.data_manager.import_transaction_csv(csv_path, chain)
            
            if transactions:
                all_transactions.extend(transactions)
                print(f"      ✅ {len(transactions)} transactions imported")
            else:
                print(f"      ❌ No transactions found")
        
        if all_transactions:
            self.data_manager.save_transactions(all_transactions)
            
            # Show summary
            chains = set(tx['chain'] for tx in all_transactions)
            platforms = set(tx['platform'] for tx in all_transactions)
            total_gas = sum(tx.get('gas_fees', 0) or 0 for tx in all_transactions)
            
            print(f"\n✅ Batch Import Complete!")
            print(f"   📊 Total: {len(all_transactions)} transactions")
            print(f"   ⛓️  Chains: {', '.join(chains)}")
            print(f"   🏪 Platforms: {len(platforms)} different")
            print(f"   ⛽ Total Gas: ${total_gas:.6f}")
            print(f"   💾 Saved to: data/JSON_out/clm_transactions.json")
        else:
            print("\n❌ No transactions imported from any file")
    
    def transaction_query_menu(self):
        """Interactive transaction query interface"""
        from transaction_query import TransactionQueryTool
        
        query_tool = TransactionQueryTool()
        
        if not query_tool.transactions:
            print("❌ No transaction data available. Import transactions first using [i]mport option.")
            return
        
        print("🤖 ASK ABOUT YOUR TRANSACTIONS")
        print("=" * 80)
        print("💬 You can ask in natural language! Examples:")
        print("   • 'Show me all Orca transactions from last 30 days'")
        print("   • 'How much gas did I spend on Solana?'")
        print("   • 'What are my top 5 most expensive transactions?'")
        print("   • 'How many Jupiter transactions this month?'")
        print("=" * 80)
        
        # Show quick overview first
        stats = query_tool.quick_stats()
        print(f"\n📊 Database Overview:")
        print(f"   📈 Total Transactions: {stats['total_transactions']:,}")
        print(f"   ⛽ Total Gas Fees: ${stats['total_gas_fees']:.6f}")
        print(f"   ⛓️  Chains: {', '.join(stats['chains'])}")
        print(f"   🏪 Platforms: {len(stats['platforms'])} different")
        print(f"   👛 Unique Wallets: {stats['unique_wallets']}")
        print(f"   📅 Date Range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
        while True:
            print("\n" + "=" * 80)
            print("🔍 Query Options:")
            print("  [0] Natural Language Query (Ask anything!)")
            print("  [1] Custom Query Builder")
            print("  [2] Top Gas Spenders")
            print("  [3] Platform Analysis")
            print("  [4] Chain Breakdown")
            print("  [5] Time Window Analysis")
            print("  [b] Back to Main Menu")
            
            choice = input("\nSelect query: ").strip().lower()
            
            if choice in ['b', 'back']:
                break
            
            elif choice == '0':
                print("\n🤖 NATURAL LANGUAGE QUERY")
                print("-" * 50)
                print("💬 Ask me anything about your transactions!")
                print("   Examples: 'orca last 30 days', 'total gas solana', 'jupiter transactions'")
                
                question = input("\n❓ Your question: ").strip().lower()
                
                if not question:
                    continue
                
                # Parse natural language and execute query
                result = self.parse_natural_query(question, query_tool)
                if result:
                    print(f"\n🎯 ANSWER")
                    print("-" * 30)
                    print(result)
                else:
                    print("❌ Sorry, I couldn't understand that question. Try the Custom Query Builder instead.")
            
            elif choice == '1':
                print("\n🛠️  CUSTOM QUERY BUILDER")
                print("-" * 50)
                
                # Get filter inputs
                chain = input("🔗 Chain (SOL/ETH/SUI/BASE/ARB) [Enter for all]: ").strip().upper() or None
                platform = input("🏪 Platform contains (Orca/Jupiter/etc.) [Enter for all]: ").strip() or None
                start_date = input("📅 Start date (YYYY-MM-DD) [Enter for all]: ").strip() or None
                end_date = input("📅 End date (YYYY-MM-DD) [Enter for all]: ").strip() or None
                
                try:
                    min_gas_input = input("⛽ Min gas fees [Enter for all]: ").strip()
                    min_gas = float(min_gas_input) if min_gas_input else None
                except:
                    min_gas = None
                
                try:
                    limit_input = input("📊 Limit results [Enter for no limit]: ").strip()
                    limit = int(limit_input) if limit_input else None
                except:
                    limit = None
                
                # Execute query
                result = query_tool.query(
                    chain=chain, platform=platform,
                    start_date=start_date, end_date=end_date,
                    min_gas=min_gas, limit=limit
                )
                
                # Display results
                print(f"\n🎯 QUERY RESULTS")
                print("-" * 50)
                if result['filters_applied']:
                    print(f"🔍 Filters Applied: {', '.join(result['filters_applied'])}")
                print(f"📊 Matching Transactions: {result['total_transactions']:,}")
                
                if 'analytics' in result and 'error' not in result['analytics']:
                    analytics = result['analytics']
                    print(f"\n💰 Financial Summary:")
                    print(f"   ⛽ Total Gas: ${analytics['gas_fees']['total']:.6f}")
                    print(f"   📊 Average Gas: ${analytics['gas_fees']['average']:.6f}")
                    print(f"   📈 Max Gas: ${analytics['gas_fees']['max']:.6f}")
                    print(f"   📉 Min Gas: ${analytics['gas_fees']['min']:.6f}")
                    
                    print(f"\n🌐 Network Distribution:")
                    for chain_name, count in analytics['chains'].items():
                        percentage = (count / analytics['count']) * 100
                        print(f"   {chain_name}: {count:,} ({percentage:.1f}%)")
                    
                    print(f"\n🏪 Top Platforms:")
                    sorted_platforms = sorted(analytics['platforms'].items(), key=lambda x: x[1], reverse=True)
                    for platform, count in sorted_platforms[:5]:
                        percentage = (count / analytics['count']) * 100
                        print(f"   {platform}: {count:,} ({percentage:.1f}%)")
                    
                    if 'time_window' in analytics:
                        tw = analytics['time_window']
                        print(f"\n📅 Time Analysis:")
                        print(f"   📊 Span: {tw['span_days']} days")
                        print(f"   📈 Period: {tw['earliest'][:10]} to {tw['latest'][:10]}")
                        if 'daily_activity' in analytics:
                            da = analytics['daily_activity']
                            print(f"   📊 Avg/Day: {da['avg_per_day']:.1f} transactions")
                            print(f"   🔥 Peak Day: {da['most_active_day']} ({da['transactions_on_most_active']} txs)")
            
            elif choice == '2':
                print("\n🔥 TOP 10 GAS SPENDERS")
                print("-" * 50)
                spenders = query_tool.top_gas_spenders(10)
                for i, spender in enumerate(spenders, 1):
                    print(f"{i:2}. {spender['wallet']} - ${spender['total_gas']:.6f} ({spender['tx_count']} txs, avg: ${spender['avg_gas']:.6f})")
            
            elif choice == '3':
                print("\n🏪 PLATFORM ANALYSIS")
                print("-" * 50)
                platforms = query_tool.platform_analysis()
                sorted_platforms = sorted(platforms.items(), key=lambda x: x[1]['transactions'], reverse=True)
                
                for platform, stats in sorted_platforms:
                    print(f"\n📊 {platform}:")
                    print(f"   🔢 Transactions: {stats['transactions']:,}")
                    print(f"   ⛽ Total Gas: ${stats['total_gas']:.6f}")
                    print(f"   📊 Avg Gas/Tx: ${stats['avg_gas_per_tx']:.6f}")
                    print(f"   👛 Unique Wallets: {stats['unique_wallets']}")
            
            elif choice == '4':
                print("\n⛓️  CHAIN BREAKDOWN")
                print("-" * 50)
                result = query_tool.query()
                if 'analytics' in result:
                    chains = result['analytics']['chains']
                    total = sum(chains.values())
                    
                    for chain, count in sorted(chains.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / total) * 100
                        print(f"{chain}: {count:,} transactions ({percentage:.1f}%)")
            
            elif choice == '5':
                print("\n📅 TIME WINDOW ANALYSIS")
                print("-" * 50)
                
                # Query for recent periods
                periods = [
                    ("Last 7 days", 7),
                    ("Last 30 days", 30),
                    ("Last 90 days", 90)
                ]
                
                for period_name, days in periods:
                    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                    result = query_tool.query(start_date=start_date)
                    
                    if result['total_transactions'] > 0:
                        analytics = result['analytics']
                        print(f"\n📊 {period_name}:")
                        print(f"   🔢 Transactions: {analytics['count']:,}")
                        print(f"   ⛽ Total Gas: ${analytics['gas_fees']['total']:.6f}")
                        print(f"   📊 Avg Gas: ${analytics['gas_fees']['average']:.6f}")
                        if 'daily_activity' in analytics:
                            print(f"   📈 Avg/Day: {analytics['daily_activity']['avg_per_day']:.1f}")
                    else:
                        print(f"\n📊 {period_name}: No transactions")
            
            else:
                print("❌ Invalid choice")
            
            if choice in ['0', '1', '2', '3', '4', '5']:
                input("\nPress Enter to continue...")
    
    def parse_natural_query(self, question: str, query_tool):
        """Parse natural language queries and execute appropriate searches"""
        import re
        from datetime import datetime, timedelta
        
        # Initialize query parameters
        params = {}
        
        # Platform detection
        platforms = ['orca', 'jupiter', 'raydium', 'meteora', 'uniswap', 'pancakeswap']
        for platform in platforms:
            if platform in question:
                params['platform'] = platform.title()
                break
        
        # Chain detection
        chains = {'solana': 'SOL', 'sol': 'SOL', 'ethereum': 'ETH', 'eth': 'ETH', 
                 'sui': 'SUI', 'base': 'BASE', 'arbitrum': 'ARB', 'arb': 'ARB'}
        for chain_name, chain_code in chains.items():
            if chain_name in question:
                params['chain'] = chain_code
                break
        
        # Time period detection
        time_patterns = {
            r'last (\d+) days?': lambda m: (datetime.now() - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d'),
            r'(\d+) days? ago': lambda m: (datetime.now() - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d'),
            r'this month': lambda m: datetime.now().strftime('%Y-%m-01'),
            r'last month': lambda m: (datetime.now() - timedelta(days=30)).strftime('%Y-%m-01'),
            r'this week': lambda m: (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        }
        
        for pattern, date_func in time_patterns.items():
            match = re.search(pattern, question)
            if match:
                params['start_date'] = date_func(match)
                break
        
        # Gas-related queries
        if any(word in question for word in ['gas', 'fees', 'cost', 'spend', 'spent']):
            gas_query = True
        else:
            gas_query = False
        
        # Top/expensive queries
        top_match = re.search(r'top (\d+)', question)
        if top_match:
            params['limit'] = int(top_match.group(1))
        
        # Execute appropriate query based on question type
        try:
            if 'gas spender' in question or 'expensive' in question:
                # Top gas spenders
                limit = params.get('limit', 5)
                spenders = query_tool.top_gas_spenders(limit)
                result = f"🔥 Top {limit} Gas Spenders:\n"
                for i, spender in enumerate(spenders, 1):
                    result += f"{i}. {spender['wallet']} - ${spender['total_gas']:.6f} ({spender['tx_count']} txs)\n"
                return result
            
            elif any(word in question for word in ['how many', 'count', 'number']):
                # Count query
                query_result = query_tool.query(**params)
                platform_text = f" on {params['platform']}" if 'platform' in params else ""
                chain_text = f" on {params['chain']}" if 'chain' in params else ""
                time_text = f" since {params['start_date']}" if 'start_date' in params else ""
                
                return f"📊 Found {query_result['total_transactions']:,} transactions{platform_text}{chain_text}{time_text}"
            
            elif gas_query:
                # Gas spending query
                query_result = query_tool.query(**params)
                if 'analytics' in query_result:
                    analytics = query_result['analytics']
                    platform_text = f" on {params['platform']}" if 'platform' in params else ""
                    chain_text = f" on {params['chain']}" if 'chain' in params else ""
                    time_text = f" since {params['start_date']}" if 'start_date' in params else ""
                    
                    result = f"💰 Gas Analysis{platform_text}{chain_text}{time_text}:\n"
                    result += f"   💸 Total Gas: ${analytics['gas_fees']['total']:.6f}\n"
                    result += f"   📊 Average: ${analytics['gas_fees']['average']:.6f}\n"
                    result += f"   📈 Max: ${analytics['gas_fees']['max']:.6f}\n"
                    result += f"   📉 Min: ${analytics['gas_fees']['min']:.6f}\n"
                    result += f"   🔢 Transactions: {analytics['count']:,}"
                    return result
            
            else:
                # General query
                query_result = query_tool.query(**params)
                if 'analytics' in query_result and 'error' not in query_result['analytics']:
                    analytics = query_result['analytics']
                    
                    result = f"📊 Query Results:\n"
                    result += f"   🔢 Transactions: {analytics['count']:,}\n"
                    result += f"   💰 Total Gas: ${analytics['gas_fees']['total']:.6f}\n"
                    
                    if 'platform' not in params and analytics.get('platforms'):
                        top_platforms = sorted(analytics['platforms'].items(), key=lambda x: x[1], reverse=True)[:3]
                        result += f"   🏪 Top Platforms: {', '.join([f'{p}({c})' for p, c in top_platforms])}\n"
                    
                    if 'chain' not in params and analytics.get('chains'):
                        result += f"   ⛓️  Chains: {', '.join([f'{c}({count})' for c, count in analytics['chains'].items()])}\n"
                    
                    if 'time_window' in analytics:
                        tw = analytics['time_window']
                        result += f"   📅 Time Span: {tw['span_days']} days"
                    
                    return result
        
        except Exception as e:
            return f"❌ Error processing query: {e}"
        
        return None

def main():
    tracker = CLMTracker()
    
    # Default CSV paths
    neutral_csv = "data/Tokens_Trade_Sheet - Neutral Positions.csv"
    long_csv = "data/Tokens_Trade_Sheet - Long Positions.csv"
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "convert":
            if len(sys.argv) < 4:
                print("Usage: python clm.py convert <neutral_csv> <long_csv>")
                return
            
            neutral_csv = sys.argv[2]
            long_csv = sys.argv[3]
            
            if not os.path.exists(neutral_csv):
                print(f"❌ File not found: {neutral_csv}")
                return
            if not os.path.exists(long_csv):
                print(f"❌ File not found: {long_csv}")
                return
                
            tracker.data_manager.update_positions(neutral_csv, long_csv)
            
        elif command == "monitor":
            tracker.data_manager.load_positions()
            tracker.run_cli()
            
    else:
        # Enhanced auto-detect mode with automatic CSV scanning
        print("🚀 CLM Portfolio Tracker - Auto-detect mode")
        print("🔍 Scanning for CSV files in data folder...")
        
        # Use the new automatic detection system
        results = tracker.data_manager.auto_detect_and_process_csvs()
        
        # Check if we found any data to process
        total_new_files = len(results['new_files']) + len(results['updated_files'])
        
        if total_new_files > 0:
            print("🔄 Processing new/updated CSV files...")
            tracker.data_manager.merge_incremental_data(results['processed_data'])
        else:
            # Fall back to legacy mode if no new files found
            if os.path.exists(neutral_csv) and os.path.exists(long_csv):
                if tracker.data_manager.check_for_updates(neutral_csv, long_csv):
                    print("🔄 Legacy CSV files changed, updating positions...")
                    tracker.data_manager.update_positions(neutral_csv, long_csv)
                else:
                    print("✅ Loading existing data...")
                    tracker.data_manager.load_positions()
            else:
                print("⚠️  No CSV files found!")
                print("\nSetup Options:")
                print(f"1. Place CSV files in the data/ folder")
                print(f"2. Supported formats: positions, transactions, balances")
                print(f"3. Or use legacy paths: {neutral_csv} and {long_csv}")
                print("4. Then run 'python clm.py' again")
                return
        
        # Start monitoring
        tracker.run_cli()

if __name__ == "__main__":
    main()