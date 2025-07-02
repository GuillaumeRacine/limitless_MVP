#!/usr/bin/env python3
"""
CLM Portfolio Tracker - Main CLI Controller
"""

import sys
import os
import pandas as pd
from time import sleep
from datetime import datetime, timedelta

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from clm_data import CLMDataManager
from views.active_positions import ActivePositionsView
from views.transactions import TransactionsView
from views.historical_returns import HistoricalReturnsView
from views.allocation_breakdown import AllocationBreakdownView
from views.prices import PricesView
from views.historical_performance import HistoricalPerformanceView
from views.market_analysis import MarketAnalysisView

class CLMTracker:
    def __init__(self):
        self.data_manager = CLMDataManager()
        self.active_view = ActivePositionsView(self.data_manager)
        self.transactions_view = TransactionsView(self.data_manager)
        self.historical_view = HistoricalReturnsView(self.data_manager)
        self.breakdown_view = AllocationBreakdownView(self.data_manager)
        self.prices_view = PricesView(self.data_manager)
        self.historical_performance_view = HistoricalPerformanceView(self.data_manager)
        self.market_analysis_view = MarketAnalysisView()
        self.last_auto_refresh = datetime.now()  # Track time of last auto-refresh
        
    def run_cli(self):
        """Main CLI loop"""
        while True:
            # Check if 60 minutes have passed since last auto-refresh
            time_since_refresh = datetime.now() - self.last_auto_refresh
            if time_since_refresh > timedelta(minutes=60):
                print("🔄 Auto-refreshing prices (60 minutes elapsed)...")
                self.data_manager.refresh_prices_and_status()
                self.last_auto_refresh = datetime.now()
                
                
                sleep(1)  # Brief pause to show message
            else:
                # Regular refresh on each loop
                self.data_manager.refresh_prices_and_status()
            
            # Clear screen and show main view
            print("\033[2J\033[H")
            self.active_view.display()
            
            # Show menu
            print(f"\n{'='*120}")
            print("📋 Main Views: [1] Active Positions  [2] Transactions  [3] Historical Returns  [4] Allocation Breakdown  [5] Prices  [6] Token Performance")
            print("📊 Market Analysis: [7] DefiLlama Dashboard")
            print("🔍 Strategy Details: [L] Long Strategy  [N] Neutral Strategy")
            
            print("🔧 Actions: [r]efresh | [i]mport transactions | [q]uit")
            
            # Show time until next auto-refresh
            time_until_refresh = timedelta(minutes=60) - (datetime.now() - self.last_auto_refresh)
            minutes_left = int(time_until_refresh.total_seconds() / 60)
            seconds_left = int(time_until_refresh.total_seconds() % 60)
            print(f"🕐 Next auto-refresh in: {minutes_left}m {seconds_left}s")
            
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
                elif choice in ['7', 'market', 'defillama', 'market analysis']:
                    print("\033[2J\033[H")
                    self.market_analysis_view.display()
                    input("\nPress Enter to return...")
                elif choice in ['r', 'refresh']:
                    print("🔄 Refreshing data...")
                    self.last_auto_refresh = datetime.now()  # Reset auto-refresh timer
                    continue
                elif choice in ['i', 'import']:
                    print("\033[2J\033[H")
                    self.import_transactions_menu()
                    input("\nPress Enter to return...")
                else:
                    print("❌ Invalid choice. Use 1, 2, 3, 4, 5, 6, 7, L, N, i, r, or q")
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
                    # Process legacy CSV files through the auto-detect system
                    legacy_results = {
                        'processed_data': {
                            'positions': {'long': [], 'neutral': []},
                            'transactions': [],
                            'balances': []
                        }
                    }
                    
                    # Process neutral positions
                    neutral_df = pd.read_csv(neutral_csv)
                    neutral_df = tracker.data_manager.clean_csv_data(neutral_df)
                    csv_format = tracker.data_manager.detect_csv_format(neutral_df)
                    for _, row in neutral_df.iterrows():
                        position = tracker.data_manager.parse_position(row, 'neutral', csv_format)
                        legacy_results['processed_data']['positions']['neutral'].append(position)
                    
                    # Process long positions
                    long_df = pd.read_csv(long_csv)
                    long_df = tracker.data_manager.clean_csv_data(long_df)
                    csv_format = tracker.data_manager.detect_csv_format(long_df)
                    for _, row in long_df.iterrows():
                        position = tracker.data_manager.parse_position(row, 'long', csv_format)
                        legacy_results['processed_data']['positions']['long'].append(position)
                    
                    # Merge the data
                    tracker.data_manager.merge_incremental_data(legacy_results['processed_data'])
                    
                    # Update metadata
                    metadata = {
                        "last_update": datetime.now().isoformat(),
                        "neutral_csv_hash": tracker.data_manager.get_file_hash(neutral_csv),
                        "long_csv_hash": tracker.data_manager.get_file_hash(long_csv),
                        "neutral_csv_path": neutral_csv,
                        "long_csv_path": long_csv
                    }
                    tracker.data_manager.save_metadata(metadata)
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