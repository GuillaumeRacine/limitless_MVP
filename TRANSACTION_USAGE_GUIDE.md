# Transaction System Usage Guide

## Quick Start

### Viewing Enhanced Transactions

1. **Run the main application**:
   ```bash
   python CLM.py
   ```

2. **Select Transactions view** (option 2):
   ```
   [2] Transactions
   ```

3. **Choose Bank Statement View** (option 1):
   ```
   [1] Bank Statement View (Chronological)
   ```

4. **Navigate pages or view all**:
   ```
   Enter page number (1-47) or 'all' for all transactions [default: 1]: 1
   ```

### Enhanced Display Features

The new transaction view shows:

| Column | Description | Example |
|--------|-------------|---------|
| Date | Transaction date | 2025-06-24 |
| Strategy | Wallet strategy | Long, Neutral, Yield |
| Action | Transaction type | Trade, Send, Swap |
| Token Units | Amount with symbol | 5.67 SUI, 1.23K USDC |
| USD Value | Integer USD equivalent | $1,234, $56 |
| Token Pair | Trading pair | SOL/USDC, ETH → USDC |
| Platform | Detected platform | Cetus, Uniswap V3, Orca |
| Chain | Blockchain | SUI, SOL, base, arbitrum |
| Contract | Contract address | 0x123..., N/A |

## Adding New Transaction Data

### SUI Transactions

**Step 1: Export SUI transaction CSV**
- Use SUI explorer or wallet to export transaction history
- Save as: `data/sui_[wallet_address]_activities_[date].csv`

**Step 2: Process SUI data**
```bash
python fast_sui_processor.py
```

**Step 3: Import to database**
```bash
python import_sui_transactions.py
```

### Other Chains (SOL, ETH, etc.)

**Step 1: Place CSV files in data folder**
- Supported formats: Zerion exports, DEX transaction exports, wallet exports
- Naming: `data/[chain]_[wallet]_transactions_[date].csv`

**Step 2: Run auto-detection**
```bash
python CLM.py
# Application will auto-detect new CSV files
```

## Improving Platform Detection

### Running Platform Enhancement

```bash
python enhanced_platform_detector.py
```

This will:
- Analyze all transactions in database
- Apply contract address mappings
- Use pattern recognition
- Improve platform identification rate

### Adding Custom Platform Mappings

Edit the contract mappings in `enhanced_platform_detector.py`:

```python
# Add new contract addresses
self.contract_mappings.update({
    '0xYourNewContract': 'Your Platform Name',
    'solana_program_id': 'Solana Protocol Name'
})

# Add new pattern recognition
self.platform_patterns.update({
    r'yourprotocol|yourdex': 'Your Protocol'
})
```

## Transaction Analysis

### Identifying Unclear Transactions

```bash
python analyze_unclear_transactions.py
```

This generates a report showing:
- Transactions with unknown platforms
- Missing transaction amounts
- Failed transactions
- Validation errors

### Understanding the Analysis

The analysis categorizes issues:

1. **Unknown Platform (32.0%)**: Platform detection failed
2. **Missing Amounts (25.5%)**: No token amounts found
3. **Failed Transactions (2.9%)**: Blockchain failures
4. **Zero Value (2.0%)**: Potentially spam transactions

## Advanced Features

### Blockchain Validation

For comprehensive validation with RPC calls:

```bash
# SUI full validation (slower but comprehensive)
python sui_data_enhancer.py

# SOL validation
python sol_api_validator.py

# ETH validation  
python eth_api_validator.py
```

### Custom Transaction Processing

Create your own processor for new chains:

```python
from fast_sui_processor import FastSuiProcessor

class CustomChainProcessor(FastSuiProcessor):
    def __init__(self):
        super().__init__()
        # Add custom price sources
        # Add custom asset parsing
        # Add custom platform detection
    
    def process_custom_format(self, csv_path):
        # Your custom processing logic
        pass
```

## Troubleshooting

### Common Issues

**1. RPC Timeouts**
- Issue: SUI/SOL RPC calls timeout
- Solution: Use fast processors instead of full validators
- Command: `python fast_sui_processor.py` (not `sui_data_enhancer.py`)

