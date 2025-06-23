#!/usr/bin/env python3
"""
CLM Portfolio Tracker - Main CLI Controller
"""

import sys
import os
from time import sleep
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
            print("🔧 Actions: [r]efresh | [q]uit")
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
                else:
                    print("❌ Invalid choice. Use 1, 2, 3, 4, 5, 6, L, N, r, or q")
                    sleep(1)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

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
        # Auto-detect mode
        if os.path.exists(neutral_csv) and os.path.exists(long_csv):
            # Check if update needed
            if tracker.data_manager.check_for_updates(neutral_csv, long_csv):
                print("🔄 CSV files changed, updating positions...")
                tracker.data_manager.update_positions(neutral_csv, long_csv)
            else:
                print("✅ No changes detected, loading existing data...")
                tracker.data_manager.load_positions()
            
            # Start monitoring
            tracker.run_cli()
            
        else:
            print("🚀 CLM Portfolio Tracker")
            print("\nSetup Options:")
            print(f"1. Place CSV files at: {neutral_csv} and {long_csv}")
            print("2. Or manually convert: python clm.py convert <neutral_csv> <long_csv>")
            print("3. Then monitor: python clm.py monitor")
            print("\nAuto-mode: Just run 'python clm.py' (will auto-update if CSVs changed)")

if __name__ == "__main__":
    main()