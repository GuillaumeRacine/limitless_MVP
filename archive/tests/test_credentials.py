#!/usr/bin/env python3
"""
Test Google Sheets Credentials
"""

from direct_sheets_sync import DirectSheetsSync

def test_credentials():
    print("🧪 Testing Google Sheets credentials...")
    
    # Test with no spreadsheet ID first (just credential validation)
    sync = DirectSheetsSync()
    
    if sync.service:
        print("✅ Google Sheets API service initialized successfully!")
        print(f"📧 Service account: limitless-trader@limitlessmvp.iam.gserviceaccount.com")
        print("\n🔧 Next steps:")
        print("1. Share your Google Sheet with: limitless-trader@limitlessmvp.iam.gserviceaccount.com")
        print("2. Give it 'Editor' permissions")
        print("3. Get your Spreadsheet ID from the URL")
        print("4. Test with: sync = DirectSheetsSync(spreadsheet_id='YOUR_ID')")
        return True
    else:
        print("❌ Failed to initialize Google Sheets service")
        return False

if __name__ == "__main__":
    test_credentials()