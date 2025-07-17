# CLM Portfolio Tracker

A streamlined Python CLI application for monitoring cryptocurrency liquidity mining positions with real-time price tracking.

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

**💡 Pro Tip**: Use the integrated position editor ([e] option in the main menu) to access a custom GPT tool that helps format your position data correctly.

### Run the Application
```bash
python CLM.py
```

The app will auto-detect your CSV files and start monitoring your positions with live price updates.

## Core Features

### Position Monitoring
- **Live Price Updates**: Real-time price refresh on each view
- **Visual Range Indicators**: See if positions are in-range at a glance
- **Strategy Split View**: Separate Long and Neutral position tracking
- **Multi-Chain Support**: SOL, ETH, SUI, BASE, ARB positions

### Dashboard Views
1. **[1] Active Positions** - Main dashboard with live prices and range sliders
2. **[2] Performance** - Historical returns and token performance analysis
3. **[3] Allocation** - Portfolio distribution breakdown
4. **[4] Transactions** - Transaction history view
5. **[e] Edit Positions** - Link to custom GPT tool for position data formatting

## Project Structure

```
CLM.py                     # Main CLI application
clm_data.py               # Simplified data processing and API integration
requirements.txt          # Python dependencies

views/                    # Display modules
├── active_positions.py      # Main dashboard
├── performance.py           # Combined performance analysis
├── allocation_breakdown.py  # Portfolio analysis
└── transactions.py          # Transaction history

data/                     # Your data files
├── Tokens_Trade_Sheet - Long Positions.csv
├── Tokens_Trade_Sheet - Neutral Positions.csv
└── JSON_out/            # Generated JSON files

archive/                  # Legacy components
├── views/                  # Old view files
├── old_files/             # Previous versions
├── tests/                 # Test files
└── utils/                 # Archived utilities
```

## Configuration

### Environment Variables (Optional)
Create a `.env` file from the template for optional features:
```bash
cp .env.example .env
# Edit .env with your credentials (never commit this file!)
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

## Technical Details

### Data Processing
1. CSV files → JSON conversion with simplified parsing
2. Live price fetching from DefiLlama + CoinGecko APIs  
3. Position status calculation (in-range vs out-of-range)
4. Real-time refresh on each view

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

## Architecture Changes

### Simplified Design
The codebase has been streamlined for better maintainability:
- **Consolidated Views**: Combined historical returns and token performance
- **Unified Data Manager**: Single parsing method for all value types
- **Simplified CLI**: 4-view menu system
- **Archived Legacy**: Complex V2 system and utilities moved to `archive/`

### Archive Structure
Legacy components have been moved to `archive/` for reference:
- Advanced V2 system with normalized data models
- Complex market analysis and NLP features
- Comprehensive test suites
- Utility functions for formatting and calculations

## Contributing

1. Follow existing code patterns in `views/` modules
2. Add error handling for API integrations
3. Test with sample data before production use
4. Update documentation for new features

For questions or issues, check the existing code structure and API integrations in the main application files.

## Security

### 🔒 Important Security Notes

**Never commit sensitive information:**
- The `.env` file is in `.gitignore` and should never be committed
- Use `.env.example` as a template only
- Store actual credentials only in your local `.env` file

**Safe practices:**
- Copy `.env.example` to `.env` and add real credentials
- Never add API keys directly to source code
- Rotate credentials if accidentally exposed
- Keep wallet addresses private unless intended to be public

### 🛡️ Environment File Security
```bash
# ✅ Safe - template file
.env.example

# ❌ NEVER commit this file
.env
```

The application works without any API keys - they are only needed for optional features.