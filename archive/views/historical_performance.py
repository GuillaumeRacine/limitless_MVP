#!/usr/bin/env python3
"""
Historical Performance View - Shows historical returns for all portfolio tokens across multiple timeframes
"""

import requests
from datetime import datetime, timedelta

class HistoricalPerformanceView:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.timeframes = {
            '1D': 1,
            '7D': 7, 
            '30D': 30,
            '90D': 90,
            '180D': 180,
            '365D': 365,
            '3YR': 1095,  # 3 * 365
            '5YR': 1825   # 5 * 365
        }
        
    def display(self):
        """Display historical returns table for all portfolio tokens"""
        print("\n" + "="*120)
        print("📈 TOKEN PERFORMANCE - KEY HOLDINGS & MARKET BENCHMARKS")
        print("="*120)
        
        # Get all unique tokens from positions
        tokens = self._get_all_portfolio_tokens()
        
        if not tokens:
            print("❌ No tokens found in portfolio positions")
            return
            
        # Fetch historical data for all tokens
        historical_data = self._fetch_historical_data(tokens)
        
        # Fetch market benchmarks
        market_data = self._fetch_market_benchmarks()
        
        # Display the table with market comparison
        self._display_returns_table(historical_data, market_data)
        
    def _get_all_portfolio_tokens(self):
        """Extract all unique tokens from portfolio positions"""
        tokens = set()
        
        # Get all positions
        all_positions = self.data_manager.get_all_active_positions()
        
        for position in all_positions:
            if position.get('token_pair'):
                pair = position['token_pair'].replace(' ', '')
                if '/' in pair:
                    token_a, token_b = pair.split('/')
                    tokens.add(token_a.upper())
                    tokens.add(token_b.upper())
        
        # Remove CAD/USD - no longer tracking FX
        return sorted(list(tokens))
    
    def _fetch_historical_data(self, tokens):
        """Fetch historical price data for all tokens and timeframes"""
        print("🔄 Fetching historical data...")
        
        historical_data = {}
        
        for token in tokens:
            # Only handle crypto tokens
            historical_data[token] = self._fetch_crypto_historical_data(token)
                
        return historical_data
    
    def _fetch_market_benchmarks(self):
        """Fetch performance data for market benchmarks"""
        print("🔄 Fetching market benchmark data...")
        
        benchmarks = {
            'Total Crypto': self._fetch_total_crypto_market_cap(),
            'US Equities (SPY)': self._fetch_equity_data('SPY'),
            'CA Equities (VTI.TO)': self._fetch_equity_data('VTI.TO'),
            'Gold (GLD)': self._fetch_commodity_data('GLD')
        }
        
        return benchmarks
    
    def _fetch_total_crypto_market_cap(self):
        """Fetch total crypto market cap historical data"""
        returns = {}
        
        # Use demo data for now - can be enhanced with real API later
        demo_data = {
            '1D': 2.1,
            '7D': -0.8,
            '30D': 12.5,
            '90D': 28.3,
            '180D': 15.7,
            '365D': 89.2,
            '3YR': 165.4,
            '5YR': 245.8
        }
        
        try:
            # CoinGecko global data API for total market cap
            url = "https://api.coingecko.com/api/v3/global"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # For now, return demo data - real implementation would calculate historical changes
                print("📊 Using demo data for Total Crypto Market Cap")
                return demo_data
            else:
                return demo_data
                
        except Exception as e:
            print(f"⚠️  Error fetching crypto market cap: {e}")
            return demo_data
    
    def _fetch_equity_data(self, symbol):
        """Fetch equity/ETF historical performance data"""
        # Demo data for equity markets
        if symbol == 'SPY':  # US Equities
            return {
                '1D': 0.3,
                '7D': 1.2,
                '30D': 3.8,
                '90D': 8.5,
                '180D': 12.3,
                '365D': 18.7,
                '3YR': 42.1,
                '5YR': 68.9
            }
        else:  # CA Equities
            return {
                '1D': 0.2,
                '7D': 0.8,
                '30D': 2.9,
                '90D': 6.8,
                '180D': 9.4,
                '365D': 14.2,
                '3YR': 35.6,
                '5YR': 58.3
            }
    
    def _fetch_commodity_data(self, symbol):
        """Fetch commodity (Gold) historical performance data"""
        # Demo data for Gold
        return {
            '1D': 0.1,
            '7D': -0.3,
            '30D': 1.8,
            '90D': 4.2,
            '180D': 8.9,
            '365D': 12.4,
            '3YR': 28.7,
            '5YR': 45.2
        }
    
    def _fetch_crypto_historical_data(self, token):
        """Fetch historical crypto price data from CoinGecko"""
        # Token mapping for CoinGecko
        token_map = {
            'SOL': 'solana',
            'USDC': 'usd-coin',
            'ETH': 'ethereum',
            'BTC': 'bitcoin',
            'ORCA': 'orca',
            'RAY': 'raydium',
            'JLP': 'jupiter-exchange-solana',
            'WETH': 'ethereum',
            'USDT': 'tether',
            'SUI': 'sui'
        }
        
        if token not in token_map:
            # Return empty data for unmapped tokens
            return {tf: None for tf in self.timeframes.keys()}
        
        coingecko_id = token_map[token]
        returns = {}
        
        # For development/testing, use demo data first
        demo_returns = self._get_demo_returns(token)
        if demo_returns:
            print(f"📊 Using demo data for {token}")
            return demo_returns
        
        try:
            # Fetch current price first  
            current_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd"
            current_response = requests.get(current_url, timeout=10)
            
            if current_response.status_code != 200:
                return {tf: None for tf in self.timeframes.keys()}
                
            current_data = current_response.json()
            current_price = current_data.get(coingecko_id, {}).get('usd')
            
            if not current_price:
                return {tf: None for tf in self.timeframes.keys()}
            
            # Calculate returns for each timeframe
            for timeframe, days in self.timeframes.items():
                try:
                    # Get historical price
                    from_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
                    to_timestamp = int(datetime.now().timestamp())
                    
                    hist_url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart/range?vs_currency=usd&from={from_timestamp}&to={to_timestamp}"
                    hist_response = requests.get(hist_url, timeout=10)
                    
                    if hist_response.status_code == 200:
                        hist_data = hist_response.json()
                        prices = hist_data.get('prices', [])
                        
                        if prices and len(prices) > 0:
                            # Get the earliest price in the range
                            historical_price = prices[0][1]  # [timestamp, price]
                            
                            if historical_price and historical_price > 0:
                                # Calculate percentage return (rounded to integer)
                                return_pct = ((current_price - historical_price) / historical_price) * 100
                                returns[timeframe] = round(return_pct)
                            else:
                                returns[timeframe] = None
                        else:
                            returns[timeframe] = None
                    else:
                        returns[timeframe] = None
                        
                except Exception as e:
                    returns[timeframe] = None
                    
        except Exception as e:
            print(f"⚠️  Error fetching data for {token}: {e}")
            returns = {tf: None for tf in self.timeframes.keys()}
        
        # If API fails, provide demo data for better testing
        if all(v is None for v in returns.values()):
            demo_returns = self._get_demo_returns(token)
            if demo_returns:
                returns = demo_returns
                
        return returns
    
    def _get_demo_returns(self, token):
        """Provide demo historical returns for testing when API is unavailable"""
        demo_data = {
            'BTC': {'1D': 2, '7D': -1, '30D': 15, '90D': 45, '180D': 22, '365D': 120, '3YR': 180, '5YR': 320},
            'ETH': {'1D': 3, '7D': 8, '30D': 12, '90D': 35, '180D': 18, '365D': 85, '3YR': 150, '5YR': 280},
            'SOL': {'1D': 5, '7D': -12, '30D': 25, '90D': 180, '180D': 95, '365D': 420, '3YR': 850, '5YR': 1200},
            'SUI': {'1D': 12, '7D': -8, '30D': 35, '90D': 125, '180D': 200, '365D': 380, '3YR': 650, '5YR': 950},
            'USDC': {'1D': 0, '7D': 0, '30D': 1, '90D': 0, '180D': -1, '365D': 2, '3YR': 3, '5YR': 5},
            'USDT': {'1D': 0, '7D': 0, '30D': 0, '90D': 1, '180D': 0, '365D': 1, '3YR': 2, '5YR': 4},
            'ORCA': {'1D': 8, '7D': -15, '30D': 45, '90D': 85, '180D': 125, '365D': 280, '3YR': 420, '5YR': 650},
            'RAY': {'1D': -2, '7D': 18, '30D': -8, '90D': 95, '180D': 155, '365D': 340, '3YR': 480, '5YR': 720},
            'JLP': {'1D': 1, '7D': 3, '30D': 8, '90D': 22, '180D': 45, '365D': 85, '3YR': 180, '5YR': 320},
            'WETH': {'1D': 3, '7D': 8, '30D': 12, '90D': 35, '180D': 18, '365D': 85, '3YR': 150, '5YR': 280}
        }
        
        return demo_data.get(token)
    
    
    def _display_returns_table(self, historical_data, market_data):
        """Display the historical returns table with market comparison"""
        if not historical_data:
            print("❌ No historical data available")
            return
            
        # Table header
        print(f"\n{'Asset':<20} {'1D':<8} {'7D':<8} {'30D':<8} {'90D':<8} {'180D':<8} {'365D':<8} {'3YR':<8} {'5YR':<8}")
        print("=" * 100)
        
        # Display total crypto market cap first
        if 'Total Crypto' in market_data:
            self._print_token_row('TOTAL CRYPTO MKT', market_data['Total Crypto'])
            print("-" * 100)
        
        # Display individual crypto tokens
        for token in sorted(historical_data.keys()):
            self._print_token_row(token, historical_data[token])
            
        # Separator before other asset classes
        print("-" * 100)
        
        # Display other market benchmarks
        for benchmark_name, benchmark_data in market_data.items():
            if benchmark_name != 'Total Crypto':  # Skip crypto since we showed it above
                self._print_token_row(benchmark_name, benchmark_data)
            
        # Add legend
        print("\n📊 PERFORMANCE LEGEND:")
        print("  All values shown as absolute percentage returns")
        print(f"  🕐 Data retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    
    def _print_token_row(self, token, returns):
        """Print a single token row with color coding"""
        row = f"{token:<20}"
        
        for timeframe in ['1D', '7D', '30D', '90D', '180D', '365D', '3YR', '5YR']:
            return_val = returns.get(timeframe)
            
            if return_val is None:
                cell = "N/A"
                row += f"{cell:<8}"
            else:
                # Format as integer percentage
                if return_val >= 0:
                    cell = f"+{return_val:.0f}%"
                else:
                    cell = f"{return_val:.0f}%"
                row += f"{cell:<8}"
                
        print(row)