#!/usr/bin/env python3
"""
Test Real Screenshot Processing
Tests the system with the actual SOL/USDC screenshot data
"""

from yield_extractor import YieldExtractor
from pathlib import Path

def test_real_screenshot():
    """Test with the real SOL/USDC screenshot"""
    
    extractor = YieldExtractor()
    screenshot_path = "/Users/gui/Documents/Code/Limitless_MVP/data/trading_screenshots/trading_screenshot_20250630_141313.png"
    
    print("=== Testing Real SOL/USDC Screenshot ===\n")
    
    # Extract yield data from the real screenshot
    yield_data = extractor.extract_yield_from_screenshot_path(screenshot_path)
    
    if not yield_data:
        print("❌ No yield data extracted")
        return False
    
    print(f"📸 Screenshot data extracted:")
    print(f"   Token Pair: {yield_data['token_pair']}")
    print(f"   Platform: {yield_data['platform']}")
    print(f"   Current Position Value: ${yield_data['position_value']:,.2f}")
    print(f"   Yield Earned: ${yield_data['yield_earned']:,.2f}")
    print(f"   Current Price: ${yield_data['current_price']:.4f}")
    print(f"   In Range: {yield_data['in_range']}")
    
    # Find matching position
    matching_position = extractor.find_matching_position(yield_data)
    
    if not matching_position:
        print(f"\n❌ No matching position found")
        
        # Show available positions for debugging
        print("\n🔍 Available active positions:")
        all_active = extractor.active_long + extractor.active_neutral
        for pos in all_active:
            pair = pos.get('token_pair', 'Unknown')
            platform = pos.get('platform', 'Unknown')
            entry_val = pos.get('entry_value', 0)
            if 'SOL' in pair.upper():
                print(f"   - {pair} on {platform} (${entry_val:,.2f}) - ID: {pos.get('id', 'Unknown')}")
        
        return False
    
    print(f"\n✅ Found matching position:")
    print(f"   ID: {matching_position.get('id')}")
    print(f"   Token Pair: {matching_position.get('token_pair')}")
    print(f"   Platform: {matching_position.get('platform')}")
    print(f"   Entry Value: ${matching_position.get('entry_value', 0):,.2f}")
    print(f"   Entry Date: {matching_position.get('entry_date')}")
    print(f"   Days Active: {matching_position.get('days_active', 'Unknown')}")
    print(f"   Strategy: {matching_position.get('strategy')}")
    
    # Test the closing calculation
    print(f"\n" + "="*60)
    print("📊 POSITION CLOSING CALCULATION")
    print("="*60)
    
    closed_position = extractor.close_position_with_yield(matching_position, yield_data)
    
    print(f"\n📈 Final Position Summary:")
    print(f"   Entry Value: ${matching_position.get('entry_value', 0):,.2f}")
    print(f"   Exit Value: ${closed_position.get('exit_value', 0):,.2f}")
    print(f"   Yield Earned: ${closed_position.get('claimed_yield_value', 0):,.2f}")
    print(f"   Yield Return: {closed_position.get('claimed_yield_return', 0):.2f}%")
    print(f"   Price Return: {closed_position.get('price_return', 0):.2f}%")
    print(f"   Net Return: {closed_position.get('net_return', 0):.2f}%")
    print(f"   Calculated APR: {closed_position.get('yield_apr', 0):.2f}%")
    print(f"   Exit Date: {closed_position.get('exit_date')}")
    
    return True

if __name__ == "__main__":
    success = test_real_screenshot()
    
    if success:
        print(f"\n" + "="*60)
        print("✅ System ready to process real screenshots!")
        print("   The position would be closed with accurate yield calculations")
    else:
        print(f"\n❌ System needs adjustment for this screenshot")