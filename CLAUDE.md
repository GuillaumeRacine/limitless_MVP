# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CLM Portfolio Tracker is a streamlined Python CLI application for monitoring cryptocurrency liquidity mining positions with real-time price tracking and AI-powered market analysis. It tracks Long and Neutral strategy positions across multiple chains and platforms through CSV import and 60-minute auto-refresh cycles.

## Architecture

The application follows a clean modular MVC-like pattern:

### Core Application
- **`CLM.py`** - Main CLI controller with interactive menu system
- **`clm_data.py`** - Core data manager handling CSV imports, JSON persistence, and price fetching

### Views (Display Layer)
- **`views/active_positions.py`** - Live position monitoring with range status and integrated token performance
- **`views/allocation_breakdown.py`** - Portfolio allocation analysis
- **`views/historical_returns.py`** - Performance tracking
- **`views/historical_performance.py`** - Multi-timeframe token performance analysis
- **`views/prices.py`** - Real-time pricing dashboard with FX rates
- **`views/transactions.py`** - Transaction history

### Utilities (Shared Components)
- **`utils/formatting.py`** - Shared formatting utilities (currency, percentages, numbers)
- **`utils/calculations.py`** - Common calculation functions (totals, averages, allocations)

## Key Data Flow

1. CSV files contain raw position data (`data/Tokens_Trade_Sheet - Long Positions.csv`, `data/Tokens_Trade_Sheet - Neutral Positions.csv`)
2. CLMDataManager converts CSVs to JSON format in `data/JSON_out/` directory with automatic token pair normalization
3. Position status is updated with live prices from DefiLlama + CoinGecko APIs + FX rates
4. Advanced pricing calculations handle wrapped tokens, pool tokens, and perpetual positions
5. Views render formatted displays with real-time timestamps and visual range indicators

## Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
# Auto-detect mode (recommended)
python CLM.py

# Manual conversion then monitor
python CLM.py convert <neutral_csv> <long_csv>
python CLM.py monitor

