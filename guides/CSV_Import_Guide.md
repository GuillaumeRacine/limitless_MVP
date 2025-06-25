# Enhanced CSV Import Guide

The CLM Portfolio Tracker now supports importing CSV files from multiple sources and chains, capturing comprehensive transaction data, wallet information, and balance details.

## Supported CSV Formats

### 1. Position CSV (Default - Existing Format)
Your current format with position details, ranges, and performance metrics.

**Required Columns:**
- `Position Details` or `Position`
- `Wallet` 
- `Chain`
- `Platform`
- `Total Entry Value` or `Entry Value (cash in)`

**Enhanced Optional Columns:**
- `Transaction ID` / `Tx Hash` - Entry transaction hash
- `Exit Transaction ID` / `Exit Tx Hash` - Exit transaction hash  
- `Gas Fees` / `Network Fees` - Total gas fees paid
- `Contract Address` / `Pool Address` - Smart contract address
- `Block Number` / `Entry Block` - Block number of entry transaction

### 2. Transaction CSV (New)
For importing transaction data from wallet/DEX exports.

**Supported Columns:**
- `Transaction ID` / `Tx Hash` / `Hash` (required)
- `Wallet Address` / `Address` (required)
- `Chain` / `Blockchain` / `Network`
- `Platform` / `Protocol` / `Exchange`
- `Timestamp` / `Date`
- `Gas Fees` / `Network Fees`
- `Block Number` / `Block`
- `Contract Address`

### 3. Balance CSV (New)  
For importing current portfolio balance snapshots.

**Supported Columns:**
- `Wallet Address` / `Address` (required)
- `Current Balance` / `Balance` / `LP Tokens`
- `Token A Balance` / `Base Token Balance`
- `Token B Balance` / `Quote Token Balance`
- `Chain` / `Network`
- `Platform` / `Protocol`
- `Contract Address` / `Token Address`

## Usage Examples

### Single CSV Import

```python
from clm_data import CLMDataManager

manager = CLMDataManager()

# Import transactions from Solana DEX
transactions = manager.import_transaction_csv('solana_dex_export.csv', 'SOL')

# Import current balances from Ethereum wallet
balances = manager.import_balance_csv('eth_wallet_balances.csv', 'ETH')

# Save imported data
manager.save_transactions(transactions)
manager.save_balances(balances)
```

### Multi-Chain Batch Import

```python
# Configure multiple CSV files
csv_configs = [
    {
        'path': 'data/solana_transactions.csv',
        'chain': 'SOL', 
        'type': 'transactions'
    },
    {
        'path': 'data/ethereum_balances.csv',
        'chain': 'ETH',
        'type': 'balances'
    },
    {
        'path': 'data/sui_positions.csv', 
        'chain': 'SUI',
        'type': 'positions',
        'strategy': 'long'
    }
]

# Import all at once
results = manager.import_multi_chain_csvs(csv_configs)

# Results contain:
# - results['transactions'] - All transaction records
# - results['balances'] - All balance records  
# - results['positions'] - Position data by strategy
# - results['errors'] - Any import errors
```

## Chain-Specific Considerations

### Solana
- **Wallet Format**: Base58 encoded (e.g., `DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k`)
- **Transaction IDs**: Base58 transaction signatures
- **Common Platforms**: Orca, Raydium, Jupiter
- **Gas**: Measured in SOL (typically 0.000005 - 0.01 SOL)

### Ethereum
- **Wallet Format**: Hex addresses (e.g., `0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a`)
- **Transaction IDs**: Hex transaction hashes (0x...)
- **Common Platforms**: Uniswap, SushiSwap, Curve
- **Gas**: Measured in ETH (varies with network congestion)

### Sui
- **Wallet Format**: Hex addresses with 0x prefix
- **Transaction IDs**: Base64 encoded digests
- **Common Platforms**: Cetus, Turbos
- **Gas**: Measured in SUI

### Base/Arbitrum
- **Similar to Ethereum** (EVM compatible)
- **Platforms**: Aerodrome (Base), GMX (Arbitrum)
- **Lower gas fees than mainnet Ethereum**

## Data Structure

### Enhanced Position Data
```json
{
  "id": "abc123def456",
  "position_details": "SOL/USDC",
  "strategy": "long",
  "platform": "Orca",
  "token_pair": "SOL/USDC",
  "chain": "SOL",
  "wallet": "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k",
  "entry_value": 25000.00,
  "transaction_data": {
    "entry_tx_id": "7kj9dHJ2k3H4J5K6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0",
    "exit_tx_id": "",
    "gas_fees_paid": 0.0025,
    "block_number": "245678901"
  },
  "contract_data": {
    "contract_address": "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP",
    "pool_address": "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP"
  },
  "balance_data": {
    "current_lp_balance": 1250.75,
    "token_a_balance": 625.00,
    "token_b_balance": 625.75
  }
}
```

### Transaction Data
```json
{
  "id": "tx123abc456",
  "tx_hash": "7kj9dHJ2k3H4J5K6L7M8N9O0P1Q2R3S4T5U6V7W8X9Y0Z1A2B3C4D5E6F7G8H9I0",
  "wallet": "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k",
  "chain": "SOL",
  "platform": "Orca",
  "timestamp": "2024-06-20 10:30:00",
  "gas_fees": 0.0025,
  "block_number": "245678901",
  "contract_address": "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP",
  "imported_at": "2024-06-24T10:30:00",
  "raw_data": { /* Original CSV row data */ }
}
```

### Balance Data
```json
{
  "id": "bal789xyz012",
  "wallet": "0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a",
  "chain": "ETH",
  "platform": "Uniswap",
  "token_pair": "ETH/USDC",
  "lp_balance": 1250.75,
  "token_a_balance": 0.534,
  "token_b_balance": 1245.30,
  "contract_address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
  "snapshot_date": "2024-06-24T10:30:00",
  "raw_data": { /* Original CSV row data */ }
}
```

## Output Files

The enhanced system creates additional JSON files:

- `data/JSON_out/clm_long.json` - Long positions (enhanced with transaction/balance data)
- `data/JSON_out/clm_neutral.json` - Neutral positions (enhanced)
- `data/JSON_out/clm_closed.json` - Closed positions (enhanced)
- `data/JSON_out/clm_transactions.json` - **NEW** - Transaction records
- `data/JSON_out/clm_balances.json` - **NEW** - Balance snapshots
- `data/JSON_out/clm_metadata.json` - Import metadata

## Backward Compatibility

The enhanced system is **fully backward compatible** with your existing CSV format. All current functionality continues to work unchanged, with new fields being optional additions.

## Error Handling

- **Missing files**: Skipped with warning message
- **Invalid data**: Rows with parsing errors are logged but don't stop the import
- **Format detection**: Automatic detection of CSV format based on column headers
- **Flexible mapping**: Multiple possible column names supported for each field

## Testing

Run the example script to test with sample data:

```bash
python enhanced_csv_import_example.py
```

This creates sample CSV files and demonstrates all import functionality.