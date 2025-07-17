#!/usr/bin/env python3
"""
Performance View - Combined historical returns and token performance analysis
"""

import statistics
from datetime import datetime, timedelta

class PerformanceView:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def display(self):
        """Display comprehensive performance analysis"""
        print("\n" + "="*100)
        print("📈 PERFORMANCE ANALYSIS")
        print("="*100)
        
        # Get position data
        closed_positions = self.data_manager.get_positions_by_strategy('closed')
        active_positions = self.data_manager.get_all_active_positions()
        
        if not closed_positions and not active_positions:
            print("📊 No position data available for analysis.")
            return
        
        # Performance summary
        self._display_performance_summary(closed_positions, active_positions)
        
        # Strategy comparison
        self._display_strategy_comparison(closed_positions, active_positions)
        
        # Platform performance
        self._display_platform_performance(closed_positions, active_positions)
        
        # Token performance section
        self._display_token_performance()
        
        print("\n💡 This view analyzes completed and ongoing positions to identify patterns and opportunities.")
    
    def _display_performance_summary(self, closed_positions, active_positions):
        """Display overall performance metrics"""
        print("\n📊 PERFORMANCE SUMMARY")
        print("-" * 50)
        
        # Closed positions stats
        if closed_positions:
            closed_returns = [p['net_return'] for p in closed_positions if p['net_return'] is not None]
            if closed_returns:
                avg_closed = statistics.mean(closed_returns)
                median_closed = statistics.median(closed_returns)
                best_closed = max(closed_returns)
                worst_closed = min(closed_returns)
                
                print(f"🏁 Closed Positions ({len(closed_positions)}):")
                print(f"   Average Return: {avg_closed:.1f}%")
                print(f"   Median Return:  {median_closed:.1f}%")
                print(f"   Best Return:    {best_closed:.1f}%")
                print(f"   Worst Return:   {worst_closed:.1f}%")
        
        # Active positions stats
        if active_positions:
            active_returns = [p['net_return'] for p in active_positions if p['net_return'] is not None]
            if active_returns:
                avg_active = statistics.mean(active_returns)
                median_active = statistics.median(active_returns)
                
                print(f"\n🔄 Active Positions ({len(active_positions)}):")
                print(f"   Current Avg Return: {avg_active:.1f}%")
                print(f"   Current Median:     {median_active:.1f}%")
    
    def _display_strategy_comparison(self, closed_positions, active_positions):
        """Compare long vs neutral strategy performance"""
        print("\n⚖️  STRATEGY COMPARISON")
        print("-" * 50)
        
        all_positions = closed_positions + active_positions
        
        # Group by strategy
        long_positions = [p for p in all_positions if p['strategy'] == 'long']
        neutral_positions = [p for p in all_positions if p['strategy'] == 'neutral']
        
        for strategy, positions in [('Long', long_positions), ('Neutral', neutral_positions)]:
            if positions:
                returns = [p['net_return'] for p in positions if p['net_return'] is not None]
                total_value = sum([p['entry_value'] for p in positions if p['entry_value']])
                
                if returns:
                    avg_return = statistics.mean(returns)
                    win_rate = len([r for r in returns if r > 0]) / len(returns) * 100
                    
                    print(f"📈 {strategy} Strategy ({len(positions)} positions):")
                    print(f"   Total Entry Value: ${total_value:,.0f}")
                    print(f"   Average Return:    {avg_return:.1f}%")
                    print(f"   Win Rate:          {win_rate:.0f}%")
                    print()
    
    def _display_platform_performance(self, closed_positions, active_positions):
        """Analyze performance by platform"""
        print("\n🏪 PLATFORM PERFORMANCE")
        print("-" * 50)
        
        all_positions = closed_positions + active_positions
        
        # Group by platform
        platforms = {}
        for position in all_positions:
            platform = position.get('platform', 'Unknown')
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(position)
        
        for platform, positions in sorted(platforms.items()):
            if len(positions) > 1:  # Only show platforms with multiple positions
                returns = [p['net_return'] for p in positions if p['net_return'] is not None]
                total_value = sum([p['entry_value'] for p in positions if p['entry_value']])
                
                if returns:
                    avg_return = statistics.mean(returns)
                    win_rate = len([r for r in returns if r > 0]) / len(returns) * 100
                    
                    print(f"🏪 {platform} ({len(positions)} positions):")
                    print(f"   Total Entry Value: ${total_value:,.0f}")
                    print(f"   Average Return:    {avg_return:.1f}%")
                    print(f"   Win Rate:          {win_rate:.0f}%")
                    print()
    
    def _display_token_performance(self):
        """Display current token performance"""
        print("\n💰 TOKEN PERFORMANCE")
        print("-" * 50)
        
        # Get tokens from positions
        tokens = self._get_portfolio_tokens()
        
        if not tokens:
            print("❌ No tokens found in portfolio")
            return
        
        # Display token prices and changes
        prices = self.data_manager.prices
        price_changes = self.data_manager.price_changes
        
        print("┌────────┬──────────┬──────────┐")
        print("│ Token  │ Price    │ 24h      │")
        print("├────────┼──────────┼──────────┤")
        
        for token in sorted(tokens):
            price = prices.get(token, 0)
            change = price_changes.get(token, 0)
            
            # Format price based on value
            if price >= 1000:
                price_str = f"${price:,.0f}"
            elif price >= 1:
                price_str = f"${price:.2f}"
            else:
                price_str = f"${price:.4f}"
            
            # Format change with color indicator
            if change > 0:
                change_str = f"+{change:.1f}%"
            else:
                change_str = f"{change:.1f}%"
            
            print(f"│ {token:<6} │ {price_str:>8} │ {change_str:>8} │")
        
        print("└────────┴──────────┴──────────┘")
    
    def _get_portfolio_tokens(self):
        """Get all unique tokens from portfolio"""
        tokens = set()
        
        for position in self.data_manager.get_all_active_positions():
            if position.get('token_pair'):
                pair = position['token_pair'].replace(' ', '')
                if '/' in pair:
                    token_a, token_b = pair.split('/')
                    tokens.add(token_a.upper())
                    tokens.add(token_b.upper())
        
        return sorted(list(tokens))