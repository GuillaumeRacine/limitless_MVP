#!/usr/bin/env python3
"""
Natural Language Query Interface for DeFiLlama
Converts user queries to API calls with LLM enhancement
"""

import json
import re
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Load environment variables (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Optional LLM imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class NaturalLanguageQuery:
    """Parse natural language queries without external LLM dependencies"""
    
    def __init__(self):
        # Keywords for different query types
        self.query_patterns = {
            'tvl': ['tvl', 'total value locked', 'liquidity', 'how much'],
            'yields': ['yield', 'apy', 'apr', 'returns', 'best pools', 'highest'],
            'fees': ['fees', 'revenue', 'earnings', 'protocol fees'],
            'stablecoins': ['stable', 'stablecoin', 'usdc', 'usdt', 'dai'],
            'protocols': ['protocol', 'platform', 'dex', 'defi'],
            'chains': ['chain', 'network', 'blockchain', 'on sol', 'on ethereum']
        }
        
        # Chain mappings
        self.chain_map = {
            'sol': 'Solana', 'solana': 'Solana',
            'eth': 'Ethereum', 'ethereum': 'Ethereum',
            'sui': 'Sui',
            'base': 'Base',
            'arb': 'Arbitrum', 'arbitrum': 'Arbitrum',
            'polygon': 'Polygon', 'matic': 'Polygon',
            'avax': 'Avalanche', 'avalanche': 'Avalanche',
            'bsc': 'BSC', 'bnb': 'BSC',
            'optimism': 'Optimism', 'op': 'Optimism'
        }
        
        # Time mappings
        self.time_map = {
            'today': 1, 'daily': 1, '24h': 1, '1d': 1,
            'week': 7, 'weekly': 7, '7d': 7,
            'month': 30, 'monthly': 30, '30d': 30,
            'quarter': 90, '90d': 90,
            'year': 365, 'yearly': 365, '365d': 365
        }
    
    def parse(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into API parameters"""
        query_lower = query.lower()
        
        # Detect query type
        query_type = self._detect_query_type(query_lower)
        
        # Extract parameters
        params = {
            'query_type': query_type,
            'chain': self._extract_chain(query_lower),
            'protocol': self._extract_protocol(query_lower),
            'timeframe': self._extract_timeframe(query_lower),
            'filters': self._extract_filters(query_lower)
        }
        
        # Generate human-readable interpretation
        params['interpretation'] = self._generate_interpretation(params)
        
        return params
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of query"""
        for query_type, keywords in self.query_patterns.items():
            if any(keyword in query for keyword in keywords):
                return query_type
        return 'general'
    
    def _extract_chain(self, query: str) -> Optional[str]:
        """Extract chain from query"""
        for alias, chain in self.chain_map.items():
            if alias in query:
                return chain
        return None
    
    def _extract_protocol(self, query: str) -> Optional[str]:
        """Extract protocol name from query"""
        # Look for quoted strings or specific protocol names
        quoted = re.findall(r'"([^"]*)"', query)
        if quoted:
            return quoted[0]
        
        # Common protocols
        protocols = ['uniswap', 'aave', 'compound', 'curve', 'sushiswap', 
                    'pancakeswap', 'orca', 'raydium', 'cetus']
        for protocol in protocols:
            if protocol in query:
                return protocol
        
        return None
    
    def _extract_timeframe(self, query: str) -> int:
        """Extract timeframe in days"""
        for keyword, days in self.time_map.items():
            if keyword in query:
                return days
        return 30  # Default to 30 days
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract additional filters"""
        filters = {}
        
        # Min TVL filter
        tvl_match = re.search(r'(?:over|above|greater than|>\s*)[\$]?([\d,]+)(?:m|million)?', query)
        if tvl_match:
            value = float(tvl_match.group(1).replace(',', ''))
            if 'm' in query or 'million' in query:
                value *= 1_000_000
            filters['min_tvl'] = value
        
        # Min APY filter
        apy_match = re.search(r'(?:over|above|greater than|>\s*)([\d.]+)%', query)
        if apy_match:
            filters['min_apy'] = float(apy_match.group(1))
        
        # Token pair filter
        pair_match = re.search(r'(\w+)[/-](\w+)', query)
        if pair_match:
            filters['token_pair'] = f"{pair_match.group(1)}/{pair_match.group(2)}"
        
        return filters
    
    def _generate_interpretation(self, params: Dict[str, Any]) -> str:
        """Generate human-readable interpretation"""
        parts = []
        
        if params['query_type'] == 'yields':
            parts.append("Search for yield opportunities")
        elif params['query_type'] == 'tvl':
            parts.append("Get TVL data")
        elif params['query_type'] == 'fees':
            parts.append("Analyze protocol fees")
        elif params['query_type'] == 'stablecoins':
            parts.append("Check stablecoin metrics")
        else:
            parts.append("General DeFi query")
        
        if params['chain']:
            parts.append(f"on {params['chain']}")
        
        if params['protocol']:
            parts.append(f"for {params['protocol']}")
        
        if params['filters']:
            if 'min_tvl' in params['filters']:
                parts.append(f"with TVL > ${params['filters']['min_tvl']:,.0f}")
            if 'min_apy' in params['filters']:
                parts.append(f"with APY > {params['filters']['min_apy']}%")
            if 'token_pair' in params['filters']:
                parts.append(f"for {params['filters']['token_pair']} pools")
        
        return " ".join(parts)


class LLMQueryEnhancer:
    """LLM-powered query understanding and enhancement"""
    
    def __init__(self, provider: str = "auto"):
        self.provider = provider
        self.setup_llm()
    
    def setup_llm(self):
        """Setup LLM client based on available providers"""
        if self.provider == "auto":
            # Auto-detect best available provider
            openai_key = os.getenv('OPENAI_API_KEY')
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            
            if ANTHROPIC_AVAILABLE and anthropic_key and anthropic_key.startswith('sk-ant-'):
                try:
                    self.provider = "anthropic"
                    self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                    print("🧠 Using Anthropic Claude")
                except Exception as e:
                    print(f"⚠️  Anthropic setup failed: {e}")
                    self.provider = "local"
            elif OPENAI_AVAILABLE and openai_key and openai_key.startswith('sk-'):
                try:
                    self.provider = "openai"
                    print("🧠 Using OpenAI GPT")
                except Exception as e:
                    print(f"⚠️  OpenAI setup failed: {e}")
                    self.provider = "local"
            else:
                self.provider = "local"
                print("🏠 Using local pattern matching")
        elif self.provider == "openai" and OPENAI_AVAILABLE:
            pass  # Will be handled in _query_openai
        elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
    
    def enhance_query(self, user_query: str) -> Dict[str, Any]:
        """Use LLM to understand and enhance the query"""
        if self.provider == "local":
            return self._local_parse(user_query)
        
        prompt = self._build_enhancement_prompt(user_query)
        
        try:
            if self.provider == "openai":
                return self._query_openai(prompt)
            elif self.provider == "anthropic":
                return self._query_anthropic(prompt)
        except Exception as e:
            # Silent fallback to local parsing
            return self._local_parse(user_query)
    
    def _build_enhancement_prompt(self, user_query: str) -> str:
        """Build prompt for LLM query understanding"""
        return f"""
You are a DeFi data analyst. Convert this natural language query into structured parameters for DeFiLlama API calls.

User Query: "{user_query}"

Return ONLY a JSON object with these fields:
{{
    "query_type": "yields|tvl|fees|stablecoins|protocols|general",
    "chain": "chain name or null",
    "protocol": "protocol name or null", 
    "timeframe_days": number or 30,
    "filters": {{
        "min_tvl": number or null,
        "min_apy": number or null,
        "token_pair": "TOKEN/TOKEN or null",
        "category": "category or null"
    }},
    "interpretation": "human readable interpretation",
    "confidence": 0.0-1.0
}}

Examples:
- "Best SOL yields over 15%" → query_type: "yields", chain: "Solana", filters: {{"min_apy": 15}}
- "TVL on Ethereum last month" → query_type: "tvl", chain: "Ethereum", timeframe_days: 30
- "Uniswap fees" → query_type: "fees", protocol: "Uniswap"
"""
    
    def _query_openai(self, prompt: str) -> Dict[str, Any]:
        """Query OpenAI GPT"""
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        return json.loads(result_text)
    
    def _query_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Query Anthropic Claude"""
        response = self.anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text.strip()
        return json.loads(result_text)
    
    def _local_parse(self, user_query: str) -> Dict[str, Any]:
        """Fallback to local parsing with greeting handling"""
        query_lower = user_query.lower().strip()
        
        # Handle simple greetings and help
        if query_lower in ['hey', 'hello', 'hi']:
            return {
                'query_type': 'greeting',
                'interpretation': 'Greeting - Ask me about DeFi data!',
                'confidence': 1.0,
                'response': "Hello! I can help you query DeFi data. Try asking:\n• 'What's the TVL on Solana?'\n• 'Best ETH yields over 15%'\n• 'Show me stablecoin data'"
            }
        elif query_lower in ['help', 'what can you do']:
            return {
                'query_type': 'help',
                'interpretation': 'Help request',
                'confidence': 1.0,
                'response': "I can help you query DeFi data:\n\n🔍 Query Types:\n• TVL: 'What's the TVL on Solana?'\n• Yields: 'Best ETH yields over 20%'\n• Protocols: 'Search for Uniswap data'\n• Fees: 'Protocol fees for Aave'\n• Stablecoins: 'Compare stablecoin market caps'\n\n💡 Try being specific with chains, percentages, and amounts!"
            }
        
        nlp = NaturalLanguageQuery()
        local_result = nlp.parse(user_query)
        local_result["confidence"] = 0.7  # Lower confidence for local parsing
        return local_result


class SmartDeFiLlamaQuery:
    """Enhanced query builder with LLM integration"""
    
    def __init__(self, defillama_client, llm_provider: Optional[str] = "auto"):
        self.client = defillama_client
        self.nlp = NaturalLanguageQuery()
        self.llm_enhancer = LLMQueryEnhancer(llm_provider) if llm_provider else None
        
        # Enhanced example queries
        self.example_queries = [
            "Show me the best ETH yields on Arbitrum with over 15% APY",
            "What's the TVL on Solana compared to last month?",
            "Find USDC/ETH pools with over 10% APY and $5M TVL",
            "Show protocol fees for top 10 DeFi protocols",
            "Compare stablecoin market caps and their price stability",
            "Find the highest yielding pools on Base with low risk",
            "What are the best DeFi opportunities on Sui right now?",
            "Show me protocols that earned over $1M in fees last week"
        ]
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """Process natural language query and return results"""
        # Use LLM enhancement if available, fallback to local parsing
        if self.llm_enhancer:
            params = self.llm_enhancer.enhance_query(user_input)
            provider_info = f" (via {self.llm_enhancer.provider.upper()})"
        else:
            params = self.nlp.parse(user_input)
            provider_info = " (local)"
        
        # Keep interpretation clean for user display
        
        # Handle special query types first
        if params['query_type'] in ['greeting', 'help']:
            return {
                'query': params['interpretation'],
                'results': {'message': params.get('response', 'Hello!')},
                'special': True
            }
        
        # Execute based on query type
        if params['query_type'] == 'yields':
            return self._handle_yields_query(params)
        elif params['query_type'] == 'tvl':
            return self._handle_tvl_query(params)
        elif params['query_type'] == 'fees':
            return self._handle_fees_query(params)
        elif params['query_type'] == 'stablecoins':
            return self._handle_stablecoins_query(params)
        else:
            return self._handle_general_query(params)
    
    def _handle_yields_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle yield-related queries"""
        pools = self.client.get_pool_yields(chain=params['chain'])
        
        if not pools:
            return {'error': 'No yield data available'}
        
        # Apply filters
        filtered_pools = pools
        if params['filters']:
            if 'min_tvl' in params['filters']:
                filtered_pools = [p for p in filtered_pools 
                                if p.get('tvlUsd', 0) >= params['filters']['min_tvl']]
            if 'min_apy' in params['filters']:
                filtered_pools = [p for p in filtered_pools 
                                if p.get('apy', 0) >= params['filters']['min_apy']]
            if 'token_pair' in params['filters']:
                pair = params['filters']['token_pair'].upper()
                filtered_pools = [p for p in filtered_pools 
                                if pair in p.get('symbol', '').upper()]
        
        # Sort by APY
        filtered_pools.sort(key=lambda x: x.get('apy', 0), reverse=True)
        
        return {
            'query': params['interpretation'],
            'results': filtered_pools[:20],
            'count': len(filtered_pools)
        }
    
    def _handle_tvl_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TVL-related queries"""
        if params['chain']:
            summary = self.client.get_chain_summary(params['chain'])
            return {
                'query': params['interpretation'],
                'results': summary,
                'chain': params['chain']
            }
        else:
            tvl_data = self.client.get_current_tvl()
            return {
                'query': params['interpretation'],
                'results': tvl_data[:10]
            }
    
    def _handle_fees_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fees-related queries"""
        fees_data = self.client.get_fees_overview()
        
        if not fees_data:
            return {
                'query': params.get('interpretation', 'Protocol fees query'),
                'error': 'No fees data available'
            }
        
        protocol = params.get('protocol')
        if protocol:
            # Filter for specific protocol - handle different data structures
            protocol_fees = []
            for f in fees_data:
                if isinstance(f, dict):
                    name = f.get('name', '').lower()
                    if protocol.lower() in name:
                        protocol_fees.append(f)
                elif isinstance(f, str):
                    if protocol.lower() in f.lower():
                        protocol_fees.append({'name': f})
            
            return {
                'query': params.get('interpretation', 'Protocol fees query'),
                'results': protocol_fees
            }
        
        # Convert strings to dict format if needed
        if fees_data and isinstance(fees_data[0], str):
            formatted_fees = [{'name': f} for f in fees_data[:15]]
        else:
            formatted_fees = fees_data[:15]
        
        return {
            'query': params.get('interpretation', 'Protocol fees query'),
            'results': formatted_fees
        }
    
    def _handle_stablecoins_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stablecoin-related queries"""
        stables = self.client.get_stablecoins()
        
        if stables and 'peggedAssets' in stables:
            return {
                'query': params['interpretation'],
                'results': stables['peggedAssets'][:10]
            }
        
        return {'error': 'No stablecoin data available'}
    
    def _handle_general_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general queries"""
        if params['protocol']:
            # Search for protocol
            protocols = self.client.search_protocols(params['protocol'])
            return {
                'query': params['interpretation'],
                'results': protocols[:10]
            }
        
        # Default to showing top protocols by TVL
        tvl_data = self.client.get_current_tvl()
        return {
            'query': params['interpretation'],
            'results': tvl_data[:10]
        }