**2. Missing Platforms**
- Issue: Many transactions show "Unknown" platform
- Solution: Run platform enhancement
- Command: `python enhanced_platform_detector.py`

**3. Import Errors**
- Issue: CSV format not recognized
- Solution: Check CSV column headers match expected format
- Fix: Rename columns to match standard format (see below)

**4. No Token Units Displayed**
- Issue: Token Units column is empty
- Solution: Check CSV has amount and currency columns
- Fix: Ensure data has 'Buy Amount', 'Sell Amount', or 'Amount' fields

### CSV Format Requirements

**Standard format expected**:
```csv
Date,Transaction Type,Buy Amount,Buy Currency,Sell Amount,Sell Currency,Buy Fiat Amount,Sell Fiat Amount
2025-06-24,trade,5.67,SUI,,,$15.12,
```

**SUI enhanced format**:
```csv
Type,Time,Asset,Interacted with,Digest,Gas Fee,Timestamp
Swap,1750169724007,"-904SUI,2647USDC","0x123...(Cetus)",FyhF...,0.067 SUI,"2025-06-24 14:15:24 UTC"
```

### Performance Optimization

**For large datasets**:
1. Use fast processors instead of full validators
2. Process in smaller batches
3. Run during off-peak hours
4. Monitor memory usage

**Speed comparison**:
- Fast processor: ~50 transactions/second
- Full validator: ~1 transaction/second (due to RPC calls)

## Best Practices

### Data Organization

1. **Consistent naming**: Use clear, descriptive filenames
2. **Date organization**: Include dates in filenames
3. **Chain separation**: Keep different chains in separate files
4. **Regular backups**: Backup processed data regularly

### Workflow Recommendations

1. **Daily routine**:
   - Export new transactions from wallets/exchanges
   - Run fast processing
   - Import to database
   - Review unclear transactions weekly

2. **Weekly analysis**:
   - Run platform enhancement
   - Analyze unclear transactions
   - Review and fix any issues
   - Update contract mappings if needed

3. **Monthly review**:
   - Full data validation with RPC calls
   - Performance analysis
   - Platform detection accuracy review

### Monitoring Data Quality

Check these metrics regularly:
- Platform detection rate (target: >85%)
- USD value coverage (target: >90% of value transactions)
- Failed transaction rate (target: <5%)
- Missing amounts (target: <20%)

## API Integration

### Using the Transaction System Programmatically

```python
from clm_data import CLMDataManager
from views.transactions import TransactionsView

# Load transaction data
data_manager = CLMDataManager()
transactions = data_manager.load_transactions()

# Create transaction view
view = TransactionsView(data_manager)

# Get specific transaction data
for tx in transactions:
    if tx['chain'] == 'SUI':
        token_units = view._extract_token_units(tx['raw_data'])
        usd_value = view._extract_usd_value(tx['raw_data'])
        print(f"{token_units} = {usd_value}")
```

### Custom Analysis

```python
import pandas as pd

# Load as DataFrame for analysis
df = pd.DataFrame(transactions)

# Analyze by chain
chain_stats = df.groupby('chain').agg({
    'gas_fees': 'sum',
    'id': 'count'
}).rename(columns={'id': 'transaction_count'})

# Analyze by platform
platform_stats = df['platform'].value_counts()

# Find high-value transactions
high_value = df[df['raw_data'].apply(
    lambda x: x.get('total_usd_value', 0) > 1000
)]
```

## Support and Updates

### Getting Help

1. **Check documentation**: Review this guide and API reference
2. **Run analysis tools**: Use built-in analysis to identify issues
3. **Review logs**: Check console output for error messages
4. **Test with small datasets**: Validate with known good data first

### Keeping Updated

The transaction system is actively developed. To stay current:
1. Regularly update contract mappings
2. Add new platform patterns as protocols launch
3. Monitor platform detection rates
4. Update RPC endpoints if needed

### Contributing Improvements

To improve platform detection:
1. Add new contract addresses you encounter
2. Submit platform patterns for new protocols
3. Report parsing issues with specific CSV formats
4. Share performance optimizations