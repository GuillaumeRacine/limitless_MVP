"""Shared formatting utilities for the CLM Portfolio Tracker"""

def format_currency(value, decimals=2):
    """Format currency with appropriate decimals and fallback for None values"""
    if value is None:
        return "N/A"
    if abs(value) < 1 and value != 0:
        return f"${value:.6f}"
    return f"${value:,.{decimals}f}"

def format_percentage(value, decimals=1):
    """Format percentage consistently with fallback for None values"""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"

def format_number_short(value):
    """Format large numbers with K/M notation"""
    if value is None:
        return "N/A"
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"{value/1_000:.1f}K"
    return str(int(value)) if isinstance(value, (int, float)) else str(value)

def format_days(days):
    """Format days with fallback for None values"""
    if days is None:
        return "N/A"
    return str(int(days))

def format_token_amount(amount, decimals=6):
    """Format token amounts with appropriate precision"""
    if amount is None:
        return "N/A"
    if abs(amount) < 0.001:
        return f"{amount:.8f}"
    elif abs(amount) < 1:
        return f"{amount:.{decimals}f}"
    else:
        return f"{amount:,.{decimals}f}"

def truncate_hash(hash_str, length=8):
    """Truncate hash strings for display"""
    if not hash_str or hash_str == "N/A":
        return "N/A"
    return f"{hash_str[:length]}..." if len(hash_str) > length else hash_str