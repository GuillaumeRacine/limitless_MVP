#!/usr/bin/env python3
"""
Market Analysis View - DefiLlama Integration
"""

import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.defillama_client import DefiLlamaClient
from utils.formatting import format_currency, format_percentage, format_number_short
from utils.nlp_query import SmartDeFiLlamaQuery

class MarketAnalysisView:
    def __init__(self):
        self.client = DefiLlamaClient()
        self.smart_query = SmartDeFiLlamaQuery(self.client)
        
        # Default chains to track
        self.tracked_chains = [
            'Solana', 'Ethereum', 'Sui', 'Base', 'Arbitrum', 
            'Polygon', 'Avalanche', 'BSC', 'Optimism'
        ]
        
        # Chain display names and colors
        self.chain_info = {
            'Solana': {'symbol': 'SOL', 'color': '🟣'},
            'Ethereum': {'symbol': 'ETH', 'color': '🔵'},
            'Sui': {'symbol': 'SUI', 'color': '💙'},
            'Base': {'symbol': 'BASE', 'color': '🔷'},
            'Arbitrum': {'symbol': 'ARB', 'color': '🔵'},
            'Polygon': {'symbol': 'MATIC', 'color': '🟪'},
            'Avalanche': {'symbol': 'AVAX', 'color': '🔴'},
            'BSC': {'symbol': 'BNB', 'color': '🟡'},
            'Optimism': {'symbol': 'OP', 'color': '🔴'}
        }
    
    def display(self):
        """Main market analysis dashboard"""
        print("\033[2J\033[H")  # Clear screen
        
        print("="*120)
        print("📊 MARKET ANALYSIS - DEFI LANDSCAPE")
        print("="*120)
        
        # Main menu
        while True:
            print("\n📋 Market Analysis Options:")
            print("   [1] Chain Overview Dashboard")
            print("   [2] Monthly Chain Statistics")
            print("   [3] Yield Opportunities Scanner")
            print("   [4] Protocol Deep Dive")
            print("   [5] Custom DefiLlama Query")
            print("   [6] Real-time Market Monitor")
            print("   [7] 🤖 Natural Language Query (Ask anything!)")
            print("   [q] Return to main menu")
            
            choice = input("\nSelect option: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '1':
                self.display_chain_overview()
            elif choice == '2':
                self.display_monthly_stats()
            elif choice == '3':
                self.display_yield_scanner()
            elif choice == '4':
                self.display_protocol_dive()
            elif choice == '5':
                self.display_custom_query()
            elif choice == '6':
                self.display_market_monitor()
            elif choice == '7':
                self.display_natural_language_query()
            else:
                print("❌ Invalid choice")
                continue
            
            input("\nPress Enter to return to market analysis menu...")
    
    def display_chain_overview(self):
        """Display overview of all tracked chains"""
        print("\n" + "="*120)
        print("🌍 MULTI-CHAIN TVL OVERVIEW")
        print("="*120)
        
        print("🔄 Fetching current TVL data...")
        tvl_data = self.client.get_current_tvl()
        
        if not tvl_data:
            print("❌ Failed to fetch TVL data")
            return
        
        # Filter for tracked chains
        tracked_data = []
        for chain_data in tvl_data:
            chain_name = chain_data.get('name', '')
            if chain_name in self.tracked_chains:
                tracked_data.append(chain_data)
        
        # Sort by TVL
        tracked_data.sort(key=lambda x: x.get('tvl', 0), reverse=True)
        
        # Display table
        print(f"\n{'Chain':<12} {'Symbol':<8} {'TVL':<15} {'1D Change':<12} {'7D Change':<12} {'30D Change':<12} {'Protocols':<10}")
        print("-" * 100)
        
        for chain_data in tracked_data:
            chain_name = chain_data.get('name', 'Unknown')
            info = self.chain_info.get(chain_name, {'symbol': '???', 'color': '⚪'})
            
            tvl = chain_data.get('tvl', 0)
            change_1d = ((tvl / chain_data.get('tvlPrevDay', tvl)) - 1) * 100 if chain_data.get('tvlPrevDay') else 0
            change_7d = ((tvl / chain_data.get('tvlPrevWeek', tvl)) - 1) * 100 if chain_data.get('tvlPrevWeek') else 0
            change_30d = ((tvl / chain_data.get('tvlPrevMonth', tvl)) - 1) * 100 if chain_data.get('tvlPrevMonth') else 0
            
            protocols = chain_data.get('protocols', 0)
            
            # Color coding for changes
            def format_change(change):
                if change > 0:
                    return f"🟢 +{change:.1f}%"
                elif change < 0:
                    return f"🔴 {change:.1f}%"
                else:
                    return f"⚪ {change:.1f}%"
            
            print(f"{info['color']} {chain_name:<10} {info['symbol']:<8} "
                  f"${format_number_short(tvl):<14} "
                  f"{format_change(change_1d):<15} "
                  f"{format_change(change_7d):<15} "
                  f"{format_change(change_30d):<15} "
                  f"{protocols:<10}")
        
        # Total TVL
        total_tvl = sum(c.get('tvl', 0) for c in tracked_data)
        print(f"\n💰 Total Tracked TVL: ${format_number_short(total_tvl)}")
        print(f"🕐 Data as of: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def display_monthly_stats(self):
        """Display month-by-month statistics for selected chains"""
        print("\n" + "="*120)
        print("📅 MONTHLY CHAIN STATISTICS")
        print("="*120)
        
        # Let user select chains
        print("\nAvailable chains:")
        for i, chain in enumerate(self.tracked_chains, 1):
            info = self.chain_info.get(chain, {'symbol': '???', 'color': '⚪'})
            print(f"   [{i}] {info['color']} {chain} ({info['symbol']})")
        
        chain_choice = input("\nSelect chain number (or 'all' for summary): ").strip()
        
        if chain_choice.lower() == 'all':
            # Show summary for all chains
            print("\n🔄 Fetching monthly data for all chains...")
            for chain in self.tracked_chains[:3]:  # Limit to first 3 to avoid rate limits
                self._display_chain_monthly(chain, months=6)
        else:
            try:
                chain_index = int(chain_choice) - 1
                if 0 <= chain_index < len(self.tracked_chains):
                    selected_chain = self.tracked_chains[chain_index]
                    months = int(input("Number of months to show (default 12): ") or "12")
                    self._display_chain_monthly(selected_chain, months)
                else:
                    print("❌ Invalid chain selection")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def _display_chain_monthly(self, chain: str, months: int = 12):
        """Display monthly statistics for a specific chain"""
        info = self.chain_info.get(chain, {'symbol': '???', 'color': '⚪'})
        print(f"\n{info['color']} {chain.upper()} - MONTHLY BREAKDOWN")
        print("-" * 80)
        
        print(f"🔄 Fetching {months} months of data for {chain}...")
        monthly_stats = self.client.get_monthly_stats(chain, months)
        
        if not monthly_stats:
            print(f"❌ No data available for {chain}")
            return
        
        print(f"\n{'Month':<10} {'Avg TVL':<15} {'Start TVL':<15} {'End TVL':<15} {'Growth':<10}")
        print("-" * 70)
        
        for stat in monthly_stats:
            month = stat['month']
            avg_tvl = stat['avg_tvl']
            start_tvl = stat['start_tvl']
            end_tvl = stat['end_tvl']
            
            growth = ((end_tvl / start_tvl) - 1) * 100 if start_tvl > 0 else 0
            growth_indicator = "🟢" if growth > 0 else "🔴" if growth < 0 else "⚪"
            
            print(f"{month:<10} "
                  f"${format_number_short(avg_tvl):<14} "
                  f"${format_number_short(start_tvl):<14} "
                  f"${format_number_short(end_tvl):<14} "
                  f"{growth_indicator} {growth:+.1f}%")
    
    def display_yield_scanner(self):
        """Scan for best yield opportunities"""
        print("\n" + "="*120)
        print("🎯 YIELD OPPORTUNITIES SCANNER")
        print("="*120)
        
        # Get user preferences
        print("\nFilter options:")
        min_tvl = float(input("Minimum TVL (in millions, default 1): ") or "1") * 1000000
        min_apy = float(input("Minimum APY % (default 5): ") or "5")
        
        chain_filter = input("Chain filter (leave empty for all): ").strip()
        if chain_filter and chain_filter not in self.tracked_chains:
            print(f"⚠️  Chain '{chain_filter}' not in tracked list, showing all chains")
            chain_filter = None
        
        print(f"\n🔄 Scanning pools with TVL > ${format_number_short(min_tvl)} and APY > {min_apy}%...")
        
        pools = self.client.get_pool_yields(chain=chain_filter)
        
        if not pools:
            print("❌ Failed to fetch yield data")
            return
        
        # Filter pools
        filtered_pools = []
        for pool in pools:
            tvl = pool.get('tvlUsd', 0)
            apy = pool.get('apy', 0)
            
            if tvl >= min_tvl and apy >= min_apy:
                filtered_pools.append(pool)
        
        # Sort by APY
        filtered_pools.sort(key=lambda x: x.get('apy', 0), reverse=True)
        
        # Display top opportunities
        print(f"\n🏆 TOP YIELD OPPORTUNITIES ({len(filtered_pools)} found)")
        print(f"{'Protocol':<15} {'Chain':<10} {'Pool':<25} {'APY':<8} {'TVL':<12} {'Risk':<8}")
        print("-" * 90)
        
        for pool in filtered_pools[:20]:  # Top 20
            protocol = pool.get('project', 'Unknown')[:14]
            chain = pool.get('chain', 'Unknown')[:9]
            symbol = pool.get('symbol', 'Unknown')[:24]
            apy = pool.get('apy', 0)
            tvl = pool.get('tvlUsd', 0)
            
            # Simple risk assessment based on TVL and APY
            if tvl > 50000000 and apy < 20:
                risk = "🟢 Low"
            elif tvl > 10000000 and apy < 50:
                risk = "🟡 Med"
            else:
                risk = "🔴 High"
            
            print(f"{protocol:<15} {chain:<10} {symbol:<25} "
                  f"{apy:>6.1f}% ${format_number_short(tvl):>10} {risk}")
        
        if not filtered_pools:
            print("❌ No pools found matching your criteria")
    
    def display_protocol_dive(self):
        """Deep dive into a specific protocol"""
        print("\n" + "="*120)
        print("🔬 PROTOCOL DEEP DIVE")
        print("="*120)
        
        protocol_name = input("\nEnter protocol name to analyze: ").strip()
        
        if not protocol_name:
            print("❌ Protocol name required")
            return
        
        # Search for protocol
        print(f"🔍 Searching for '{protocol_name}'...")
        protocols = self.client.search_protocols(protocol_name)
        
        if not protocols:
            print(f"❌ No protocols found matching '{protocol_name}'")
            return
        
        # Display search results
        if len(protocols) > 1:
            print(f"\n📋 Found {len(protocols)} protocols:")
            for i, protocol in enumerate(protocols[:10], 1):
                print(f"   [{i}] {protocol.get('name', 'Unknown')} - TVL: ${format_number_short(protocol.get('tvl', 0))}")
            
            choice = input("\nSelect protocol number: ").strip()
            try:
                selected = protocols[int(choice) - 1]
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                return
        else:
            selected = protocols[0]
        
        # Get detailed protocol data
        slug = selected.get('slug', '')
        print(f"\n🔄 Fetching detailed data for {selected.get('name', 'Unknown')}...")
        
        protocol_data = self.client.get_protocol_tvl(slug)
        
        if not protocol_data:
            print("❌ Failed to fetch protocol data")
            return
        
        # Display protocol information
        self._display_protocol_details(protocol_data)
    
    def _display_protocol_details(self, protocol_data: dict):
        """Display detailed protocol information"""
        name = protocol_data.get('name', 'Unknown')
        tvl = protocol_data.get('tvl', 0)
        chains = protocol_data.get('chains', [])
        
        print(f"\n📊 {name.upper()} ANALYSIS")
        print("-" * 60)
        print(f"💰 Current TVL: ${format_number_short(tvl)}")
        print(f"⛓️  Active Chains: {', '.join(chains)}")
        
        # Chain breakdown
        chain_tvls = protocol_data.get('chainTvls', {})
        if chain_tvls:
            print(f"\n🌍 Chain Distribution:")
            for chain, chain_tvl in sorted(chain_tvls.items(), key=lambda x: x[1], reverse=True):
                if isinstance(chain_tvl, (int, float)) and chain_tvl > 0:
                    percentage = (chain_tvl / tvl) * 100 if tvl > 0 else 0
                    print(f"   {chain}: ${format_number_short(chain_tvl)} ({percentage:.1f}%)")
        
        # Historical TVL trend
        tvl_history = protocol_data.get('tvl', [])
        if isinstance(tvl_history, list) and len(tvl_history) > 1:
            recent_tvls = tvl_history[-30:]  # Last 30 data points
            if len(recent_tvls) > 1:
                change = ((recent_tvls[-1]['totalLiquidityUSD'] / recent_tvls[0]['totalLiquidityUSD']) - 1) * 100
                trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                print(f"\n📊 Recent Trend: {trend} {change:+.1f}% (30 periods)")
    
    def display_custom_query(self):
        """Interactive DefiLlama query interface"""
        print("\n" + "="*120)
        print("🔧 CUSTOM DEFILLAMA QUERY")
        print("="*120)
        
        print("\nAvailable query types:")
        print("   [1] Search protocols")
        print("   [2] Get chain summary")
        print("   [3] Find best pools for token pair")
        print("   [4] Protocol fees analysis")
        print("   [5] Stablecoin analysis")
        
        query_type = input("\nSelect query type: ").strip()
        
        if query_type == '1':
            self._query_search_protocols()
        elif query_type == '2':
            self._query_chain_summary()
        elif query_type == '3':
            self._query_token_pairs()
        elif query_type == '4':
            self._query_protocol_fees()
        elif query_type == '5':
            self._query_stablecoins()
        else:
            print("❌ Invalid query type")
    
    def _query_search_protocols(self):
        """Search protocols query"""
        query = input("Enter search term: ").strip()
        if not query:
            return
        
        protocols = self.client.search_protocols(query)
        
        print(f"\n🔍 Search results for '{query}':")
        for protocol in protocols[:10]:
            print(f"   📋 {protocol.get('name', 'Unknown')}")
            print(f"      TVL: ${format_number_short(protocol.get('tvl', 0))}")
            print(f"      Chains: {', '.join(protocol.get('chains', []))}")
            print()
    
    def _query_chain_summary(self):
        """Chain summary query"""
        chain = input("Enter chain name: ").strip()
        if not chain:
            return
        
        print(f"🔄 Generating summary for {chain}...")
        summary = self.client.get_chain_summary(chain)
        
        if summary.get('tvl'):
            print(f"\n📊 {chain.upper()} SUMMARY")
            print(f"💰 Current TVL: ${format_number_short(summary['tvl']['current'])}")
            print(f"📈 24h Change: {((summary['tvl']['current'] / summary['tvl']['change_1d']) - 1) * 100:+.1f}%")
            
            if summary['top_pools']:
                print(f"\n🏆 Top Yield Pools:")
                for pool in summary['top_pools'][:5]:
                    print(f"   {pool.get('symbol', 'Unknown')}: {pool.get('apy', 0):.1f}% APY")
    
    def _query_token_pairs(self):
        """Token pair analysis query"""
        token_a = input("Enter first token (e.g., SOL): ").strip().upper()
        token_b = input("Enter second token (e.g., USDC): ").strip().upper()
        
        if not token_a or not token_b:
            return
        
        print(f"🔄 Finding pools for {token_a}/{token_b}...")
        
        # This would use the existing pool search functionality
        pools = self.client.get_pool_yields()
        if pools:
            matching_pools = []
            for pool in pools:
                symbol = pool.get('symbol', '').upper()
                if token_a in symbol and token_b in symbol:
                    matching_pools.append(pool)
            
            if matching_pools:
                print(f"\n💫 Found {len(matching_pools)} {token_a}/{token_b} pools:")
                for pool in sorted(matching_pools, key=lambda x: x.get('apy', 0), reverse=True)[:10]:
                    print(f"   {pool.get('project', 'Unknown')} ({pool.get('chain', 'Unknown')}): "
                          f"{pool.get('apy', 0):.1f}% APY, ${format_number_short(pool.get('tvlUsd', 0))} TVL")
            else:
                print(f"❌ No pools found for {token_a}/{token_b}")
    
    def _query_protocol_fees(self):
        """Protocol fees analysis"""
        print("🔄 Fetching protocol fees overview...")
        fees_data = self.client.get_fees_overview()
        
        if fees_data:
            print(f"\n💰 TOP PROTOCOLS BY FEES (24h)")
            print(f"{'Protocol':<20} {'Fees 24h':<15} {'Revenue 24h':<15}")
            print("-" * 50)
            
            for protocol in fees_data[:15]:
                name = protocol.get('name', 'Unknown')[:19]
                fees_24h = protocol.get('total24h', 0)
                revenue_24h = protocol.get('revenue24h', 0)
                
                print(f"{name:<20} ${format_number_short(fees_24h):<14} ${format_number_short(revenue_24h):<14}")
    
    def _query_stablecoins(self):
        """Stablecoin analysis"""
        print("🔄 Fetching stablecoin data...")
        stablecoins = self.client.get_stablecoins()
        
        if stablecoins and 'peggedAssets' in stablecoins:
            print(f"\n🪙 TOP STABLECOINS BY MARKET CAP")
            print(f"{'Name':<15} {'Symbol':<8} {'Market Cap':<15} {'Price':<8}")
            print("-" * 50)
            
            for coin in stablecoins['peggedAssets'][:10]:
                name = coin.get('name', 'Unknown')[:14]
                symbol = coin.get('symbol', 'Unknown')[:7]
                mcap = coin.get('circulating', {}).get('peggedUSD', 0)
                price = coin.get('price', 1.0)
                
                print(f"{name:<15} {symbol:<8} ${format_number_short(mcap):<14} ${price:.4f}")
    
    def display_market_monitor(self):
        """Real-time market monitoring dashboard"""
        print("\n" + "="*120)
        print("⚡ REAL-TIME MARKET MONITOR")
        print("="*120)
        
        print("🔄 This would show a continuously updating dashboard...")
        print("💡 Features to implement:")
        print("   - Live TVL updates every 30 seconds")
        print("   - Price alerts for tracked tokens")
        print("   - Yield opportunity notifications")
        print("   - Protocol TVL change alerts")
        print("\n⚠️  Real-time monitoring requires continuous API calls")
        print("   Consider rate limiting and API costs")
    
    def display_natural_language_query(self):
        """Natural language interface for DeFiLlama queries"""
        print("\n" + "="*120)
        print("🤖 NATURAL LANGUAGE DEFI QUERY")
        print("="*120)
        
        # Show LLM provider status
        provider = getattr(self.smart_query.llm_enhancer, 'provider', 'local') if self.smart_query.llm_enhancer else 'local'
        if provider == 'openai':
            print("🧠 Enhanced with OpenAI GPT")
        elif provider == 'anthropic':
            print("🧠 Enhanced with Anthropic Claude")
        else:
            print("🏠 Using local pattern matching (fast & reliable)")
        
        print("\n💡 Ask me anything about DeFi! Examples:")
        for example in self.smart_query.example_queries:
            print(f"   • {example}")
        
        print("\n💬 Type 'help' for more examples or 'back' to return")
        
        while True:
            user_query = input("\n🔍 Your question: ").strip()
            
            if user_query.lower() in ['back', 'exit', 'quit']:
                break
            elif user_query.lower() == 'help':
                self._show_query_help()
                continue
            elif not user_query:
                print("❌ Please enter a question")
                continue
            
            try:
                # Process the natural language query
                results = self.smart_query.process_query(user_query)
                
                # Display results based on query type
                self._display_query_results(results)
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                print("💡 Try rephrasing your question or use simpler terms")
    
    def _show_query_help(self):
        """Show detailed help for natural language queries"""
        print("\n📚 QUERY HELP")
        print("-" * 80)
        print("\n🎯 Query Types:")
        print("   • TVL: 'What's the TVL on Solana?', 'Show total value locked'")
        print("   • Yields: 'Best ETH yields', 'Find pools over 20% APY'")
        print("   • Protocols: 'Search for Uniswap', 'Top protocols by TVL'")
        print("   • Fees: 'Protocol fees for Aave', 'Top earning protocols'")
        print("   • Chains: 'Compare chains', 'Arbitrum stats'")
        
        print("\n🔧 Filters you can use:")
        print("   • Chain: 'on Solana', 'on Ethereum', 'on Base'")
        print("   • Min TVL: 'over $10 million', 'above 5m TVL'")
        print("   • Min APY: 'over 15%', 'above 20% APY'")
        print("   • Token pairs: 'ETH/USDC pools', 'SOL-USDT'")
        print("   • Time: 'last week', 'past month', '30 days'")
    
    def _display_query_results(self, results: dict):
        """Display results from natural language query"""
        if 'error' in results:
            print(f"❌ {results['error']}")
            return
        
        # Handle special responses (greetings, help)
        if results.get('special'):
            print(f"\n💬 {results.get('query', 'Response')}")
            print("-" * 80)
            if isinstance(results['results'], dict) and 'message' in results['results']:
                print(results['results']['message'])
            return
        
        print(f"\n✅ {results.get('query', 'Query results')}")
        print("-" * 80)
        
        if 'results' not in results or not results['results']:
            print("❌ No results found")
            return
        
        # Determine result type and display accordingly
        first_result = results['results'][0] if isinstance(results['results'], list) else results['results']
        
        if isinstance(results['results'], dict):
            # Single result (like chain summary)
            self._display_dict_result(results['results'])
        elif 'apy' in first_result:
            # Yield results
            self._display_yield_results(results['results'])
        elif 'tvl' in first_result or 'tvlUsd' in first_result:
            # TVL/Protocol results
            self._display_tvl_results(results['results'])
        elif 'total24h' in first_result:
            # Fees results
            self._display_fees_results(results['results'])
        elif 'peggedUSD' in str(first_result):
            # Stablecoin results
            self._display_stablecoin_results(results['results'])
        else:
            # Generic display
            self._display_generic_results(results['results'])
    
    def _display_yield_results(self, pools):
        """Display yield/pool results in clean format"""
        if not pools:
            print("❌ No yield opportunities found")
            return
            
        print(f"\n🎯 Found {len(pools)} yield opportunities:")
        print(f"\n{'Pool':<30} {'APY':<8} {'TVL':<12} {'Platform':<15}")
        print("-" * 70)
        
        for pool in pools[:10]:  # Show top 10
            symbol = pool.get('symbol', 'Unknown')[:29]
            apy = pool.get('apy', 0)
            tvl = pool.get('tvlUsd', 0)
            protocol = pool.get('project', 'Unknown')[:14]
            
            print(f"{symbol:<30} {apy:>6.1f}% ${format_number_short(tvl):>10} {protocol:<15}")
    
    def _display_tvl_results(self, protocols):
        """Display TVL/protocol results in clean format"""
        if not protocols:
            print("❌ No protocol data found")
            return
            
        print(f"\n📊 Top Protocols by TVL:")
        print(f"\n{'Protocol':<25} {'TVL':<15} {'Category':<15}")
        print("-" * 60)
        
        for protocol in protocols[:8]:  # Show top 8
            name = protocol.get('name', 'Unknown')[:24]
            tvl = protocol.get('tvl', 0)
            category = protocol.get('category', 'DeFi')[:14]
            
            print(f"{name:<25} ${format_number_short(tvl):<14} {category:<15}")
    
    def _display_fees_results(self, fees):
        """Display fees results"""
        print(f"\n{'Protocol':<20} {'24h Fees':<15} {'24h Revenue':<15}")
        print("-" * 50)
        
        for protocol in fees[:15]:
            name = protocol.get('name', 'Unknown')[:19]
            fees_24h = protocol.get('total24h', 0)
            revenue_24h = protocol.get('revenue24h', 0)
            
            print(f"{name:<20} ${format_number_short(fees_24h):<14} ${format_number_short(revenue_24h):<14}")
    
    def _display_stablecoin_results(self, stables):
        """Display stablecoin results"""
        print(f"\n{'Name':<15} {'Symbol':<8} {'Market Cap':<15} {'Price':<8}")
        print("-" * 50)
        
        for coin in stables[:10]:
            name = coin.get('name', 'Unknown')[:14]
            symbol = coin.get('symbol', 'Unknown')[:7]
            mcap = coin.get('circulating', {}).get('peggedUSD', 0)
            price = coin.get('price', 1.0)
            
            print(f"{name:<15} {symbol:<8} ${format_number_short(mcap):<14} ${price:.4f}")
    
    def _display_dict_result(self, result):
        """Display dictionary result (like chain summary) in clean format"""
        if 'tvl' in result and isinstance(result['tvl'], dict):
            # Clean TVL display - only show what was asked for
            current_tvl = result['tvl'].get('current', 0)
            print(f"\n💰 Solana Total Value Locked: ${format_number_short(current_tvl)}")
            
            change_1d = result['tvl'].get('change_1d', 0)
            if change_1d != 0:
                change_symbol = "📈" if change_1d > 0 else "📉"
                print(f"{change_symbol} 24h Change: {change_1d:+.1f}%")
        
        # Show timestamp
        timestamp = result.get('timestamp')
        if timestamp:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            print(f"\n🕐 Data as of: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _display_generic_results(self, results):
        """Generic display for unknown result types"""
        for i, result in enumerate(results[:10], 1):
            print(f"\n{i}. {result.get('name', 'Result')}:")
            for key, value in result.items():
                if key != 'name' and value:
                    print(f"   {key}: {value}")

if __name__ == "__main__":
    view = MarketAnalysisView()
    view.display()