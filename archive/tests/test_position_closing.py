#!/usr/bin/env python3
"""
Test Position Closing System
Demonstrates how to close a position with yield data from screenshots
"""

import json
from pathlib import Path
from datetime import datetime
from yield_extractor import YieldExtractor

def test_close_clm_position():
    """Test closing the active CLM SOL/USDC position with example yield data"""
    
    extractor = YieldExtractor()
    
    print("=== Testing Position Closing System ===\n")
    
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
    
    print("✅ Found active CLM SOL/USDC position:")
    print(f"   ID: {clm_position.get('id')}")
    print(f"   Entry Value: ${clm_position.get('entry_value', 0):,.2f}")
    print(f"   Entry Date: {clm_position.get('entry_date')}")
    print(f"   Platform: {clm_position.get('platform')}")
    print(f"   Strategy: {clm_position.get('strategy')}")
    print(f"   Range: ${clm_position.get('min_range', 0):.2f} - ${clm_position.get('max_range', 0):.2f}")
    
    # Simulate yield data from a screenshot (this is what you'd extract from a closing screenshot)
    example_yield_data = {
        "token_pair": "SOL/USDC",
        "platform": "CLM",
        "position_value": 24500.00,  # Exit value
        "yield_earned": 450.00,      # Yield earned
        "apr": 85.5,                 # APR
        "current_price": 155.50,     # Current SOL price
        "price_range_min": 130.0,    # Min range
        "price_range_max": 158.75,   # Max range
        "in_range": True,            # Position status
        "extracted_at": datetime.now().isoformat()
    }
    
    print(f"\n📊 Example yield data from screenshot:")
    print(f"   Position Value: ${example_yield_data['position_value']:,.2f}")
    print(f"   Yield Earned: ${example_yield_data['yield_earned']:,.2f}")
    print(f"   APR: {example_yield_data['apr']:.2f}%")
    print(f"   Current Price: ${example_yield_data['current_price']:.2f}")
    print(f"   In Range: {example_yield_data['in_range']}")
    
    # Debug the matching process
    print(f"\n🔍 Debug matching process:")
    print(f"   Target pair: {example_yield_data['token_pair']}")
    print(f"   Target platform: {example_yield_data['platform']}")
    print(f"   Target value: ${example_yield_data['position_value']:,.2f}")
    
    print(f"\n   CLM Position details:")
    print(f"   - Token pair: '{clm_position.get('token_pair')}'")
    print(f"   - Platform: '{clm_position.get('platform')}'")
    print(f"   - Entry value: ${clm_position.get('entry_value', 0):,.2f}")
    
    print(f"\n   Normalized comparisons:")
    print(f"   - Target pair normalized: '{extractor.normalize_token_pair(example_yield_data['token_pair'])}'")
    print(f"   - CLM pair normalized: '{extractor.normalize_token_pair(clm_position.get('token_pair', ''))}'")
    print(f"   - Target platform normalized: '{extractor.normalize_platform(example_yield_data['platform'])}'")
    print(f"   - CLM platform normalized: '{extractor.normalize_platform(clm_position.get('platform', ''))}'")
    
    # Check value difference
    value_diff = abs(clm_position.get('entry_value', 0) - example_yield_data['position_value']) / example_yield_data['position_value']
    print(f"   - Value difference: {value_diff:.2%} (threshold: 10%)")
    
    # Test the matching
    matched_position = extractor.find_matching_position(example_yield_data)
    
    if matched_position:
        print(f"\n✅ Position matching successful!")
        print(f"   Matched Position ID: {matched_position.get('id')}")
        
        # Show what the closed position would look like
        closed_position = extractor.close_position_with_yield(matched_position, example_yield_data)
        
        print(f"\n📈 Position closure preview:")
        print(f"   Exit Value: ${closed_position.get('exit_value', 0):,.2f}")
        print(f"   Yield Earned: ${closed_position.get('claimed_yield_value', 0):,.2f}")
        print(f"   Yield Return: {closed_position.get('claimed_yield_return', 0):.2f}%")
        print(f"   Price Return: {closed_position.get('price_return', 0):.2f}%")
        print(f"   Net Return: {closed_position.get('net_return', 0):.2f}%")
        print(f"   Final APR: {closed_position.get('yield_apr', 0):.2f}%")
        print(f"   Exit Date: {closed_position.get('exit_date')}")
        
        # Ask for confirmation
        print(f"\n" + "="*60)
        print("🔄 To actually close this position, you would:")
        print("1. Take a screenshot of the position's final state")
        print("2. Update the yield_extractor.py with the screenshot data")
        print("3. Run: extractor.process_screenshot_for_closing(screenshot_path)")
        print("4. The position would be moved from active to closed")
        
        return True
    else:
        print(f"\n❌ Position matching failed")
        return False

def show_current_positions():
    """Show current active positions"""
    extractor = YieldExtractor()
    
    print("\n=== Current Active Positions ===")
    
    all_active = extractor.active_long + extractor.active_neutral
    
    for i, position in enumerate(all_active, 1):
        print(f"\n{i}. {position.get('token_pair', 'Unknown')} ({position.get('strategy', 'Unknown')})")
        print(f"   Platform: {position.get('platform', 'Unknown')}")
        print(f"   Entry Value: ${position.get('entry_value', 0):,.2f}")
        print(f"   Entry Date: {position.get('entry_date', 'Unknown')}")
        print(f"   ID: {position.get('id', 'Unknown')}")
        
        if position.get('min_range') is not None and position.get('max_range') is not None:
            print(f"   Range: ${position.get('min_range', 0):.2f} - ${position.get('max_range', 0):.2f}")
    
    print(f"\nTotal active positions: {len(all_active)}")

if __name__ == "__main__":
    show_current_positions()
    print("\n" + "="*80 + "\n")
    test_close_clm_position()