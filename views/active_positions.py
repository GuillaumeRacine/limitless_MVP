#!/usr/bin/env python3
"""
Active Positions View - Job to be done: Monitor active CLM positions and range status
Split by strategy: Long and Neutral are separate businesses
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

class ActivePositionsView:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def display(self):
        """Display active positions with improved formatting for large terminal"""
        # Get all position data
        long_positions = self.data_manager.get_positions_by_strategy('long')
        neutral_positions = self.data_manager.get_positions_by_strategy('neutral')
        
        # Sort positions by value (highest to lowest)
        long_positions = sorted(long_positions, key=lambda p: p.get('entry_value', 0) or 0, reverse=True)
        neutral_positions = sorted(neutral_positions, key=lambda p: p.get('entry_value', 0) or 0, reverse=True)
        
        # Calculate total portfolio value
        long_value = sum(p.get('entry_value', 0) or 0 for p in long_positions)
        neutral_value = sum(p.get('entry_value', 0) or 0 for p in neutral_positions)
        total_value = long_value + neutral_value
        
        # Calculate percentages for strategy allocation
        long_pct = long_value / total_value * 100 if total_value > 0 else 0
        neutral_pct = neutral_value / total_value * 100 if total_value > 0 else 0
        
        # Get latest prices and FX rates
        prices = self.data_manager.prices
        fx_rates = self.data_manager.fx_rates
        usd_cad_rate = fx_rates.get('USD_CAD', 1.3665)  # Default if not available
        
        # Calculate 24h change (placeholder - replace with actual calculation if available)
        daily_change_pct = 2.4  # Example value
        
        # Display header with portfolio summary (adjusted for full-width terminal)
        print("╔════════════════════════════════════════════════════════════════════════════════════╗")
        print(f"║ 📊 CRYPTO CLM PORTFOLIO DASHBOARD                  ${total_value:,.0f} (+{daily_change_pct:.1f}% 24h) ║")
        
        # Create visual bar for strategy allocation (adjusted for wider display)
        bar_width = 30  # Wider bar for better visibility
        long_bar_width = int((long_pct / 100) * bar_width)
        long_bar = "█" * long_bar_width
        neutral_bar = "░" * (bar_width - long_bar_width)
        bar = f"{long_bar}{neutral_bar}"
        
        print(f"║ Long: {long_pct:.1f}% │{bar}│ Neutral: {neutral_pct:.1f}%   USD/CAD: {usd_cad_rate:.4f} ║")
        print("╚════════════════════════════════════════════════════════════════════════════════════╝")
        print()
        
        # Display Long Strategy positions
        print(f"📈 LONG STRATEGY POSITIONS (${long_value:,.0f})")
        self._display_positions_table(long_positions)
        print()
        
        # Display Neutral Strategy positions
        print(f"⚖️  NEUTRAL STRATEGY POSITIONS (${neutral_value:,.0f})")
        self._display_positions_table(neutral_positions)
        print()
        
        # Display Token Prices and Allocation by Chain
        self._display_token_prices_and_allocation()
        
        # Display last refresh time (but no additional section headers)
        last_refresh = getattr(self.data_manager, 'last_price_update', datetime.now())
        print(f"\n🕐 Last refreshed: {last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
        
    def _display_positions_table(self, positions):
        """Display a table of positions with improved formatting for large terminal"""
        if not positions:
            print("  No positions found")
            return
        
        # Print table header (adjusted width for better alignment)
        print("┌────────────┬─────────┬─────┬────────┬──────────┬───────────┬────────────────┬───────────┐")
        print("│ Position   │ Value   │ %   │ Chain  │ Platform │ Min       │ Range Slider   │ Max       │")
        print("├────────────┼─────────┼─────┼────────┼──────────┼───────────┼────────────────┼───────────┤")
        
        # Calculate total value for percentage calculation
        total_value = sum(p.get('entry_value', 0) or 0 for p in positions)
        
        # Print each position
        for position in positions:
            # Extract position details
            position_name = self._format_position_name(position.get('token_pair', 'Unknown'))
            entry_value = position.get('entry_value', 0) or 0
            percentage = (entry_value / total_value * 100) if total_value > 0 else 0
            chain = position.get('chain', 'Unknown')
            platform = position.get('platform', 'Unknown')
            min_range = position.get('min_range')
            max_range = position.get('max_range')
            current_price = position.get('current_price')
            range_status = position.get('range_status', 'unknown')
            
            # Generate range slider based on current price and range
            range_slider = self._generate_range_slider(current_price, min_range, max_range, range_status)
            
            # Format the values for display
            value_fmt = f"${entry_value:,.0f}"
            pct_fmt = f"{percentage:.0f}%"
            min_fmt = f"${min_range:.2f}" if min_range is not None else "N/A"
            max_fmt = f"${max_range:.2f}" if max_range is not None else "N/A"
            
            # Truncate strings to fit in columns
            position_name = position_name[:10]
            chain = chain[:6]
            platform = platform[:8]
            
            # Print the row with proper alignment and wider slider column
            print(f"│ {position_name:<10} │ {value_fmt:>7} │ {pct_fmt:>3} │ {chain:<6} │ {platform:<8} │ {min_fmt:>9} │ {range_slider:^14} │ {max_fmt:>9} │")
        
        # Print table footer
        print("└────────────┴─────────┴─────┴────────┴──────────┴───────────┴────────────────┴───────────┘")
    
    def _format_position_name(self, token_pair):
        """Format the position name for display"""
        if not token_pair:
            return "Unknown"
        
        # Standardize token pair format
        if "/" in token_pair:
            return token_pair
        elif "+" in token_pair:
            tokens = token_pair.split("+")
            return f"{tokens[0].strip()}/USD"
        else:
            return token_pair
    
    def _generate_range_slider(self, current_price, min_range, max_range, range_status):
        """Generate a visual range slider based on current price and range"""
        # Handle positions without ranges
        if min_range is None or max_range is None:
            return "Market Order"
        
        # Handle current price missing
        if current_price is None:
            return "├──────?──────┤"
        
        # Generate slider based on price position relative to range
        if range_status == 'out_of_range_low':
            return "🚨●┤────────────├"
        elif range_status == 'out_of_range_high':
            return "├────────────┤●🚨"
        elif range_status == 'no_range':
            return "Market Order"
        elif range_status == 'in_range':
            # Calculate position within range
            range_width = max_range - min_range
            if range_width <= 0:
                position_ratio = 0.5  # Default to middle if range is invalid
            else:
                position_ratio = (current_price - min_range) / range_width
                position_ratio = max(0, min(1, position_ratio))  # Clamp between 0 and 1
            
            # Create slider with position indicator (wider for better visibility)
            slider_positions = 14  # Total width of slider
            position_index = int(position_ratio * (slider_positions - 3)) + 1
            
            slider = ['─'] * slider_positions
            slider[0] = '├'
            slider[-1] = '┤'
            slider[position_index] = '●'
            
            return ''.join(slider)
        else:
            # Default case for unknown status
            return "├──────?──────┤"
    
    def _display_token_prices_and_allocation(self):
        """Display token prices and allocation information in a structured format for large terminal"""
        # Get price data
        prices = self.data_manager.prices
        price_changes = self.data_manager.price_changes if hasattr(self.data_manager, 'price_changes') else {}
        
        # Calculate chain allocation
        chain_allocation = self._calculate_chain_allocation()
        
        # Define target tokens for display
        target_tokens = ['BTC', 'ETH', 'SOL', 'SUI', 'JLP', 'USDC']
        
        # Print tables side by side (adjusted for better alignment)
        print("💰 TOKEN PRICES                        📊 ALLOCATION BY CHAIN")
        print("┌────────┬──────────┬──────┐          ┌──────────┬─────┬─────────────────────┐")
        print("│ Token  │ Price    │ 24h  │          │ Chain    │ %   │ Chart               │")
        print("├────────┼──────────┼──────┤          ├──────────┼─────┼─────────────────────┤")
        
        # Determine how many rows to display (max of tokens or chains)
        max_rows = max(len(target_tokens), len(chain_allocation))
        chain_data = list(chain_allocation.items())
        
        # Print rows for each token and chain
        for i in range(max_rows):
            # Token data
            token = target_tokens[i] if i < len(target_tokens) else ""
            price = prices.get(token, 0) if token else 0
            change = price_changes.get(token, 0) if token else 0
            
            # Format price based on value
            if token:
                if price > 1000:
                    price_str = f"${price:,.0f}"
                elif price > 1:
                    price_str = f"${price:.2f}"
                else:
                    price_str = f"${price:.6f}"
                
                # Format 24h change
                change_str = f"{change:+.1f}%" if change else "N/A"
            else:
                price_str = ""
                change_str = ""
                
            # Chain data for this row
            chain_name = chain_data[i][0] if i < len(chain_data) else ""
            chain_pct = chain_data[i][1] if i < len(chain_data) else 0
            
            # Create visual chart for chain allocation (wider for better visibility)
            chart = ""
            if i < len(chain_data):
                chart_width = 20
                bars = int((chain_pct / 100) * chart_width)
                chart = "█" * bars + "░" * (chart_width - bars)
            
            # Format chain percentage
            chain_pct_str = f"{chain_pct:.0f}%" if i < len(chain_data) else ""
            
            # Print token and chain rows with proper alignment
            token_part = f"│ {token:<6} │ {price_str:>8} │ {change_str:>4} │" if token else "│        │          │      │"
            
            # Add extra spacing between tables
            if chain_name:
                chain_part = f"          │ {chain_name:<8} │ {chain_pct_str:>3} │ {chart:<19} │"
            else:
                chain_part = "          │          │     │                     │"
            
            print(f"{token_part}{chain_part}")
        
        # Print footer rows
        print("└────────┴──────────┴──────┘          └──────────┴─────┴─────────────────────┘")
    
    def _calculate_chain_allocation(self):
        """Calculate allocation percentages by blockchain"""
        all_positions = self.data_manager.get_all_active_positions()
        total_value = sum(p.get('entry_value', 0) or 0 for p in all_positions)
        
        # Group by chain
        chain_values = {}
        for position in all_positions:
            chain = position.get('chain', 'Unknown')
            entry_value = position.get('entry_value', 0) or 0
            
            if chain not in chain_values:
                chain_values[chain] = 0
            chain_values[chain] += entry_value
        
        # Calculate percentages
        chain_percentages = {}
        for chain, value in chain_values.items():
            percentage = (value / total_value * 100) if total_value > 0 else 0
            chain_percentages[chain] = percentage
        
        # Sort by percentage (descending)
        return dict(sorted(chain_percentages.items(), key=lambda x: x[1], reverse=True))
    
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
                percent_str = f"{percentage:.0f}%"
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
    
    def _create_simple_slider(self, position):
        """Create a simple visual slider for the rightmost column"""
        current_price = position.get('current_price', 0)
        min_range = position.get('min_range')
        max_range = position.get('max_range')
        range_status = position.get('range_status', 'unknown')
        
        # Return dash if no range data
        if not min_range or not max_range or range_status == 'no_range':
            return "Market Order"
        
        if current_price:
            # Calculate position on slider (0-1, can be outside bounds)
            try:
                price_ratio = (current_price - min_range) / (max_range - min_range)
            except:
                price_ratio = 0.5  # Default to middle if calculation fails
            
            # Create slider (wider for better visibility)
            slider_positions = 14
            slider = ['─'] * slider_positions
            slider[0] = '├'
            slider[-1] = '┤'
            
            # Position indicator
            if range_status == 'out_of_range_low':
                # Below range
                return "🚨●┤────────────├"
            elif range_status == 'out_of_range_high':
                # Above range
                return "├────────────┤●🚨"
            elif price_ratio <= 0:
                # Near below range
                slider[0] = '⚠'
                return ''.join(slider)
            elif price_ratio >= 1:
                # Near above range
                slider[-1] = '⚠'
                return ''.join(slider)
            else:
                # Within range
                position_index = int(price_ratio * (slider_positions - 3)) + 1
                position_index = max(1, min(slider_positions - 2, position_index))  # Keep within bounds
                slider[position_index] = '●'
                return ''.join(slider)
        else:
            return "├──────?──────┤"