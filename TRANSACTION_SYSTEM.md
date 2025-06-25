# Transaction System Documentation

## Overview

The CLM Portfolio Tracker includes a comprehensive multi-chain transaction processing system that validates, enhances, and analyzes cryptocurrency transactions across multiple blockchains.

## Supported Chains

- **Solana (SOL)**: DEX transactions, token swaps, liquidity operations
- **SUI**: DeFi protocol interactions, swaps, liquidity farming
- **Ethereum**: Layer 1 transactions, DeFi protocols
- **Base**: Layer 2 transactions, Coinbase ecosystem
- **Arbitrum**: Layer 2 scaling solution transactions
- **Optimism**: Layer 2 optimistic rollup transactions
- **Polygon**: Ethereum sidechain transactions

## Core Components

### 1. Blockchain Validators

#### SUI API Validator (`sui_api_validator.py`)
- **RPC Integration**: Direct connection to SUI fullnode RPC
- **Transaction Validation**: Cross-validates CSV data against blockchain
- **Enhanced Data**: Extracts balance changes, events, and object changes
- **Metadata Parsing**: Coin metadata and token information

```python
from sui_api_validator import SuiAPIValidator

validator = SuiAPIValidator()
tx_data = validator.get_transaction("digest_hash")
parsed = validator.parse_transaction_data(tx_data)
```

#### SOL API Validator (`sol_api_validator.py`)
- **Solana RPC**: Connection to Solana mainnet-beta
- **Program Analysis**: Identifies DEX programs and protocols
- **Transaction History**: Comprehensive signature retrieval
- **Account Monitoring**: Balance and activity tracking

#### ETH API Validator (`eth_api_validator.py`)
- **Ethereum RPC**: Multi-chain EVM support
- **Contract Interaction**: Smart contract transaction analysis
- **Gas Optimization**: Transaction cost analysis
- **Bridge Detection**: Cross-chain transaction identification

### 2. Data Enhancement Pipeline

#### Enhanced Platform Detection
The system uses multiple detection methods:

1. **Contract Address Mapping**
   ```python
   contract_mappings = {
       '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45': 'Uniswap V3',
       '0x827922686190790b37229fd06084350e74485b72': 'Aerodrome',
       'whirLbMiicVdio4qvUfM5K': 'Orca Whirlpool'
   }
   ```

2. **Pattern Recognition**
   - Transaction type analysis
   - Chain-specific defaults
   - Token pair inference

3. **Text Analysis**
   - Protocol name extraction
   - Exchange identification
   - Bridge detection

### 3. Transaction Processing

#### Data Import Flow
```
CSV Files → Fast Processor → Blockchain Validation → Enhancement → Database Storage
```

#### Processing Scripts

**Fast SUI Processor** (`fast_sui_processor.py`):
- Rapid CSV processing without RPC calls
- Price calculation using CoinGecko API
- Asset parsing and categorization
- Platform extraction from interaction data

**SUI Data Enhancer** (`sui_data_enhancer.py`):
- Full RPC validation (slower but comprehensive)
- Historical price integration
- USD value calculation
- Detailed blockchain validation

## Transaction Analysis

### Platform Distribution
Current platform identification rates:
- **84.7% Overall**: Significant improvement from ~53%
- **Solana**: 755 transactions (29.7%)
- **Transfer**: 424 transactions (16.7%)
- **DEX**: 408 transactions (16.1%)
- **Cetus (SUI)**: 290 transactions (11.4%)
- **Bridge**: 91 transactions (3.6%)

### Enhanced Transaction View

The transaction display includes:

| Date | Strategy | Action | Token Units | USD Value | Token Pair | Platform | Chain |
|------|----------|--------|-------------|-----------|------------|----------|-------|
| 2025-06-24 | Long | Trade | 0.004015 cbBTC | $583 | USDC → cbBTC | DEX | base |
| 2025-06-24 | Long | Send | 394.18 USDC | $540 | Sell USDC | Transfer | base |

