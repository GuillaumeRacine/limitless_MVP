# Transaction Matching & Reconciliation System - Research & Architecture

## Executive Summary

This document outlines the research findings and architectural design for building a comprehensive transaction matching system for the CLM Portfolio Tracker. The system will capture multi-chain transaction data, automatically match transactions to positions, and provide reconciliation workflows for accurate accounting and performance measurement.

## Project Goals

1. **Clean Data Inputs**: Automated ingestion from multiple sources (APIs, CSV exports)
2. **Automatic Transaction Matching**: 80%+ transactions matched to positions/wallets without manual intervention
3. **Manual Reconciliation Workflow**: User-friendly interface for handling unmatched transactions
4. **Performance Analytics**: Calculate fees, slippage, IL, and net returns per position

## Multi-Chain Transaction Data Sources

### 1. Ethereum & Layer 2 Networks (Arbitrum, Optimism, Polygon, Base)

#### Primary API Providers
- **Alchemy** (Recommended Primary)
  - 100% data accuracy (0 inconsistent blocks in testing)
  - 10x faster performance than competitors (38.72ms vs 426.28ms)
  - Comprehensive L2 support (Arbitrum, Optimism, Polygon, Base)
  - Enhanced Transfers API for complete transaction history
  - Endpoints: `https://eth-mainnet.g.alchemy.com/v2/`, `https://arb-mainnet.g.alchemy.com/v2/`

- **Moralis** (Backup/Alternative)
  - Cross-chain wallet API covering all major EVM chains
  - Real-time transaction access arranged by block number
  - Internal transaction data per block/wallet
  - Good for cross-chain aggregation

- **Etherscan/Arbiscan/etc.** (Free Tier/Backup)
  - Direct blockchain explorer APIs
  - Rate-limited but reliable for low-volume needs
  - Native CSV export functionality

#### CSV Export Options
- **Zerion Premium** ($99/year)
  - 38+ chains including all major L2s
  - Spam filtering, unlimited transactions (~300k limit)
  - Token prices and addresses included
  - Advanced filtering by transaction type, assets, networks
  
- **Etherscan Direct Export**
  - Free basic transaction export
  - Limited to single addresses
  - Manual process per wallet

### 2. Solana Network

#### Primary API Providers
- **Helius** (Recommended Primary)
  - Enhanced Transactions API with 100+ parsers
  - Human-readable transaction decoding
  - Real-time streaming capabilities
  - Intelligent priority fee calculations
  - Address: `https://mainnet.helius-rpc.com/`

- **QuickNode** (Alternative/Backup)
  - Comprehensive Solana RPC endpoints
  - Good performance and reliability
  - WebSocket support for real-time data

#### CSV Export Options
- **CoinStats** (Current Sample Source)
  - Portfolio tracking with transaction export
  - Balances and transaction history
  - Format: Portfolio, Coin Name, Symbol, Exchange, Type, Amount, Price, Date, Notes

### 3. SUI Network

#### Primary API Providers
- **Sui Official RPC** (Primary)
  - `https://fullnode.mainnet.sui.io:443`
  - Native JSON-RPC API with comprehensive transaction methods
  - GraphQL interface available (RPC 2.0)

- **QuickNode** (Alternative)
  - Third-party Sui RPC endpoints
  - Enhanced developer tools and APIs

- **Ankr** (Backup)
  - Reliable Sui API endpoints
  - Web3 data access

## Current Position Data Structure Analysis

Based on existing JSON files, each position contains:
```json
{
  "id": "unique_identifier",
  "strategy": "long|neutral", 
  "platform": "Orca|CLM|etc",
  "token_pair": "SOL/USDC",
  "chain": "SOL|ETH|ARB|etc",
  "wallet": "wallet_address",
  "entry_value": 23190.0,
  "entry_date": "Jun 20",
  "min_range": 130.0,
  "max_range": 158.75
}
```

## Transaction Matching System Architecture

### 1. Data Ingestion Layer

#### Multi-Source Transaction Collectors
```python
class TransactionCollector:
    def __init__(self):
        self.eth_collector = EthereumCollector()  # Alchemy API
        self.sol_collector = SolanaCollector()    # Helius API  
        self.sui_collector = SuiCollector()       # Sui RPC
        self.csv_importer = CSVImporter()         # Zerion/CoinStats CSV
    
    def collect_all_transactions(self, wallets_config):
        # Parallel collection from all sources
        pass
```

