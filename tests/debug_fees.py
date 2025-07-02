#!/usr/bin/env python3
"""
Debug fees query issue
"""

import sys
sys.path.append('.')

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

from utils.defillama_client import DefiLlamaClient
from utils.nlp_query import SmartDeFiLlamaQuery, NaturalLanguageQuery

def debug_fees():
    print("🔍 Debugging fees query...")
    
    # Test local parsing
    nlp = NaturalLanguageQuery()
    params = nlp.parse("protocol fees for Uniswap")
    
    print(f"Parsed parameters: {params}")
    print(f"Protocol value: {params.get('protocol', 'None')}")
    print(f"Query type: {params.get('query_type', 'None')}")
    
    # Test DeFiLlama client
    client = DefiLlamaClient()
    print(f"\n🔄 Testing DefiLlama fees overview...")
    
    try:
        fees_data = client.get_fees_overview()
        if fees_data:
            print(f"✅ Got {len(fees_data)} protocols")
            print(f"First protocol type: {type(fees_data[0])}")
            print(f"First protocol: {fees_data[0] if fees_data else 'None'}")
            if len(fees_data) > 1:
                print(f"Second protocol type: {type(fees_data[1])}")
                print(f"Second protocol: {fees_data[1]}")
        else:
            print("❌ No fees data returned")
    except Exception as e:
        print(f"❌ Fees API error: {e}")
    
    # Test smart query
    print(f"\n🤖 Testing smart query...")
    smart_query = SmartDeFiLlamaQuery(client)
    
    try:
        result = smart_query.process_query("protocol fees for Uniswap")
        print(f"✅ Smart query result keys: {result.keys()}")
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
    except Exception as e:
        print(f"❌ Smart query error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_fees()