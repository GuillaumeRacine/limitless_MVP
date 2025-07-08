#!/usr/bin/env python3
"""
Test script for the new data management system.
This demonstrates CRUD operations and direct API integrations.
"""

import os
import sys
from datetime import datetime
from data_manager_v2 import DataManagerV2
from platform_apis import PlatformAPIManager
from data_models import StrategyType, PositionType, PositionStatus, TransactionType

def test_basic_crud_operations():
    """Test basic CRUD operations"""
    print("=== Testing Basic CRUD Operations ===")
    
    # Initialize data manager
    dm = DataManagerV2()
    
    # Test wallet operations
    print("\n1. Testing Wallet Operations:")
    wallet = dm.create_wallet(
        address="DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k",
        chain="solana",
        label="Main Trading Wallet"
    )
    print(f"Created wallet: {wallet.id} - {wallet.address}")
    
    # Test token operations
    print("\n2. Testing Token Operations:")
    sol_token = dm.get_token_by_symbol("SOL")
    usdc_token = dm.get_token_by_symbol("USDC")
    print(f"Found SOL token: {sol_token.id} - {sol_token.symbol}")
    print(f"Found USDC token: {usdc_token.id} - {usdc_token.symbol}")
    
    # Test platform operations
    print("\n3. Testing Platform Operations:")
    raydium_platform = dm.get_platform_by_name("Raydium")
    print(f"Found Raydium platform: {raydium_platform.id} - {raydium_platform.name}")
    
    # Test trading pair operations
    print("\n4. Testing Trading Pair Operations:")
    trading_pair = dm.create_trading_pair(
        base_token_id=sol_token.id,
        quote_token_id=usdc_token.id,
        platform_id=raydium_platform.id,
        pool_address="POOL_ADDRESS_HERE"
    )
    print(f"Created trading pair: {trading_pair.id} - {sol_token.symbol}/{usdc_token.symbol}")
    
    # Test position operations
    print("\n5. Testing Position Operations:")
    position = dm.create_position(
        wallet_id=wallet.id,
        trading_pair_id=trading_pair.id,
        strategy_type=StrategyType.LONG,
        position_type=PositionType.CLM,
        entry_value_usd=21105.0,
        entry_date=datetime.now(),
        min_range=140.0,
        max_range=171.0
    )
    print(f"Created position: {position.id} - {position.strategy_type.value}")
    
    # Test transaction operations
    print("\n6. Testing Transaction Operations:")
    transaction = dm.create_transaction(
        wallet_id=wallet.id,
        tx_hash="TX_HASH_HERE",
        chain="solana",
        platform_id=raydium_platform.id,
        transaction_type=TransactionType.ENTRY,
        position_id=position.id,
        timestamp=datetime.now()
    )
    print(f"Created transaction: {transaction.id} - {transaction.transaction_type.value}")
    
    # Test price data operations
    print("\n7. Testing Price Data Operations:")
    price_data = dm.add_price_data(
        token_id=sol_token.id,
        price_usd=145.50,
        source="raydium_api"
    )
    print(f"Added price data: {price_data.id} - ${price_data.price_usd}")
    
    # Test portfolio snapshot
    print("\n8. Testing Portfolio Snapshot:")
    snapshot = dm.create_portfolio_snapshot(
        wallet_id=wallet.id,
        total_value_usd=21105.0,
        position_count=1,
        pnl_24h=150.0
    )
    print(f"Created portfolio snapshot: {snapshot.id} - ${snapshot.total_value_usd}")
    
    print("\n=== CRUD Operations Test Complete ===")
    return wallet, position, trading_pair

def test_data_relationships():
    """Test data relationships and lookups"""
    print("\n=== Testing Data Relationships ===")
    
    dm = DataManagerV2()
    
    # Get all wallets
    wallets = dm.list_wallets()
    print(f"Total wallets: {len(wallets)}")
    
    # Get all positions for a wallet
    if wallets:
        wallet = wallets[0]
        positions = dm.list_positions(wallet_id=wallet.id)
        print(f"Positions for wallet {wallet.address}: {len(positions)}")
        
        # Get transactions for this wallet
        transactions = dm.list_transactions(wallet_id=wallet.id)
        print(f"Transactions for wallet {wallet.address}: {len(transactions)}")
        
        # Get portfolio snapshots
        snapshots = dm.get_portfolio_snapshots(wallet.id)
        print(f"Portfolio snapshots: {len(snapshots)}")
    
    # Get all active positions
    active_positions = dm.list_positions(status=PositionStatus.ACTIVE)
    print(f"Total active positions: {len(active_positions)}")
    
    print("=== Data Relationships Test Complete ===")

def test_platform_apis():
    """Test direct platform API integrations"""
    print("\n=== Testing Platform APIs ===")
    
    # Initialize API manager
    api_manager = PlatformAPIManager()
    
    # Test health check
    print("\n1. API Health Check:")
    health = api_manager.health_check()
    for platform, is_healthy in health.items():
        status = "✓" if is_healthy else "✗"
        print(f"  {platform}: {status}")
    
    # Test token price fetching (with mock data since we need real IDs)
    print("\n2. Token Price Testing:")
    print("  Note: This requires real token IDs/addresses to work")
    
    # Example of how to get prices (would need real token addresses)
    # sol_price = api_manager.get_token_price('raydium', 'SOL_TOKEN_ADDRESS')
    # print(f"SOL price from Raydium: ${sol_price}")
    
    print("=== Platform APIs Test Complete ===")

