#!/usr/bin/env python3
"""
CLI interface for the new data management system.
This provides a command-line interface to test and manage the V2 data system.
"""

import sys
import argparse
from datetime import datetime
from data_manager_v2 import DataManagerV2
from platform_apis import PlatformAPIManager
from data_models import StrategyType, PositionType, PositionStatus, TransactionType

class CLMV2CLI:
    def __init__(self):
        self.dm = DataManagerV2()
        self.api_manager = PlatformAPIManager()
    
    def list_wallets(self):
        """List all wallets"""
        wallets = self.dm.list_wallets()
        
        if not wallets:
            print("No wallets found.")
            return
        
        print(f"\n{'ID':<10} {'Address':<50} {'Chain':<10} {'Label':<20}")
        print("-" * 90)
        
        for wallet in wallets:
            print(f"{wallet.id[:8]:<10} {wallet.address:<50} {wallet.chain:<10} {wallet.label or 'N/A':<20}")
    
    def list_positions(self, wallet_id=None, status=None):
        """List positions with optional filtering"""
        if status:
            try:
                status = PositionStatus(status)
            except ValueError:
                print(f"Invalid status: {status}. Valid options: active, closed, liquidated")
                return
        
        positions = self.dm.list_positions(wallet_id=wallet_id, status=status)
        
        if not positions:
            print("No positions found.")
            return
        
        print(f"\n{'ID':<10} {'Wallet':<12} {'Pair':<15} {'Strategy':<10} {'Type':<8} {'Entry $':<12} {'Status':<10}")
        print("-" * 90)
        
        for position in positions:
            # Get trading pair info
            trading_pair = self.dm.get_trading_pair(position.trading_pair_id)
            base_token = self.dm.get_token(trading_pair.base_token_id)
            quote_token = self.dm.get_token(trading_pair.quote_token_id)
            pair_str = f"{base_token.symbol}/{quote_token.symbol}"
            
            wallet = self.dm.get_wallet(position.wallet_id)
            
            print(f"{position.id[:8]:<10} {wallet.address[:10]:<12} {pair_str:<15} "
                  f"{position.strategy_type.value:<10} {position.position_type.value:<8} "
                  f"${position.entry_value_usd or 0:<11.2f} {position.status.value:<10}")
    
    def list_platforms(self):
        """List all platforms"""
        platforms = self.dm.list_platforms()
        
        if not platforms:
            print("No platforms found.")
            return
        
        print(f"\n{'ID':<12} {'Name':<15} {'Type':<8} {'Chain':<10} {'API Endpoint':<30}")
        print("-" * 80)
        
        for platform in platforms:
            print(f"{platform.id:<12} {platform.name:<15} {platform.protocol_type:<8} "
                  f"{platform.chain:<10} {platform.api_endpoint or 'N/A':<30}")
    
    def list_tokens(self):
        """List all tokens"""
        tokens = self.dm.list_tokens()
        
        if not tokens:
            print("No tokens found.")
            return
        
        print(f"\n{'ID':<8} {'Symbol':<10} {'Name':<20} {'Chain':<10} {'Type':<10}")
        print("-" * 60)
        
        for token in tokens:
            print(f"{token.id:<8} {token.symbol:<10} {token.name:<20} {token.chain:<10} {token.token_type:<10}")
    
    def create_wallet(self, address, chain, label=None):
        """Create a new wallet"""
        try:
            wallet = self.dm.create_wallet(address=address, chain=chain, label=label)
            print(f"Created wallet: {wallet.id} - {wallet.address}")
            return wallet
        except Exception as e:
            print(f"Error creating wallet: {e}")
    
    def create_position(self, wallet_id, base_token, quote_token, platform, strategy, position_type, entry_value, min_range=None, max_range=None):
        """Create a new position"""
        try:
            # Get or create wallet
            wallet = self.dm.get_wallet(wallet_id)
            if not wallet:
                print(f"Wallet {wallet_id} not found.")
                return
            
            # Get tokens
            base_token_obj = self.dm.get_token_by_symbol(base_token)
            quote_token_obj = self.dm.get_token_by_symbol(quote_token)
            
            if not base_token_obj or not quote_token_obj:
                print(f"Token not found: {base_token} or {quote_token}")
                return
            
            # Get platform
            platform_obj = self.dm.get_platform_by_name(platform)
            if not platform_obj:
                print(f"Platform {platform} not found.")
                return
            
            # Get or create trading pair
            trading_pair = self.dm.find_trading_pair(
                base_token_obj.id, quote_token_obj.id, platform_obj.id
            )
            if not trading_pair:
                trading_pair = self.dm.create_trading_pair(
                    base_token_id=base_token_obj.id,
                    quote_token_id=quote_token_obj.id,
                    platform_id=platform_obj.id
                )
            
            # Create position
            position = self.dm.create_position(
                wallet_id=wallet.id,
                trading_pair_id=trading_pair.id,
                strategy_type=StrategyType(strategy),
                position_type=PositionType(position_type),
                entry_value_usd=float(entry_value),
                min_range=float(min_range) if min_range else None,
                max_range=float(max_range) if max_range else None
            )
            
            print(f"Created position: {position.id} - {base_token}/{quote_token} on {platform}")
            return position
            
        except Exception as e:
            print(f"Error creating position: {e}")
    
    def get_position_details(self, position_id):
        """Get detailed information about a position"""
        position = self.dm.get_position(position_id)
        if not position:
            print(f"Position {position_id} not found.")
            return
        
        # Get related data
        wallet = self.dm.get_wallet(position.wallet_id)
        trading_pair = self.dm.get_trading_pair(position.trading_pair_id)
        base_token = self.dm.get_token(trading_pair.base_token_id)
        quote_token = self.dm.get_token(trading_pair.quote_token_id)
        platform = self.dm.get_platform(trading_pair.platform_id)
        
        print(f"\nPosition Details:")
        print(f"  ID: {position.id}")
        print(f"  Wallet: {wallet.address}")
        print(f"  Trading Pair: {base_token.symbol}/{quote_token.symbol}")
        print(f"  Platform: {platform.name}")
        print(f"  Strategy: {position.strategy_type.value}")
        print(f"  Type: {position.position_type.value}")
        print(f"  Entry Value: ${position.entry_value_usd or 0:.2f}")
        print(f"  Range: {position.min_range} - {position.max_range}")
        print(f"  Status: {position.status.value}")
        print(f"  Created: {position.created_at}")
        print(f"  Updated: {position.updated_at}")
        
        # Get transactions for this position
        transactions = self.dm.list_transactions(position_id=position.id)
        if transactions:
            print(f"\n  Transactions ({len(transactions)}):")
            for tx in transactions:
                print(f"    {tx.id[:8]} - {tx.transaction_type.value} - {tx.tx_hash[:16]}...")
    
    def health_check(self):
        """Check API health"""
        print("\nPlatform API Health Check:")
        health = self.api_manager.health_check()
        
        for platform, is_healthy in health.items():
            status = "✓ Healthy" if is_healthy else "✗ Unhealthy"
            print(f"  {platform.capitalize()}: {status}")
    
    def portfolio_summary(self, wallet_id=None):
        """Show portfolio summary"""
        if wallet_id:
            wallets = [self.dm.get_wallet(wallet_id)]
            if not wallets[0]:
                print(f"Wallet {wallet_id} not found.")
                return
        else:
            wallets = self.dm.list_wallets()
        
        print("\nPortfolio Summary:")
        print("=" * 60)
        
        total_value = 0
        total_positions = 0
        
        for wallet in wallets:
            if not wallet:
                continue
                
            positions = self.dm.list_positions(wallet_id=wallet.id)
            active_positions = self.dm.list_positions(wallet_id=wallet.id, status=PositionStatus.ACTIVE)
            
            wallet_value = sum(p.entry_value_usd or 0 for p in positions)
            total_value += wallet_value
            total_positions += len(positions)
            
            print(f"\nWallet: {wallet.address[:16]}...")
            print(f"  Total Positions: {len(positions)}")
            print(f"  Active Positions: {len(active_positions)}")
            print(f"  Total Value: ${wallet_value:,.2f}")
            
            # Platform breakdown
            platform_breakdown = {}
            for position in positions:
                trading_pair = self.dm.get_trading_pair(position.trading_pair_id)
                platform = self.dm.get_platform(trading_pair.platform_id)
                platform_breakdown[platform.name] = platform_breakdown.get(platform.name, 0) + (position.entry_value_usd or 0)
            
            if platform_breakdown:
                print("  Platform Breakdown:")
                for platform, value in platform_breakdown.items():
                    print(f"    {platform}: ${value:,.2f}")
        
        print(f"\nOverall Summary:")
        print(f"  Total Wallets: {len(wallets)}")
        print(f"  Total Positions: {total_positions}")
        print(f"  Total Portfolio Value: ${total_value:,.2f}")

