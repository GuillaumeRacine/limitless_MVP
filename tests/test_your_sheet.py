#!/usr/bin/env python3
"""
Test Your Specific Google Sheet Structure
"""

from direct_sheets_sync import DirectSheetsSync

def test_your_sheet_structure():
    """Test your specific Google Sheet"""
    
    SPREADSHEET_ID = "1pstVaBwJaFdqQlSFDGnVJ06V13jc_od0SaY0wZ0yyzU"
    
    print("🧪 Testing your specific Google Sheet structure...")
    
    # Initialize sync
    sync = DirectSheetsSync(spreadsheet_id=SPREADSHEET_ID)
    
    if not sync.service:
        print("❌ Failed to initialize service")
        return False
    
    # Test reading from different sheets
    sheet_names = ["Long Positions", "Neutral Positions", "Overview"]
    
    for sheet_name in sheet_names:
        print(f"\n📋 Testing sheet: '{sheet_name}'")
        
        try:
            # Try to read the first few rows to see the structure
            range_name = f"'{sheet_name}'!A1:Z10"
            result = sync.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            print(f"✅ Successfully read {len(values)} rows from '{sheet_name}'")
            
            # Show the first row (headers)
            if values:
                headers = values[0] if values[0] else []
                print(f"   Headers: {headers[:10]}...")  # Show first 10 columns
                
                # Check if this looks like position data
                position_keywords = ['position', 'id', 'token', 'platform', 'entry', 'yield']
                header_text = ' '.join(headers).lower()
                
                if any(keyword in header_text for keyword in position_keywords):
                    print(f"   ✅ This looks like position data!")
                    
                    # Show a few data rows
                    if len(values) > 1:
                        print(f"   📊 Sample data rows:")
                        for i, row in enumerate(values[1:4], 1):  # Show rows 2-4
                            if row:
                                print(f"      Row {i+1}: {row[:5]}...")  # First 5 columns
                else:
                    print(f"   ℹ️  Doesn't appear to contain position data")
            
        except Exception as e:
            print(f"❌ Error reading '{sheet_name}': {e}")
    
    return True

def test_write_to_sheet():
    """Test writing to your sheet"""
    
    SPREADSHEET_ID = "1pstVaBwJaFdqQlSFDGnVJ06V13jc_od0SaY0wZ0yyzU"
    
    print(f"\n" + "="*60)
    print("🔄 TESTING WRITE ACCESS")
    print("="*60)
    
    sync = DirectSheetsSync(spreadsheet_id=SPREADSHEET_ID)
    
    # Test writing to Overview sheet (safer than position sheets)
    test_range = "'Overview'!A1"
    test_value = f"Test from Claude Code - {datetime.now().strftime('%H:%M:%S')}"
    
    try:
        body = {
            'values': [[test_value]]
        }
        
        result = sync.service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=test_range,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"✅ Successfully wrote test value to Overview!A1")
        print(f"   Value: '{test_value}'")
        print(f"   Check your Overview sheet - cell A1 should show the test message")
        
        return True
        
    except Exception as e:
        print(f"❌ Write test failed: {e}")
        if "403" in str(e):
            print("   This suggests the service account doesn't have Editor permissions")
        return False

def main():
    """Run tests on your specific sheet"""
    
    print("=" * 80)
    print("🎯 TESTING YOUR GOOGLE SHEET")
    print("=" * 80)
    
    # Test reading
    read_ok = test_your_sheet_structure()
    
    if read_ok:
        # Test writing
        write_ok = test_write_to_sheet()
        
        if write_ok:
            print(f"\n✅ Your Google Sheet is fully accessible!")
            print(f"📊 Ready to sync position data")
        else:
            print(f"\n❌ Write access failed")
            print(f"   Check service account permissions")
    else:
        print(f"\n❌ Read access failed")

if __name__ == "__main__":
    from datetime import datetime
    main()