# Pricing Data Sources Research & Recommendations

## Current Token Requirements

Based on your existing codebase analysis, you're currently tracking:
- **Crypto tokens**: SOL, USDC, ETH, BTC, ORCA, RAY, JLP, WETH, USDT
- **FX pairs**: CAD/USD (requested)
- **Update frequency**: Hourly refresh desired
- **Historical data**: 1+ years required

## Cryptocurrency Pricing APIs

### 1. CoinGecko API

**Pros:**
- Most generous free tier: 30 calls/minute, 10,000 calls/month
- Covers 8M+ coins across 232 networks
- Excellent coverage of your tokens (all supported)
- Strong historical data availability
- Reliable uptime and performance
- Already partially implemented in your codebase

**Cons:**
- Rate limits may be restrictive for frequent updates
- Pro features require paid subscription

**Pricing:**
- Free: 30 calls/min, 10k/month
- Analyst ($49/month): 500 calls/min, 1M/month
- Lite ($99/month): 500 calls/min, 10M/month

**Historical Data:** Available for all major tokens, varies by coin launch date

### 2. CoinMarketCap API

**Pros:**
- Enterprise-grade reliability
- Supports 93 fiat currencies + 4 precious metals
- Historical data back to 2013
- 1-minute update frequency
- Excellent API documentation

**Cons:**
- No meaningful free tier
- More expensive than competitors
- Primarily focused on large-cap tokens

**Pricing:**
- Basic ($39/month): 10,000 calls/month
- Standard ($99/month): 100,000 calls/month
- Professional ($399/month): 1M calls/month

**Historical Data:** Comprehensive, dating back to 2013

### 3. Alpha Vantage

**Pros:**
- Multi-asset coverage (crypto, forex, stocks)
- Historical data back to 2011 for Bitcoin
- 50+ technical indicators included
- Good for combined crypto/forex needs

**Cons:**
- Very restrictive free tier (500 requests/day)
- Limited crypto coverage compared to specialists
- Focus more on traditional finance

**Pricing:**
- Free: 500 requests/day
- Premium plans start at $25/month

### 4. DefiLlama API

**Pros:**
- Comprehensive DeFi-focused data aggregator
- Covers exotic tokens not available on traditional exchanges
- Combines multiple pricing sources (CoinGecko, DEX pools, bridge assets)
- Strong methodology for hard-to-price tokens
- Both free and Pro tiers available
- Historical data access included
- Open-source and transparent methodology
- Hourly updates for most protocols
- No API key required for free tier

**Cons:**
- Primarily focused on DeFi tokens (may miss some CEX-only tokens)
- Less comprehensive than pure price APIs for traditional crypto
- Pro tier pricing not clearly disclosed
- Relatively newer compared to established providers

**Pricing:**
- Free tier: Full access to basic endpoints, no API key required
- Pro tier: Enhanced performance, higher limits, advanced endpoints (pricing undisclosed)

**Historical Data:** Multi-year historical data available, supports timestamp queries

**Unique Features:**
- Prices LP tokens through underlying assets
- Handles bridge assets and wrapped tokens intelligently  
- On-chain pricing for tokens missing from CEX/CoinGecko
- Protocol-specific adapters for accurate DeFi pricing

### 5. Solana-Specific DEX APIs

**Jupiter API**
- **Pros**: Best rates through DEX aggregation, real-time Solana prices, free to use
- **Cons**: Solana ecosystem only, may lack historical data depth
- **Best for**: Real-time SOL, ORCA, RAY, JLP prices

**Raydium API** 
- **Endpoint**: `https://api.raydium.io/v2/main/price`
- **Pros**: Direct DEX pricing, real-time updates, free
- **Cons**: Limited to Raydium liquidity pools

**Bitquery Solana API**
- **Pros**: Comprehensive DEX data, WebSocket support, historical data
- **Cons**: Complex pricing structure, may be overkill

## Foreign Exchange (FX) APIs

### 1. ExchangeRate.host (Recommended for FX)

**Pros:**
- Completely free with no API key required
- CAD/USD pair supported
- Historical data available
- High reliability (handles thousands of requests/second)
- Simple JSON API

**Cons:**
- Limited to basic exchange rate data
- 60-minute update frequency

**Endpoint Example**: `https://api.exchangerate.host/latest?base=CAD&symbols=USD`

### 2. Fixer.io

**Pros:**
- 170+ currencies including CAD/USD
- 60-second updates on paid plans
- Reliable data sourced from banks/ECB
- Good historical data coverage

**Cons:**
- Free tier limited to 100 requests/month
- Requires API key

**Pricing:**
- Free: 100 requests/month
- Basic ($10/month): 1,000 requests/month

### 3. Alpha Vantage FX

**Pros:**
- 20+ years of historical forex data
- Multiple timeframes (1-min to monthly)
- Combined with crypto API

**Cons:**
- Same 500 requests/day limit applies to all endpoints
- May not be sufficient for hourly updates

## Recommended Architecture

### Updated Hybrid Approach - Best Value & Coverage

