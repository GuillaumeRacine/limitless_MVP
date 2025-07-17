#!/usr/bin/env python3
"""
Test script for NLP query system
"""

import os
from utils.nlp_query import LLMQueryEnhancer, NaturalLanguageQuery

def test_env_loading():
    """Test environment variable loading"""
    print("🔍 Testing environment variables...")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"OpenAI key found: {bool(openai_key)} (starts with sk-: {openai_key.startswith('sk-') if openai_key else False})")
    print(f"Anthropic key found: {bool(anthropic_key)} (starts with sk-ant-: {anthropic_key.startswith('sk-ant-') if anthropic_key else False})")
    
    if openai_key:
        print(f"OpenAI key preview: {openai_key[:15]}...{openai_key[-10:]}")
    if anthropic_key:
        print(f"Anthropic key preview: {anthropic_key[:20]}...{anthropic_key[-10:]}")

def test_llm_setup():
    """Test LLM provider setup"""
    print("\n🧠 Testing LLM setup...")
    
    try:
        enhancer = LLMQueryEnhancer("auto")
        print(f"Provider selected: {enhancer.provider}")
        return enhancer
    except Exception as e:
        print(f"❌ LLM setup failed: {e}")
        return None

def test_local_parsing():
    """Test local parsing functionality"""
    print("\n🏠 Testing local parsing...")
    
    nlp = NaturalLanguageQuery()
    
    test_queries = [
        "hey",
        "hello",
        "what is the TVL on Solana",
        "best ETH yields",
        "show me stablecoins",
        "protocol fees for Uniswap"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            result = nlp.parse(query)
            print(f"  Type: {result['query_type']}")
            print(f"  Chain: {result.get('chain', 'None')}")
            print(f"  Interpretation: {result.get('interpretation', 'None')}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_llm_queries(enhancer):
    """Test LLM query enhancement"""
    if not enhancer:
        print("\n⚠️  Skipping LLM tests - no enhancer available")
        return
    
    print(f"\n🤖 Testing LLM queries with {enhancer.provider}...")
    
    test_queries = [
        "what is the TVL on Solana",
        "best yields on Ethereum over 10%",
        "show me stablecoin data"
    ]
    
    for query in test_queries:
        print(f"\nTesting: '{query}'")
        try:
            result = enhancer.enhance_query(query)
            print(f"  ✅ Success!")
            print(f"  Type: {result.get('query_type', 'unknown')}")
            print(f"  Chain: {result.get('chain', 'None')}")
            print(f"  Confidence: {result.get('confidence', 'N/A')}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_simple_responses():
    """Test handling of simple greetings"""
    print("\n💬 Testing simple response handling...")
    
    enhancer = LLMQueryEnhancer("auto")
    
    simple_queries = ["hey", "hello", "hi", "help"]
    
    for query in simple_queries:
        print(f"\nQuery: '{query}'")
        try:
            result = enhancer.enhance_query(query)
            print(f"  Type: {result['query_type']}")
            if 'response' in result:
                print(f"  Response: {result['response'][:50]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 NLP Query System Test")
    print("=" * 50)
    
    # Load env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment loaded")
    except:
        print("⚠️  No dotenv, using system environment")
    
    # Run tests
    test_env_loading()
    enhancer = test_llm_setup()
    test_local_parsing()
    test_llm_queries(enhancer)
    test_simple_responses()
    
    print("\n🎯 Test completed!")