#### Wallet Configuration
```python
WALLET_CONFIG = {
    "SOL": {
        "long_strategy": "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k",
        "neutral_strategy": "Djrzp7SyiTsDre41hgaUCh99Aw7PrchetGDbdm3GfHo6", 
        "yield_wallet": "yield_wallet_address"
    },
    "ETH": {
        "long_strategy": "0x...",
        "neutral_strategy": "0x...",
        "yield_wallet": "0x..."
    },
    "SUI": {
        "long_strategy": "0x...",
        "neutral_strategy": "0x...", 
        "yield_wallet": "0x..."
    }
}
```

### 2. Transaction Normalization Layer

#### Unified Transaction Format
```python
@dataclass
class UnifiedTransaction:
    tx_id: str
    chain: str
    wallet_address: str
    timestamp: datetime
    type: str  # deposit, withdraw, swap, claim, fee
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    gas_fee: float
    platform: str
    raw_data: dict
    confidence_score: float
```

#### Chain-Specific Parsers
- **Ethereum/L2 Parser**: ERC-20 transfers, DEX swaps, LP operations
- **Solana Parser**: SPL token transfers, Raydium/Orca/Jupiter interactions
- **SUI Parser**: Coin transfers, DEX operations, Move call transactions

### 3. Matching Engine

#### Rule-Based Matching System
```python
class TransactionMatcher:
    def __init__(self):
        self.matchers = [
            ExactAmountMatcher(),      # Exact amount + time window
            PlatformMatcher(),         # Platform-specific transaction patterns
            TokenPairMatcher(),        # Token pair correlation
            TimeWindowMatcher(),       # Fuzzy time-based matching
            WalletStrategyMatcher()    # Wallet-to-strategy mapping
        ]
    
    def match_transaction(self, transaction, positions):
        matches = []
        for matcher in self.matchers:
            match = matcher.find_match(transaction, positions)
            if match:
                matches.append(match)
        return self.rank_matches(matches)
```

#### Matching Strategies

1. **High Confidence Matches (Auto-Accept)**
   - Exact entry amount match within 24-hour window
   - Platform-specific transaction signatures
   - Token pair exact match with known position

2. **Medium Confidence Matches (Review Required)**
   - Amount matches within 5% variance
   - Time window matches but amount slightly off
   - Platform matches but token pair variation

3. **Low Confidence Matches (Manual Review)**
   - Wallet matches but no other correlations
   - Similar amounts but different time periods
   - Unknown transaction types

### 4. Reconciliation Workflow

#### Interactive Matching Interface
```python
class ReconciliationInterface:
    def show_unmatched_transactions(self):
        # Display unmatched transactions with suggested matches
        pass
    
    def manual_match_transaction(self, tx_id, position_id):
        # Allow user to manually link transaction to position
        pass
    
    def create_new_position(self, transaction):
        # Create new position from unmatched transaction
        pass
    
    def mark_as_fee_or_other(self, tx_id, category):
        # Categorize non-position transactions
        pass
```

#### Reconciliation Dashboard Features
- **Unmatched Transactions Queue**: Sorted by amount/importance
- **Suggested Matches**: ML-powered suggestions with confidence scores
- **Batch Operations**: Match multiple similar transactions
- **Transaction History**: Audit trail of all matching decisions
- **Missing Transaction Detection**: Alert for expected but missing transactions

### 5. Performance Analytics Engine

#### Position Performance Calculator
```python
class PerformanceCalculator:
    def calculate_position_metrics(self, position_id):
        transactions = self.get_position_transactions(position_id)
        
        metrics = {
            'total_fees': self.sum_gas_fees(transactions),
            'slippage': self.calculate_slippage(transactions),
            'impermanent_loss': self.calculate_il(transactions),
            'yield_claimed': self.sum_yield_claims(transactions),
            'net_return': self.calculate_net_return(transactions)
        }
        return metrics
```

#### Key Metrics Tracked
- **Transaction Fees**: Gas costs per position across all chains
- **Slippage**: Entry/exit execution vs expected prices
- **Impermanent Loss**: Real-time IL calculation with price movements
- **Yield/Rewards**: Claimed rewards and fees earned
- **Net Returns**: Total performance after all costs

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- Multi-chain API integration (Alchemy, Helius, Sui RPC)
- Transaction normalization layer
- Basic wallet configuration system
- CSV import functionality

