#!/usr/bin/env python3
"""
Position Closing Preview Test
Shows exactly what will happen when closing the position without making changes
"""

import json
from yield_extractor import YieldExtractor
from datetime import datetime
from pathlib import Path

def preview_position_closing():
    """Preview the position closing without making any changes"""
    
    extractor = YieldExtractor()
    
    print("=" * 80)
    print("🔍 POSITION CLOSING PREVIEW TEST")
    print("=" * 80)
    
    # Find the CLM position
    clm_position = None
    for position in extractor.active_neutral:
        if (position.get("token_pair") == "SOL/USDC" and 
            position.get("platform") == "CLM"):
            clm_position = position
            break
    
    if not clm_position:
        print("❌ CLM SOL/USDC position not found")
        return False
    
    # Show current position
    print("\n📋 CURRENT ACTIVE POSITION:")
    print("-" * 40)
    for key, value in clm_position.items():
        print(f"   {key}: {value}")
    
    # Create yield data
    yield_data = {
        "token_pair": "SOL/USDC",
        "platform": "CLM",
        "position_value": 21104.77,
        "yield_earned": 675.304,
        "current_price": 156.6799,
        "price_range_min": 128.221338,
        "price_range_max": 156.717989,
        "in_range": True,
        "extracted_at": datetime.now().isoformat()
    }
    
    # Create the closed position (preview only)
    closed_position = extractor.close_position_with_yield(clm_position, yield_data)
    
    print("\n📋 RESULTING CLOSED POSITION:")
    print("-" * 40)
    for key, value in closed_position.items():
        if key in clm_position and clm_position[key] != value:
            print(f"   {key}: {clm_position[key]} → {value} ✏️")
        elif key not in clm_position:
            print(f"   {key}: {value} ✨")
        else:
            print(f"   {key}: {value}")
    
    return clm_position, closed_position, yield_data

def show_json_changes(original_pos, closed_pos):
    """Show what changes would be made to JSON files"""
    
    print("\n" + "=" * 80)
    print("📄 JSON FILE CHANGES PREVIEW")
    print("=" * 80)
    
    print("\n🗂️  clm_neutral.json (ACTIVE POSITIONS):")
    print("   ACTION: Remove this position")
    print(f"   REMOVED: Position ID {original_pos.get('id')} ({original_pos.get('token_pair')} on {original_pos.get('platform')})")
    
    print("\n🗂️  clm_closed.json (CLOSED POSITIONS):")
    print("   ACTION: Add this position")
    print("   ADDED: New closed position with yield data")
    
    # Show key fields that changed
    print("\n📊 KEY CHANGES:")
    changes = [
        ("status", original_pos.get("status", "open"), closed_pos.get("status")),
        ("is_active", original_pos.get("is_active", True), closed_pos.get("is_active")),
        ("exit_date", original_pos.get("exit_date"), closed_pos.get("exit_date")),
        ("exit_value", original_pos.get("exit_value"), closed_pos.get("exit_value")),
        ("claimed_yield_value", original_pos.get("claimed_yield_value"), closed_pos.get("claimed_yield_value")),
        ("yield_apr", original_pos.get("yield_apr"), closed_pos.get("yield_apr")),
        ("net_return", original_pos.get("net_return"), closed_pos.get("net_return"))
    ]
    
    for field, old_val, new_val in changes:
        if old_val != new_val:
            print(f"   • {field}: {old_val} → {new_val}")

def show_csv_impact(closed_pos):
    """Show how this would appear in CSV/sheets"""
    
    print("\n" + "=" * 80)
    print("📊 CSV/SPREADSHEET IMPACT")
    print("=" * 80)
    
    print("\n📋 This position would appear in 'Closed Positions' with:")
    
    # Key metrics for spreadsheet
    metrics = [
        ("Position ID", closed_pos.get("id")),
        ("Token Pair", closed_pos.get("token_pair")),
        ("Platform", closed_pos.get("platform")),
        ("Strategy", closed_pos.get("strategy")),
        ("Entry Date", closed_pos.get("entry_date")),
        ("Exit Date", closed_pos.get("exit_date")),
        ("Entry Value", f"${closed_pos.get('entry_value', 0):,.2f}"),
        ("Exit Value", f"${closed_pos.get('exit_value', 0):,.2f}"),
        ("Days Active", closed_pos.get("days_active", 0)),
        ("Yield Earned", f"${closed_pos.get('claimed_yield_value', 0):,.2f}"),
        ("Yield Return %", f"{closed_pos.get('claimed_yield_return', 0):.2f}%"),
        ("Price Return %", f"{closed_pos.get('price_return', 0):.2f}%"),
        ("Net Return %", f"{closed_pos.get('net_return', 0):.2f}%"),
        ("APR %", f"{closed_pos.get('yield_apr', 0):.2f}%"),
        ("Final Price", f"${closed_pos.get('final_price', 0):.4f}"),
        ("Was In Range", closed_pos.get("was_in_range", False))
    ]
    
    for label, value in metrics:
        print(f"   {label:.<20} {value}")

def test_json_structure():
    """Test that the JSON structure is valid"""
    
    print("\n" + "=" * 80)
    print("🧪 JSON STRUCTURE VALIDATION")
    print("=" * 80)
    
    extractor = YieldExtractor()
    
    # Test loading current files
    try:
        long_positions = len(extractor.active_long)
        neutral_positions = len(extractor.active_neutral)
        closed_positions = len(extractor.closed_positions)
        
        print(f"✅ Current JSON files valid:")
        print(f"   Long positions: {long_positions}")
        print(f"   Neutral positions: {neutral_positions}")
        print(f"   Closed positions: {closed_positions}")
        
        return True
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
        return False

def main():
    """Run the complete preview test"""
    
    # Test JSON structure first
    if not test_json_structure():
        return
    
    # Preview the position closing
    result = preview_position_closing()
    if not result:
        return
    
    original_pos, closed_pos, yield_data = result
    
    # Show JSON changes
    show_json_changes(original_pos, closed_pos)
    
    # Show CSV impact
    show_csv_impact(closed_pos)
    
    print("\n" + "=" * 80)
    print("✅ PREVIEW COMPLETE")
    print("=" * 80)
    print("\nThis test shows exactly what would happen when closing the position.")
    print("No actual changes were made to any files.")
    print("\nTo proceed with actual closing:")
    print("1. Review the calculations above")
    print("2. Confirm the APR calculation (354.30%) is correct")
    print("3. Run the actual closing process if satisfied")

if __name__ == "__main__":
    main()