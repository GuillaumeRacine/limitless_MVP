#!/usr/bin/env python3
"""
Actual Position Closing Test
Performs the real closing and shows the JSON results
"""

import json
import shutil
from pathlib import Path
from yield_extractor import YieldExtractor
from datetime import datetime

def backup_data_files():
    """Create backup of current data files"""
    
    data_dir = Path(__file__).parent / "data" / "JSON_out"
    backup_dir = Path(__file__).parent / "data" / "backup_before_closing"
    
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = ["clm_long.json", "clm_neutral.json", "clm_closed.json"]
    
    print("💾 Creating backup of data files...")
    for filename in files_to_backup:
        source = data_dir / filename
        backup = backup_dir / f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if source.exists():
            shutil.copy2(source, backup)
            print(f"   ✅ Backed up: {filename}")
    
    return backup_dir

def restore_from_backup(backup_dir):
    """Restore files from backup"""
    
    data_dir = Path(__file__).parent / "data" / "JSON_out"
    
    print("🔄 Restoring from backup...")
    for backup_file in backup_dir.glob("*.backup_*"):
        original_name = backup_file.name.split('.backup_')[0]
        target = data_dir / original_name
        shutil.copy2(backup_file, target)
        print(f"   ✅ Restored: {original_name}")

def perform_actual_closing():
    """Perform the actual position closing"""
    
    print("=" * 80)
    print("🚀 PERFORMING ACTUAL POSITION CLOSING")
    print("=" * 80)
    
    # Create backup first
    backup_dir = backup_data_files()
    
    try:
        # Initialize extractor
        extractor = YieldExtractor()
        
        # Record initial counts
        initial_long = len(extractor.active_long)
        initial_neutral = len(extractor.active_neutral)
        initial_closed = len(extractor.closed_positions)
        
        print(f"\n📊 Initial state:")
        print(f"   Long positions: {initial_long}")
        print(f"   Neutral positions: {initial_neutral}")
        print(f"   Closed positions: {initial_closed}")
        
        # Create yield data for CLM position
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
        
        # Find the position to close
        target_position = None
        for position in extractor.active_neutral:
            if (position.get("token_pair") == "SOL/USDC" and 
                position.get("platform") == "CLM"):
                target_position = position
                break
        
        if not target_position:
            print("❌ Target position not found!")
            return False
        
        print(f"\n🎯 Found target position: {target_position.get('id')}")
        
        # Perform the closing
        print(f"\n🔄 Processing position closure...")
        
        # Create closed position
        closed_position = extractor.close_position_with_yield(target_position, yield_data)
        
        # Add to closed positions
        extractor.closed_positions.append(closed_position)
        
        # Remove from active neutral positions
        extractor.active_neutral = [
            p for p in extractor.active_neutral 
            if p.get("id") != target_position.get("id")
        ]
        
        # Save all files
        extractor.save_json_file(extractor.data_dir / "clm_long.json", extractor.active_long)
        extractor.save_json_file(extractor.data_dir / "clm_neutral.json", extractor.active_neutral)
        extractor.save_json_file(extractor.data_dir / "clm_closed.json", extractor.closed_positions)
        
        # Record final counts
        final_long = len(extractor.active_long)
        final_neutral = len(extractor.active_neutral)
        final_closed = len(extractor.closed_positions)
        
        print(f"\n📊 Final state:")
        print(f"   Long positions: {final_long} (no change)")
        print(f"   Neutral positions: {final_neutral} (was {initial_neutral})")
        print(f"   Closed positions: {final_closed} (was {initial_closed})")
        
        print(f"\n✅ Position successfully closed!")
        print(f"   Position ID: {closed_position.get('id')}")
        print(f"   Yield earned: ${closed_position.get('claimed_yield_value', 0):,.2f}")
        print(f"   APR: {closed_position.get('yield_apr', 0):.2f}%")
        print(f"   Net return: {closed_position.get('net_return', 0):.2f}%")
        
        return True, backup_dir, closed_position
        
    except Exception as e:
        print(f"❌ Error during closing: {e}")
        print("🔄 Restoring from backup...")
        restore_from_backup(backup_dir)
        return False, backup_dir, None

