#!/usr/bin/env python3
"""
Add Dummy Row to Long Positions Sheet
"""

from custom_sheets_sync import CustomSheetsSync
from datetime import datetime
import random

def add_dummy_to_long_sheet():
    """Add a dummy position to the Long Positions sheet"""
    
    SPREADSHEET_ID = "1pstVaBwJaFdqQlSFDGnVJ06V13jc_od0SaY0wZ0yyzU"
    
    sync = CustomSheetsSync(spreadsheet_id=SPREADSHEET_ID)
    
    print("🧪 Adding dummy position to Long Positions sheet...")
    
    # First, let's check the structure of the Long Positions sheet
    try:
        # Read the headers to understand the structure
        header_result = sync.service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="'Long Positions'!1:1"
        ).execute()
        
        headers = header_result.get('values', [[]])[0]
        print(f"📋 Long Positions sheet headers: {headers}")
        
    except Exception as e:
        print(f"❌ Error reading headers: {e}")
        return False
    
    # Generate realistic dummy data for long position
    dummy_data = {
        'position_details': f"BTC/ETH Liquidity Pool",
        'strategy': 'Long',
        'wallet': f"0x{random.randint(10**15, 10**16-1):016x}...",
        'chain': 'Base',
        'platform': 'Aerodrome',
        'entry_value': round(random.uniform(20000, 35000), 2),
        'entry_date': '2025-06-28',
        'status': 'Closed',
        'days_active': 3,
        'min_range': round(random.uniform(50000, 55000), 2),
        'max_range': round(random.uniform(70000, 75000), 2),
        'exit_date': datetime.now().strftime("%Y-%m-%d"),
        'yield_earned': round(random.uniform(400, 800), 2),
        'apr': round(random.uniform(200, 350), 2),
        'position_id': f"long_test_{random.randint(100000, 999999)}"
    }
    
    # Calculate derived values
    dummy_data['exit_value'] = dummy_data['entry_value'] + dummy_data['yield_earned'] + random.uniform(-200, 200)
    dummy_data['yield_return'] = (dummy_data['yield_earned'] / dummy_data['entry_value']) * 100
    dummy_data['price_return'] = ((dummy_data['exit_value'] - dummy_data['yield_earned'] - dummy_data['entry_value']) / dummy_data['entry_value']) * 100
    dummy_data['net_return'] = dummy_data['yield_return'] + dummy_data['price_return']
    
    print(f"📊 Dummy Long position data:")
    print(f"   Position: {dummy_data['position_details']}")
    print(f"   Strategy: {dummy_data['strategy']}")
    print(f"   Platform: {dummy_data['platform']} ({dummy_data['chain']})")
    print(f"   Entry Value: ${dummy_data['entry_value']:,.2f}")
    print(f"   Exit Value: ${dummy_data['exit_value']:,.2f}")
    print(f"   Yield Earned: ${dummy_data['yield_earned']:,.2f}")
    print(f"   Yield Return: {dummy_data['yield_return']:.2f}%")
    print(f"   APR: {dummy_data['apr']:.2f}%")
    print(f"   Net Return: {dummy_data['net_return']:.2f}%")
    print(f"   Range: ${dummy_data['min_range']:,.0f} - ${dummy_data['max_range']:,.0f}")
    
    try:
        # Based on Long Positions sheet structure
        # Headers: Position Details, Strategy, Wallet, Chain, Platform, Total Entry Value, Entry Date, Status, Days #, Min Range, ...
        row_data = [
            dummy_data['position_details'],                      # Position Details
            dummy_data['strategy'],                              # Strategy
            dummy_data['wallet'],                                # Wallet
            dummy_data['chain'],                                 # Chain
            dummy_data['platform'],                              # Platform
            f"${dummy_data['entry_value']:,.2f}",               # Total Entry Value
            dummy_data['entry_date'],                            # Entry Date
            dummy_data['status'],                                # Status
            dummy_data['days_active'],                           # Days #
            f"${dummy_data['min_range']:,.0f}",                 # Min Range
            f"${dummy_data['max_range']:,.0f}",                 # Max Range
            dummy_data['exit_date'],                             # Exit Date (additional)
            f"${dummy_data['exit_value']:,.2f}",                # Exit Value (additional)
            f"${dummy_data['yield_earned']:,.2f}",              # Yield Earned (additional)
            f"{dummy_data['yield_return']:.2f}%",               # Yield Return % (additional)
            f"{dummy_data['price_return']:.2f}%",               # Price Return % (additional)
            f"{dummy_data['net_return']:.2f}%",                 # Net Return % (additional)
            f"{dummy_data['apr']:.1f}%",                        # APR (additional)
            dummy_data['position_id'],                          # Position ID (additional)
            "🧪 LONG TEST DATA",                                # Note (additional)
            f"Closed at {datetime.now().strftime('%H:%M')}"     # Timestamp (additional)
        ]
        
        # Add the row to Long Positions sheet
        body = {
            'values': [row_data]
        }
        
        result = sync.service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="'Long Positions'!A:U",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"\n✅ Successfully added dummy position to Long Positions sheet!")
        print(f"   Position ID: {dummy_data['position_id']}")
        print(f"   Updated rows: {result.get('updates', {}).get('updatedRows', 'unknown')}")
        
        # Also update Overview with Long position summary
        summary_text = (
            f"🧪 LONG TEST: {dummy_data['position_details']} | "
            f"Yield: ${dummy_data['yield_earned']:,.2f} | "
            f"APR: {dummy_data['apr']:.1f}% | "
            f"Added: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        overview_body = {
            'values': [[summary_text]]
        }
        
        sync.service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range="'Overview'!D1",
            valueInputOption='RAW',
            body=overview_body
        ).execute()
        
        print(f"✅ Added Long position summary to Overview sheet (cell D1)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding dummy Long position: {e}")
        return False

def main():
    """Add dummy position to Long Positions sheet"""
    
    print("=" * 80)
    print("🧪 LONG POSITIONS SHEET TEST")
    print("=" * 80)
    
    success = add_dummy_to_long_sheet()
    
    if success:
        print(f"\n🎉 LONG POSITIONS TEST SUCCESSFUL!")
        print(f"📊 Check your Google Sheet:")
        print(f"   1. Go to 'Long Positions' tab")
        print(f"   2. Look for 'BTC/ETH Liquidity Pool' at the bottom")
        print(f"   3. Status should show 'Closed'")
        print(f"   4. Should have complete yield and return data")
        print(f"   5. Check 'Overview' tab cell D1 for Long summary")
        
        print(f"\n✅ Both Neutral and Long sheets integration confirmed!")
        print(f"🚀 Real position closings will populate both sheet types")
    else:
        print(f"\n❌ Long positions test failed")

if __name__ == "__main__":
    main()