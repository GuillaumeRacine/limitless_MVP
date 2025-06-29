# CLM Portfolio Tracker

A streamlined Python CLI application for monitoring cryptocurrency liquidity mining positions across DeFi protocols. Features automatic 60-minute price refresh, real-time position tracking, and comprehensive portfolio analysis.

## Project Overview

The CLM Portfolio Tracker helps cryptocurrency traders monitor their liquidity mining positions by:
- **Auto-refresh**: Automatic price updates every 60 minutes while running
- **CSV Import**: Direct import of position data from trading sheets
- **Multi-API Pricing**: Live prices from DefiLlama, CoinGecko, and FX APIs
- **Visual Indicators**: Range sliders showing position status at a glance
- **Portfolio Analysis**: Returns, fees, performance metrics, and allocation breakdowns

## Features

### 🎯 Position Monitoring
- **Auto-Refresh**: 60-minute automatic price updates with countdown timer
- **Strategy Split View**: Separate tracking for Long and Neutral strategies  
- **Range Visualization**: Visual sliders showing current price vs min/max ranges
- **Status Indicators**: Immediate feedback on in-range vs out-of-range positions
- **Live Price Integration**: Real-time prices from DefiLlama and CoinGecko APIs

### 📊 Multiple Views
1. **Active Positions**: Main dashboard with range sliders, status, and integrated token performance
2. **Transactions**: Historical transaction analysis
3. **Historical Returns**: Performance tracking over time
4. **Allocation Breakdown**: Portfolio distribution analysis
5. **Prices**: Real-time pricing data with FX rates
6. **Token Performance**: Historical returns across multiple timeframes (1D-5YR)

### 💰 Enhanced Pricing System
- **Multi-Source Data**: DefiLlama (DeFi focus) + CoinGecko (traditional crypto)
- **Advanced Pair Calculations**: Ratio pricing for wrapped tokens (WBTC/SOL, cbBTC/SOL, whETH/SOL)
- **Pool Token Support**: Special handling for liquidity pool tokens (JLP/SOL inversion)
- **Perpetual Positions**: Single-side range monitoring with liquidation tracking
- **FX Rate Support**: CAD/USD conversion rates with live updates
- **Intelligent Fallback**: Graceful degradation when APIs unavailable
- **Real-time Timestamps**: Price refresh tracking with display timestamps

## Architecture

### Core Components

```
CLM.py                 # Main CLI controller and menu system
clm_data.py           # Data manager for CSV import, JSON persistence, API calls
views/                # Display modules for different data presentations
├── active_positions.py    # Main position monitoring with range visualization
├── allocation_breakdown.py # Portfolio allocation analysis
├── historical_returns.py  # Performance tracking
├── transactions.py        # Transaction history
└── prices.py             # Real-time pricing dashboard
```

### Data Flow

1. **CSV Import**: Raw position data from trading sheets
2. **JSON Persistence**: Processed data stored in `data/JSON_out/`
3. **API Integration**: Live prices from DefiLlama/CoinGecko/FX APIs
4. **Status Updates**: Range calculations and position status determination
5. **View Rendering**: Formatted CLI displays with highlighting and sliders

## Getting Started

### Prerequisites

- Python 3.8+
- Required packages: `pandas`, `requests`

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Limitless_MVP
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Prepare your data:
   - Place CSV files at: `data/Tokens_Trade_Sheet - Long Positions.csv`
   - Place CSV files at: `data/Tokens_Trade_Sheet - Neutral Positions.csv`

### Running the Application

```bash
# Auto-detect mode (recommended)
python CLM.py

# Manual conversion then monitor
python CLM.py convert <neutral_csv> <long_csv>
python CLM.py monitor
```

## CSV Data Format

Your CSV files should contain the following columns:

### Required Columns
- `Position Details`: Platform and token pair (e.g., "Raydium | SOL/USDC")
- `Entry Date`: Position opening date
- `Entry Value (cash in)` / `Total Entry Value`: Initial investment amount
- `Min Range`: Lower boundary of liquidity range
- `Max Range`: Upper boundary of liquidity range
- `Days #`: Days position has been active

### Optional Columns
- `Exit Date`: Position closing date (for closed positions)
- `Exit Value`: Final position value
- `Net Return`: Overall return percentage
- `Claimed Yield Value`: Fees/rewards collected
- `IL`: Impermanent loss percentage
- `Transaction Fees`: Fee percentages
- `Yield APR`: Annual percentage rate

## API Integration

### Pricing Sources

1. **DefiLlama API** (Primary for DeFi tokens)
   - Endpoint: `https://coins.llama.fi/prices/current/{coin_ids}`
   - Best for: SOL, ORCA, RAY, JLP and other DeFi tokens
   - Features: No API key required, excellent DeFi coverage

2. **CoinGecko API** (Backup for traditional crypto)
   - Endpoint: `https://api.coingecko.com/api/v3/simple/price`
   - Best for: BTC, ETH, USDC, USDT
   - Rate Limits: 30 calls/minute (free tier)

3. **ExchangeRate API** (FX rates)
   - Endpoint: `https://open.er-api.com/v6/latest/USD`
   - Purpose: CAD/USD conversion rates
   - Features: Free, no API key required

