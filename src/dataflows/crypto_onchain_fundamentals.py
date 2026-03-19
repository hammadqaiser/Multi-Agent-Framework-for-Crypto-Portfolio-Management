"""

Data Source: CoinGecko API (Free tier, no key required)
API Rate Limits (CoinGecko Free Tier)
- 10-50 calls/minute
- No API key required for basic endpoints
- Consider caching results to avoid hitting limits

Author: Crypto MAS Project
"""

import requests
import json
from typing import Dict
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _format_number(num: float) -> str:
    """Format large numbers for readability."""
    if num is None:
        return "N/A"
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"


def _make_request(endpoint: str, params: Dict = None) -> Dict:
    """Make API request to CoinGecko (free tier)."""
    url = f"{COINGECKO_BASE_URL}/{endpoint}"
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API error: {e}")
        return {"error": str(e)}


def _get_coin_id(symbol: str) -> str:
    """Convert crypto symbol to CoinGecko ID."""
    # Common mappings
    symbol_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "BNB": "binancecoin",
        "SOL": "solana",
        "XRP": "ripple",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "AVAX": "avalanche-2",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "ATOM": "cosmos",
        "LTC": "litecoin",
        "NEAR": "near",
        "APT": "aptos",
        "ARB": "arbitrum",
        "OP": "optimism",
        "FTM": "fantom",
        "XLM": "stellar",
        "ALGO": "algorand",
        "ICP": "internet-computer",
        "FIL": "filecoin",
        "TRX": "tron",
        "AXS": "axie-infinity",
        "SAND": "the-sandbox",
        "JUP": "jupiter",
        "HYPE" : "hyperliquid",
        "CAKE": "pancakeswap",
    }
    
    symbol_upper = symbol.upper()
    return symbol_map.get(symbol_upper, symbol.lower())


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def get_crypto_fundamentals(ticker: str, curr_date: str = None) -> str:
    """
    Retrieve comprehensive fundamental data for a cryptocurrency.
    
    Crypto equivalent of stock company overview.
    
    Args:
        ticker (str): Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        curr_date (str): Current date yyyy-mm-dd (optional)
    
    Returns:
        str: Formatted text report with fundamental data
    """
    logger.info(f"Fetching fundamentals for {ticker}")
    
    coin_id = _get_coin_id(ticker)
    
    # Get comprehensive coin data
    data = _make_request(f"coins/{coin_id}", {
        "localization": "false",
        "tickers": "false",
        "community_data": "true",
        "developer_data": "true",
        "sparkline": "false"
    })
    
    if "error" in data:
        return f"Error: Failed to fetch data for {ticker}"
    
    # Extract key metrics
    md = data.get("market_data", {})
    cd = data.get("community_data", {})
    dd = data.get("developer_data", {})
    
    # Build report
    report = f"""
{'='*70}
CRYPTO FUNDAMENTAL ANALYSIS: {data.get('name', 'Unknown')} ({ticker.upper()})
{'='*70}

MARKET DATA
-----------
Current Price:           {_format_number(md.get('current_price', {}).get('usd', 0))}
Market Cap:              {_format_number(md.get('market_cap', {}).get('usd', 0))}
Market Cap Rank:         #{md.get('market_cap_rank', 'N/A')}
Fully Diluted Value:     {_format_number(md.get('fully_diluted_valuation', {}).get('usd'))}
24h Trading Volume:      {_format_number(md.get('total_volume', {}).get('usd', 0))}

PRICE CHANGES
-------------
24h Change:              {md.get('price_change_percentage_24h', 0):.2f}%
7d Change:               {md.get('price_change_percentage_7d', 0):.2f}%
30d Change:              {md.get('price_change_percentage_30d', 0):.2f}%
1y Change:               {md.get('price_change_percentage_1y', 0):.2f}%

SUPPLY (TOKENOMICS)
-------------------
Circulating Supply:      {md.get('circulating_supply', 0):,.0f}
Total Supply:            {md.get('total_supply', 0):,.0f}
Max Supply:              {md.get('max_supply') or 'Unlimited'}
Supply %:                {(md.get('circulating_supply', 0) / md.get('total_supply', 1) * 100):.1f}%

ALL-TIME HIGH/LOW
-----------------
ATH:                     {_format_number(md.get('ath', {}).get('usd', 0))}
ATH Date:                {md.get('ath_date', {}).get('usd', 'N/A')[:10]}
Distance from ATH:       {md.get('ath_change_percentage', {}).get('usd', 0):.2f}%

ATL:                     {_format_number(md.get('atl', {}).get('usd', 0))}
ATL Date:                {md.get('atl_date', {}).get('usd', 'N/A')[:10]}
Distance from ATL:       {md.get('atl_change_percentage', {}).get('usd', 0):.2f}%

LIQUIDITY
---------
Market Cap/Volume:       {md.get('market_cap', {}).get('usd', 0) / md.get('total_volume', {}).get('usd', 1):.2f}x


PROJECT INFO
------------
Genesis Date:            {data.get('genesis_date')}
Categories:              {', '.join(data.get('categories', [])[:4]) or 'N/A'}
Homepage:                {data.get('links', {}).get('homepage', ['N/A'])[0]}

Last Updated:            {data.get('last_updated', 'N/A')}
{'='*70}
"""
    
    logger.info(f"Successfully fetched fundamentals for {ticker}")
    return report