### Phase 2: Matching Engine (Week 2-3)
- Rule-based matching system
- Confidence scoring algorithm
- High-confidence auto-matching
- Match persistence and audit trail

### Phase 3: Reconciliation Interface (Week 3-4)
- CLI-based reconciliation workflow
- Manual matching interface
- Batch operations support
- Transaction categorization system

### Phase 4: Performance Analytics (Week 4-5)
- Position-level performance calculations
- Fee and slippage tracking
- Net return calculations
- Integration with existing views

### Phase 5: Advanced Features (Week 5-6)
- ML-powered matching suggestions
- Missing transaction detection
- Advanced reporting and analytics
- Data export and backup systems

## Data Storage Schema

### Transaction Storage
```sql
CREATE TABLE transactions (
    tx_id VARCHAR PRIMARY KEY,
    chain VARCHAR NOT NULL,
    wallet_address VARCHAR NOT NULL,
    timestamp DATETIME NOT NULL,
    type VARCHAR NOT NULL,
    token_in VARCHAR,
    token_out VARCHAR,
    amount_in DECIMAL,
    amount_out DECIMAL,
    gas_fee DECIMAL,
    platform VARCHAR,
    raw_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transaction_matches (
    id INTEGER PRIMARY KEY,
    tx_id VARCHAR NOT NULL,
    position_id VARCHAR,
    match_type VARCHAR, -- position, fee, yield, other
    confidence_score DECIMAL,
    matched_by VARCHAR, -- auto, manual
    matched_at DATETIME,
    notes TEXT,
    FOREIGN KEY (tx_id) REFERENCES transactions(tx_id)
);
```

## Cost Analysis

### API Costs (Monthly, assuming 10K transactions/month)
- **Alchemy**: $49/month (Growth plan) - 300M compute units
- **Helius**: $99/month (Professional) - 1M requests
- **Zerion Premium**: $99/year for CSV exports
- **Total Monthly**: ~$160 (for comprehensive coverage)

### Free Tier Options
- **Etherscan APIs**: 5 calls/second (limited but functional)
- **Sui Official RPC**: Free usage with rate limits
- **CSV Manual Exports**: Time-intensive but zero cost

## Security Considerations

### API Key Management
- Environment variables for all API keys
- Separate keys for different environments
- Key rotation policy (quarterly)

### Data Privacy
- Local storage of transaction data
- Wallet address anonymization options
- Secure backup and recovery procedures

### Rate Limiting
- Implement exponential backoff
- Request queuing for high-volume periods
- Error handling and retry logic

## Success Metrics

### Matching Accuracy Targets
- **80%+ Auto-Match Rate**: High-confidence matches requiring no manual intervention
- **<5% False Positive Rate**: Incorrect automatic matches
- **Complete Position Coverage**: All positions have associated transactions

### Performance Targets
- **Transaction Processing**: <1 second per transaction normalization
- **Batch Processing**: 1000 transactions in <30 seconds
- **API Response Times**: <2 seconds for all data fetching

### User Experience Goals
- **Reconciliation Time**: <10 minutes for 100 unmatched transactions
- **Data Freshness**: Real-time updates for new transactions
- **Error Rate**: <1% transaction import failures

## Risk Mitigation

### Data Reliability
- **Multiple API Sources**: Primary/backup API strategy
- **Transaction Verification**: Cross-reference between sources when possible
- **Data Validation**: Sanity checks on amounts, dates, and addresses

### System Reliability
- **Error Handling**: Graceful degradation when APIs fail
- **Data Backup**: Regular exports of matched transaction data
- **Recovery Procedures**: Clear steps for data corruption or loss

### Cost Management
- **Usage Monitoring**: Track API call volumes and costs
- **Rate Limiting**: Prevent accidental cost overruns
- **Free Tier Fallbacks**: Backup options when paid APIs unavailable

## Next Steps

1. **Validate Wallet Addresses**: Confirm the three wallet addresses per chain
2. **API Key Setup**: Obtain API keys for primary data sources
3. **Proof of Concept**: Build basic transaction fetching for one chain
4. **CSV Format Analysis**: Detailed analysis of export formats from Zerion/similar tools
5. **User Workflow Design**: Create mockups for reconciliation interface

This architecture provides a robust foundation for accurate transaction tracking and position performance measurement across multiple chains while maintaining flexibility for future enhancements and scaling.