**Primary Crypto Data Source: DefiLlama + CoinGecko**
- **DefiLlama Free** for DeFi tokens (SOL, ORCA, RAY, JLP) with superior methodology
- **CoinGecko Free** for traditional crypto (BTC, ETH, USDC, USDT)
- Multi-year historical data from both sources
- Combined free tiers provide excellent coverage

**Solana-Specific Real-Time: Jupiter/Raydium APIs**
- Use for real-time SOL, ORCA, RAY, JLP prices
- Supplement historical data with current DEX pricing
- Free and specifically optimized for Solana ecosystem

**FX Data Source: ExchangeRate.host**
- Free and reliable for CAD/USD rates
- Hourly updates sufficient for FX
- No API key management required

### Alternative Premium Approach

**For Production with Budget**
- **DefiLlama Pro** for comprehensive DeFi data with enhanced performance
- **CoinGecko Analyst** ($49/month) for traditional crypto with higher limits
- Combined approach provides maximum coverage and reliability

### Implementation Strategy

```python
# Updated data sources hierarchy:
1. DefiLlama API (DeFi tokens + multi-year historical data)
2. CoinGecko API (traditional crypto + historical data)
3. Jupiter/Raydium APIs (Solana-specific real-time prices)
4. ExchangeRate.host (FX rates)
5. Fallback to cached/demo prices if all fail
```

### Cost Analysis

**Development Phase (Updated):**
- DefiLlama Free: $0
- CoinGecko Free: $0
- Jupiter/Raydium: $0  
- ExchangeRate.host: $0
- **Total: $0/month**

**Production Phase Options:**

**Budget Option:**
- DefiLlama Free + CoinGecko Free: $0/month
- Excellent coverage with combined free tiers

**Premium Option:**
- DefiLlama Pro + CoinGecko Analyst: ~$49-99/month
- Maximum performance and data coverage

### DefiLlama Advantages for Your Use Case

**Why DefiLlama is Valuable for Multi-Year Data:**
- **Superior DeFi Token Coverage**: Handles exotic tokens like JLP that may not be on CoinGecko
- **Intelligent Pricing**: Uses DEX liquidity, LP decomposition, and bridge asset mapping
- **Historical Depth**: Multi-year data with timestamp-based queries
- **Free Tier Generosity**: No API key required, comprehensive access
- **Transparency**: Open-source methodology, verifiable calculations
- **DeFi-Native**: Built specifically for DeFi ecosystem needs

## Implementation Recommendations

### Phase 1: Enhanced Free Implementation (Updated)
1. **Add DefiLlama API** for DeFi tokens (SOL, ORCA, RAY, JLP) with historical data
2. **Optimize CoinGecko usage** for traditional crypto (BTC, ETH, USDC, USDT)
3. **Add Jupiter API** for real-time Solana DEX prices
4. **Integrate ExchangeRate.host** for CAD/USD rates
5. **Implement intelligent caching** to maximize all free tier limits
6. **Add fallback logic** between DefiLlama and CoinGecko for overlapping tokens

### Phase 2: Production Scaling
1. **Consider DefiLlama Pro** for enhanced DeFi data performance
2. **Add historical data persistence** for multi-year analysis capabilities
3. **Implement data validation** across multiple sources
4. **Add monitoring and alerting** for API failures
5. **Create data export capabilities** for offline analysis

### Key Technical Considerations

1. **Rate Limit Management**: Implement exponential backoff and request queuing
2. **Data Persistence**: Store historical data locally to reduce API calls
3. **Fallback Strategy**: Multiple data sources prevent single points of failure
4. **Caching**: Intelligent caching reduces costs and improves performance
5. **Error Handling**: Graceful degradation when APIs are unavailable

## DefiLlama API Endpoints for Implementation

Based on the research, here are key DefiLlama endpoints for your use case:

### Token Price Endpoints
```python
# Current prices
GET https://coins.llama.fi/prices/current/{coin_ids}

# Historical prices (supports timestamp queries)
GET https://coins.llama.fi/prices/historical/{timestamp}/{coin_ids}

# Example coin IDs for your tokens:
# SOL: "coingecko:solana" 
# ORCA: "coingecko:orca"
# RAY: "coingecko:raydium"
# JLP: May need specific chain:address format
```

### Data Structure
```json
{
  "coins": {
    "coingecko:solana": {
      "price": 98.50,
      "symbol": "SOL",
      "timestamp": 1640995200,
      "confidence": 0.99
    }
  }
}
```

## Final Recommendation

**DefiLlama is an excellent addition** to your pricing strategy, especially for multi-year historical data:

1. **Superior DeFi Coverage**: Better handling of tokens like JLP, ORCA, RAY
2. **Free Historical Data**: Multi-year access without API key requirements
3. **Intelligent Methodology**: DEX-aware pricing for accurate DeFi token values
4. **Zero Cost Start**: Perfect for development and testing
5. **Complement Existing**: Works alongside your current CoinGecko setup

**Updated Recommended Stack:**
- **DefiLlama** (primary for DeFi tokens + historical analysis)
- **CoinGecko** (backup + traditional crypto)
- **Jupiter/Raydium** (real-time Solana prices)
- **ExchangeRate.host** (CAD/USD FX)

This approach provides the best balance of cost, reliability, and comprehensive data coverage for your specific use case while enabling sophisticated multi-year analysis.