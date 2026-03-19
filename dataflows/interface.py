"""
Crypto Data Interface & Routing System

Routes data requests to appropriate crypto data modules.

Author: Crypto MAS Project
"""

import logging
from typing import Callable, Dict, Any

# Import crypto data modules
from .crypto_onchain_fundamentals import (
    get_crypto_fundamentals,
    get_supply_data,
    get_market_activity,
    get_market_performance,
)

from .crypto_market_data import (
    get_crypto_ohlcv,
    get_current_price,
    #get_price_at_date,
    #get_multiple_prices,
)

from .crypto_technical_indicators import (
    get_crypto_indicator,
    list_available_indicators,
    SUPPORTED_INDICATORS,
    INDICATOR_DESCRIPTIONS,
)

from .crypto_news import (
    get_global_news,
    get_coin_news,
    search_news,
)

# Configuration (we'll create this next)
# from .config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TOOL CATEGORIES & ORGANIZATION
# ============================================================================

TOOLS_CATEGORIES = {
    "market_data": {
        "description": "OHLCV price data and real-time quotes",
        "tools": [
            "get_crypto_ohlcv",
            "get_current_price",
            #"get_price_at_date",
            #"get_multiple_prices",
        ]
    },
    "technical_indicators": {
        "description": "Technical analysis indicators",
        "tools": [
            "get_crypto_indicator",
            "list_available_indicators",
        ]
    },
    "fundamental_data": {
        "description": "On-chain metrics, tokenomics, market fundamentals",
        "tools": [
            "get_crypto_fundamentals",
            "get_supply_data",
            "get_market_activity",
            "get_market_performance",
        ]
    },
    "news_data": {
        "description": "Crypto news aggregation from multiple sources",
        "tools": [
            "get_coin_news",
            "get_global_news",
            "search_news",
        ]
    }
}


# ============================================================================
# METHOD MAPPING (Tools → Implementations)
# ============================================================================

METHOD_IMPLEMENTATIONS: Dict[str, Callable] = {
    # Market Data Tools
    "get_crypto_ohlcv": get_crypto_ohlcv,
    "get_current_price": get_current_price,
    #"get_price_at_date": get_price_at_date,
    #"get_multiple_prices": get_multiple_prices,
    
    # Technical Indicators
    "get_crypto_indicator": get_crypto_indicator,
    "list_available_indicators": list_available_indicators,
    
    # Fundamental Data
    "get_crypto_fundamentals": get_crypto_fundamentals,
    "get_supply_data": get_supply_data,
    "get_market_activity": get_market_activity,
    "get_market_performance": get_market_performance,
    
    # News Data
    "get_coin_news": get_coin_news,
    "get_global_news": get_global_news,
    "search_news": search_news,
}


# ============================================================================
# ROUTING FUNCTIONS (Public API)
# ============================================================================

def get_category_for_method(method: str) -> str:
    """
    Get the category that contains the specified method.
    
    Args:
        method: Tool method name
    
    Returns:
        Category name
        
    Raises:
        ValueError: If method not found
    """
    for category, info in TOOLS_CATEGORIES.items():
        if method in info["tools"]:
            return category
    
    raise ValueError(
        f"Method '{method}' not found. "
        f"Available methods: {list(METHOD_IMPLEMENTATIONS.keys())}"
    )


def route_to_implementation(method: str, *args, **kwargs) -> Any:
    """
    Route method call to appropriate implementation.
    
    This is the main entry point for all data requests.
    Handles error handling and logging.
    
    Args:
        method: Tool method name
        *args: Positional arguments for the method
        **kwargs: Keyword arguments for the method
    
    Returns:
        Result from the method implementation
        
    Raises:
        ValueError: If method not supported
        RuntimeError: If method execution fails
        
    """
    logger.info(f"Routing request for method: {method}")
    
    # Validate method exists
    if method not in METHOD_IMPLEMENTATIONS:
        available = list(METHOD_IMPLEMENTATIONS.keys())
        raise ValueError(
            f"Method '{method}' not supported. "
            f"Available methods: {available}"
        )
    
    # Get implementation
    implementation = METHOD_IMPLEMENTATIONS[method]
    
    # Log call details
    category = get_category_for_method(method)
    logger.info(f"Category: {category}, Implementation: {implementation.__name__}")
    
    # Execute with error handling
    try:
        logger.debug(f"Calling {method} with args={args}, kwargs={kwargs}")
        result = implementation(*args, **kwargs)
        logger.info(f"Successfully executed {method}")
        return result
        
    except Exception as e:
        logger.error(f"Error executing {method}: {e}")
        raise RuntimeError(f"Failed to execute {method}: {str(e)}")


# ============================================================================
# TOOL DISCOVERY & METADATA
# ============================================================================

def list_available_tools() -> Dict[str, list]:
    """
    Get all available tools organized by category.
    
    Returns:
        Dictionary mapping categories to tool lists
    """
    return {
        category: info["tools"]
        for category, info in TOOLS_CATEGORIES.items()
    }


def get_tool_info(method: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific tool.
    
    Args:
        method: Tool method name
    
    Returns:
        Dictionary with tool metadata
    """
    if method not in METHOD_IMPLEMENTATIONS:
        raise ValueError(f"Method '{method}' not found")
    
    category = get_category_for_method(method)
    implementation = METHOD_IMPLEMENTATIONS[method]
    
    return {
        "method": method,
        "category": category,
        "description": TOOLS_CATEGORIES[category]["description"],
        "implementation": implementation.__name__,
        "docstring": implementation.__doc__,
    }


def print_tools_summary():
    """Print a formatted summary of all available tools."""
    print("\n" + "="*70)
    print("CRYPTO MAS - AVAILABLE DATA TOOLS")
    print("="*70 + "\n")
    
    for category, info in TOOLS_CATEGORIES.items():
        print(f"\n {category.upper()}")
        print(f"   {info['description']}")
        print(f"   Tools ({len(info['tools'])}):")
        for tool in info['tools']:
            print(f"      • {tool}")
    
    print("\n" + "="*70 + "\n")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING CRYPTO INTERFACE & ROUTING")
    print("="*70 + "\n")
    
    # Test 1: List all tools
    print("1. Available Tools:")
    print_tools_summary()
    
    # Test 2: Get price data
    print("\n2. Testing get_crypto_ohlcv (BTC)...")
    result = get_crypto_ohlcv("BTC", "2026-02-01", "2026-03-17")
    print(result)

    
    # Test 3: Get indicator
    print("\n3. Testing get_crypto_indicator (RSI)...")
    result = get_crypto_indicator("BTC", "rsi", "2026-02-01", "2026-03-17")
    print(result)

    
    # Test 4: Get fundamentals
    print("\n4. Testing get_crypto_fundamentals (BTC)...")
    result = get_crypto_fundamentals("BTC")
    print(result)
    
    # Test 5: Get news
    print("\n5. Testing get_coin_news (BTC)...")
    result = get_coin_news("BTC")
    print(result)
    
    # Test 6: Route validation
    print("\n6. Testing invalid method...")
    try:
        route_to_implementation("invalid_method", "BTC")
    except ValueError as e:
        print(f" Correctly caught error: {e}")
    
    # Test 7: Tool info
    print("\n7. Testing get_tool_info...")
    info = get_tool_info("get_crypto_ohlcv")
    print(f"   Method: {info['method']}")
    print(f"   Category: {info['category']}")
    print(f"   Implementation: {info['implementation']}")
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE!")
    print("="*70 + "\n")