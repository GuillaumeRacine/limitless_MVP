# API Reference - Transaction System

## Core Classes and Methods

### SuiAPIValidator

Full SUI blockchain integration with RPC validation.

#### Constructor
```python
SuiAPIValidator(rpc_url="https://fullnode.mainnet.sui.io:443")
```

#### Key Methods

**get_transaction(tx_digest: str) -> Dict**
```python
# Fetch detailed transaction information
tx_data = validator.get_transaction("FyhFDN9FEuEnGBJhwBfTTpAW8YA2auhz2rg7thAVF1V9")
```

**parse_transaction_data(tx_data: Dict) -> Dict**
```python
# Parse SUI transaction into structured format
parsed = validator.parse_transaction_data(tx_data)
# Returns: digest, timestamp_ms, gas_used, balance_changes, events
```

**validate_csv_transaction(csv_row: Dict) -> Dict**
```python
# Cross-validate CSV data against blockchain
result = validator.validate_csv_transaction({
    'Digest': 'transaction_hash',
    'Time': '1750169724007',
    'Gas Fee': '0.067507972 SUI'
})
```

**enhance_transaction_data(csv_path: str, output_path: str)**
```python
# Process entire CSV file with blockchain validation
validator.enhance_transaction_data(
    'data/sui_transactions.csv',
    'data/sui_enhanced.csv'
)
```

### FastSuiProcessor

High-speed SUI transaction processing without RPC calls.

#### Methods

**process_csv_file(input_path: str, output_path: str) -> DataFrame**
```python
processor = FastSuiProcessor()
df = processor.process_csv_file(
    'data/sui_raw.csv',
    'data/sui_processed.csv'
)
```

**parse_asset_string(asset_str: str) -> List[Dict]**
```python
# Parse complex asset strings
assets = processor.parse_asset_string("-904.000000003SUI,2647.652454USDC")
# Returns: [{'amount': 904.0, 'symbol': 'SUI', 'direction': 'out'}, ...]
```

**extract_platforms(interacted_str: str) -> List[str]**
```python
# Extract platform names from interaction data
platforms = processor.extract_platforms("0x8093d002...(Cetus Aggregator)")
# Returns: ['Cetus']
```

### EnhancedPlatformDetector

Intelligent platform detection using multiple methods.

#### Methods

**enhance_all_transactions()**
```python
detector = EnhancedPlatformDetector()
detector.enhance_all_transactions()
# Processes all transactions in database
```

**detect_platform_from_contract(contract_address: str, chain: str) -> Optional[str]**
```python
platform = detector.detect_platform_from_contract(
    "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",
    "ethereum"
)
# Returns: "Uniswap V3"
```

**detect_platform_from_text(text_data: List[str]) -> Optional[str]**
```python
platform = detector.detect_platform_from_text([
    "swap uniswap v3",
    "ethereum mainnet"
])
# Returns: "Uniswap"
```

## Transaction View Enhancements

### Enhanced Display Methods

**_extract_token_units(raw_data: dict) -> str**
```python
# Extract clean token amount with symbol
units = view._extract_token_units({
    'parsed_amount': 5.67,
    'parsed_symbol': 'SUI'
})
# Returns: "5.67 SUI"
```

**_extract_usd_value(raw_data: dict) -> str**
```python
# Extract USD value as integer
usd = view._extract_usd_value({
    'total_usd_value': 1234.56
})
# Returns: "$1,234"
```

**_format_token_units_only(amount: float, currency: str) -> str**
```python
# Format token amounts with appropriate decimals
formatted = view._format_token_units_only(1234567.89, "USDC")
# Returns: "1.23M USDC"
```

## Data Enhancement Pipeline

### Enhancement Process Flow

1. **Raw Data Import**
   ```python
   # CSV files placed in data/ directory
   csv_files = [
       'data/sui_long_wallet.csv',
       'data/eth_transactions.csv'
   ]
   ```

2. **Fast Processing**
   ```python
   processor = FastSuiProcessor()
   for csv_file in csv_files:
       processor.process_csv_file(csv_file, csv_file.replace('.csv', '_processed.csv'))
   ```

3. **Database Import**
   ```python
   # Convert to transaction database format
   transactions = convert_sui_to_transaction_format(csv_path, strategy)
   data_manager.save_transactions(all_transactions)
   ```

4. **Platform Enhancement**
   ```python
   detector = EnhancedPlatformDetector()
   detector.enhance_all_transactions()
   ```

### Contract Mapping Structure

```python
contract_mappings = {
    # Ethereum Mainnet
    '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45': 'Uniswap V3',
    '0x7a250d5630b4cf539739df2c5dacb4c659f2488d': 'Uniswap V2',
    
    # Base Chain
    '0x827922686190790b37229fd06084350e74485b72': 'Aerodrome',
    '0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24': 'BaseSwap',
    
    # Solana Programs (partial match)
    '675kPX9MHTjFud3hyG3E8a': 'Orca',
    'whirLbMiicVdio4qvUfM5K': 'Orca Whirlpool',
    'routeUGWgWzqBWFcrCfv8tr': 'Raydium'
}
```

