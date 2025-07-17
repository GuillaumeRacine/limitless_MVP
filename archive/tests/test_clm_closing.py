#!/usr/bin/env python3
"""
Test CLM Position Closing with Screenshot Yield Data
Uses the $675.304 yield for the active CLM SOL/USDC position
"""

from yield_extractor import YieldExtractor
from datetime import datetime

def test_clm_position_closing():
    """Test closing the CLM position with the yield data from screenshot"""
    
    extractor = YieldExtractor()
    
    print("=== Testing CLM SOL/USDC Position Closing ===\n")
    
    # Find the active CLM SOL/USDC position
    clm_position = None
    for position in extractor.active_neutral:
        if (position.get("token_pair") == "SOL/USDC" and 
            position.get("platform") == "CLM" and
            position.get("is_active") == True):
            clm_position = position
            break
    
    if not clm_position:
        print("❌ No active CLM SOL/USDC position found")
        return False
    
    print(f"✅ Found active CLM SOL/USDC position:")
    print(f"   ID: {clm_position.get('id')}")
    print(f"   Entry Value: ${clm_position.get('entry_value', 0):,.2f}")
    print(f"   Entry Date: {clm_position.get('entry_date')}")
    print(f"   Days Active: {clm_position.get('days_active', 10)}")
    print(f"   Platform: {clm_position.get('platform')}")
    print(f"   Strategy: {clm_position.get('strategy')}")
    
    # Create yield data using the screenshot values but matched to CLM platform
    yield_data = {
        "token_pair": "SOL/USDC",
        "platform": "CLM",  # Match the actual position platform
        "position_value": 21104.77,  # Current value from screenshot
        "yield_earned": 675.304,     # Yield from screenshot
        "current_price": 156.6799,   # Current SOL price
        "price_range_min": 128.221338,
        "price_range_max": 156.717989,
        "in_range": True,
        "extracted_at": datetime.now().isoformat()
    }
    
    print(f"\n📊 Yield data to apply:")
    print(f"   Current Position Value: ${yield_data['position_value']:,.2f}")
    print(f"   Yield Earned: ${yield_data['yield_earned']:,.2f}")
    print(f"   Current SOL Price: ${yield_data['current_price']:.4f}")
    
    # Test position closing calculation
    print(f"\n" + "="*60)
    print("📊 POSITION CLOSING CALCULATION")
    print("="*60)
    
    closed_position = extractor.close_position_with_yield(clm_position, yield_data)
    
    print(f"\n📈 Final Position Summary:")
    print(f"   Entry Value: ${clm_position.get('entry_value', 0):,.2f}")
    print(f"   Exit Value: ${closed_position.get('exit_value', 0):,.2f}")
    print(f"   Value Change: ${closed_position.get('exit_value', 0) - clm_position.get('entry_value', 0):,.2f}")
    print(f"   Yield Earned: ${closed_position.get('claimed_yield_value', 0):,.2f}")
    print(f"   Yield Return: {closed_position.get('claimed_yield_return', 0):.2f}%")
    print(f"   Price Return: {closed_position.get('price_return', 0):.2f}%")
    print(f"   Net Return: {closed_position.get('net_return', 0):.2f}%")
    print(f"   Calculated APR: {closed_position.get('yield_apr', 0):.2f}%")
    
    # Show the calculation breakdown
    entry_value = clm_position.get('entry_value', 0)
    days_active = clm_position.get('days_active', 10)
    yield_return_pct = (yield_data['yield_earned'] / entry_value) * 100
    annualized_apr = yield_return_pct * (365 / days_active)
    
    print(f"\n🔢 APR Calculation Breakdown:")
    print(f"   Formula: (Yield Earned ÷ Entry Value) × (365 ÷ Days Active)")
    print(f"   Calculation: (${yield_data['yield_earned']:,.2f} ÷ ${entry_value:,.2f}) × (365 ÷ {days_active})")
    print(f"   Step 1: {yield_return_pct:.2f}% yield return")
    print(f"   Step 2: {yield_return_pct:.2f}% × {365/days_active:.1f} = {annualized_apr:.2f}% APR")
    
    print(f"\n✅ Position ready to be closed with these values!")
    
    return True

def actually_close_position():
    """Actually close the position (WARNING: This modifies data files)"""
    
    print("\n" + "="*60)
    print("⚠️  ACTUAL POSITION CLOSING")
    print("="*60)
    
    response = input("Do you want to actually close the CLM SOL/USDC position? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Position closing cancelled")
        return
    
    extractor = YieldExtractor()
    
    # Create the yield data for CLM position
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
    
    # Find and close the position
    matching_position = extractor.find_matching_position(yield_data)
    
    if matching_position:
        # Close the position
        closed_position = extractor.close_position_with_yield(matching_position, yield_data)
        
        # Add to closed positions
        extractor.closed_positions.append(closed_position)
        
        # Remove from active positions
        extractor.remove_position_from_active(matching_position)
        
        # Save updated data
        extractor.save_json_file(extractor.data_dir / "clm_long.json", extractor.active_long)
        extractor.save_json_file(extractor.data_dir / "clm_neutral.json", extractor.active_neutral)
        extractor.save_json_file(extractor.data_dir / "clm_closed.json", extractor.closed_positions)
        
        print(f"✅ Position closed successfully!")
        print(f"   Yield earned: ${yield_data['yield_earned']:,.2f}")
        print(f"   APR: {closed_position.get('yield_apr', 0):.2f}%")
        print(f"   Net return: {closed_position.get('net_return', 0):.2f}%")
    else:
        print(f"❌ Could not find matching position to close")

if __name__ == "__main__":
    success = test_clm_position_closing()
    
    if success:
        actually_close_position()