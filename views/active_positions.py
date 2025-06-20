#!/usr/bin/env python3
"""
Active Positions View - Job to be done: Monitor active CLM positions and range status
Split by strategy: Long and Neutral are separate businesses
"""

class ActivePositionsView:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def display(self):
        """Display active positions with separate tables for Long and Neutral strategies"""
        long_positions = self.data_manager.get_positions_by_strategy('long')
        neutral_positions = self.data_manager.get_positions_by_strategy('neutral')
        
        print("\n" + "="*120)
        print("🎯 ACTIVE POSITIONS - STRATEGY SPLIT VIEW")
        print("="*120)
        
        # Display both strategies side by side
        self._display_strategy_tables(long_positions, neutral_positions)
    
    def _display_strategy_tables(self, long_positions, neutral_positions):
        """Display Long and Neutral strategies as two separate tables"""
        
        # Display Long Strategy Table
        self._display_single_strategy_table(long_positions, "📈 LONG STRATEGY", "long")
        
        print("\n")  # Space between tables
        
        # Display Neutral Strategy Table  
        self._display_single_strategy_table(neutral_positions, "⚖️  NEUTRAL STRATEGY", "neutral")
    
    def _display_single_strategy_table(self, positions, title, strategy_type):
        """Display a single strategy table"""
        
        # Calculate stats for this strategy
        if not positions:
            print(f"{title}")
            print("=" * 80)
            print("📊 No active positions in this strategy")
            return
        
        total_value = sum([p['entry_value'] for p in positions if p['entry_value']])
        returns = [p['net_return'] for p in positions if p['net_return'] is not None]
        avg_return = sum(returns) / len(returns) if returns else 0
        
        out_of_range = len([p for p in positions if p['range_status'].startswith('out_of_range')])
        in_range = len([p for p in positions if p['range_status'] == 'in_range'])
        
        # Strategy header and stats
        print(f"{title}")
        print("=" * 80)
        print(f"📊 {len(positions)} Positions | 💰 ${total_value:,.0f} Entry Value | 📈 {avg_return:.1f}% Avg Return")
        print(f"✅ {in_range} In Range | ⚠️ {out_of_range} Out of Range")
        print("-" * 80)
        
        # Table header
        print(f"{'Position':<18} {'Platform':<10} {'Price Slider':<25} {'Days':<5} {'Return':<8} {'Status':<6}")
        print("-" * 80)
        
        # Sort positions: out of range first
        sorted_positions = sorted(positions, key=lambda x: (
            0 if x['range_status'].startswith('out_of_range') else 1
        ))
        
        # Display each position
        for position in sorted_positions:
            self._print_strategy_position_row(position)
    
    def _print_strategy_position_row(self, position):
        """Print a single position row in strategy table format"""
        current_price = position.get('current_price', 0)
        range_status = position.get('range_status', 'unknown')
        
        # Status indicators
        if range_status == 'in_range':
            status_icon = '🟢'
        elif range_status == 'out_of_range_low':
            status_icon = '🔴'
        elif range_status == 'out_of_range_high':
            status_icon = '🟠'
        else:
            status_icon = '⚪'
        
        # Create price slider visualization
        slider_str = self._create_price_slider(position)
        
        days_str = str(int(position['days_active'])) if position['days_active'] else "N/A"
        return_str = f"{position['net_return']:.1f}%" if position['net_return'] else "N/A"
        
        # Truncate position name to fit
        pos_name = (position['token_pair'][:18] if position['token_pair'] 
                   else position['position_details'][:18])
        platform = position['platform'][:8]
        
        print(f"{pos_name:<18} {platform:<10} {slider_str:<25} {days_str:<5} {return_str:<8} {status_icon}")
    
    def _create_price_slider(self, position):
        """Create a visual slider showing current price within min/max range"""
        current_price = position.get('current_price', 0)
        min_range = position.get('min_range')
        max_range = position.get('max_range')
        
        # Return dash if no range data
        if not min_range or not max_range or not current_price:
            return "-"
        
        # Calculate position on slider (0-1)
        price_ratio = (current_price - min_range) / (max_range - min_range)
        price_ratio = max(0, min(1, price_ratio))  # Clamp between 0 and 1
        
        # Create 15-character slider
        slider_length = 15
        position_index = int(price_ratio * (slider_length - 1))
        
        # Build slider
        slider = ['─'] * slider_length
        slider[0] = '├'  # Left bound
        slider[-1] = '┤'  # Right bound
        
        # Position indicator
        if price_ratio <= 0:
            slider[0] = '◄'  # Below range
        elif price_ratio >= 1:
            slider[-1] = '►'  # Above range
        else:
            slider[position_index] = '●'  # Current position
        
        return ''.join(slider)
    
    
    def display_strategy_detail(self, strategy):
        """Display detailed view for a specific strategy"""
        positions = self.data_manager.get_positions_by_strategy(strategy)
        strategy_name = "LONG STRATEGY" if strategy == 'long' else "NEUTRAL STRATEGY"
        strategy_icon = "📈" if strategy == 'long' else "⚖️"
        
        print(f"\n{strategy_icon} {strategy_name} - DETAILED VIEW")
        print("=" * 100)
        
        if not positions:
            print(f"📊 No active {strategy} positions found.")
            return
        
        # Strategy summary
        total_value = sum([p['entry_value'] for p in positions if p['entry_value']])
        returns = [p['net_return'] for p in positions if p['net_return'] is not None]
        avg_return = sum(returns) / len(returns) if returns else 0
        
        out_of_range = [p for p in positions if p['range_status'].startswith('out_of_range')]
        in_range = [p for p in positions if p['range_status'] == 'in_range']
        
        print(f"📊 {len(positions)} Positions | 💰 ${total_value:,.0f} Entry Value | 📈 {avg_return:.1f}% Avg Return")
        print(f"✅ {len(in_range)} In Range | ⚠️ {len(out_of_range)} Out of Range")
        print("-" * 100)
        
        # Detailed table
        print(f"{'Position':<25} {'Platform':<12} {'Wallet':<10} {'Current':<12} {'Range':<20} {'Days':<5} {'Return':<8} {'Status':<8}")
        print("-" * 100)
        
        # Sort by range status (out of range first)
        sorted_positions = sorted(positions, key=lambda x: (
            0 if x['range_status'].startswith('out_of_range') else 1
        ))
        
        for position in sorted_positions:
            current_price = position.get('current_price', 0)
            range_status = position.get('range_status', 'unknown')
            
            # Status indicators
            if range_status == 'in_range':
                status_icon = '🟢 IN'
            elif range_status == 'out_of_range_low':
                status_icon = '🔴 LOW'
            elif range_status == 'out_of_range_high':
                status_icon = '🔴 HIGH'
            else:
                status_icon = '⚪ UNK'
            
            # Format values
            current_str = f"${current_price:.2f}" if current_price else "N/A"
            
            if position['min_range'] and position['max_range']:
                if position['min_range'] >= 1:
                    range_str = f"${position['min_range']:.0f}-${position['max_range']:.0f}"
                else:
                    range_str = f"${position['min_range']:.3f}-${position['max_range']:.3f}"
            else:
                range_str = "N/A"
            
            days_str = str(int(position['days_active'])) if position['days_active'] else "N/A"
            return_str = f"{position['net_return']:.1f}%" if position['net_return'] else "N/A"
            
            # Truncate long names
            pos_name = position['token_pair'][:23] if position['token_pair'] else position['position_details'][:23]
            wallet = position['wallet'][:8]
            
            print(f"{pos_name:<25} {position['platform'][:10]:<12} {wallet:<10} "
                  f"{current_str:<12} {range_str:<20} {days_str:<5} {return_str:<8} {status_icon:<8}")