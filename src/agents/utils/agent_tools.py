"""
Crypto Analyst Agents Tools
Tools that are necessary for  crypto analyst agents  for reasoning.
Comprehensive tool interface for crypto analyst agents.

Author: Crypto MAS Project
"""

from langchain_core.tools import tool
from typing import Annotated
from slashagents.dataflows.interface import route_to_implementation


# Crypto Market Data Tools

@tool
def get_crypto_ohlcv(
    symbol: Annotated[str, "Crypto symbol (e.g., 'BTC', 'ETH')"],
    start_date: Annotated[str, "Start date YYYY-MM-DD"],
    end_date: Annotated[str, "End date YYYY-MM-DD"],
    timeframe: str = "1d"
) -> str:
    """Get OHLCV price data for cryptocurrency."""
    return route_to_implementation("get_crypto_ohlcv", symbol, start_date, end_date, timeframe)

@tool
def get_current_price(
    symbol: Annotated[str, "Crypto symbol"]
) -> str:
    """Get current price for cryptocurrency."""
    return route_to_implementation("get_current_price", symbol)

# Crypto Technical Indicators Tools

@tool
def get_crypto_indicator(
    symbol: Annotated[str, "Crypto symbol"],
    indicator: Annotated[str, "Indicator name (e.g., 'rsi', 'macd')"],
    start_date: Annotated[str, "Start date YYYY-MM-DD"],
    end_date: Annotated[str, "End date YYYY-MM-DD"],
    **kwargs
) -> str:
    """Calculate technical indicator."""
    return route_to_implementation("get_crypto_indicator", symbol, indicator, start_date, end_date, **kwargs)

# Crypto Fundamentals Data Tools

@tool
def get_crypto_fundamentals(
    symbol: Annotated[str, "Crypto symbol"]
) -> str:
    """Get fundamental data for cryptocurrency."""
    return route_to_implementation("get_crypto_fundamentals", symbol)

@tool
def get_supply_data(
    symbol: Annotated[str, "Crypto symbol"]
) -> str:
    """Return supply data (circulating, total, burned, issuance, inflation)."""
    return route_to_implementation("get_supply_data", symbol)

@tool
def get_market_activity(
    symbol: Annotated[str, "Crypto symbol"]
) -> str:
    """Return market activity data (exchange flows, whale transactions)."""
    return route_to_implementation("get_market_activity", symbol)

@tool
def get_market_performance(
    symbol: Annotated[str, "Crypto symbol"]
) -> str:
    """Return market performance data (volatility, returns, liquidity)."""
    return route_to_implementation("get_market_performance", symbol)

# Crypto News Data Tools

@tool
def get_coin_news(
    symbol: Annotated[str, "Crypto symbol for coin-specific news"],
) -> str:
    """Get news for specific cryptocurrency."""
    return route_to_implementation("get_coin_news", symbol)

@tool
def get_global_crypto_news() -> str:
    """Get global crypto news from all sources."""
    return route_to_implementation("get_global_news")

@tool
def search_crypto_news(
    query: Annotated[str, "Search keyword"]
) -> str:
    """Search crypto news by keyword."""
    return route_to_implementation("search_news", query)
       