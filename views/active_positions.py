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
        
        # Display token returns table below strategies
        self._display_token_returns()
    
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
        print("-" * 138)
        
        # Table header
        print(f"{'Position':<20} {'Entry USD':<10} {'%':<5} {'Chain':<6} {'Platform':<10} {'Min Range':<10} {'Price':<10} {'Max Range':<10} {'Status':<12} {'Days':<5} {'Return':<8} {'Range Slider'}")
        print("-" * 138)
        
        # Sort positions: out of range first
        sorted_positions = sorted(positions, key=lambda x: (
            0 if x['range_status'].startswith('out_of_range') else 1
        ))
        
        # Display each position
        for position in sorted_positions:
            self._print_strategy_position_row(position, total_value)
    
    def _print_strategy_position_row(self, position, strategy_total):
        """Print a single position row in strategy table format"""
        current_price = position.get('current_price', 0)
        range_status = position.get('range_status', 'unknown')
        
        # Status indicators
        if range_status == 'in_range':
            status_text = 'Active'
        elif range_status.startswith('out_of_range'):
            status_text = 'Out of Range'
        elif range_status == 'perp_active':
            status_text = 'Active'  # Perp within acceptable range
        elif range_status == 'perp_closed':
            status_text = 'Closed'  # Perp above liquidation
        elif range_status == 'no_range':
            status_text = 'Unknown'  # Position without ranges
        else:
            status_text = 'Unknown'
        
        # Format individual column values
        min_range = position.get('min_range')
        max_range = position.get('max_range')
        current_price = position.get('current_price', 0)
        entry_value = position.get('entry_value', 0)
        chain = position.get('chain', 'Unknown')
        
        min_str = f"${min_range:.2f}" if min_range else "N/A"
        price_str = f"${current_price:.2f}" if current_price else "N/A"
        max_str = f"${max_range:.2f}" if max_range else "N/A"
        entry_str = f"${entry_value:,.0f}" if entry_value else "N/A"
        chain_str = chain[:6]  # Truncate to fit column
        
        # Calculate percentage of strategy total
        if entry_value and strategy_total and strategy_total > 0:
            percentage = (entry_value / strategy_total) * 100
            percent_str = f"{percentage:.1f}%"
        else:
            percent_str = "N/A"
        
        days_str = str(int(position['days_active'])) if position['days_active'] else "N/A"
        return_str = f"{position['net_return']:.2f}%" if position['net_return'] else "N/A"
        
        # Create simplified slider for rightmost column
        slider_str = self._create_simple_slider(position)
        
        # Truncate position name to fit
        pos_name = (position['token_pair'][:20] if position['token_pair'] 
                   else position['position_details'][:20])
        platform = position['platform'][:10]
        
        # Apply highlighting for out of range positions
        if range_status.startswith('out_of_range'):
            # White background, black text for out of range
            line = f"{pos_name:<20} {entry_str:<10} {percent_str:<5} {chain_str:<6} {platform:<10} {min_str:<10} {price_str:<10} {max_str:<10} {status_text:<12} {days_str:<5} {return_str:<8} {slider_str}"
            print(f"\033[47m\033[30m{line}\033[0m")
        else:
            print(f"{pos_name:<20} {entry_str:<10} {percent_str:<5} {chain_str:<6} {platform:<10} {min_str:<10} {price_str:<10} {max_str:<10} {status_text:<12} {days_str:<5} {return_str:<8} {slider_str}")
    
    def _create_simple_slider(self, position):
        """Create a simple visual slider for the rightmost column"""
        current_price = position.get('current_price', 0)
        min_range = position.get('min_range')
        max_range = position.get('max_range')
        
        # Return dash if no range data
        if not min_range or not max_range:
            return "───────────"
        
        if current_price:
            # Calculate position on slider (0-1, can be outside bounds)
            price_ratio = (current_price - min_range) / (max_range - min_range)
            
            # Create 11-character slider
            slider_length = 11
            slider = ['─'] * slider_length
            slider[0] = '├'  # Left bound
            slider[-1] = '┤'  # Right bound
            
            # Position indicator
            if price_ratio <= 0:
                # Below range
                slider[0] = '◄'
                overshoot = abs(price_ratio) * 100
                if overshoot > 50:
                    slider[0] = '⮘'  # Far below
            elif price_ratio >= 1:
                # Above range
                slider[-1] = '►'
                overshoot = (price_ratio - 1) * 100
                if overshoot > 50:
                    slider[-1] = '⮚'  # Far above
            else:
                # Within range
                position_index = int(price_ratio * (slider_length - 1))
                position_index = max(1, min(slider_length - 2, position_index))  # Keep within bounds
                slider[position_index] = '●'
            
            return ''.join(slider)
        else:
            return "├─────────┤"
    
    def _create_price_slider(self, position):
        """Create a visual slider showing current price within min/max range with price details"""
        current_price = position.get('current_price', 0)
        min_range = position.get('min_range')
        max_range = position.get('max_range')
        
        # Return dash if no range data
        if not min_range or not max_range:
            return "Range: N/A | Current: N/A"
        
        # Format prices with exactly 2 decimal places
        def format_price(price):
            return f"${price:.2f}"
        
        min_str = format_price(min_range)
        max_str = format_price(max_range)
        current_str = format_price(current_price) if current_price else "N/A"
        
        # Create slider if we have current price
        if current_price:
            # Calculate position on slider (0-1, can be outside bounds)
            price_ratio = (current_price - min_range) / (max_range - min_range)
            
            # Create 12-character slider
            slider_length = 12
            slider = ['─'] * slider_length
            slider[0] = '├'  # Left bound
            slider[-1] = '┤'  # Right bound
            
            # Position indicator
            if price_ratio <= 0:
                # Below range - show how far below
                slider[0] = '◄'
                overshoot = abs(price_ratio) * 100
                if overshoot > 50:
                    slider[0] = '⮘'  # Far below
            elif price_ratio >= 1:
                # Above range - show how far above
                slider[-1] = '►'
                overshoot = (price_ratio - 1) * 100
                if overshoot > 50:
                    slider[-1] = '⮚'  # Far above
            else:
                # Within range
                position_index = int(price_ratio * (slider_length - 1))
                position_index = max(1, min(slider_length - 2, position_index))  # Keep within bounds
                slider[position_index] = '●'
            
            slider_str = ''.join(slider)
            return f"{min_str} {slider_str} {max_str} | {current_str}"
        else:
            return f"{min_str} ─────────── {max_str} | No Price"
    
    
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
        print("-" * 153)
        
        # Detailed table
        print(f"{'Position':<25} {'Entry USD':<10} {'%':<5} {'Chain':<6} {'Platform':<12} {'Min Range':<10} {'Price':<10} {'Max Range':<10} {'Status':<20} {'Days':<5} {'Return':<8} {'Range Slider'}")
        print("-" * 153)
        
        # Sort by range status (out of range first)
        sorted_positions = sorted(positions, key=lambda x: (
            0 if x['range_status'].startswith('out_of_range') else 1
        ))
        
        for position in sorted_positions:
            current_price = position.get('current_price', 0)
            range_status = position.get('range_status', 'unknown')
            min_range = position.get('min_range')
            max_range = position.get('max_range')
            
            # Status indicators with range details
            if range_status == 'in_range':
                status_str = 'Active'
            elif range_status == 'out_of_range_low':
                if current_price and min_range:
                    pct_below = ((min_range - current_price) / min_range) * 100
                    status_str = f'Out of Range -{pct_below:.2f}%'
                else:
                    status_str = 'Out of Range (Low)'
            elif range_status == 'out_of_range_high':
                if current_price and max_range:
                    pct_above = ((current_price - max_range) / max_range) * 100
                    status_str = f'Out of Range +{pct_above:.2f}%'
                else:
                    status_str = 'Out of Range (High)'
            elif range_status == 'perp_active':
                status_str = 'Active (Perp)'
            elif range_status == 'perp_closed':
                if current_price and max_range:
                    pct_above = ((current_price - max_range) / max_range) * 100
                    status_str = f'Closed +{pct_above:.2f}%'
                else:
                    status_str = 'Closed (Liquidated)'
            elif range_status == 'no_range':
                status_str = 'Unknown'
            else:
                status_str = 'Unknown'
            
            # Format price values consistently with 2 decimal places
            def format_price_detail(price):
                if not price:
                    return "N/A"
                else:
                    return f"${price:.2f}"
            
            current_str = format_price_detail(current_price)
            min_str = format_price_detail(min_range)
            max_str = format_price_detail(max_range)
            entry_value = position.get('entry_value', 0)
            chain = position.get('chain', 'Unknown')
            
            entry_str = f"${entry_value:,.0f}" if entry_value else "N/A"
            chain_str = chain[:6]  # Truncate to fit column
            
            # Calculate percentage of strategy total
            if entry_value and total_value and total_value > 0:
                percentage = (entry_value / total_value) * 100
                percent_str = f"{percentage:.1f}%"
            else:
                percent_str = "N/A"
            
            days_str = str(int(position['days_active'])) if position['days_active'] else "N/A"
            return_str = f"{position['net_return']:.2f}%" if position['net_return'] else "N/A"
            
            # Create slider for detailed view
            slider_str = self._create_simple_slider(position)
            
            # Truncate long names
            pos_name = position['token_pair'][:25] if position['token_pair'] else position['position_details'][:25]
            platform = position['platform'][:12]
            
            # Apply highlighting for out of range positions
            if range_status.startswith('out_of_range'):
                # White background, black text for out of range
                line = f"{pos_name:<25} {entry_str:<10} {percent_str:<5} {chain_str:<6} {platform:<12} {min_str:<10} {current_str:<10} {max_str:<10} {status_str:<20} {days_str:<5} {return_str:<8} {slider_str}"
                print(f"\033[47m\033[30m{line}\033[0m")
            else:
                print(f"{pos_name:<25} {entry_str:<10} {percent_str:<5} {chain_str:<6} {platform:<12} {min_str:<10} {current_str:<10} {max_str:<10} {status_str:<20} {days_str:<5} {return_str:<8} {slider_str}")
    
    def _display_token_returns(self):
        """Display token returns table for key portfolio tokens"""
        print("\n\n" + "="*120)
        print("📈 TOKEN PERFORMANCE - KEY HOLDINGS")
        print("="*120)
        
        # Define specific tokens to display
        target_tokens = ['BTC', 'ETH', 'SOL', 'SUI', 'JLP', 'USD/CAD']
        
        # Get demo returns data for these tokens
        returns_data = self._get_filtered_returns_data(target_tokens)
        
        # Display the returns table
        self._display_filtered_returns_table(returns_data)
    
    def _get_filtered_returns_data(self, tokens):
        """Get returns data for specific tokens"""
        demo_data = {
            'BTC': {'1D': 2, '7D': -1, '30D': 15, '90D': 45, '180D': 22, '365D': 120, '3YR': 180, '5YR': 320},
            'ETH': {'1D': 3, '7D': 8, '30D': 12, '90D': 35, '180D': 18, '365D': 85, '3YR': 150, '5YR': 280},
            'SOL': {'1D': 5, '7D': -12, '30D': 25, '90D': 180, '180D': 95, '365D': 420, '3YR': 850, '5YR': 1200},
            'SUI': {'1D': 12, '7D': -8, '30D': 35, '90D': 125, '180D': 200, '365D': 380, '3YR': 650, '5YR': 950},
            'JLP': {'1D': 1, '7D': 3, '30D': 8, '90D': 22, '180D': 45, '365D': 85, '3YR': 180, '5YR': 320},
            'USD/CAD': {'1D': 0, '7D': 1, '30D': -2, '90D': 3, '180D': -1, '365D': 5, '3YR': -8, '5YR': 12}
        }
        
        return {token: demo_data.get(token, {}) for token in tokens if token in demo_data}
    
    def _display_filtered_returns_table(self, returns_data):
        """Display the filtered returns table with increased spacing"""
        if not returns_data:
            print("❌ No returns data available")
            return
        
        # Table header with increased spacing
        print(f"\n{'Token':<8}   {'1D':<6}   {'7D':<6}   {'30D':<7}   {'90D':<7}   {'180D':<8}   {'365D':<8}   {'3YR':<7}   {'5YR':<7}")
        print("-" * 88)
        
        # Display crypto tokens first
        crypto_tokens = [token for token in returns_data.keys() if token != 'USD/CAD']
        for token in sorted(crypto_tokens):
            self._print_token_return_row(token, returns_data[token])
        
        # Separator and FX token
        if 'USD/CAD' in returns_data:
            print("-" * 88)
            self._print_token_return_row('USD/CAD', returns_data['USD/CAD'])
        
        # Get last price update timestamp from data manager
        last_update = getattr(self.data_manager, 'last_price_update', None)
        if last_update:
            timestamp_str = last_update.strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp_str = 'current session'
            
        print(f"\n🕐 Performance data as of {timestamp_str}")
        
        # Add price refresh timestamp at the bottom
        print(f"\n💰 Prices last refreshed: {timestamp_str}")
    
    def _print_token_return_row(self, token, returns):
        """Print a single token row with increased spacing"""
        row = f"{token:<8}"
        
        timeframes = ['1D', '7D', '30D', '90D', '180D', '365D', '3YR', '5YR']
        spacings = [6, 6, 7, 7, 8, 8, 7, 7]  # Increased spacing for each column
        
        for i, timeframe in enumerate(timeframes):
            return_val = returns.get(timeframe)
            spacing = spacings[i]
            
            if return_val is None:
                cell = "N/A"
            else:
                # Format as integer percentage
                if return_val >= 0:
                    cell = f"+{return_val}%"
                else:
                    cell = f"{return_val}%"
                    
            row += f"   {cell:<{spacing}}"
                
        print(row)