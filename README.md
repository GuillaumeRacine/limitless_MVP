# CLM Portfolio Tracker

A streamlined Python CLI application for monitoring cryptocurrency liquidity mining positions with real-time price tracking and AI-powered market analysis.

## Quick Start

### Installation
```bash
git clone <repository-url>
cd Limitless_MVP
pip install -r requirements.txt
```

### Setup Data Files
Place your CSV files in the `data/` folder:
- `data/Tokens_Trade_Sheet - Long Positions.csv`
- `data/Tokens_Trade_Sheet - Neutral Positions.csv`

### Run the Application
```bash
python CLM.py
```

The app will auto-detect your CSV files and start monitoring your positions with live price updates every 60 minutes.

## Core Features

### Position Monitoring
- **Live Price Updates**: 60-minute auto-refresh with countdown timer
- **Visual Range Indicators**: See if positions are in-range at a glance
- **Strategy Split View**: Separate Long and Neutral position tracking
- **Multi-Chain Support**: SOL, ETH, SUI, BASE, ARB positions

### Dashboard Views
1. **[1] Active Positions** - Main dashboard with live prices and range sliders
2. **[2] Transactions** - Transaction history analysis
3. **[3] Historical Returns** - Performance tracking over time
4. **[4] Allocation Breakdown** - Portfolio distribution
5. **[5] Prices** - Real-time pricing dashboard for major tokens
6. **[6] Market Analysis** - AI-powered DeFi insights with natural language queries

### AI Market Analysis
Ask questions in natural language:
- "What's the TVL on Solana?"
- "Show me the top pools on Arbitrum" 
- "What are the best yield opportunities?"

Supports OpenAI GPT and Anthropic Claude APIs.

## Project Structure

```
CLM.py                     # Main CLI application
clm_data.py               # Data processing and API integration
requirements.txt          # Python dependencies
.env                      # API keys (create your own)

views/                    # Display modules
├── active_positions.py      # Main dashboard
├── transactions.py          # Transaction history
├── historical_returns.py    # Performance tracking
├── allocation_breakdown.py  # Portfolio analysis
├── prices.py               # Real-time prices
└── market_analysis.py      # AI-powered insights

utils/                    # Shared utilities
├── formatting.py           # Display formatting
├── calculations.py         # Common calculations
├── defillama_client.py     # DeFi data API
└── nlp_query.py           # Natural language processing

data/                     # Your data files
├── Tokens_Trade_Sheet - Long Positions.csv
├── Tokens_Trade_Sheet - Neutral Positions.csv
└── JSON_out/            # Generated JSON files
```

## Configuration

### API Keys (Optional)
Create a `.env` file for AI features:
```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Supported Tokens
- **Major Crypto**: BTC, ETH, SOL, SUI
- **Stablecoins**: USDC, USDT  
- **DeFi Tokens**: ORCA, RAY, JLP
- **Wrapped Tokens**: WBTC, cbBTC, whETH

## CSV Data Format

### Required Columns
Your position CSV files need these columns:
- `Position Details`: Platform and token pair (e.g., "Raydium | SOL/USDC")
- `Entry Date`: Position opening date
- `Total Entry Value` or `Entry Value (cash in)`: Investment amount
- `Min Range`: Lower price boundary (CLM positions only)
- `Max Range`: Upper price boundary
- `Days #`: Days position has been active

### Optional Columns  
- `Exit Date`: For closed positions
- `Net Return`: Performance percentage
- `Claimed Yield Value`: Collected fees/rewards
- `IL`: Impermanent loss percentage

## Usage Examples

### Position Monitoring
The main dashboard shows your positions with visual range indicators:
```
Position         Entry USD   Chain  Platform   Price     Range Status    Days
SOL/USDC        $23,190     SOL    CLM        $138.68   ├──●──────┤     3
JLP/SOL         $22,509     SOL    Orca       $0.03     ├──────●──┤     3  
SOL/USDC        $1,346      SOL    Perp       $138.68   ───────────     3
```

### AI Market Analysis
Ask natural language questions:
```bash
> "What's the current TVL on Solana DEXs?"
> "Show me yield opportunities above 10%"  
> "What are the top performing pools this week?"
```

## Troubleshooting

### Common Issues

**No positions showing**
- Verify CSV files are in `data/` folder with correct names
- Check that `Position Details` column contains platform/token data
- Run the app - it will auto-detect and convert CSV files

**Price data unavailable**
- Check internet connection for API calls
- App falls back to demo prices automatically
- Rate limits: DefiLlama (unlimited), CoinGecko (30/min)

**AI features not working**
- Create `.env` file with your API keys
- Both OpenAI and Anthropic keys are optional
- App works without AI features for basic monitoring

## Technical Details

### Data Processing
1. CSV files → JSON conversion with auto-detection
2. Live price fetching from DefiLlama + CoinGecko APIs  
3. Position status calculation (in-range vs out-of-range)
4. 60-minute auto-refresh cycle

### Pricing Logic
- **Standard pairs** (SOL/USDC): Uses base token price
- **Wrapped tokens** (WBTC/SOL): Ratio calculation  
- **Pool tokens** (JLP/SOL): Special inversion handling
- **Perpetuals**: Single-side range monitoring only

### Multi-Chain Support
- **Solana**: Native DEX integration (Raydium, Orca)
- **Ethereum**: Layer 1 + Layer 2 support
- **SUI**: Native blockchain integration
- **Base/Arbitrum**: Layer 2 scaling solutions

## Contributing

1. Follow existing code patterns in `views/` modules
2. Add error handling for API integrations
3. Test with sample data before production use
4. Update documentation for new features

For questions or issues, check the existing code structure and API integrations in the `utils/` folder.