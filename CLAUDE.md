# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CLM Portfolio Tracker is a streamlined Python CLI application for monitoring cryptocurrency liquidity mining positions with real-time price tracking. It tracks Long and Neutral strategy positions across multiple chains and platforms through CSV import with real-time price updates.

## Architecture

The application follows a clean modular MVC-like pattern:

### Core Application
- **`CLM.py`** - Main CLI controller with simplified menu system
- **`clm_data.py`** - Core data manager handling CSV imports, JSON persistence, and price fetching

### Views (Display Layer)
- **`views/active_positions.py`** - Live position monitoring with range status and integrated token performance
- **`views/allocation_breakdown.py`** - Portfolio allocation analysis
- **`views/performance.py`** - Combined performance tracking and token analysis
- **`views/transactions.py`** - Transaction history

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
# Simple mode (recommended)
python CLM.py
```

### Data Management
- Place CSV files at default paths: `data/Tokens_Trade_Sheet - Neutral Positions.csv` and `data/Tokens_Trade_Sheet - Long Positions.csv`
- Application loads CSV files and converts to JSON format
- JSON files are stored in `data/JSON_out/` directory
- Use the integrated position editor ([e] menu option) to access the custom GPT tool for formatting position data

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

### Simplified Architecture
The codebase has been simplified with:
- Consolidated view files (performance.py combines historical returns and token performance)
- Simplified data manager with unified parsing methods
- Streamlined CLI menu system
- Archived legacy components in `archive/` directory

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
Simplified 5-option system:
- [1] Active Positions (with integrated token prices and range status)
- [2] Performance (combined historical returns and token performance)
- [3] Allocation Breakdown (portfolio allocation analysis)
- [4] Transactions (transaction history)
- [e] Edit Positions (link to custom GPT tool for position management)

## Archive Structure

### Legacy Components (moved to archive/)
- **`archive/views/`**: Old view files (historical_returns.py, historical_performance.py, prices.py, market_analysis.py)
- **`archive/old_files/`**: Previous versions (clm_data_old.py, V2 system files)
- **`archive/tests/`**: Test files and validation scripts
- **`archive/utils/`**: Utility functions (formatting, calculations, API clients)

### Archived V2 System
A more complex V2 system with normalized data models and direct platform APIs has been archived for potential future use. The current system prioritizes simplicity and maintainability.

