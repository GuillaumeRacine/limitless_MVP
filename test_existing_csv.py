#!/usr/bin/env python3
"""
Test Enhanced CSV Import on Existing Files
"""

from clm_data import CLMDataManager
import os

def main():
    # Initialize manager
    manager = CLMDataManager()
    
    # Test with your existing CSV files
    neutral_csv = 'data/Tokens_Trade_Sheet - Neutral Positions.csv'
    long_csv = 'data/Tokens_Trade_Sheet - Long Positions.csv'
    
    print('=== Testing Enhanced CSV Import on Existing Files ===')
    
    # Check if files exist
    if os.path.exists(long_csv):
        print(f'✅ Found: {long_csv}')
    else:
        print(f'❌ Missing: {long_csv}')
    
    if os.path.exists(neutral_csv):
        print(f'✅ Found: {neutral_csv}')
    else:
        print(f'❌ Missing: {neutral_csv}')
    
    # Test the enhanced import on your existing files
    try:
        manager.update_positions(neutral_csv, long_csv)
        print('✅ Enhanced CSV import successful!')
        
        # Show enhanced data structure
        if manager.long_positions:
            print('\n📋 Sample Enhanced Long Position:')
            pos = manager.long_positions[0]
            print(f'   ID: {pos["id"]}')
            print(f'   Position: {pos["position_details"]}')
            print(f'   Wallet: {pos["wallet"]}')
            print(f'   Chain: {pos["chain"]}')
            print(f'   Platform: {pos["platform"]}')
            
            # Show enhanced fields
            if 'transaction_data' in pos:
                tx_data = pos['transaction_data']
                print(f'   Transaction Data:')
                print(f'     Entry Tx: {tx_data.get("entry_tx_id", "N/A")}')
                print(f'     Gas Fees: {tx_data.get("gas_fees_paid", "N/A")}')
                
            if 'contract_data' in pos:
                contract_data = pos['contract_data']
                print(f'   Contract: {contract_data.get("contract_address", "N/A")}')
                
            if 'balance_data' in pos:
                balance_data = pos['balance_data']
                print(f'   LP Balance: {balance_data.get("current_lp_balance", "N/A")}')
        
        print(f'\n📊 Total Positions Loaded:')
        print(f'   Long: {len(manager.long_positions)}')
        print(f'   Neutral: {len(manager.neutral_positions)}')
        print(f'   Closed: {len(manager.closed_positions)}')
        
        # Test multi-chain import with your existing files
        print('\n=== Testing Multi-Chain Import Format ===')
        csv_configs = [
            {
                'path': long_csv,
                'chain': 'Mixed',  # Your file has multiple chains
                'type': 'positions',
                'strategy': 'long'
            }
        ]
        
        if os.path.exists(neutral_csv):
            csv_configs.append({
                'path': neutral_csv,
                'chain': 'Mixed',
                'type': 'positions', 
                'strategy': 'neutral'
            })
        
        results = manager.import_multi_chain_csvs(csv_configs)
        
        print('\n✅ Multi-chain import test completed!')
        
        # Show any errors
        if results['errors']:
            print('\n⚠️ Errors encountered:')
            for error in results['errors']:
                print(f'   - {error}')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()