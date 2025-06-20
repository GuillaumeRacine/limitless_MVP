#!/usr/bin/env python3
"""
Allocation Breakdown View - Detailed breakdown of portfolio allocation by strategy
"""

class AllocationBreakdownView:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def display(self):
        """Display detailed allocation breakdown for both strategies"""
        long_positions = self.data_manager.get_positions_by_strategy('long')
        neutral_positions = self.data_manager.get_positions_by_strategy('neutral')
        
        print("\n" + "="*120)
        print("💼 PORTFOLIO ALLOCATION BREAKDOWN")
        print("="*120)
        
        # Display Long Strategy Breakdown
        if long_positions:
            print(f"\n📈 LONG STRATEGY ALLOCATION")
            print("-" * 80)
            self._display_strategy_breakdown(long_positions)
        else:
            print(f"\n📈 LONG STRATEGY ALLOCATION")
            print("-" * 80)
            print("📊 No active long positions")
        
        print("\n")
        
        # Display Neutral Strategy Breakdown
        if neutral_positions:
            print(f"\n⚖️  NEUTRAL STRATEGY ALLOCATION")
            print("-" * 80)
            self._display_strategy_breakdown(neutral_positions)
        else:
            print(f"\n⚖️  NEUTRAL STRATEGY ALLOCATION")
            print("-" * 80)
            print("📊 No active neutral positions")
    
    def _display_strategy_breakdown(self, positions):
        """Display detailed allocation breakdown for a single strategy"""
        # Calculate total USD value
        total_usd = sum([p['entry_value'] for p in positions if p['entry_value']])
        
        if total_usd == 0:
            print("💰 Total USD Value: $0")
            return
        
        # Calculate allocations
        chain_allocation = {}
        platform_allocation = {}
        token_allocation = {}
        
        for position in positions:
            entry_value = position['entry_value'] or 0
            
            # Chain allocation
            chain = position['chain']
            chain_allocation[chain] = chain_allocation.get(chain, 0) + entry_value
            
            # Platform allocation  
            platform = position['platform']
            platform_allocation[platform] = platform_allocation.get(platform, 0) + entry_value
            
            # Token allocation (50/50 split for CLM pairs)
            if position['token_pair'] and '/' in position['token_pair']:
                tokens = position['token_pair'].split('/')
                token_a = tokens[0].strip().upper()
                token_b = tokens[1].strip().upper()
                
                # 50/50 allocation for each token in the pair
                token_value = entry_value / 2
                token_allocation[token_a] = token_allocation.get(token_a, 0) + token_value
                token_allocation[token_b] = token_allocation.get(token_b, 0) + token_value
        
        print(f"💰 Total USD Value: ${total_usd:,.0f}")
        print()
        
        # Display Chain Breakdown Table
        print("🔗 ALLOCATION BY CHAIN:")
        print(f"{'Chain':<20} {'USD Value':<15} {'Percentage':<10}")
        print("-" * 45)
        sorted_chains = sorted(chain_allocation.items(), key=lambda x: x[1], reverse=True)
        for chain, value in sorted_chains:
            percentage = (value / total_usd * 100)
            print(f"{chain:<20} ${value:>12,.0f} {percentage:>8.1f}%")
        
        print()
        
        # Display Platform Breakdown Table
        print("🏛️  ALLOCATION BY PLATFORM:")
        print(f"{'Platform':<20} {'USD Value':<15} {'Percentage':<10}")
        print("-" * 45)
        sorted_platforms = sorted(platform_allocation.items(), key=lambda x: x[1], reverse=True)
        for platform, value in sorted_platforms:
            percentage = (value / total_usd * 100)
            print(f"{platform:<20} ${value:>12,.0f} {percentage:>8.1f}%")
        
        print()
        
        # Display Token Breakdown Table
        print("🪙 ALLOCATION BY TOKEN (50/50 CLM Split):")
        print(f"{'Token':<20} {'USD Value':<15} {'Percentage':<10}")
        print("-" * 45)
        sorted_tokens = sorted(token_allocation.items(), key=lambda x: x[1], reverse=True)
        for token, value in sorted_tokens:
            percentage = (value / total_usd * 100)
            print(f"{token:<20} ${value:>12,.0f} {percentage:>8.1f}%")