#### Features:
- **Dual-Column Display**: Separate token units and USD values
- **Smart Filtering**: Excludes approve transactions and zero-value transfers
- **Intelligent Formatting**: Appropriate decimal places and K/M notation
- **Real-time Enhancement**: Live platform detection and categorization

### Transaction Categories

- **Swap**: Token exchanges and trading
- **Liquidity**: Adding/removing liquidity, LP operations
- **Farming**: Yield farming, reward claiming, fee collection
- **Transfer**: Send/receive operations, wallet transfers
- **Bridge**: Cross-chain transfers and relaying
- **Staking**: Delegation and staking operations

## Usage Examples

### Importing SUI Transactions
```bash
# Process SUI CSV files
python fast_sui_processor.py

# Import to main database
python import_sui_transactions.py
```

### Enhancing Platform Detection
```bash
# Run platform detection enhancement
python enhanced_platform_detector.py
```

### Analyzing Unclear Transactions
```bash
# Identify transactions needing review
python analyze_unclear_transactions.py
```

## Data Structure

### Transaction Record Format
```json
{
  "id": "unique_hash",
  "tx_hash": "blockchain_hash",
  "wallet": "wallet_address",
  "chain": "blockchain_name",
  "platform": "detected_platform",
  "timestamp": "iso_timestamp",
  "gas_fees": 0.001234,
  "raw_data": {
    "total_usd_value": 1234.56,
    "parsed_amount": 5.67,
    "parsed_symbol": "SUI",
    "tx_category": "swap",
    "platforms": ["Cetus", "Turbos"],
    "validation_status": "verified"
  }
}
```

### Enhanced Fields
- **total_usd_value**: USD value at transaction time
- **parsed_amount**: Clean token amount
- **parsed_symbol**: Standardized token symbol
- **tx_category**: Transaction classification
- **platforms**: Array of involved platforms
- **validation_status**: Blockchain validation result

## Configuration

### Wallet Mapping
The system uses predefined wallet-to-strategy mappings:

```python
wallet_strategies = {
    # Long Strategy
    "0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a": "Long",
    "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k": "Long",
    
    # Neutral Strategy  
    "0x1df6f74ae73e453bc276d84512f1cd8387b643432163221df4f4c76112bfaf66": "Neutral",
    "Djrzp7SyiTsDre41hgaUCh99Aw7PrchetGDbdm3GfHo6": "Neutral",
    
    # Yield Wallets
    "0xa1c48a832320557655096e4fb475df116f9b0215fea51ef1b189e346325b9e2d": "Yield",
    "GKvUys93yYe4U1a82u2k4VDvsxQLeCtaGyeggfh1hoBk": "Yield"
}
```

## Performance Metrics

### Recent Improvements
- **380 SUI Transactions**: Added $1.66M in transaction value
- **1,391 Enhanced Records**: Platform detection improvements
- **84.7% Identification Rate**: Up from 53% unknown platforms
- **2,541 Total Transactions**: Comprehensive multi-chain coverage

### Gas Analysis
- **Total Gas Tracked**: $4.60 across all chains
- **SUI Gas**: $4.17 (highest due to complex DeFi operations)
- **SOL Gas**: $0.44 (efficient consensus mechanism)
- **EVM Chains**: Varies by network congestion

## Troubleshooting

### Common Issues

1. **RPC Timeouts**: SUI RPC calls may timeout for large datasets
   - Solution: Use fast processor for bulk operations
   
2. **Missing Platforms**: Some contracts not in mapping
   - Solution: Add contract addresses to detection algorithm
   
3. **Price Data**: Historical prices may be approximated
   - Solution: Implement time-series price APIs

### Data Quality Checks

The system automatically identifies:
- Unknown platforms (15.3% remaining)
- Missing transaction amounts
- Failed blockchain transactions
- Validation errors and discrepancies

## Future Enhancements

- **Real-time Monitoring**: WebSocket connections for live updates
- **Advanced Analytics**: MEV detection and sandwich attack analysis
- **More Chains**: Cosmos, Avalanche, and other ecosystem support
- **Machine Learning**: Pattern-based platform detection
- **Historical Prices**: Time-accurate USD value calculations