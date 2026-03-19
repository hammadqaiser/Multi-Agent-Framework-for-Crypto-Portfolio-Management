"""
Crypto Market Data Module - Using CCXT

Data Source: CCXT (Unified API for 100+ exchanges)

Author: Crypto MAS Project
"""

import ccxt
import pandas as pd
from datetime import datetime, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Use Binance as default exchange (most liquid, best data)
# Can be changed to: 'coinbase', 'kraken', 'bybit', etc.
DEFAULT_EXCHANGE = 'binance'


def _get_exchange(exchange_name: str = DEFAULT_EXCHANGE):
    """Initialize exchange connection."""
    try:
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({
            'enableRateLimit': True,  # Respect rate limits
            'options': {'defaultType': 'spot'}  # Use spot market
        })
        return exchange
    except Exception as e:
        logger.error(f"Failed to initialize {exchange_name}: {e}")
        raise


def _format_symbol(symbol: str) -> str:
    """
    Convert symbol to CCXT format.
    
    Args:
        symbol: Crypto symbol like 'BTC', 'ETH'
    
    Returns:
        CCXT format like 'BTC/USDT'
    """
    symbol = symbol.upper()
    
    # If already in correct format, return as-is
    if '/' in symbol:
        return symbol
    
    # Default to USDT pair (most liquid)
    return f"{symbol}/USDT"


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def get_crypto_ohlcv(
    symbol: str,
    start_date: str,
    end_date: str,
    timeframe: str = '1d',
    exchange_name: str = DEFAULT_EXCHANGE
) -> str:
    """
    Get historical OHLCV data for cryptocurrency.
    
    Direct replacement for alpha_vantage get_stock() function.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        timeframe: Candle timeframe (default: '1d' for daily)
                  Options: '1m', '5m', '15m', '1h', '4h', '1d', '1w'
        exchange_name: Exchange to use (default: 'binance')
    
    Returns:
        CSV string with OHLCV data
        
    Example:
        >>> data = get_crypto_ohlcv('BTC', '2024-01-01', '2024-01-07')
        >>> print(data)
        timestamp,date,open,high,low,close,volume
        1704067200000,2024-01-01,42258.5,44953.1,41580.3,44167.6,28500.5
    """
    logger.info(f"Fetching {symbol} OHLCV from {start_date} to {end_date}")
    
    try:
        # Initialize exchange
        exchange = _get_exchange(exchange_name)
        
        # Format symbol
        trading_pair = _format_symbol(symbol)
        
        # Check if symbol exists
        exchange.load_markets()
        if trading_pair not in exchange.markets:
            logger.error(f"Symbol {trading_pair} not found on {exchange_name}")
            return f"error\nSymbol {trading_pair} not available on {exchange_name}\n"
        
        # Convert dates to timestamps (milliseconds)
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        start_ts = int(start_dt.timestamp() * 1000)
        end_ts = int((end_dt + timedelta(days=1)).timestamp() * 1000)
        
        # Fetch OHLCV data
        logger.info(f"Fetching from {exchange_name}: {trading_pair} ({timeframe})")
        
        all_ohlcv = []
        current_ts = start_ts
        
        # Fetch in batches (exchanges limit to ~1000 candles per request)
        while current_ts < end_ts:
            try:
                ohlcv = exchange.fetch_ohlcv(
                    trading_pair,
                    timeframe=timeframe,
                    since=current_ts,
                    limit=1000
                )
                
                if not ohlcv:
                    break
                
                all_ohlcv.extend(ohlcv)
                
                # Update timestamp for next batch
                current_ts = ohlcv[-1][0] + 1
                
                # Stop if we've reached the end date
                if ohlcv[-1][0] >= end_ts:
                    break
                
                # Small delay to respect rate limits
                time.sleep(exchange.rateLimit / 1000)
                
            except ccxt.NetworkError as e:
                logger.error(f"Network error: {e}")
                break
            except ccxt.ExchangeError as e:
                logger.error(f"Exchange error: {e}")
                break
        
        if not all_ohlcv:
            logger.warning(f"No data returned for {symbol}")
            return "error\nNo data available for specified date range\n"
        
        # Convert to DataFrame
        df = pd.DataFrame(
            all_ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # Filter by exact date range
        df = df[(df['timestamp'] >= start_ts) & (df['timestamp'] < end_ts)]
        
        # Add readable date column
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
        
        # Reorder columns
        df = df[['timestamp', 'date', 'open', 'high', 'low', 'close', 'volume']]
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['timestamp'])
        
        logger.info(f"Successfully fetched {len(df)} candles for {symbol}")
        
        # Convert to CSV
        return df.to_csv(index=False)
        
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        import traceback
        traceback.print_exc()
        return f"error\n{str(e)}\n"


def get_current_price(symbol: str, exchange_name: str = DEFAULT_EXCHANGE) -> dict:
    """
    Get current ticker price.
    
    Args:
        symbol: Crypto symbol
        exchange_name: Exchange to use
    
    Returns:
        Dictionary with current price info
    """
    try:
        exchange = _get_exchange(exchange_name)
        trading_pair = _format_symbol(symbol)
        
        ticker = exchange.fetch_ticker(trading_pair)
        
        return {
            'symbol': symbol.upper(),
            'last': ticker['last'],
            'bid': ticker['bid'],
            'ask': ticker['ask'],
            'high': ticker['high'],
            'low': ticker['low'],
            'volume': ticker['quoteVolume'],
            'timestamp': ticker['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Error fetching ticker: {e}")
        return {'symbol': symbol.upper(), 'error': str(e)}


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING CRYPTO MARKET DATA MODULE - CCXT VERSION")
    print("="*70)
    
    # Test 1: Historical data from 2025
    print("\n1. Testing BTC (2026-02-01 to 2026-03-15)...")
    data = get_crypto_ohlcv("BTC", "2026-02-01", "2026-03-15")
    print(data)
    
    # Test 2: Recent data
    print("\n2. Testing ETH (2026-02-01 to 2026-03-15)...")
    data = get_crypto_ohlcv("ETH", "2026-02-01", "2026-03-15")
    print(data)  
    
    # Test 3: Current price
    print("\n3. Testing get_current_price() for SOL...")
    print(get_current_price("SOL"))
    
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE!")
    print("="*70 + "\n")