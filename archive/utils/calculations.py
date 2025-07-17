"""Shared calculation utilities for the CLM Portfolio Tracker"""

def calculate_portfolio_total(positions):
    """Calculate total portfolio value from positions"""
    return sum([p.get('entry_value', 0) for p in positions if p.get('entry_value') is not None])

def calculate_average_return(positions):
    """Calculate average return across positions"""
    returns = [p.get('net_return') for p in positions if p.get('net_return') is not None]
    return sum(returns) / len(returns) if returns else 0

def calculate_percentage_allocation(position_value, total_value):
    """Calculate percentage allocation for a position"""
    if total_value == 0 or position_value is None:
        return 0
    return (position_value / total_value) * 100

def count_positions_by_status(positions, status_field='range_status'):
    """Count positions by a given status field"""
    counts = {}
    for position in positions:
        status = position.get(status_field, 'unknown')
        counts[status] = counts.get(status, 0) + 1
    return counts

def calculate_in_range_count(positions):
    """Calculate number of positions that are in range"""
    return sum(1 for p in positions if p.get('range_status') == 'in_range')

def calculate_out_of_range_count(positions):
    """Calculate number of positions that are out of range"""
    return sum(1 for p in positions if p.get('range_status') == 'out_of_range')

def filter_positions_by_strategy(positions, strategy):
    """Filter positions by strategy type"""
    return [p for p in positions if p.get('strategy') == strategy]

def calculate_position_days(entry_date, exit_date=None):
    """Calculate days a position has been active"""
    from datetime import datetime
    
    if not entry_date:
        return None
    
    try:
        if isinstance(entry_date, str):
            entry_dt = datetime.fromisoformat(entry_date.replace('Z', '+00:00'))
        else:
            entry_dt = entry_date
            
        if exit_date:
            if isinstance(exit_date, str):
                exit_dt = datetime.fromisoformat(exit_date.replace('Z', '+00:00'))
            else:
                exit_dt = exit_date
        else:
            exit_dt = datetime.now()
            
        return (exit_dt - entry_dt).days
    except (ValueError, TypeError):
        return None