def test_data_migration():
    """Test migrating existing CSV data to new format"""
    print("\n=== Testing Data Migration ===")
    
    dm = DataManagerV2()
    
    # Example: Create positions from existing CSV data structure
    print("1. Creating test positions from CSV-like data:")
    
    # Simulate CSV data (like your current structure)
    csv_positions = [
        {
            "position_details": "SOL / USDC",
            "strategy": "long",
            "platform": "Raydium",
            "wallet": "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k",
            "entry_value": 21105.0,
            "min_range": 140.0,
            "max_range": 171.0,
            "chain": "solana"
        },
        {
            "position_details": "JLP / SOL",
            "strategy": "long",
            "platform": "Orca",
            "wallet": "DKGQ3gqfq2DpwkKZyazjMY1c1vKjzoX1A9jFrhVnzA3k",
            "entry_value": 22509.0,
            "min_range": 0.0264,
            "max_range": 0.032,
            "chain": "solana"
        }
    ]
    
    for csv_pos in csv_positions:
        # Get or create wallet
        wallet = dm.get_wallet_by_address(csv_pos["wallet"])
        if not wallet:
            wallet = dm.create_wallet(
                address=csv_pos["wallet"],
                chain=csv_pos["chain"],
                label="Migrated Wallet"
            )
        
        # Get platform
        platform = dm.get_platform_by_name(csv_pos["platform"])
        
        # Parse token pair
        tokens = csv_pos["position_details"].split(" / ")
        base_token = dm.get_token_by_symbol(tokens[0])
        quote_token = dm.get_token_by_symbol(tokens[1])
        
        # Get or create trading pair
        trading_pair = dm.find_trading_pair(
            base_token.id, quote_token.id, platform.id
        )
        if not trading_pair:
            trading_pair = dm.create_trading_pair(
                base_token_id=base_token.id,
                quote_token_id=quote_token.id,
                platform_id=platform.id
            )
        
        # Create position
        position = dm.create_position(
            wallet_id=wallet.id,
            trading_pair_id=trading_pair.id,
            strategy_type=StrategyType(csv_pos["strategy"]),
            position_type=PositionType.CLM,
            entry_value_usd=csv_pos["entry_value"],
            min_range=csv_pos["min_range"],
            max_range=csv_pos["max_range"]
        )
        
        print(f"  Migrated position: {position.id} - {csv_pos['position_details']}")
    
    print("=== Data Migration Test Complete ===")

def test_advanced_queries():
    """Test advanced data queries and analytics"""
    print("\n=== Testing Advanced Queries ===")
    
    dm = DataManagerV2()
    
    # Portfolio analytics
    print("1. Portfolio Analytics:")
    wallets = dm.list_wallets()
    for wallet in wallets:
        positions = dm.list_positions(wallet_id=wallet.id)
        active_positions = dm.list_positions(wallet_id=wallet.id, status=PositionStatus.ACTIVE)
        
        total_value = sum(p.entry_value_usd or 0 for p in positions)
        print(f"  Wallet {wallet.address[:8]}...")
        print(f"    Total positions: {len(positions)}")
        print(f"    Active positions: {len(active_positions)}")
        print(f"    Total value: ${total_value:,.2f}")
    
    # Platform distribution
    print("\n2. Platform Distribution:")
    all_positions = dm.list_positions()
    platform_count = {}
    for position in all_positions:
        trading_pair = dm.get_trading_pair(position.trading_pair_id)
        platform = dm.get_platform(trading_pair.platform_id)
        platform_count[platform.name] = platform_count.get(platform.name, 0) + 1
    
    for platform, count in platform_count.items():
        print(f"  {platform}: {count} positions")
    
    # Strategy distribution
    print("\n3. Strategy Distribution:")
    strategy_count = {}
    for position in all_positions:
        strategy = position.strategy_type.value
        strategy_count[strategy] = strategy_count.get(strategy, 0) + 1
    
    for strategy, count in strategy_count.items():
        print(f"  {strategy}: {count} positions")
    
    print("=== Advanced Queries Test Complete ===")

def cleanup_test_data():
    """Clean up test data"""
    print("\n=== Cleaning Up Test Data ===")
    
    # Remove test data directory
    import shutil
    test_data_dir = "data/v2_data"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
        print(f"Removed test data directory: {test_data_dir}")
    
    print("=== Cleanup Complete ===")

def main():
    """Main test function"""
    print("Starting DataManagerV2 Test Suite")
    print("=" * 50)
    
    try:
        # Run all tests
        test_basic_crud_operations()
        test_data_relationships()
        test_platform_apis()
        test_data_migration()
        test_advanced_queries()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
        # Ask user if they want to cleanup
        cleanup = input("\nDo you want to cleanup test data? (y/n): ")
        if cleanup.lower() == 'y':
            cleanup_test_data()
        else:
            print("Test data preserved in data/v2_data/")
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()