def get_supply_data(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    """
    Get on-chain network metrics (crypto equivalent of balance sheet).
    
    Args:
        ticker (str): Cryptocurrency symbol
        freq (str): Not used (for compatibility)
        curr_date (str): Current date yyyy-mm-dd (optional)
    
    Returns:
        str: Formatted text report with network metrics
    """
    logger.info(f"Fetching network metrics for {ticker}")
    
    coin_id = _get_coin_id(ticker)
    
    # Get coin data with community/developer info
    data = _make_request(f"coins/{coin_id}", {
        "localization": "false",
        "community_data": "true",
        "developer_data": "true"
    })
    
    if "error" in data:
        return f"Error: Failed to fetch network data for {ticker}"
    
    md = data.get("market_data", {})
    dd = data.get("developer_data", {})
    
    report = f"""
{'='*70}
NETWORK HEALTH METRICS: {data.get('name', 'Unknown')} ({ticker.upper()})
{'='*70}

NETWORK VALUE
-------------
Market Capitalization:   {_format_number(md.get('market_cap', {}).get('usd', 0))}
Fully Diluted Value:     {_format_number(md.get('fully_diluted_valuation', {}).get('usd'))}
Total Value Locked:      Network dependent

SUPPLY DISTRIBUTION
-------------------
Circulating:             {md.get('circulating_supply', 0):,.0f}
Total:                   {md.get('total_supply', 0):,.0f}
Max:                     {md.get('max_supply') or 'Unlimited'}
% Circulating:           {(md.get('circulating_supply', 0) / md.get('total_supply', 1) * 100):.1f}%


Note: For detailed on-chain metrics (active addresses, transactions, etc.),
      consider using paid services like Glassnode or IntoTheBlock.
{'='*70}
"""
    
    return report


def get_market_activity(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    """
    Get market activity metrics (crypto equivalent of cash flow).
    
    Args:
        ticker (str): Cryptocurrency symbol
        freq (str): Not used (for compatibility)
        curr_date (str): Current date yyyy-mm-dd (optional)
    
    Returns:
        str: Formatted text report with market activity
    """
    logger.info(f"Fetching market activity for {ticker}")
    
    coin_id = _get_coin_id(ticker)
    
    # Get 30-day market data
    market_data = _make_request(f"coins/{coin_id}/market_chart", {
        "vs_currency": "usd",
        "days": "30",
        "interval": "daily"
    })
    
    if "error" in market_data:
        return f"Error: Failed to fetch market data for {ticker}"
    
    # Calculate metrics
    prices = [p[1] for p in market_data.get("prices", [])]
    volumes = [v[1] for v in market_data.get("total_volumes", [])]
    
    avg_price = sum(prices) / len(prices) if prices else 0
    avg_volume = sum(volumes) / len(volumes) if volumes else 0
    
    price_change = ((prices[-1] - prices[0]) / prices[0] * 100) if prices else 0
    volume_change = ((volumes[-1] - volumes[0]) / volumes[0] * 100) if volumes else 0
    
    report = f"""
{'='*70}
MARKET ACTIVITY (30 Days): {ticker.upper()}
{'='*70}

PRICE METRICS
-------------
Current Price:           {_format_number(prices[-1] if prices else 0)}
30-Day Average:          {_format_number(avg_price)}
30-Day Change:           {price_change:.2f}%
Highest:                 {_format_number(max(prices) if prices else 0)}
Lowest:                  {_format_number(min(prices) if prices else 0)}
Volatility:              {((max(prices) - min(prices)) / avg_price * 100):.2f}%

VOLUME METRICS (Activity Proxy)
--------------------------------
Recent Volume:           {_format_number(volumes[-1] if volumes else 0)}
30-Day Avg Volume:       {_format_number(avg_volume)}
Volume Change:           {volume_change:.2f}%
Volume Trend:            {"Increasing" if volume_change > 0 else "Decreasing"}

LIQUIDITY FLOW
--------------
Avg Daily Turnover:      {_format_number(avg_volume)}
Peak Volume:             {_format_number(max(volumes) if volumes else 0)}
Low Volume:              {_format_number(min(volumes) if volumes else 0)}

Note: This represents market trading activity.
      True network cash flows (fees, staking rewards) require
      blockchain-specific data sources.
{'='*70}
"""
    
    return report


def get_market_performance(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    """
    Get market performance metrics (crypto equivalent of income statement).
    
    Args:
        ticker (str): Cryptocurrency symbol
        freq (str): Not used (for compatibility)
        curr_date (str): Current date yyyy-mm-dd (optional)
    
    Returns:
        str: Formatted text report with performance metrics
    """
    logger.info(f"Fetching performance metrics for {ticker}")
    
    coin_id = _get_coin_id(ticker)
    
    # Get comprehensive data
    data = _make_request(f"coins/{coin_id}", {
        "localization": "false",
        "market_data": "true"
    })
    
    if "error" in data:
        return f"Error: Failed to fetch performance data for {ticker}"
    
    md = data.get("market_data", {})
    
    report = f"""
{'='*70}
MARKET PERFORMANCE: {data.get('name', 'Unknown')} ({ticker.upper()})
{'='*70}

RETURNS (Revenue Equivalent)
-----------------------------
24h Return:              {md.get('price_change_percentage_24h', 0):.2f}%
7d Return:               {md.get('price_change_percentage_7d', 0):.2f}%
14d Return:              {md.get('price_change_percentage_14d', 0):.2f}%
30d Return:              {md.get('price_change_percentage_30d', 0):.2f}%
60d Return:              {md.get('price_change_percentage_60d', 0):.2f}%
200d Return:             {md.get('price_change_percentage_200d', 0):.2f}%
1y Return:               {md.get('price_change_percentage_1y', 0):.2f}%

MARKET POSITION (Market Share)
-------------------------------
Market Cap:              {_format_number(md.get('market_cap', {}).get('usd', 0))}
Market Cap Rank:         #{md.get('market_cap_rank', 'N/A')}

TRADING VOLUME (Activity/Engagement)
-------------------------------------
24h Volume:              {_format_number(md.get('total_volume', {}).get('usd', 0))}
Volume/Market Cap:       {(md.get('total_volume', {}).get('usd', 0) / md.get('market_cap', {}).get('usd', 1)):.4f}

VALUATION METRICS
-----------------
Current Price:           {_format_number(md.get('current_price', {}).get('usd', 0))}
High 24h:                {_format_number(md.get('high_24h', {}).get('usd', 0))}
Low 24h:                 {_format_number(md.get('low_24h', {}).get('usd', 0))}

GROWTH INDICATORS
-----------------
ATH Performance:         {md.get('ath_change_percentage', {}).get('usd', 0):.2f}% from ATH
ATL Performance:         {md.get('atl_change_percentage', {}).get('usd', 0):.2f}% from ATL
Price vs FDV:            {(md.get('market_cap', {}).get('usd', 0) / md.get('fully_diluted_valuation', {}).get('usd', 1) * 100):.1f}%

Note: Unlike stocks, cryptos don't have traditional revenue/profit.
      Returns and market performance serve as key metrics.
{'='*70}
"""
    
    return report


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING CRYPTO FUNDAMENTALS MODULE")
    print("="*70 + "\n")
    
    test_ticker = "BTC"
    
    print(f"1. Testing get_crypto_fundamentals({test_ticker})...\n")
    print(get_crypto_fundamentals(test_ticker))
    
    print(f"\n2. Testing get_supply_data({test_ticker})...\n")
    print(get_supply_data(test_ticker))
    
    print(f"\n3. Testing get_market_activity({test_ticker})...\n")
    print(get_market_activity(test_ticker))
    
    print(f"\n4. Testing get_market_performance({test_ticker})...\n")
    print(get_market_performance(test_ticker))
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE!")
    print("="*70 + "\n")