def verify_json_structure(closed_position):
    """Verify the JSON files have correct structure"""
    
    print(f"\n" + "=" * 80)
    print("🔍 VERIFYING JSON STRUCTURE")
    print("=" * 80)
    
    data_dir = Path(__file__).parent / "data" / "JSON_out"
    
    # Load and verify each file
    files_to_check = [
        ("clm_long.json", "Long positions"),
        ("clm_neutral.json", "Neutral positions"), 
        ("clm_closed.json", "Closed positions")
    ]
    
    for filename, description in files_to_check:
        filepath = data_dir / filename
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            print(f"✅ {description} ({filename}):")
            print(f"   - Valid JSON: ✅")
            print(f"   - Records: {len(data)}")
            
            if filename == "clm_closed.json" and closed_position:
                # Verify our closed position is in there
                found_closed = any(
                    pos.get('id') == closed_position.get('id') 
                    for pos in data
                )
                print(f"   - Contains our closed position: {'✅' if found_closed else '❌'}")
                
                if found_closed:
                    # Show the closed position data
                    our_pos = next(
                        pos for pos in data 
                        if pos.get('id') == closed_position.get('id')
                    )
                    print(f"   - Yield value: ${our_pos.get('claimed_yield_value', 0):,.2f}")
                    print(f"   - APR: {our_pos.get('yield_apr', 0):.2f}%")
                    print(f"   - Status: {our_pos.get('status')}")
                    print(f"   - Exit date: {our_pos.get('exit_date')}")
                    
        except json.JSONDecodeError as e:
            print(f"❌ {description} ({filename}): Invalid JSON - {e}")
        except Exception as e:
            print(f"❌ {description} ({filename}): Error - {e}")

def show_csv_representation(closed_position):
    """Show how this would look in CSV format"""
    
    print(f"\n" + "=" * 80)
    print("📊 CSV REPRESENTATION")
    print("=" * 80)
    
    # Create CSV-like representation
    csv_headers = [
        "Position ID", "Token Pair", "Platform", "Strategy", "Entry Date", "Exit Date",
        "Entry Value", "Exit Value", "Days Active", "Yield Earned", "Yield Return %",
        "Price Return %", "Net Return %", "APR %", "Final Price", "In Range"
    ]
    
    csv_values = [
        closed_position.get('id', ''),
        closed_position.get('token_pair', ''),
        closed_position.get('platform', ''),
        closed_position.get('strategy', ''),
        closed_position.get('entry_date', ''),
        closed_position.get('exit_date', ''),
        f"${closed_position.get('entry_value', 0):,.2f}",
        f"${closed_position.get('exit_value', 0):,.2f}",
        closed_position.get('days_active', ''),
        f"${closed_position.get('claimed_yield_value', 0):,.2f}",
        f"{closed_position.get('claimed_yield_return', 0):.2f}%",
        f"{closed_position.get('price_return', 0):.2f}%",
        f"{closed_position.get('net_return', 0):.2f}%",
        f"{closed_position.get('yield_apr', 0):.2f}%",
        f"${closed_position.get('final_price', 0):.4f}",
        closed_position.get('was_in_range', False)
    ]
    
    print("📋 CSV Headers:")
    print("   " + " | ".join(csv_headers))
    print("\n📋 CSV Values:")
    print("   " + " | ".join(csv_values))

def main():
    """Main function"""
    
    print("⚠️  This will actually modify your JSON files!")
    print("✅ Backups will be created automatically.")
    print("🚀 Proceeding with position closing...")
    
    # Perform the actual closing
    success, backup_dir, closed_position = perform_actual_closing()
    
    if success and closed_position:
        # Verify the results
        verify_json_structure(closed_position)
        show_csv_representation(closed_position)
        
        print(f"\n" + "=" * 80)
        print("✅ CLOSING COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"✅ Position {closed_position.get('id')} has been closed")
        print(f"💾 Backups stored in: {backup_dir}")
        print(f"📄 JSON files updated successfully")
        print(f"💰 Yield recorded: ${closed_position.get('claimed_yield_value', 0):,.2f}")
        print(f"📈 APR calculated: {closed_position.get('yield_apr', 0):.2f}%")
    else:
        print(f"\n❌ Closing failed - files restored from backup")

if __name__ == "__main__":
    main()