### Supported Tokens

Currently configured for:
- **Major Crypto**: BTC, ETH, SOL, SUI
- **Stablecoins**: USDC, USDT
- **DeFi Tokens**: ORCA, RAY, JLP
- **Wrapped Tokens**: WETH, WBTC, cbBTC, whETH
- **Position Types**: CLM (Concentrated Liquidity), Perpetuals (single-side monitoring)

## Development Guide

### Key Classes

**CLMDataManager** (`clm_data.py`)
- Handles CSV import and JSON persistence
- Manages API calls for live pricing
- Calculates position status and range indicators
- Methods:
  - `update_positions()`: Import/update from CSV
  - `get_token_prices()`: Fetch live prices
  - `refresh_prices_and_status()`: Update all data

**ActivePositionsView** (`views/active_positions.py`)
- Main position display with range visualization
- Creates visual sliders and status indicators
- Methods:
  - `display()`: Main strategy split view
  - `display_strategy_detail()`: Detailed position breakdown
  - `_create_simple_slider()`: Visual range indicator

### Display Format

**Position Table Layout:**
```
Position             Entry USD  %     Chain  Platform   Min Range  Price      Max Range  Status       Days  Return   Range Slider
------------------------------------------------------------------------------------------------------------------------------------------
SOL/USDC             $23,190    41.8% SOL    CLM        $130.00    $138.68    $158.75    Active       3     N/A      ├──●──────┤
JLP/SOL              $22,509    16.0% Sol    Orca       $0.03      $0.03      $0.03      Active       3     N/A      ├──────●──┤
SOL/USDC             $1,346     2.4%  SOL    Perp       N/A        $138.68    $159.34    Active       3     N/A      ───────────
WBTC/SOL             $17,754    12.7% Sol    Orca       $628.00    $744.33    $767.00    Active       3     N/A      ├───────●─┤
```

**Visual Indicators:**
- `├──────●──┤` = Price within range (active)
- `◄─────────┤` = Price below range 
- `├─────────►` = Price above range
- `⮘─────────┤` = Price far below range (50%+ deviation)

### Adding New Features

1. **New View Module**:
   - Create file in `views/` directory
   - Implement `display()` method
   - Add to `CLM.py` menu system

2. **New API Integration**:
   - Add method to `CLMDataManager`
   - Update `get_token_prices()` to include new source
   - Add error handling and fallback logic

3. **New Token Support**:
   - Update token mappings in `_fetch_defillama_prices()`
   - Add CoinGecko mapping if needed
   - Test with sample data

### Testing

No formal test framework currently implemented. Manual testing approach:

1. Use sample CSV files with known data
2. Verify position parsing and calculations
3. Test CLI navigation and display formatting
4. Validate API integrations with mock responses

### Configuration

Key configuration files:
- `requirements.txt`: Python dependencies
- `CLAUDE.md`: AI assistant context and commands
- `prices.md`: API research and recommendations

## Data Storage

### JSON Files (`data/JSON_out/`)
- `clm_long.json`: Long strategy positions
- `clm_neutral.json`: Neutral strategy positions  
- `clm_closed.json`: Closed/exited positions
- `clm_metadata.json`: Import timestamps and file hashes
- `clm_positions.json`: Combined position data (if exists)

### CSV Files (`data/`)
- Source trading sheets with position data
- Auto-detected for changes via file hash comparison
- Supports custom file paths via command line

## CLI Navigation

**Main Menu Options:**
- `[1]` Active Positions - Main dashboard with integrated token performance
- `[2]` Transactions - Transaction history
- `[3]` Historical Returns - Performance analysis
- `[4]` Allocation Breakdown - Portfolio distribution
- `[5]` Prices - Real-time pricing dashboard
- `[6]` Token Performance - Historical returns across multiple timeframes
- `[L]` Long Strategy Details
- `[N]` Neutral Strategy Details
- `[r]` Refresh data
- `[q]` Quit application

**Enhanced Features:**
- Real-time price refresh timestamps displayed at bottom
- Automatic token pair normalization for different CSV formats
- Intelligent position status for CLM and Perpetual positions

## Troubleshooting

### Common Issues

**No positions showing:**
- Check CSV file paths and format
- Verify Position Details column contains data
- Run with `convert` command to rebuild JSON files

**Price data unavailable:**
- Check internet connection
- API rate limits may be exceeded
- Application falls back to demo prices automatically

**Display formatting issues:**
- Ensure terminal width is at least 120 characters
- Some terminals may not support Unicode slider characters

### Performance Considerations

- API calls are cached per session
- JSON files updated incrementally (not full rebuild)
- Position status calculated only when prices change
- Rate limiting implemented for all API sources

## Contributing

When adding features:
1. Follow existing code patterns and naming conventions
2. Update both main and detailed views consistently  
3. Add appropriate error handling and fallbacks
4. Test with various data scenarios
5. Update documentation and help text

## License

[Add your license information here]

## Support

For issues or questions:
- Check the troubleshooting section above
- Review API documentation in `prices.md`
- Examine sample data format requirements