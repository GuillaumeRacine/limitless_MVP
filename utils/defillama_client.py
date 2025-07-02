#!/usr/bin/env python3
"""
DefiLlama API Client
Comprehensive client for accessing DefiLlama data
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

class DefiLlamaClient:
    def __init__(self):
        self.base_url = "https://api.llama.fi"
        self.yields_url = "https://yields.llama.fi"
        self.coins_url = "https://coins.llama.fi"
        self.stablecoins_url = "https://stablecoins.llama.fi"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
    def _make_request(self, url: str, params: dict = None) -> Optional[Dict]:
        """Make rate-limited request to DefiLlama API"""
        # Simple rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        try:
            response = requests.get(url, params=params, timeout=15)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️  API error {response.status_code}: {url}")
                return None
                
        except Exception as e:
            print(f"⚠️  Request failed: {e}")
            return None
    
    # ============== PROTOCOLS & TVL ==============
    
    def get_protocols(self) -> Optional[List[Dict]]:
        """Get all protocols with basic info"""
        url = f"{self.base_url}/protocols"
        return self._make_request(url)
    
    def get_protocol_tvl(self, protocol: str) -> Optional[Dict]:
        """Get TVL history for a specific protocol"""
        url = f"{self.base_url}/protocol/{protocol}"
        return self._make_request(url)
    
    def get_chain_tvl(self, chain: str) -> Optional[List[Dict]]:
        """Get TVL history for a specific chain"""
        url = f"{self.base_url}/v2/historicalChainTvl/{chain}"
        return self._make_request(url)
    
    def get_current_tvl(self) -> Optional[Dict]:
        """Get current total TVL across all chains"""
        url = f"{self.base_url}/v2/chains"
        return self._make_request(url)
    
    # ============== YIELDS & POOLS ==============
    
    def get_pool_yields(self, chain: str = None, protocol: str = None) -> Optional[List[Dict]]:
        """Get yield data for pools"""
        url = f"{self.yields_url}/pools"
        
        data = self._make_request(url)
        if not data or 'data' not in data:
            return None
            
        pools = data['data']
        
        # Filter by chain
        if chain:
            pools = [p for p in pools if p.get('chain', '').lower() == chain.lower()]
        
        # Filter by protocol
        if protocol:
            pools = [p for p in pools if p.get('project', '').lower() == protocol.lower()]
        
        return pools
    
    def get_yield_chart(self, pool_id: str) -> Optional[Dict]:
        """Get historical yield data for a specific pool"""
        url = f"{self.yields_url}/chart/{pool_id}"
        return self._make_request(url)
    
    # ============== PRICES ==============
    
    def get_current_prices(self, coins: List[str]) -> Optional[Dict]:
        """Get current prices for multiple coins"""
        coin_ids = ','.join(coins)
        url = f"{self.coins_url}/prices/current/{coin_ids}"
        return self._make_request(url)
    
    def get_historical_prices(self, coin_id: str, timestamp: int) -> Optional[Dict]:
        """Get historical price at specific timestamp"""
        url = f"{self.coins_url}/prices/historical/{timestamp}/{coin_id}"
        return self._make_request(url)
    
    def get_price_chart(self, coin_id: str, period: str = "365d") -> Optional[Dict]:
        """Get price chart data"""
        # Calculate timestamps based on period
        end_time = int(datetime.now().timestamp())
        
        if period == "7d":
            start_time = int((datetime.now() - timedelta(days=7)).timestamp())
        elif period == "30d":
            start_time = int((datetime.now() - timedelta(days=30)).timestamp())
        elif period == "365d":
            start_time = int((datetime.now() - timedelta(days=365)).timestamp())
        else:
            start_time = int((datetime.now() - timedelta(days=30)).timestamp())
        
        url = f"{self.coins_url}/chart/{coin_id}"
        params = {
            'start': start_time,
            'end': end_time,
            'span': 1 if period == "7d" else 24  # Hourly for 7d, daily for longer
        }
        
        return self._make_request(url, params)
    
    # ============== DEX DATA ==============
    
    def get_dex_volumes(self) -> Optional[List[Dict]]:
        """Get DEX volume data"""
        url = f"{self.base_url}/overview/dexs"
        return self._make_request(url)
    
    def get_dex_protocol(self, protocol: str) -> Optional[Dict]:
        """Get specific DEX protocol data"""
        url = f"{self.base_url}/dex/{protocol}"
        return self._make_request(url)
    
    # ============== STABLECOINS ==============
    
    def get_stablecoins(self) -> Optional[Dict]:
        """Get stablecoin data"""
        url = f"{self.stablecoins_url}/stablecoins"
        return self._make_request(url)
    
    def get_stablecoin_chains(self, stablecoin_id: int) -> Optional[Dict]:
        """Get stablecoin distribution across chains"""
        url = f"{self.stablecoins_url}/stablecoin/{stablecoin_id}"
        return self._make_request(url)
    
    # ============== FEES ==============
    
    def get_fees_overview(self) -> Optional[List[Dict]]:
        """Get protocol fees overview"""
        url = f"{self.base_url}/overview/fees"
        return self._make_request(url)
    
    def get_protocol_fees(self, protocol: str) -> Optional[Dict]:
        """Get fees for specific protocol"""
        url = f"{self.base_url}/fees/{protocol}"
        return self._make_request(url)
    
    # ============== HELPER METHODS ==============
    
    def search_protocols(self, query: str) -> List[Dict]:
        """Search for protocols by name"""
        protocols = self.get_protocols()
        if not protocols:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for protocol in protocols:
            name = protocol.get('name', '').lower()
            slug = protocol.get('slug', '').lower()
            
            if query_lower in name or query_lower in slug:
                matches.append(protocol)
        
        return matches
    
    def get_chain_summary(self, chain: str) -> Dict:
        """Get comprehensive summary for a chain"""
        summary = {
            'chain': chain,
            'timestamp': datetime.now().isoformat(),
            'tvl': None,
            'protocols': [],
            'top_pools': [],
            'dex_volume': None
        }
        
        # Get TVL data
        current_tvl = self.get_current_tvl()
        if current_tvl:
            for chain_data in current_tvl:
                if chain_data.get('name', '').lower() == chain.lower():
                    summary['tvl'] = {
                        'current': chain_data.get('tvl', 0),
                        'change_1d': chain_data.get('tvlPrevDay', 0),
                        'change_7d': chain_data.get('tvlPrevWeek', 0),
                        'change_30d': chain_data.get('tvlPrevMonth', 0)
                    }
                    break
        
        # Get top protocols on chain
        protocols = self.get_protocols()
        if protocols:
            chain_protocols = [p for p in protocols if chain.lower() in [c.lower() for c in p.get('chains', [])]]
            summary['protocols'] = sorted(chain_protocols, key=lambda x: x.get('tvl', 0), reverse=True)[:10]
        
        # Get top yield pools
        pools = self.get_pool_yields(chain=chain)
        if pools:
            # Filter and sort pools
            valid_pools = [p for p in pools if p.get('tvlUsd', 0) > 100000]  # Min $100k TVL
            summary['top_pools'] = sorted(valid_pools, key=lambda x: x.get('apy', 0), reverse=True)[:10]
        
        return summary
    
    def get_token_info(self, token_symbol: str) -> Dict:
        """Get comprehensive token information"""
        # This would need mapping of symbols to coin IDs
        # For now, return basic structure
        return {
            'symbol': token_symbol,
            'price': None,
            'market_cap': None,
            'volume_24h': None,
            'price_change': {
                '1h': None,
                '24h': None,
                '7d': None
            }
        }

    def get_monthly_stats(self, chain: str, months: int = 12) -> List[Dict]:
        """Get month-by-month statistics for a chain"""
        stats = []
        
        # Get historical TVL
        tvl_data = self.get_chain_tvl(chain)
        if not tvl_data:
            return stats
        
        # Group by month
        monthly_data = {}
        for entry in tvl_data:
            timestamp = entry.get('date')
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                month_key = dt.strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = []
                monthly_data[month_key].append(entry)
        
        # Calculate monthly averages
        for month, entries in sorted(monthly_data.items(), reverse=True)[:months]:
            if entries:
                avg_tvl = sum(e.get('tvl', 0) for e in entries) / len(entries)
                stats.append({
                    'month': month,
                    'avg_tvl': avg_tvl,
                    'entries': len(entries),
                    'start_tvl': entries[0].get('tvl', 0),
                    'end_tvl': entries[-1].get('tvl', 0)
                })
        
        return stats