### Platform Pattern Recognition

```python
platform_patterns = {
    r'uniswap|uni-v[23]': 'Uniswap',
    r'sushiswap|sushi': 'SushiSwap',
    r'orca|whirlpool': 'Orca',
    r'cetus': 'Cetus',
    r'aerodrome|aero': 'Aerodrome',
    r'wormhole|portal': 'Wormhole'
}
```

## Transaction Categories

### Classification System

```python
def classify_transaction(tx_type: str, assets: List[Dict]) -> str:
    """
    Categories:
    - swap: Token exchanges
    - liquidity: LP operations  
    - farming: Yield farming
    - staking: Delegation
    - transfer: Send/receive
    - bridge: Cross-chain
    - mint_burn: Token creation/destruction
    - other: Unclassified
    """
```

### Category Rules

- **Swap**: Contains "swap", "trade", "exchange"
- **Liquidity**: Contains "liquidity", "mint", "burn", "deposit", "withdraw"
- **Farming**: Contains "harvest", "claim", "collectfee", "compound"
- **Transfer**: Contains "send", "receive", "transfer"
- **Bridge**: Contains "bridge", "relay", "crosschain"
- **Staking**: Contains "stake", "unstake", "delegate"

## Database Schema

### Transaction Record Structure

```python
{
    "id": "md5_hash_of_tx_and_wallet",
    "tx_hash": "blockchain_transaction_hash", 
    "wallet": "wallet_address",
    "chain": "blockchain_name",
    "platform": "detected_platform_name",
    "timestamp": "iso_8601_timestamp",
    "gas_fees": 0.001234,  # float in native token
    "block_number": "block_height_string",
    "contract_address": "smart_contract_address",
    "imported_at": "iso_8601_import_time",
    "raw_data": {
        # Original CSV fields
        "Type": "transaction_type",
        "Asset": "asset_string", 
        "Interacted with": "contract_list",
        
        # Enhanced fields
        "total_usd_value": 1234.56,
        "parsed_amount": 5.67,
        "parsed_symbol": "SUI",
        "parsed_direction": "in|out",
        "tx_category": "swap|liquidity|farming|transfer|bridge|staking|other",
        "platforms": ["Platform1", "Platform2"],
        "main_platform": "Primary_Platform",
        "validation_status": "verified|processed|unverified",
        "strategy": "long|neutral|yield"
    }
}
```

## Error Handling

### Common Error Patterns

**RPC Timeout**
```python
try:
    tx_data = validator.get_transaction(digest)
except TimeoutError:
    # Fallback to fast processing
    tx_data = None
```

**Invalid Transaction Data**
```python
try:
    parsed = validator.parse_transaction_data(tx_data)
except (KeyError, ValueError) as e:
    logger.error(f"Failed to parse transaction: {e}")
    return None
```

**Platform Detection Fallback**
```python
platform = (
    detect_from_contract(contract) or
    detect_from_text(text_fields) or
    detect_from_action(action, chain) or
    "Unknown"
)
```

## Performance Optimization

### Batch Processing

```python
# Process in chunks to avoid timeouts
chunk_size = 50
for i in range(0, len(transactions), chunk_size):
    chunk = transactions[i:i+chunk_size]
    process_chunk(chunk)
    time.sleep(0.1)  # Rate limiting
```

### Caching Strategy

```python
# Price data caching
price_cache = {}
cache_key = f"{symbol}_{timestamp}"
if cache_key in price_cache:
    return price_cache[cache_key]
```

### Memory Management

```python
# Process large datasets incrementally
def process_large_csv(csv_path):
    chunk_reader = pd.read_csv(csv_path, chunksize=1000)
    for chunk in chunk_reader:
        process_chunk(chunk)
        yield chunk  # Generator pattern
```

## Integration Examples

### Complete Processing Pipeline

```python
def process_new_chain_data(chain_name, csv_files):
    """Complete processing pipeline for new chain data"""
    
    # 1. Fast processing
    processor = FastSuiProcessor()  # Or chain-specific processor
    for csv_file in csv_files:
        processed_file = csv_file.replace('.csv', '_processed.csv')
        processor.process_csv_file(csv_file, processed_file)
    
    # 2. Import to database
    data_manager = CLMDataManager()
    for processed_file in processed_files:
        transactions = convert_to_transaction_format(processed_file, chain_name)
        existing = data_manager.load_transactions()
        all_transactions = existing + transactions
        data_manager.save_transactions(all_transactions)
    
    # 3. Enhance platform detection
    detector = EnhancedPlatformDetector()
    detector.enhance_all_transactions()
    
    # 4. Analyze results
    analyzer = UnclearTransactionAnalyzer()
    analyzer.analyze_unclear_transactions()
```

### Custom Platform Detection

```python
# Add new platform mappings
detector = EnhancedPlatformDetector()
detector.contract_mappings.update({
    '0xnew_contract_address': 'New Platform',
    'solana_program_id': 'New Solana Protocol'
})

# Add new pattern recognition
detector.platform_patterns.update({
    r'newprotocol|newdex': 'New Protocol'
})

# Run enhanced detection
detector.enhance_all_transactions()
```