#!/usr/bin/env python3
"""
Direct platform API integrations for real-time data.
This implements the "closest to ground truth" approach using official APIs.
"""

import requests
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

class PlatformAPI(ABC):
    """Base class for platform API integrations"""
    
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    @abstractmethod
    def get_pool_info(self, pool_id: str) -> Dict[str, Any]:
        """Get pool information"""
        pass
    
    @abstractmethod
    def get_position_info(self, position_id: str) -> Dict[str, Any]:
        """Get position information"""
        pass
    
    @abstractmethod
    def get_token_price(self, token_address: str) -> float:
        """Get token price"""
        pass

class RaydiumAPI(PlatformAPI):
    """Raydium official API integration"""
    
    def __init__(self):
        super().__init__("https://api.raydium.io/v2")
    
    def get_pool_info(self, pool_id: str) -> Dict[str, Any]:
        """Get Raydium pool information"""
        try:
            response = self.session.get(f"{self.base_url}/ammV3/pools/{pool_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Raydium pool info: {e}")
            return {}
    
    def get_position_info(self, position_nft_mint: str) -> Dict[str, Any]:
        """Get Raydium position information"""
        try:
            response = self.session.get(f"{self.base_url}/ammV3/positions/{position_nft_mint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Raydium position info: {e}")
            return {}
    
    def get_token_price(self, token_address: str) -> float:
        """Get token price from Raydium"""
        try:
            response = self.session.get(f"{self.base_url}/main/price")
            response.raise_for_status()
            prices = response.json()
            return float(prices.get(token_address, 0))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Raydium token price: {e}")
            return 0.0
    
    def get_all_pools(self) -> List[Dict[str, Any]]:
        """Get all Raydium pools"""
        try:
            response = self.session.get(f"{self.base_url}/ammV3/pools")
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Raydium pools: {e}")
            return []

