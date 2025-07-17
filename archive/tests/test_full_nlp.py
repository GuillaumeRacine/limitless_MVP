#!/usr/bin/env python3
"""
Full integration test for NLP query system
"""

import os
import sys
sys.path.append('.')

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment loaded from .env")
except ImportError:
    print("⚠️  No dotenv, using system environment")

from utils.defillama_client import DefiLlamaClient
from utils.nlp_query import SmartDeFiLlamaQuery

def test_full_integration():
    """Test the complete NLP to DeFiLlama pipeline"""
    print("\n🔄 Testing full integration...")
    
    # Setup
    client = DefiLlamaClient()
    smart_query = SmartDeFiLlamaQuery(client, "auto")
    
    print(f"LLM Provider: {smart_query.llm_enhancer.provider if smart_query.llm_enhancer else 'None'}")
    
    # Test queries
    test_queries = [
        "hey",
        "help", 
        "what is the TVL on Solana",
        "best yields on Ethereum",
        "show me stablecoin data",
        "protocol fees for Uniswap"
    ]
    
    for query in test_queries:
        print(f"\n" + "="*60)
        print(f"🔍 Query: '{query}'")
        print("-" * 60)
        
        try:
            result = smart_query.process_query(query)
            
            print(f"✅ Success: {result.get('query', 'No interpretation')}")
            
            if result.get('special'):
                print("💬 Special response:")
                if 'results' in result and 'message' in result['results']:
                    print(result['results']['message'])
            elif 'results' in result:
                if isinstance(result['results'], dict):
                    print(f"📊 Result type: Dictionary")
                    for key, value in list(result['results'].items())[:3]:
                        print(f"  {key}: {str(value)[:100]}...")
                elif isinstance(result['results'], list):
                    print(f"📊 Result type: List ({len(result['results'])} items)")
                    for i, item in enumerate(result['results'][:3], 1):
                        if isinstance(item, dict):
                            name = item.get('name', item.get('symbol', f'Item {i}'))
                            print(f"  {i}. {name}")
                        else:
                            print(f"  {i}. {str(item)[:50]}...")
            else:
                print("❌ No results in response")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 FULL NLP INTEGRATION TEST")
    print("=" * 60)
    
    # Check environment
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"OpenAI Key: {'✅' if openai_key else '❌'}")
    print(f"Anthropic Key: {'✅' if anthropic_key else '❌'}")
    
    test_full_integration()
    
    print(f"\n🎯 Test completed!")