def main():
    """Main CLI function"""
    cli = CLMV2CLI()
    
    parser = argparse.ArgumentParser(description='CLM Portfolio Tracker V2 CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List commands
    list_parser = subparsers.add_parser('list', help='List items')
    list_parser.add_argument('item', choices=['wallets', 'positions', 'platforms', 'tokens'], help='Item to list')
    list_parser.add_argument('--wallet-id', help='Filter by wallet ID')
    list_parser.add_argument('--status', choices=['active', 'closed', 'liquidated'], help='Filter by status')
    
    # Create commands
    create_parser = subparsers.add_parser('create', help='Create items')
    create_subparsers = create_parser.add_subparsers(dest='create_item', help='Item to create')
    
    # Create wallet
    wallet_parser = create_subparsers.add_parser('wallet', help='Create wallet')
    wallet_parser.add_argument('address', help='Wallet address')
    wallet_parser.add_argument('chain', help='Blockchain')
    wallet_parser.add_argument('--label', help='Wallet label')
    
    # Create position
    position_parser = create_subparsers.add_parser('position', help='Create position')
    position_parser.add_argument('wallet_id', help='Wallet ID')
    position_parser.add_argument('base_token', help='Base token symbol')
    position_parser.add_argument('quote_token', help='Quote token symbol')
    position_parser.add_argument('platform', help='Platform name')
    position_parser.add_argument('strategy', choices=['long', 'neutral', 'short'], help='Strategy type')
    position_parser.add_argument('position_type', choices=['clm', 'perp', 'spot'], help='Position type')
    position_parser.add_argument('entry_value', type=float, help='Entry value in USD')
    position_parser.add_argument('--min-range', type=float, help='Minimum range')
    position_parser.add_argument('--max-range', type=float, help='Maximum range')
    
    # Get commands
    get_parser = subparsers.add_parser('get', help='Get item details')
    get_parser.add_argument('item', choices=['position'], help='Item to get')
    get_parser.add_argument('id', help='Item ID')
    
    # Health check
    subparsers.add_parser('health', help='Check API health')
    
    # Portfolio summary
    portfolio_parser = subparsers.add_parser('portfolio', help='Show portfolio summary')
    portfolio_parser.add_argument('--wallet-id', help='Specific wallet ID')
    
    # Test command
    subparsers.add_parser('test', help='Run test suite')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            if args.item == 'wallets':
                cli.list_wallets()
            elif args.item == 'positions':
                cli.list_positions(wallet_id=args.wallet_id, status=args.status)
            elif args.item == 'platforms':
                cli.list_platforms()
            elif args.item == 'tokens':
                cli.list_tokens()
        
        elif args.command == 'create':
            if args.create_item == 'wallet':
                cli.create_wallet(args.address, args.chain, args.label)
            elif args.create_item == 'position':
                cli.create_position(
                    args.wallet_id, args.base_token, args.quote_token, 
                    args.platform, args.strategy, args.position_type, 
                    args.entry_value, args.min_range, args.max_range
                )
        
        elif args.command == 'get':
            if args.item == 'position':
                cli.get_position_details(args.id)
        
        elif args.command == 'health':
            cli.health_check()
        
        elif args.command == 'portfolio':
            cli.portfolio_summary(args.wallet_id)
        
        elif args.command == 'test':
            print("Running test suite...")
            import subprocess
            subprocess.run([sys.executable, 'test_data_manager_v2.py'])
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()