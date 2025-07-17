#!/usr/bin/env python3
"""
CLM Portfolio Tracker - Main CLI Controller
"""

import sys
import os
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from clm_data import CLMDataManager
from views.active_positions import ActivePositionsView
from views.transactions import TransactionsView
from views.performance import PerformanceView
from views.allocation_breakdown import AllocationBreakdownView

class CLMTracker:
    def __init__(self):
        self.data_manager = CLMDataManager()
        self.active_view = ActivePositionsView(self.data_manager)
        self.transactions_view = TransactionsView(self.data_manager)
        self.performance_view = PerformanceView(self.data_manager)
        self.breakdown_view = AllocationBreakdownView(self.data_manager)
        
    def run_cli(self):
        """Simplified main CLI loop"""
        while True:
            # Refresh prices on each loop
            self.data_manager.refresh_prices_and_status()
            
            # Clear screen and show main view
            print("\033[2J\033[H")
            self.active_view.display()
            
            # Show simplified menu
            print(f"\n{'='*120}")
            print("Views: [1] Active  [2] Performance  [3] Allocation  [4] Transactions  [e]dit  [q]uit")
            print("="*120)
            
            try:
                choice = input("\nSelect: ").lower().strip()
                
                if choice in ['q', 'quit']:
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    continue  # Stay on home view
                elif choice == '2':
                    self._show_view(self.performance_view)
                elif choice == '3':
                    self._show_view(self.breakdown_view)
                elif choice == '4':
                    self._show_view(self.transactions_view)
                elif choice in ['e', 'edit']:
                    self._show_edit_link()
                else:
                    print("❌ Invalid choice")
                    input("Press Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    
    def _show_view(self, view):
        """Helper to display a view and wait for user"""
        print("\033[2J\033[H")
        view.display()
        input("\nPress Enter to return...")
    
    def _show_edit_link(self):
        """Display the position editing tool link"""
        print("\033[2J\033[H")
        print("🔧 CLM POSITION EDITOR")
        print("="*120)
        print()
        print("📝 Custom GPT Tool for Position Management:")
        print("   https://chatgpt.com/share/68792b62-7bb4-8009-9f05-3431d386ebca")
        print()
        print("💡 This tool helps you:")
        print("   • Format position data for CSV import")
        print("   • Create properly structured JSON files")
        print("   • Prepare active positions for the CLM tracker")
        print("   • Convert various data formats to the required schema")
        print()
        print("📋 Instructions:")
        print("   1. Copy your position data to the ChatGPT tool")
        print("   2. Follow the tool's guidance to format the data")
        print("   3. Export the formatted CSV/JSON files")
        print("   4. Place files in the data/ directory")
        print("   5. Restart the CLM tracker to load new positions")
        print()
        input("Press Enter to return to main menu...")
    

def main():
    tracker = CLMTracker()
    
    # CSV file paths (prioritize combined file)
    combined_csv = "data/Tokens_Trade_Sheet - Positions Status.csv"
    neutral_csv = "data/Tokens_Trade_Sheet - Neutral Positions.csv"
    long_csv = "data/Tokens_Trade_Sheet - Long Positions.csv"
    
    print("🚀 CLM Portfolio Tracker")
    
    # Check for combined CSV file first
    if os.path.exists(combined_csv):
        print("📁 Found combined positions CSV file")
        tracker.data_manager.load_from_combined_csv(combined_csv)
    elif os.path.exists(neutral_csv) and os.path.exists(long_csv):
        print("📁 Found separate position CSV files")
        tracker.data_manager.load_from_csv(neutral_csv, long_csv)
    else:
        # Try loading existing JSON data
        if tracker.data_manager.load_positions():
            print("✅ Loaded existing data")
        else:
            print("⚠️  No data found!")
            print(f"\nPlace CSV files at:")
            print(f"  - {combined_csv} (combined positions)")
            print(f"  OR")
            print(f"  - {neutral_csv}")
            print(f"  - {long_csv}")
            return
    
    # Start monitoring
    tracker.run_cli()

if __name__ == "__main__":
    main()