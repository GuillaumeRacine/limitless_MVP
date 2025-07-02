#!/usr/bin/env python3
"""
Add Dummy Row to Google Sheet for Testing
"""

from custom_sheets_sync import CustomSheetsSync
from datetime import datetime
import random

def add_dummy_position():
    """Add a dummy position to test the Google Sheets integration"""
    
    SPREADSHEET_ID = "1pstVaBwJaFdqQlSFDGnVJ06V13jc_od0SaY0wZ0yyzU"
    
    sync = CustomSheetsSync(spreadsheet_id=SPREADSHEET_ID)
    
    print("🧪 Adding dummy position to test Google Sheets integration...")
    
    # Generate realistic dummy data
    dummy_data = {
        'position': f"ETH/USDC Test Position",
        'type': 'CLM',
        'strategy': 'Long',
        'status': 'Closed',
        'wallet': f"0x{random.randint(10**15, 10**16-1):016x}...",
        'chain': 'ETH',
        'platform': 'Uniswap',
        'entry_value': round(random.uniform(15000, 25000), 2),
        'entry_date': '2025-06-29',
        'days_active': 2,
        'exit_date': datetime.now().strftime("%Y-%m-%d"),
        'yield_earned': round(random.uniform(200, 500), 2),
        'apr': round(random.uniform(150, 400), 2),
        'position_id': f"test_{random.randint(100000, 999999)}"
    }
    
    # Calculate some derived values
    dummy_data['exit_value'] = dummy_data['entry_value'] + dummy_data['yield_earned'] + random.uniform(-500, 500)
    dummy_data['yield_return'] = (dummy_data['yield_earned'] / dummy_data['entry_value']) * 100
    
    print(f"📊 Dummy position data:")
    print(f"   Position: {dummy_data['position']}")
    print(f"   Entry Value: ${dummy_data['entry_value']:,.2f}")
    print(f"   Exit Value: ${dummy_data['exit_value']:,.2f}")
    print(f"   Yield Earned: ${dummy_data['yield_earned']:,.2f}")
    print(f"   Yield Return: {dummy_data['yield_return']:.2f}%")
    print(f"   APR: {dummy_data['apr']:.2f}%")
    print(f"   Days Active: {dummy_data['days_active']}")
    print(f"   Status: {dummy_data['status']}")
    
    try:
        # Prepare row data based on your sheet structure
        # Headers: Position, Type, Strategy, Status, Wallet, Chain, Platform, Entry Value, Entry Date, Days #
        row_data = [
            dummy_data['position'],                              # Position
            dummy_data['type'],                                  # Type
            dummy_data['strategy'],                              # Strategy
            dummy_data['status'],                                # Status
            dummy_data['wallet'],                                # Wallet
            dummy_data['chain'],                                 # Chain
            dummy_data['platform'],                              # Platform
            f"${dummy_data['entry_value']:,.2f}",               # Entry Value
            dummy_data['entry_date'],                            # Entry Date
            dummy_data['days_active'],                           # Days #
            dummy_data['exit_date'],                             # Exit Date (extra column)
            f"${dummy_data['yield_earned']:,.2f}",              # Yield Earned (extra column)
            f"{dummy_data['apr']:.1f}%",                        # APR (extra column)
            f"${dummy_data['exit_value']:,.2f}",                # Exit Value (extra column)
            f"{dummy_data['yield_return']:.2f}%",               # Yield Return % (extra column)
            dummy_data['position_id'],                          # Position ID (extra column)
            "🧪 DUMMY TEST DATA"                                # Note (extra column)
        ]
        
        # Add the row to Neutral Positions sheet
        body = {
            'values': [row_data]
        }
        
        result = sync.service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="'Neutral Positions'!A:Q",
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"\n✅ Successfully added dummy position to your Google Sheet!")
        print(f"   Added to Neutral Positions sheet")
        print(f"   Position ID: {dummy_data['position_id']}")
        print(f"   Updated rows: {result.get('updates', {}).get('updatedRows', 'unknown')}")
        
        # Also add a summary to Overview sheet
        summary_text = (
            f"🧪 TEST: Dummy position added at {datetime.now().strftime('%H:%M:%S')}\n"
            f"ETH/USDC Test Position | Yield: ${dummy_data['yield_earned']:,.2f} | APR: {dummy_data['apr']:.1f}%"
        )
        
        overview_body = {
            'values': [[summary_text]]
        }
        
        sync.service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range="'Overview'!C1",
            valueInputOption='RAW',
            body=overview_body
        ).execute()
        
        print(f"✅ Added test summary to Overview sheet")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding dummy position: {e}")
        return False

def main():
    """Add dummy position to demonstrate Google Sheets integration"""
    
    print("=" * 80)
    print("🧪 GOOGLE SHEETS INTEGRATION TEST")
    print("=" * 80)
    
    success = add_dummy_position()
    
    if success:
        print(f"\n🎉 TEST SUCCESSFUL!")
        print(f"📊 Check your Google Sheet:")
        print(f"   1. Go to 'Neutral Positions' tab")
        print(f"   2. Look for 'ETH/USDC Test Position' at the bottom")
        print(f"   3. Status should show 'Closed'")
        print(f"   4. Should have yield data and APR")
        print(f"   5. Check 'Overview' tab cell C1 for summary")
        
        print(f"\n✅ This proves the Google Sheets integration is working!")
        print(f"🚀 Real position closings will work the same way")
    else:
        print(f"\n❌ Test failed - check the error messages above")

if __name__ == "__main__":
    main()