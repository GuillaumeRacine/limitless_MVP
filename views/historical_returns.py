#!/usr/bin/env python3
"""
Historical Returns View - Job to be done: Analyze performance across time periods and strategies
"""

from datetime import datetime, timedelta
import statistics

class HistoricalReturnsView:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def display(self):
        """Display historical returns analysis"""
        print("\n" + "="*100)
        print("📈 HISTORICAL RETURNS")
        print("="*100)
        
        # Get closed positions for historical analysis
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
        
        # Best and worst performers
        self._display_top_performers(closed_positions)
        
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
        platform_stats = {}
        for position in all_positions:
            platform = position['platform']
            if platform not in platform_stats:
                platform_stats[platform] = {
                    'positions': [],
                    'total_value': 0,
                    'returns': []
                }
            
            platform_stats[platform]['positions'].append(position)
            if position['entry_value']:
                platform_stats[platform]['total_value'] += position['entry_value']
            if position['net_return'] is not None:
                platform_stats[platform]['returns'].append(position['net_return'])
        
        # Display platform stats
        for platform, stats in sorted(platform_stats.items(), 
                                     key=lambda x: len(x[1]['positions']), 
                                     reverse=True):
            if stats['returns']:
                avg_return = statistics.mean(stats['returns'])
                count = len(stats['positions'])
                total_value = stats['total_value']
                
                print(f"🏢 {platform} ({count} positions):")
                print(f"   Total Value: ${total_value:,.0f}")
                print(f"   Avg Return:  {avg_return:.1f}%")
                print()
    
    def _display_top_performers(self, closed_positions):
        """Show best and worst performing closed positions"""
        if not closed_positions:
            return
            
        print("\n🏆 TOP PERFORMERS (Closed Positions)")
        print("-" * 50)
        
        # Filter positions with returns
        positions_with_returns = [p for p in closed_positions if p['net_return'] is not None]
        
        if len(positions_with_returns) >= 3:
            # Best performers
            best = sorted(positions_with_returns, key=lambda x: x['net_return'], reverse=True)[:3]
            print("🥇 Best Performers:")
            for i, pos in enumerate(best, 1):
                print(f"   {i}. {pos['token_pair']} ({pos['platform']}): {pos['net_return']:.1f}%")
            
            # Worst performers
            worst = sorted(positions_with_returns, key=lambda x: x['net_return'])[:3]
            print("\n🔻 Worst Performers:")
            for i, pos in enumerate(worst, 1):
                print(f"   {i}. {pos['token_pair']} ({pos['platform']}): {pos['net_return']:.1f}%")
        
        print(f"\n📊 Analysis based on {len(positions_with_returns)} closed positions with return data.")