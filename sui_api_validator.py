#!/usr/bin/env python3
"""
SUI API Validator - Cross-validate and augment SUI transaction data using SUI RPC
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
import pandas as pd

class SuiAPIValidator:
    def __init__(self, rpc_url="https://fullnode.mainnet.sui.io:443"):
        self.rpc_url = rpc_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
    def _make_rpc_call(self, method: str, params: List[Any]) -> Dict:
        """Make a JSON-RPC call to SUI node"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            response = self.session.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                print(f"RPC Error: {result['error']}")
                return None
                
            return result.get('result')
        except Exception as e:
            print(f"RPC call failed: {e}")
            return None
    
    def get_transaction(self, tx_digest: str) -> Dict:
        """Get detailed transaction information"""
        params = [
            tx_digest,
            {
                "showInput": True,
                "showRawInput": False,
                "showEffects": True,
                "showEvents": True,
                "showObjectChanges": True,
                "showBalanceChanges": True
            }
        ]
        
        return self._make_rpc_call("sui_getTransactionBlock", params)
    
    def get_transactions_for_address(self, address: str, cursor: str = None, limit: int = 50) -> Dict:
        """Get transactions for a specific address"""
        query = {
            "filter": {
                "FromAddress": address
            },
            "options": {
                "showInput": True,
                "showEffects": True,
                "showEvents": True,
                "showBalanceChanges": True
            }
        }
        
        params = [query]
        if cursor:
            params.append(cursor)
        params.append(limit)
        params.append(False)  # descending order
        
        return self._make_rpc_call("suix_queryTransactionBlocks", params)
    
    def get_object(self, object_id: str) -> Dict:
        """Get object details (useful for token info)"""
        params = [
            object_id,
            {
                "showType": True,
                "showOwner": True,
                "showPreviousTransaction": True,
                "showDisplay": True,
                "showContent": True,
                "showBcs": False,
                "showStorageRebate": True
            }
        ]
        
        return self._make_rpc_call("sui_getObject", params)
    
    def get_balance(self, address: str, coin_type: str = None) -> Dict:
        """Get balance for an address"""
        params = [address]
        if coin_type:
            params.append(coin_type)
            
        if coin_type:
            return self._make_rpc_call("suix_getBalance", params)
        else:
            return self._make_rpc_call("suix_getAllBalances", params)
    
    def get_coin_metadata(self, coin_type: str) -> Dict:
        """Get metadata for a coin type"""
        return self._make_rpc_call("suix_getCoinMetadata", [coin_type])
    
    def parse_transaction_data(self, tx_data: Dict) -> Dict:
        """Parse SUI transaction data into a structured format"""
        if not tx_data:
            return None
            
        try:
            parsed = {
                'digest': tx_data.get('digest'),
                'timestamp_ms': tx_data.get('timestampMs'),
                'checkpoint': tx_data.get('checkpoint'),
                'sender': None,
                'gas_used': 0,
                'status': 'Unknown',
                'balance_changes': [],
                'events': [],
                'object_changes': []
            }
            
            # Parse transaction input
            if 'transaction' in tx_data and 'data' in tx_data['transaction']:
                data = tx_data['transaction']['data']
                parsed['sender'] = data.get('sender')
                
                # Get gas information
                if 'gasData' in data:
                    gas_data = data['gasData']
                    parsed['gas_budget'] = int(gas_data.get('budget', 0))
                    parsed['gas_price'] = int(gas_data.get('price', 0))
            
            # Parse effects
            if 'effects' in tx_data:
                effects = tx_data['effects']
                parsed['status'] = effects['status']['status']
                
                # Calculate gas used
                if 'gasUsed' in effects:
                    gas_used = effects['gasUsed']
                    storage_cost = int(gas_used.get('storageCost', 0))
                    storage_rebate = int(gas_used.get('storageRebate', 0))
                    computation_cost = int(gas_used.get('computationCost', 0))
                    parsed['gas_used'] = (storage_cost - storage_rebate + computation_cost) / 1e9  # Convert to SUI
            
            # Parse balance changes
            if 'balanceChanges' in tx_data:
                for change in tx_data['balanceChanges']:
                    parsed['balance_changes'].append({
                        'owner': change.get('owner'),
                        'coin_type': change.get('coinType'),
                        'amount': int(change.get('amount', 0))
                    })
            
            # Parse events
            if 'events' in tx_data:
                for event in tx_data['events']:
                    parsed['events'].append({
                        'type': event.get('type'),
                        'parsed_json': event.get('parsedJson', {})
                    })
            
            # Parse object changes
            if 'objectChanges' in tx_data:
                for change in tx_data['objectChanges']:
                    parsed['object_changes'].append({
                        'type': change.get('type'),
                        'object_type': change.get('objectType'),
                        'object_id': change.get('objectId')
                    })
            
            return parsed
            
        except Exception as e:
            print(f"Error parsing transaction: {e}")
            return None
    
    def validate_csv_transaction(self, csv_row: Dict) -> Dict:
        """Validate and enhance a transaction from CSV data"""
        # Extract transaction digest from CSV
        digest = csv_row.get('Digest', '')
        if not digest:
            return {'status': 'error', 'message': 'No transaction digest found'}
        
        # Fetch transaction from blockchain
        tx_data = self.get_transaction(digest)
        if not tx_data:
            return {'status': 'error', 'message': 'Transaction not found on chain'}
        
        # Parse blockchain data
        parsed = self.parse_transaction_data(tx_data)
        if not parsed:
            return {'status': 'error', 'message': 'Failed to parse transaction'}
        
        # Compare with CSV data
        validation_result = {
            'status': 'validated',
            'digest': digest,
            'csv_data': csv_row,
            'chain_data': parsed,
            'discrepancies': []
        }
        
        # Check timestamp
        csv_timestamp = csv_row.get('Time')
        if csv_timestamp and parsed['timestamp_ms']:
            csv_ts = int(csv_timestamp)
            chain_ts = int(parsed['timestamp_ms'])
            if abs(csv_ts - chain_ts) > 1000:  # Allow 1 second difference
                validation_result['discrepancies'].append({
                    'field': 'timestamp',
                    'csv': csv_ts,
                    'chain': chain_ts
                })
        
        # Check gas fee
        csv_gas = csv_row.get('Gas Fee', '').replace(' SUI', '')
        if csv_gas:
            try:
                csv_gas_float = float(csv_gas)
                chain_gas_float = parsed['gas_used']
                if abs(csv_gas_float - chain_gas_float) > 0.0001:
                    validation_result['discrepancies'].append({
                        'field': 'gas_fee',
                        'csv': csv_gas_float,
                        'chain': chain_gas_float
                    })
            except:
                pass
        
        return validation_result
    
    def enhance_transaction_data(self, csv_path: str, output_path: str = None):
        """Read CSV file and enhance with blockchain data"""
        print(f"Reading CSV file: {csv_path}")
        df = pd.read_csv(csv_path)
        
        enhanced_data = []
        total = len(df)
        
        for idx, row in df.iterrows():
            print(f"Processing transaction {idx+1}/{total}...")
            
            # Validate against blockchain
            validation = self.validate_csv_transaction(row.to_dict())
            
            if validation['status'] == 'validated':
                chain_data = validation['chain_data']
                
                # Enhance row with blockchain data
                enhanced_row = row.to_dict()
                enhanced_row['block_number'] = chain_data.get('checkpoint')
                enhanced_row['tx_status'] = chain_data.get('status')
                enhanced_row['sender'] = chain_data.get('sender')
                enhanced_row['gas_used_sui'] = chain_data.get('gas_used')
                
                # Add balance changes
                if chain_data['balance_changes']:
                    balance_changes_str = json.dumps(chain_data['balance_changes'])
                    enhanced_row['balance_changes'] = balance_changes_str
                
                # Add validation status
                enhanced_row['validation_status'] = 'verified'
                enhanced_row['discrepancies'] = len(validation['discrepancies'])
                
                enhanced_data.append(enhanced_row)
            else:
                # Keep original data but mark as unverified
                enhanced_row = row.to_dict()
                enhanced_row['validation_status'] = 'unverified'
                enhanced_row['validation_error'] = validation.get('message')
                enhanced_data.append(enhanced_row)
            
            # Rate limiting
            time.sleep(0.1)
        
        # Create enhanced dataframe
        enhanced_df = pd.DataFrame(enhanced_data)
        
        # Save to file
        if output_path:
            enhanced_df.to_csv(output_path, index=False)
            print(f"Enhanced data saved to: {output_path}")
        
        # Print summary
        verified = len([x for x in enhanced_data if x.get('validation_status') == 'verified'])
        print(f"\nValidation Summary:")
        print(f"Total transactions: {total}")
        print(f"Verified: {verified}")
        print(f"Unverified: {total - verified}")
        
        return enhanced_df

def main():
    """Example usage"""
    validator = SuiAPIValidator()
    
    # Test with a specific transaction
    test_digest = "FyhFDN9FEuEnGBJhwBfTTpAW8YA2auhz2rg7thAVF1V9"
    print(f"Testing with transaction: {test_digest}")
    
    tx_data = validator.get_transaction(test_digest)
    if tx_data:
        parsed = validator.parse_transaction_data(tx_data)
        print(json.dumps(parsed, indent=2))
    
    # Example of enhancing CSV data
    # csv_files = [
    #     "data/sui_0x811c7733b0e283051b3639c529eeb17784f9b19d275a7c368a3979f509ea519a_activities_2025-06-24_22_15.csv",
    #     "data/sui_0x1df6f74ae73e453bc276d84512f1cd8387b643432163221df4f4c76112bfaf66_activities_2025-06-24_22_19.csv",
    #     "data/sui_0xa1c48a832320557655096e4fb475df116f9b0215fea51ef1b189e346325b9e2d_activities_2025-06-24_22_20.csv"
    # ]
    # 
    # for csv_file in csv_files:
    #     output_file = csv_file.replace('.csv', '_enhanced.csv')
    #     validator.enhance_transaction_data(csv_file, output_file)

if __name__ == "__main__":
    main()