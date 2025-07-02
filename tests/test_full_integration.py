#!/usr/bin/env python3
"""
Test Full Google Sheets Integration
"""

from direct_sheets_sync import DirectSheetsSync
from integrated_position_closer import IntegratedPositionCloser

def test_sheets_connection():
    """Test connection to the actual Google Sheet"""
    
    SPREADSHEET_ID = "1pstVaBwJaFdqQlSFDGnVJ06V13jc_od0SaY0wZ0yyzU"
    
    print("🧪 Testing Google Sheets connection...")
    print(f"📊 Spreadsheet ID: {SPREADSHEET_ID}")
    
    # Initialize sync
    sync = DirectSheetsSync(spreadsheet_id=SPREADSHEET_ID)
    
    # Test connection
    if sync.test_connection():
        print("\n✅ Successfully connected to your Google Sheet!")
        
        # Test finding a position
        print(f"\n🔍 Testing position lookup...")
        
        # Try to find our closed position
        position_id = "bddb2d6dc4a3"
        row_num = sync.find_position_row(position_id)
        
        if row_num:
            print(f"✅ Found position {position_id} at row {row_num}")
        else:
            print(f"❌ Position {position_id} not found in sheet")
            print("   (This is normal if you haven't added positions to the sheet yet)")
        
        return True
    else:
        print("\n❌ Failed to connect to Google Sheet")
        print("   Check that the service account has been shared with Editor permissions")
        return False

def test_integrated_closer():
    """Test the integrated position closer with Google Sheets"""
    
    SPREADSHEET_ID = "1pstVaBwJaFdqQlSFDGnVJ06V13jc_od0SaY0wZ0yyzU"
    
    print(f"\n" + "="*80)
    print("🚀 TESTING INTEGRATED POSITION CLOSER")
    print("="*80)
    
    # Initialize integrated closer
    closer = IntegratedPositionCloser(spreadsheet_id=SPREADSHEET_ID)
    
    if closer.auto_sync_enabled:
        print("✅ Integrated position closer ready with Google Sheets auto-sync!")
        
        # Test sync of our already-closed position
        print(f"\n🔄 Testing sync of closed position...")
        
        position_id = "bddb2d6dc4a3"
        success = closer.manual_sync_position(position_id)
        
        if success:
            print(f"✅ Position {position_id} synced to Google Sheets!")
            print(f"   Check your sheet - it should show:")
            print(f"   - Status: closed")
            print(f"   - Yield: $675.30")
            print(f"   - APR: 354.30%")
            print(f"   - Exit Date: 2025-06-30")
        else:
            print(f"❌ Failed to sync position {position_id}")
        
        return success
    else:
        print("❌ Auto-sync not enabled")
        return False

def main():
    """Run the full integration test"""
    
    print("=" * 80)
    print("🎯 FULL GOOGLE SHEETS INTEGRATION TEST")
    print("=" * 80)
    
    # Test basic connection
    connection_ok = test_sheets_connection()
    
    if connection_ok:
        # Test integrated closer
        integration_ok = test_integrated_closer()
        
        if integration_ok:
            print(f"\n" + "="*80)
            print("🎉 GOOGLE SHEETS INTEGRATION SUCCESSFUL!")
            print("="*80)
            print("✅ Connection working")
            print("✅ Position sync working")
            print("✅ Ready for automated screenshot → Google Sheets workflow!")
            
            print(f"\n🚀 Next time you process a screenshot:")
            print(f"   1. Screenshot taken")
            print(f"   2. Yield extracted")
            print(f"   3. Position closed in JSON")
            print(f"   4. Google Sheets automatically updated")
            print(f"   5. All done!")
        else:
            print(f"\n❌ Integration test failed")
    else:
        print(f"\n❌ Connection test failed")

if __name__ == "__main__":
    main()