# Direct monitor (assumes JSON files exist)
python CLM.py monitor
```

### Data Management
- Place CSV files at default paths: `data/Tokens_Trade_Sheet - Neutral Positions.csv` and `data/Tokens_Trade_Sheet - Long Positions.csv`
- Application auto-detects CSV changes and updates JSON files
- JSON files are stored in `data/JSON_out/` directory

## Development Notes

### Position States
- **Active positions**: Split between Long and Neutral strategies
- **Closed positions**: Moved automatically when exit date or status indicates closure
- **Range status**: Tracks if current price is within min/max range for liquidity positions

### Data Structure
Each position includes:
- Strategy type (long/neutral)
- Platform and token pair information
- Entry/exit values and dates
- Performance metrics (returns, IL, fees)
- Range boundaries and current status (note: true for CLM positions, perpetuals only have a max range and a 0 min range)
- Unique positions IDsmultiple source for tracking updates

### Enhanced Price Integration
- **Multi-Source APIs**: DefiLlama (primary for DeFi), CoinGecko (backup), ExchangeRate API (FX)
- **Advanced Calculations**: 
  - Ratio pricing for wrapped tokens (WBTC/SOL = BTC_price / SOL_price)
  - Pool token inversions (JLP/SOL = JLP_USD / SOL_USD)
  - Single-side perpetual monitoring (only max range matters)
- **Token Pair Normalization**: Automatic conversion of "SOL + USD" → "SOL/USDC", "SOL short" → "SOL/USDC"
- **Intelligent Fallback**: Demo prices with graceful degradation
- **Real-time Timestamps**: Price refresh tracking displayed to user
- **Supported Tokens**: BTC, ETH, SOL, SUI, USDC, USDT, ORCA, RAY, JLP, WBTC, cbBTC, whETH

### Testing
No formal test framework is currently implemented. Manual testing involves:
1. Using sample CSV files with known data
2. Verifying position parsing and calculations
3. Testing CLI navigation and display formatting

When adding new features, ensure they follow the existing pattern of separating data management (CLMDataManager) from display logic (Views).

## Recent Enhancements (June 2025)

### Position Status Logic
- **CLM Positions**: Full range monitoring (min_range to max_range) with visual sliders
- **Perpetual Positions**: Single-side monitoring (price vs max_range only)
  - `perp_active`: Price below liquidation level → Status: "Active"
  - `perp_closed`: Price above liquidation level → Status: "Closed"

### Pricing Calculations
- **Standard Pairs**: Direct token price lookup (SOL/USDC uses SOL price)
- **Wrapped Tokens**: Ratio calculations (WBTC/SOL = BTC_price ÷ SOL_price)
- **Pool Tokens**: Special handling (JLP/SOL = JLP_USD ÷ SOL_USD)
- **Token Normalization**: CSV parsing converts various formats to consistent token/USDC pairs

### Display Features
- **Integrated Performance**: Token returns (1D-5YR) displayed below position tables
- **Entry Values & Percentages**: Shows entry USD amounts and strategy allocation percentages
- **Chain Information**: Displays blockchain (SOL, SUI, BASE, ARB) for each position
- **Real-time Timestamps**: Price refresh timestamps shown at bottom of displays

### CLI Menu System
Includes 7 main views plus strategy details and natural language querying:
- [1] Active Positions (with integrated token prices)
- [2] Transactions
- [3] Historical Returns  
- [4] Allocation Breakdown
- [5] Prices (real-time dashboard)
- [6] Token Performance (standalone historical view)
- [7] DefiLlama Dashboard (with AI-powered natural language queries)
- [L] Long Strategy Details
- [N] Neutral Strategy Details

## Transaction System Enhancements (December 2025)

### Multi-Chain Transaction Support
- **SUI Integration**: Full SUI blockchain transaction processing with RPC validation
- **Enhanced Data Processing**: 380+ SUI transactions imported with platform detection
- **Cross-Chain Tracking**: SOL, ETH, SUI, Base, Arbitrum, Optimism transaction support

### Advanced Platform Detection
- **84.7% Platform Identification Rate**: Enhanced from ~53% through intelligent detection
- **Contract Address Mapping**: Comprehensive DEX and protocol contract database
- **Pattern Recognition**: Transaction type and chain-specific platform inference
- **1,391 Transactions Enhanced**: Massive improvement in platform clarity

### Enhanced Transaction View
- **Dual-Column Display**: Separate "Token Units" and "USD Value" columns
- **Smart Filtering**: Automatically excludes approve transactions and zero-value transfers
- **Intelligent Formatting**: K/M notation for large amounts, appropriate decimals for small amounts
- **USD Integer Display**: Clean integer USD values when token units > 0.00

### Blockchain Validation Infrastructure
- **SUI RPC Client** (`sui_api_validator.py`): Full blockchain validation and data enhancement
- **ETH RPC Client** (`eth_api_validator.py`): Ethereum ecosystem transaction validation  
- **SOL RPC Client** (`sol_api_validator.py`): Solana program and transaction analysis
- **Data Enhancement Pipeline**: Automatic USD value calculation and platform detection

### Transaction Analysis Tools
- **Comprehensive Analytics**: Platform efficiency, gas costs, and strategy breakdowns
- **Unclear Transaction Detection**: Automated identification of transactions needing review
- **Historical Price Integration**: USD value calculation at transaction time
- **Multi-Format Support**: CSV imports from various DEX and wallet sources

## Data Management System V2 (January 2025)

### New Normalized Architecture
A new data management system has been implemented alongside the existing CSV import method for testing and future production use.

#### Core Components
- **`data_models.py`**: Normalized data models with proper relationships using dataclasses and enums
- **`data_manager_v2.py`**: Full CRUD operations for all entities with JSON-based storage
- **`platform_apis.py`**: Direct platform API integrations for real-time data
- **`test_data_manager_v2.py`**: Comprehensive test suite for all functionality
- **`clm_v2_cli.py`**: Command-line interface for V2 system management

#### Data Model Schema
```python
# Core entities with proper relationships
Wallet → Positions → Transactions
Token ← TradingPair → Platform
Position ← PriceData → Portfolio Snapshots
```

#### Direct Platform Integration
- **Raydium API**: `https://api.raydium.io/v2/` - AMM pools and positions
- **Orca API**: `https://api.orca.so/v1/` - Whirlpool data
- **Jupiter API**: `https://api.jup.ag/` - Perpetual positions
- **CETUS API**: `https://api-sui.cetus.zone/` - SUI DEX data
- **GMX API**: `https://api.gmx.io/` - Arbitrum perpetuals

#### Key Features
- **Normalized Schema**: Eliminates data duplication and inconsistencies
- **Type Safety**: Dataclasses with enums prevent data corruption
- **Direct APIs**: "Closest to ground truth" approach eliminates third-party data risks
- **Real-time Updates**: Live data from official platform APIs
- **Parallel Testing**: Runs alongside existing system for validation
- **JSON Storage**: Database-ready structure with proper relationships

#### Testing V2 System
```bash
# Run comprehensive test suite
python test_data_manager_v2.py

# CLI operations
python clm_v2_cli.py list wallets
python clm_v2_cli.py create position wallet_id SOL USDC raydium long clm 1000
python clm_v2_cli.py portfolio
python clm_v2_cli.py health  # Check API connectivity
```

#### Migration Path
The V2 system is designed to eventually replace the current CSV import method after thorough testing. It provides:
- Better data integrity through normalized relationships
- Real-time updates from official platform APIs
- Scalable architecture for production use
- Comprehensive testing framework
- Direct blockchain data access without third-party intermediaries

