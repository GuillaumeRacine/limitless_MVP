#!/usr/bin/env python3
"""
New Data Manager with CRUD operations and direct API integrations.
This runs alongside the existing CLMDataManager for testing.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from data_models import (
    Wallet, Token, Platform, TradingPair, Position, Transaction, 
    PriceData, PortfolioSnapshot, TokenAmount, PerformanceMetrics,
    StrategyType, PositionType, PositionStatus, TransactionType,
    DataModelEncoder, from_dict
)

class DataManagerV2:
    def __init__(self, data_dir: str = "data/v2_data"):
        self.data_dir = data_dir
        self.ensure_data_dir()
        
        # JSON file paths
        self.wallets_file = os.path.join(data_dir, "wallets.json")
        self.tokens_file = os.path.join(data_dir, "tokens.json")
        self.platforms_file = os.path.join(data_dir, "platforms.json")
        self.trading_pairs_file = os.path.join(data_dir, "trading_pairs.json")
        self.positions_file = os.path.join(data_dir, "positions.json")
        self.transactions_file = os.path.join(data_dir, "transactions.json")
        self.price_data_file = os.path.join(data_dir, "price_data.json")
        self.portfolio_snapshots_file = os.path.join(data_dir, "portfolio_snapshots.json")
        
        # Initialize seed data
        self.initialize_seed_data()
    
    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_to_file(self, data: List[Any], file_path: str):
        """Save data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, cls=DataModelEncoder, indent=2)
    
    def load_from_file(self, file_path: str, data_class) -> List[Any]:
        """Load data from JSON file"""
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            return [from_dict(data_class, item) for item in data]
    
    def initialize_seed_data(self):
        """Initialize with known tokens and platforms from current data"""
        # Initialize tokens if not exists
        if not os.path.exists(self.tokens_file):
            tokens = [
                Token(id="sol", symbol="SOL", name="Solana", chain="solana", token_type="native"),
                Token(id="usdc", symbol="USDC", name="USD Coin", chain="multi", token_type="native"),
                Token(id="usdt", symbol="USDT", name="Tether", chain="multi", token_type="native"),
                Token(id="eth", symbol="ETH", name="Ethereum", chain="ethereum", token_type="native"),
                Token(id="btc", symbol="BTC", name="Bitcoin", chain="bitcoin", token_type="native"),
                Token(id="sui", symbol="SUI", name="Sui", chain="sui", token_type="native"),
                Token(id="wbtc", symbol="WBTC", name="Wrapped Bitcoin", chain="ethereum", token_type="wrapped"),
                Token(id="cbbtc", symbol="cbBTC", name="Coinbase Wrapped Bitcoin", chain="base", token_type="wrapped"),
                Token(id="wheth", symbol="whETH", name="Wrapped Ethereum", chain="solana", token_type="wrapped"),
                Token(id="weth", symbol="WETH", name="Wrapped Ethereum", chain="ethereum", token_type="wrapped"),
                Token(id="jlp", symbol="JLP", name="Jupiter LP Token", chain="solana", token_type="pool"),
                Token(id="orca", symbol="ORCA", name="Orca", chain="solana", token_type="native"),
                Token(id="ray", symbol="RAY", name="Raydium", chain="solana", token_type="native"),
            ]
            self.save_to_file([token.__dict__ for token in tokens], self.tokens_file)
        
        # Initialize platforms if not exists
        if not os.path.exists(self.platforms_file):
            platforms = [
                Platform(id="raydium", name="Raydium", protocol_type="dex", chain="solana", 
                        api_endpoint="https://api.raydium.io/v2/"),
                Platform(id="orca", name="Orca", protocol_type="dex", chain="solana",
                        api_endpoint="https://api.orca.so/v1/"),
                Platform(id="jupiter", name="Jupiter", protocol_type="perp", chain="solana",
                        api_endpoint="https://api.jup.ag/"),
                Platform(id="cetus", name="CETUS", protocol_type="dex", chain="sui",
                        api_endpoint="https://api-sui.cetus.zone/"),
                Platform(id="aerodrome", name="Aerodrome", protocol_type="dex", chain="base"),
                Platform(id="gmx", name="GMX", protocol_type="perp", chain="arbitrum",
                        api_endpoint="https://api.gmx.io/"),
            ]
            self.save_to_file([platform.__dict__ for platform in platforms], self.platforms_file)
    
    # CRUD Operations for Wallets
    def create_wallet(self, address: str, chain: str, label: str = None) -> Wallet:
        """Create a new wallet"""
        wallet = Wallet(id=None, address=address, chain=chain, label=label)
        wallets = self.load_from_file(self.wallets_file, Wallet)
        wallets.append(wallet)
        self.save_to_file([w.__dict__ for w in wallets], self.wallets_file)
        return wallet
    
    def get_wallet(self, wallet_id: str) -> Optional[Wallet]:
        """Get wallet by ID"""
        wallets = self.load_from_file(self.wallets_file, Wallet)
        return next((w for w in wallets if w.id == wallet_id), None)
    
    def get_wallet_by_address(self, address: str) -> Optional[Wallet]:
        """Get wallet by address"""
        wallets = self.load_from_file(self.wallets_file, Wallet)
        return next((w for w in wallets if w.address == address), None)
    
    def update_wallet(self, wallet_id: str, **kwargs) -> bool:
        """Update wallet"""
        wallets = self.load_from_file(self.wallets_file, Wallet)
        for i, wallet in enumerate(wallets):
            if wallet.id == wallet_id:
                for key, value in kwargs.items():
                    if hasattr(wallet, key):
                        setattr(wallet, key, value)
                self.save_to_file([w.__dict__ for w in wallets], self.wallets_file)
                return True
        return False
    
    def delete_wallet(self, wallet_id: str) -> bool:
        """Delete wallet"""
        wallets = self.load_from_file(self.wallets_file, Wallet)
        wallets = [w for w in wallets if w.id != wallet_id]
        self.save_to_file([w.__dict__ for w in wallets], self.wallets_file)
        return True
    
    def list_wallets(self) -> List[Wallet]:
        """List all wallets"""
        return self.load_from_file(self.wallets_file, Wallet)
    
    # CRUD Operations for Tokens
    def create_token(self, symbol: str, name: str, chain: str, **kwargs) -> Token:
        """Create a new token"""
        token = Token(id=None, symbol=symbol, name=name, chain=chain, **kwargs)
        tokens = self.load_from_file(self.tokens_file, Token)
        tokens.append(token)
        self.save_to_file([t.__dict__ for t in tokens], self.tokens_file)
        return token
    
    def get_token(self, token_id: str) -> Optional[Token]:
        """Get token by ID"""
        tokens = self.load_from_file(self.tokens_file, Token)
        return next((t for t in tokens if t.id == token_id), None)
    
    def get_token_by_symbol(self, symbol: str, chain: str = None) -> Optional[Token]:
        """Get token by symbol"""
        tokens = self.load_from_file(self.tokens_file, Token)
        if chain:
            return next((t for t in tokens if t.symbol == symbol and t.chain == chain), None)
        return next((t for t in tokens if t.symbol == symbol), None)
    
    def list_tokens(self) -> List[Token]:
        """List all tokens"""
        return self.load_from_file(self.tokens_file, Token)
    
    # CRUD Operations for Platforms
    def create_platform(self, name: str, protocol_type: str, chain: str, **kwargs) -> Platform:
        """Create a new platform"""
        platform = Platform(id=None, name=name, protocol_type=protocol_type, chain=chain, **kwargs)
        platforms = self.load_from_file(self.platforms_file, Platform)
        platforms.append(platform)
        self.save_to_file([p.__dict__ for p in platforms], self.platforms_file)
        return platform
    
    def get_platform(self, platform_id: str) -> Optional[Platform]:
        """Get platform by ID"""
        platforms = self.load_from_file(self.platforms_file, Platform)
        return next((p for p in platforms if p.id == platform_id), None)
    
    def get_platform_by_name(self, name: str) -> Optional[Platform]:
        """Get platform by name"""
        platforms = self.load_from_file(self.platforms_file, Platform)
        return next((p for p in platforms if p.name.lower() == name.lower()), None)
    
    def list_platforms(self) -> List[Platform]:
        """List all platforms"""
        return self.load_from_file(self.platforms_file, Platform)
    
    # CRUD Operations for Trading Pairs
    def create_trading_pair(self, base_token_id: str, quote_token_id: str, 
                          platform_id: str, **kwargs) -> TradingPair:
        """Create a new trading pair"""
        pair = TradingPair(id=None, base_token_id=base_token_id, 
                          quote_token_id=quote_token_id, platform_id=platform_id, **kwargs)
        pairs = self.load_from_file(self.trading_pairs_file, TradingPair)
        pairs.append(pair)
        self.save_to_file([p.__dict__ for p in pairs], self.trading_pairs_file)
        return pair
    
    def get_trading_pair(self, pair_id: str) -> Optional[TradingPair]:
        """Get trading pair by ID"""
        pairs = self.load_from_file(self.trading_pairs_file, TradingPair)
        return next((p for p in pairs if p.id == pair_id), None)
    
    def find_trading_pair(self, base_token_id: str, quote_token_id: str, 
                         platform_id: str) -> Optional[TradingPair]:
        """Find trading pair by tokens and platform"""
        pairs = self.load_from_file(self.trading_pairs_file, TradingPair)
        return next((p for p in pairs if p.base_token_id == base_token_id and 
                    p.quote_token_id == quote_token_id and p.platform_id == platform_id), None)
    
    def list_trading_pairs(self) -> List[TradingPair]:
        """List all trading pairs"""
        return self.load_from_file(self.trading_pairs_file, TradingPair)
    
    # CRUD Operations for Positions
    def create_position(self, wallet_id: str, trading_pair_id: str, 
                       strategy_type: StrategyType, position_type: PositionType, 
                       **kwargs) -> Position:
        """Create a new position"""
        position = Position(id=None, wallet_id=wallet_id, trading_pair_id=trading_pair_id,
                          strategy_type=strategy_type, position_type=position_type, **kwargs)
        positions = self.load_from_file(self.positions_file, Position)
        positions.append(position)
        self.save_to_file([p.__dict__ for p in positions], self.positions_file)
        return position
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """Get position by ID"""
        positions = self.load_from_file(self.positions_file, Position)
        return next((p for p in positions if p.id == position_id), None)
    
    def update_position(self, position_id: str, **kwargs) -> bool:
        """Update position"""
        positions = self.load_from_file(self.positions_file, Position)
        for i, position in enumerate(positions):
            if position.id == position_id:
                for key, value in kwargs.items():
                    if hasattr(position, key):
                        setattr(position, key, value)
                position.updated_at = datetime.now()
                self.save_to_file([p.__dict__ for p in positions], self.positions_file)
                return True
        return False
    
    def delete_position(self, position_id: str) -> bool:
        """Delete position"""
        positions = self.load_from_file(self.positions_file, Position)
        positions = [p for p in positions if p.id != position_id]
        self.save_to_file([p.__dict__ for p in positions], self.positions_file)
        return True
    
    def list_positions(self, wallet_id: str = None, status: PositionStatus = None) -> List[Position]:
        """List positions with optional filtering"""
        positions = self.load_from_file(self.positions_file, Position)
        
        if wallet_id:
            positions = [p for p in positions if p.wallet_id == wallet_id]
        
        if status:
            positions = [p for p in positions if p.status == status]
        
        return positions
    
    # CRUD Operations for Transactions
    def create_transaction(self, wallet_id: str, tx_hash: str, chain: str, **kwargs) -> Transaction:
        """Create a new transaction"""
        transaction = Transaction(id=None, wallet_id=wallet_id, tx_hash=tx_hash, 
                                chain=chain, **kwargs)
        transactions = self.load_from_file(self.transactions_file, Transaction)
        transactions.append(transaction)
        self.save_to_file([t.__dict__ for t in transactions], self.transactions_file)
        return transaction
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        transactions = self.load_from_file(self.transactions_file, Transaction)
        return next((t for t in transactions if t.id == transaction_id), None)
    
    def get_transaction_by_hash(self, tx_hash: str) -> Optional[Transaction]:
        """Get transaction by hash"""
        transactions = self.load_from_file(self.transactions_file, Transaction)
        return next((t for t in transactions if t.tx_hash == tx_hash), None)
    
    def list_transactions(self, wallet_id: str = None, position_id: str = None) -> List[Transaction]:
        """List transactions with optional filtering"""
        transactions = self.load_from_file(self.transactions_file, Transaction)
        
        if wallet_id:
            transactions = [t for t in transactions if t.wallet_id == wallet_id]
        
        if position_id:
            transactions = [t for t in transactions if t.position_id == position_id]
        
        return transactions
    
    # Price Data Operations
    def add_price_data(self, token_id: str, price_usd: float, source: str = "direct_api") -> PriceData:
        """Add price data point"""
        price_data = PriceData(id=None, token_id=token_id, price_usd=price_usd, 
                             timestamp=datetime.now(), source=source)
        price_history = self.load_from_file(self.price_data_file, PriceData)
        price_history.append(price_data)
        self.save_to_file([p.__dict__ for p in price_history], self.price_data_file)
        return price_data
    
    def get_latest_price(self, token_id: str) -> Optional[PriceData]:
        """Get latest price for token"""
        price_history = self.load_from_file(self.price_data_file, PriceData)
        token_prices = [p for p in price_history if p.token_id == token_id]
        return max(token_prices, key=lambda x: x.timestamp) if token_prices else None
    
    # Portfolio Snapshot Operations
    def create_portfolio_snapshot(self, wallet_id: str, total_value_usd: float, 
                                position_count: int, **kwargs) -> PortfolioSnapshot:
        """Create portfolio snapshot"""
        snapshot = PortfolioSnapshot(id=None, wallet_id=wallet_id, timestamp=datetime.now(),
                                   total_value_usd=total_value_usd, position_count=position_count, **kwargs)
        snapshots = self.load_from_file(self.portfolio_snapshots_file, PortfolioSnapshot)
        snapshots.append(snapshot)
        self.save_to_file([s.__dict__ for s in snapshots], self.portfolio_snapshots_file)
        return snapshot
    
    def get_portfolio_snapshots(self, wallet_id: str) -> List[PortfolioSnapshot]:
        """Get portfolio snapshots for wallet"""
        snapshots = self.load_from_file(self.portfolio_snapshots_file, PortfolioSnapshot)
        return [s for s in snapshots if s.wallet_id == wallet_id]