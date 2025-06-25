# 📥 Transaction CSV Import Guide

You now have **4 easy ways** to import your full transaction CSV files:

## **Method 1: Main CLI Menu (Easiest) ⭐**

1. **Copy your transaction CSV** to the `data/` folder
2. **Run the main app**: `python CLM.py`
3. **Press `[i]`** for "import transactions" 
4. **Choose your import option**:
   - `[a]` - Auto-import all transaction files
   - `[s]` - Select specific file by number
   - `[c]` - Cancel

### Example:
```bash
python CLM.py
# In the menu, press: i
# Then: a (to auto-import) or s (to select specific file)
```

---

## **Method 2: Dedicated Import Script**

1. **Copy your CSV** to `data/` folder with a transaction-related name:
   - `data/my_sol_transactions.csv`
   - `data/wallet_export.csv`
   - `data/dex_transactions.csv`

2. **Run the import script**: `python import_my_transactions.py`

---

## **Method 3: Direct Python Script**

Create a simple script to import your specific file:

```python
from clm_data import CLMDataManager

manager = CLMDataManager()

# Import your transaction CSV
transactions = manager.import_transaction_csv('data/my_transactions.csv', 'SOL')

# Save the data
if transactions:
    manager.save_transactions(transactions)
    print(f"✅ Imported {len(transactions)} transactions")
```

---

## **Method 4: Multi-Chain Batch Import**

For multiple CSV files from different chains:

```python
from clm_data import CLMDataManager

manager = CLMDataManager()

csv_configs = [
    {'path': 'data/solana_txs.csv', 'chain': 'SOL', 'type': 'transactions'},
    {'path': 'data/ethereum_txs.csv', 'chain': 'ETH', 'type': 'transactions'},
    {'path': 'data/sui_txs.csv', 'chain': 'SUI', 'type': 'transactions'}
]

results = manager.import_multi_chain_csvs(csv_configs)
```

---

## **CSV Format Requirements**

### **Required Columns** (at least one of each):
- **Transaction ID**: `Transaction ID`, `Tx Hash`, `Hash`
- **Wallet**: `Wallet Address`, `Address`, `Wallet`

### **Optional but Recommended**:
- **Platform**: `Platform`, `Protocol`, `Exchange`
- **Chain**: `Chain`, `Blockchain`, `Network`
- **Timestamp**: `Timestamp`, `Date`, `Entry Date`
- **Gas Fees**: `Gas Fees`, `Network Fees`
- **Block Number**: `Block Number`, `Block`
- **Contract**: `Contract Address`, `Pool Address`

### **Example CSV Structure**:
```csv
Transaction ID,Wallet Address,Chain,Platform,Timestamp,Gas Fees,Block Number,Contract Address
7kj9dHJ2k3H4...,DKGQ3gqfq2DpwkK...,SOL,Orca,2024-06-20 10:30:00,$0.003,245678901,9W959DqEETiGZoc...
8lm0eIK3l4I5...,DKGQ3gqfq2DpwkK...,SOL,Raydium,2024-06-20 11:15:00,$0.002,245678902,AVs9TA4nWDzfPJE...
```

---

## **Supported Chains**

- **SOL** (Solana) - Default
- **ETH** (Ethereum)
- **SUI** (Sui)
- **BASE** (Base)
- **ARB** (Arbitrum)

Chain is auto-detected from filename or you can specify manually.

---

## **Output**

All imported transactions are saved to:
- **JSON file**: `data/JSON_out/clm_transactions.json`
- **Integrated** with your existing positions automatically
- **Accessible** through the main app's [2] Transactions view

---

## **Quick Start** ⚡

**For SOL transactions** (most common):

1. **Copy** your SOL transaction export to `data/sol_transactions.csv`
2. **Run**: `python CLM.py`
3. **Press**: `i` → `a` (auto-import)
4. **Done!** ✅

Your transaction data will be immediately available in the main application!

---

## **Troubleshooting**

### **"No transactions imported"**
- Check CSV has the required columns (Transaction ID, Wallet Address)
- Verify CSV is properly formatted (not corrupted)
- Make sure file is in `data/` directory

### **"CSV format not detected"**
- Add keywords to filename: `my_sol_transactions.csv`
- Use Method 3 (direct script) to specify format manually

### **"Gas fees not parsing"**
- Ensure gas fees are in format: `$0.003` or `0.003`
- Check for extra spaces or special characters

**Need help?** The system includes detailed error messages and fallback options for most scenarios!