class OrcaAPI(PlatformAPI):
    """Orca official API integration"""
    
    def __init__(self):
        super().__init__("https://api.orca.so/v1")
    
    def get_pool_info(self, pool_address: str) -> Dict[str, Any]:
        """Get Orca whirlpool information"""
        try:
            response = self.session.get(f"{self.base_url}/whirlpool/{pool_address}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Orca pool info: {e}")
            return {}
    
    def get_position_info(self, position_pubkey: str) -> Dict[str, Any]:
        """Get Orca position information"""
        try:
            response = self.session.get(f"{self.base_url}/position/{position_pubkey}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Orca position info: {e}")
            return {}
    
    def get_token_price(self, token_mint: str) -> float:
        """Get token price from Orca"""
        try:
            response = self.session.get(f"{self.base_url}/token/{token_mint}/price")
            response.raise_for_status()
            return float(response.json().get('price', 0))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Orca token price: {e}")
            return 0.0
    
    def get_all_whirlpools(self) -> List[Dict[str, Any]]:
        """Get all Orca whirlpools"""
        try:
            response = self.session.get(f"{self.base_url}/whirlpools")
            response.raise_for_status()
            return response.json().get('whirlpools', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Orca whirlpools: {e}")
            return []

class JupiterAPI(PlatformAPI):
    """Jupiter official API integration"""
    
    def __init__(self):
        super().__init__("https://api.jup.ag")
    
    def get_pool_info(self, pool_id: str) -> Dict[str, Any]:
        """Get Jupiter perp pool information"""
        try:
            response = self.session.get(f"{self.base_url}/perps/v1/pools/{pool_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Jupiter pool info: {e}")
            return {}
    
    def get_position_info(self, wallet_address: str) -> Dict[str, Any]:
        """Get Jupiter perp positions for wallet"""
        try:
            response = self.session.get(f"{self.base_url}/perps/v1/positions/{wallet_address}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Jupiter position info: {e}")
            return {}
    
    def get_token_price(self, token_symbol: str) -> float:
        """Get token price from Jupiter"""
        try:
            response = self.session.get(f"{self.base_url}/price/v2", params={'ids': token_symbol})
            response.raise_for_status()
            data = response.json()
            return float(data.get('data', {}).get(token_symbol, {}).get('price', 0))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Jupiter token price: {e}")
            return 0.0
    
    def get_perp_stats(self, market: str) -> Dict[str, Any]:
        """Get Jupiter perp market stats"""
        try:
            response = self.session.get(f"{self.base_url}/perps/v1/stats/{market}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Jupiter perp stats: {e}")
            return {}

class CetusAPI(PlatformAPI):
    """CETUS official API integration"""
    
    def __init__(self):
        super().__init__("https://api-sui.cetus.zone")
    
    def get_pool_info(self, pool_id: str) -> Dict[str, Any]:
        """Get CETUS pool information"""
        try:
            response = self.session.get(f"{self.base_url}/v2/sui/pools/{pool_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching CETUS pool info: {e}")
            return {}
    
    def get_position_info(self, position_id: str) -> Dict[str, Any]:
        """Get CETUS position information"""
        try:
            response = self.session.get(f"{self.base_url}/v2/sui/positions/{position_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching CETUS position info: {e}")
            return {}
    
    def get_token_price(self, coin_type: str) -> float:
        """Get token price from CETUS"""
        try:
            response = self.session.get(f"{self.base_url}/v2/sui/coin_price", params={'coin_type': coin_type})
            response.raise_for_status()
            return float(response.json().get('price', 0))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching CETUS token price: {e}")
            return 0.0
    
    def get_all_pools(self) -> List[Dict[str, Any]]:
        """Get all CETUS pools"""
        try:
            response = self.session.get(f"{self.base_url}/v2/sui/pools")
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching CETUS pools: {e}")
            return []

class GMXAPI(PlatformAPI):
    """GMX official API integration"""
    
    def __init__(self):
        super().__init__("https://api.gmx.io")
    
    def get_pool_info(self, pool_id: str) -> Dict[str, Any]:
        """Get GMX pool information"""
        try:
            response = self.session.get(f"{self.base_url}/pools/{pool_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GMX pool info: {e}")
            return {}
    
    def get_position_info(self, account: str, market: str) -> Dict[str, Any]:
        """Get GMX position information"""
        try:
            response = self.session.get(f"{self.base_url}/positions", 
                                      params={'account': account, 'market': market})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GMX position info: {e}")
            return {}
    
    def get_token_price(self, token_address: str) -> float:
        """Get token price from GMX"""
        try:
            response = self.session.get(f"{self.base_url}/prices", params={'token': token_address})
            response.raise_for_status()
            return float(response.json().get('price', 0))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GMX token price: {e}")
            return 0.0
    
    def get_markets(self) -> List[Dict[str, Any]]:
        """Get all GMX markets"""
        try:
            response = self.session.get(f"{self.base_url}/markets")
            response.raise_for_status()
            return response.json().get('markets', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GMX markets: {e}")
            return []

class PlatformAPIManager:
    """Manager class for all platform APIs"""
    
    def __init__(self):
        self.apis = {
            'raydium': RaydiumAPI(),
            'orca': OrcaAPI(),
            'jupiter': JupiterAPI(),
            'cetus': CetusAPI(),
            'gmx': GMXAPI(),
        }
    
    def get_api(self, platform_name: str) -> Optional[PlatformAPI]:
        """Get API instance for platform"""
        return self.apis.get(platform_name.lower())
    
    def get_pool_info(self, platform_name: str, pool_id: str) -> Dict[str, Any]:
        """Get pool info from specified platform"""
        api = self.get_api(platform_name)
        if api:
            return api.get_pool_info(pool_id)
        return {}
    
    def get_position_info(self, platform_name: str, position_id: str) -> Dict[str, Any]:
        """Get position info from specified platform"""
        api = self.get_api(platform_name)
        if api:
            return api.get_position_info(position_id)
        return {}
    
    def get_token_price(self, platform_name: str, token_identifier: str) -> float:
        """Get token price from specified platform"""
        api = self.get_api(platform_name)
        if api:
            return api.get_token_price(token_identifier)
        return 0.0
    
    def get_all_prices(self, token_identifiers: Dict[str, str]) -> Dict[str, float]:
        """Get prices from all available platforms"""
        prices = {}
        for platform_name, token_id in token_identifiers.items():
            price = self.get_token_price(platform_name, token_id)
            if price > 0:
                prices[platform_name] = price
        return prices
    
    def health_check(self) -> Dict[str, bool]:
        """Check if all APIs are responding"""
        health = {}
        for platform_name, api in self.apis.items():
            try:
                # Try a simple API call to check connectivity
                response = api.session.get(f"{api.base_url}/", timeout=5)
                health[platform_name] = response.status_code < 500
            except:
                health[platform_name] = False
        return health

