#!/usr/bin/env python3
"""
New normalized data models for CLM Portfolio Tracker.
This runs alongside the existing CSV import system for testing.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class StrategyType(Enum):
    LONG = "long"
    NEUTRAL = "neutral"
    SHORT = "short"

class PositionType(Enum):
    CLM = "clm"
    PERP = "perp"
    SPOT = "spot"

class PositionStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"

class TransactionType(Enum):
    ENTRY = "entry"
    EXIT = "exit"
    CLAIM = "claim"
    FEE = "fee"

@dataclass
class Wallet:
    id: str
    address: str
    chain: str
    label: Optional[str] = None
    created_at: datetime = None
    last_activity: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Token:
    id: str
    symbol: str
    name: str
    contract_address: Optional[str] = None
    chain: str = None
    decimals: int = 18
    token_type: str = "native"  # native|wrapped|pool|synthetic
    price_sources: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.price_sources is None:
            self.price_sources = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Platform:
    id: str
    name: str
    protocol_type: str  # dex|perp|lending|farm
    chain: str
    contract_addresses: List[str] = None
    api_endpoint: Optional[str] = None
    fee_structure: Dict[str, Any] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.contract_addresses is None:
            self.contract_addresses = []
        if self.fee_structure is None:
            self.fee_structure = {}

@dataclass
class TradingPair:
    id: str
    base_token_id: str
    quote_token_id: str
    platform_id: str
    pool_address: Optional[str] = None
    fee_tier: Optional[float] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class PerformanceMetrics:
    price_return: Optional[float] = None
    yield_return: Optional[float] = None
    impermanent_loss: Optional[float] = None
    net_return: Optional[float] = None
    yield_apr: Optional[float] = None
    gas_fees_total: Optional[float] = None

@dataclass
class Position:
    id: str
    wallet_id: str
    trading_pair_id: str
    strategy_type: StrategyType
    position_type: PositionType
    entry_transaction_id: Optional[str] = None
    exit_transaction_id: Optional[str] = None
    entry_value_usd: Optional[float] = None
    exit_value_usd: Optional[float] = None
    entry_date: Optional[datetime] = None
    exit_date: Optional[datetime] = None
    min_range: Optional[float] = None
    max_range: Optional[float] = None
    status: PositionStatus = PositionStatus.ACTIVE
    performance_metrics: PerformanceMetrics = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.performance_metrics is None:
            self.performance_metrics = PerformanceMetrics()
        
        # Convert enum strings to enums if needed
        if isinstance(self.strategy_type, str):
            self.strategy_type = StrategyType(self.strategy_type)
        if isinstance(self.position_type, str):
            self.position_type = PositionType(self.position_type)
        if isinstance(self.status, str):
            self.status = PositionStatus(self.status)

@dataclass
class TokenAmount:
    token_id: str
    amount: float
    usd_value: Optional[float] = None

@dataclass
class Transaction:
    id: str
    wallet_id: str
    tx_hash: str
    chain: str
    platform_id: Optional[str] = None
    transaction_type: TransactionType = None
    position_id: Optional[str] = None
    timestamp: datetime = None
    block_number: Optional[int] = None
    gas_fees_usd: Optional[float] = None
    token_amounts: List[TokenAmount] = None
    raw_data: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.token_amounts is None:
            self.token_amounts = []
        if self.raw_data is None:
            self.raw_data = {}
        if isinstance(self.transaction_type, str):
            self.transaction_type = TransactionType(self.transaction_type)

@dataclass
class PriceData:
    id: str
    token_id: str
    price_usd: float
    timestamp: datetime
    source: str = "direct_api"
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

@dataclass
class PortfolioSnapshot:
    id: str
    wallet_id: str
    timestamp: datetime
    total_value_usd: float
    position_count: int
    pnl_24h: Optional[float] = None
    allocation_breakdown: Dict[str, float] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.allocation_breakdown is None:
            self.allocation_breakdown = {}

class DataModelEncoder(json.JSONEncoder):
    """Custom JSON encoder for data models"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, '__dict__'):
            return asdict(obj)
        return super().default(obj)

def from_dict(data_class, data_dict):
    """Convert dictionary to dataclass instance"""
    # Handle datetime fields
    datetime_fields = ['created_at', 'updated_at', 'last_activity', 'entry_date', 'exit_date', 'timestamp']
    for field in datetime_fields:
        if field in data_dict and data_dict[field] and isinstance(data_dict[field], str):
            try:
                data_dict[field] = datetime.fromisoformat(data_dict[field])
            except ValueError:
                pass
    
    # Handle nested dataclasses
    if data_class == Position and 'performance_metrics' in data_dict:
        if isinstance(data_dict['performance_metrics'], dict):
            data_dict['performance_metrics'] = PerformanceMetrics(**data_dict['performance_metrics'])
    
    if data_class == Transaction and 'token_amounts' in data_dict:
        if isinstance(data_dict['token_amounts'], list):
            data_dict['token_amounts'] = [
                TokenAmount(**item) if isinstance(item, dict) else item 
                for item in data_dict['token_amounts']
            ]
    
    return data_class(**data_dict)