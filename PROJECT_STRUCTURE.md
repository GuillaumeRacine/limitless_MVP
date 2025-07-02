# CLM Portfolio Tracker - Project Structure

## Core Application Files
```
CLM.py              # Main CLI controller and entry point
clm_data.py         # Data manager for CSV processing and price fetching
requirements.txt    # Python dependencies
.env               # Environment variables (API keys)
```

## Views (Display Layer)
```
views/
├── active_positions.py     # Main dashboard with position monitoring
├── transactions.py         # Transaction history and analysis
├── historical_returns.py   # Performance tracking
├── allocation_breakdown.py # Portfolio allocation analysis
├── prices.py              # Real-time pricing dashboard
├── historical_performance.py # Token performance analysis
└── market_analysis.py     # DeFiLlama integration with AI queries
```

## Utilities
```
utils/
├── defillama_client.py    # DeFiLlama API client
├── formatting.py          # Shared formatting functions
├── calculations.py        # Common calculations
└── nlp_query.py          # Natural language query processor
```

## Data
```
data/
├── Tokens_Trade_Sheet - Long Positions.csv     # Long strategy positions
├── Tokens_Trade_Sheet - Neutral Positions.csv  # Neutral strategy positions
└── JSON_out/                                   # Generated JSON files
    ├── clm_long.json
    ├── clm_neutral.json
    ├── clm_closed.json
    ├── clm_transactions.json
    ├── clm_metadata.json
    └── csv_tracking.json
```

## Documentation
```
docs/
├── guides/                    # User guides
├── API_REFERENCE.md          # API documentation
├── TRANSACTION_SYSTEM.md     # Transaction system docs
└── TRANSACTION_USAGE_GUIDE.md # Transaction usage guide
```

## Tests
```
tests/
├── test_nlp.py              # NLP system tests
├── test_full_nlp.py         # Full integration tests
└── debug_fees.py            # Debugging utilities
```

## Key Features

### 🎯 Core Functionality
- **CSV Import**: Automatic detection and processing of position CSV files
- **Real-time Pricing**: Multi-source API integration (DeFiLlama, CoinGecko, FX rates)
- **Position Monitoring**: Live range status for CLM and perpetual positions
- **Multi-chain Support**: SOL, ETH, SUI, BASE, ARB transaction tracking

### 🤖 AI-Powered Features
- **Natural Language Queries**: Ask questions like "What's the TVL on Solana?"
- **Smart Parsing**: Understands filters, chains, percentages, and amounts
- **Multi-Provider Support**: OpenAI GPT, Anthropic Claude, local fallback

### 📊 Views & Analytics
- **Strategy Split View**: Separate Long and Neutral position tracking
- **Transaction Analysis**: Multi-chain transaction history with platform detection
- **Performance Tracking**: Historical returns and token performance
- **Portfolio Breakdown**: Allocation analysis and real-time prices

### 🔄 Automation
- **Auto-refresh**: 60-minute price updates with countdown timer
- **CSV Monitoring**: Detects changes and updates JSON automatically
- **Error Handling**: Graceful fallbacks for API failures