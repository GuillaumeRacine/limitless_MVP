#!/usr/bin/env python3
"""
Prices View - Display current token prices and FX rates
"""

from datetime import datetime

class PricesView:
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def display(self):
        """Display current prices and FX rates"""
        print("\n" + "="*120)
        print("💰 REAL-TIME PRICING DATA")
        print("="*120)
        
        # Force refresh prices
        self.data_manager.get_token_prices()
        
        self._display_crypto_prices()
        self._display_fx_rates()
        self._display_price_sources()
        self._display_portfolio_values()
        
    def _display_crypto_prices(self):
        """Display cryptocurrency prices"""
        print("\n📈 CRYPTOCURRENCY PRICES")
        print("-" * 60)
        
        if not self.data_manager.prices:
            print("❌ No price data available")
            return
            
        # Group tokens by category
        major_tokens = ['BTC', 'ETH', 'SOL']
        stablecoins = ['USDC', 'USDT']
        defi_tokens = ['ORCA', 'RAY', 'JLP']
        
        self._display_price_category("Major Cryptocurrencies", major_tokens)
        self._display_price_category("Stablecoins", stablecoins)
        self._display_price_category("DeFi Tokens", defi_tokens)
        
    def _display_price_category(self, category_name, tokens):
        """Display prices for a specific category"""
        category_prices = {token: self.data_manager.prices.get(token) 
                          for token in tokens 
                          if self.data_manager.prices.get(token) is not None}
        
        if not category_prices:
            return
            
        print(f"\n{category_name}:")
        for token, price in category_prices.items():
            if price < 1:
                price_str = f"${price:.6f}"
            elif price < 100:
                price_str = f"${price:.2f}"
            else:
                price_str = f"${price:,.2f}"
            print(f"  {token:6} {price_str:>12}")
    
    def _display_fx_rates(self):
        """Display foreign exchange rates"""
        print("\n💱 FOREIGN EXCHANGE RATES")
        print("-" * 40)
        
        if not self.data_manager.fx_rates:
            print("❌ No FX data available")
            return
            
        for pair, rate in self.data_manager.fx_rates.items():
            from_curr, to_curr = pair.split('_')
            print(f"  1 {from_curr} = {rate:.4f} {to_curr}")
    
    def _display_price_sources(self):
        """Display information about price sources"""
        print("\n📊 PRICE SOURCES")
        print("-" * 30)
        print("  🦙 DefiLlama: DeFi tokens (SOL, ORCA, RAY, JLP)")
        print("  🦎 CoinGecko: Traditional crypto (BTC, ETH, stablecoins)")
        print("  💱 ExchangeRate-API: FX rates (CAD/USD)")
        print(f"  🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _display_portfolio_values(self):
        """Display portfolio values in different currencies"""
        print("\n🏦 PORTFOLIO VALUE CONVERSION")
        print("-" * 45)
        
        # Get total portfolio value
        all_positions = self.data_manager.get_all_active_positions()
        
        if not all_positions:
            print("❌ No active positions to analyze")
            return
            
        total_usd = 0
        position_count = 0
        
        for position in all_positions:
            if position.get('entry_value'):
                total_usd += position['entry_value']
                position_count += 1
        
        if total_usd == 0:
            print("❌ No position values available")
            return
            
        print(f"  Active Positions: {position_count}")
        print(f"  Total Value (USD): ${total_usd:,.2f}")
        
        # Convert to CAD if FX rates available
        if 'USD_CAD' in self.data_manager.fx_rates:
            usd_cad_rate = self.data_manager.fx_rates['USD_CAD']
            total_cad = total_usd * usd_cad_rate
            print(f"  Total Value (CAD): ${total_cad:,.2f}")
            print(f"  Exchange Rate: 1 USD = {usd_cad_rate:.4f} CAD")
    
    def display_token_details(self, token_symbol):
        """Display detailed information for a specific token"""
        token = token_symbol.upper()
        
        print(f"\n📋 TOKEN DETAILS: {token}")
        print("=" * 50)
        
        # Current price
        if token in self.data_manager.prices:
            price = self.data_manager.prices[token]
            print(f"Current Price: ${price:.6f}" if price < 1 else f"Current Price: ${price:,.2f}")
        else:
            print("❌ Price not available")
            return
        
        # Find positions using this token
        all_positions = self.data_manager.get_all_active_positions()
        token_positions = []
        
        for position in all_positions:
            if position.get('token_pair'):
                pair = position['token_pair'].replace(' ', '')
                if '/' in pair:
                    token_a, token_b = pair.split('/')
                    if token_a.upper() == token or token_b.upper() == token:
                        token_positions.append(position)
        
        if token_positions:
            print(f"\nPositions using {token}: {len(token_positions)}")
            total_exposure = sum(pos.get('entry_value', 0) for pos in token_positions)
            print(f"Total Exposure: ${total_exposure:,.2f}")
            
            # Show individual positions
            for i, pos in enumerate(token_positions[:5], 1):  # Show first 5
                platform = pos.get('platform', 'Unknown')
                pair = pos.get('token_pair', 'Unknown')
                value = pos.get('entry_value', 0)
                print(f"  {i}. {platform} - {pair}: ${value:,.2f}")
                
            if len(token_positions) > 5:
                print(f"  ... and {len(token_positions) - 5} more positions")
        else:
            print(f"\n❌ No active positions found using {token}")