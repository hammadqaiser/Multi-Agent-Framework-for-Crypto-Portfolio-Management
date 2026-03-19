"""
Crypto Technical Indicators Module

Uses pandas-ta library for comprehensive technical analysis
Works with CCXT data from crypto_market_data.py

Author: Crypto MAS Project
"""

import pandas as pd
import pandas_ta as ta
from datetime import datetime
from io import StringIO
import logging

# Import our OHLCV module
from .crypto_market_data import get_crypto_ohlcv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# INDICATOR DESCRIPTIONS
# ============================================================================

INDICATOR_DESCRIPTIONS = {
    "sma_50": "50 SMA: Medium-term trend indicator.",
    "sma_200": "200 SMA: Long-term trend trend confirmation.",
    "ema_10": "10 EMA: Very reactive short-term trend.",
    "ema_21": "21 EMA: Crypto swing-trading favorite.",
    "rsi": "RSI: Overbought >70, oversold <30.",
    "macd": "MACD: Momentum + trend indicator.",
    "bbands_upper": "Bollinger Upper Band: Volatility zone.",
    "bbands_middle": "Bollinger Mid Band: 20 SMA baseline.",
    "bbands_lower": "Bollinger Lower Band: Oversold signal.",
    "atr": "ATR: Volatility, helps for stop-loss.",
    "adx": "ADX: Trend strength indicator.",
}


SUPPORTED_INDICATORS = {
    "sma_50": "50 SMA",
    "sma_200": "200 SMA",
    "ema_10": "10 EMA",
    "ema_21": "21 EMA",
    "rsi": "Relative Strength Index",
    "macd": "MACD Line",
    "macd_signal": "MACD Signal Line",
    "macd_histogram": "MACD Histogram",
    "bbands_upper": "Bollinger Upper Band",
    "bbands_middle": "Bollinger Middle Band",
    "bbands_lower": "Bollinger Lower Band",
    "atr": "Average True Range",
    "adx": "Average Directional Index",
}


# ============================================================================
# CORE FUNCTION
# ============================================================================

def get_crypto_indicator(
    symbol: str,
    indicator: str,
    start_date: str,
    end_date: str,
    timeframe: str = "1d",
    **kwargs,
) -> str:

    logger.info(f"Calculating {indicator} for {symbol}")

    if indicator not in SUPPORTED_INDICATORS:
        return f"Error: Unsupported indicator '{indicator}'."

    # Fetch OHLCV CSV
    csv_data = get_crypto_ohlcv(symbol, start_date, end_date, timeframe=timeframe)
    if csv_data.startswith("error"):
        return f"Error fetching OHLCV data: {csv_data}"

    # Load CSV -> DataFrame
    df = pd.read_csv(StringIO(csv_data))
    # Enforce numeric types
    numeric_cols = ["open", "high", "low", "close", "volume"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Drop rows with missing prices
    df = df.dropna(subset=["open", "high", "low", "close"])

    # Ensure sorted
    df = df.sort_values("date").reset_index(drop=True)

    # Rename for pandas-ta compatibility
    df = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    })

    # Calculate indicator
    df = _calculate_indicator(df, indicator, **kwargs)

    if df is None or indicator not in df.columns:
        return f"Error calculating indicator '{indicator}'."

    return _format_output(symbol, indicator, df, start_date, end_date)


# ============================================================================
# INDICATOR CALCULATION ENGINE
# ============================================================================

def _calculate_indicator(df: pd.DataFrame, indicator: str, **kwargs) -> pd.DataFrame:
    """
    Calculate indicator using pandas-ta with MAXIMUM reliability.
    """
    length = kwargs.get("length", 14)
    fast = kwargs.get("fast", 12)
    slow = kwargs.get("slow", 26)
    signal = kwargs.get("signal", 9)

    try:
        # ---- MOVING AVERAGES ----
        if indicator == "sma_50":
            df[indicator] = ta.sma(df["Close"], length=50)

        elif indicator == "sma_200":
            df[indicator] = ta.sma(df["Close"], length=200)

        elif indicator == "ema_10":
            df[indicator] = ta.ema(df["Close"], length=10)

        elif indicator == "ema_21":
            df[indicator] = ta.ema(df["Close"], length=21)

        # ---- RSI ----
        elif indicator == "rsi":
            df[indicator] = ta.rsi(df["Close"], length=length)

        # ---- MACD (FIXED + UNIVERSAL HANDLING) ----
        elif indicator in ["macd", "macd_signal", "macd_histogram"]:
            macd = ta.macd(df["Close"], fast=fast, slow=slow, signal=signal)

            if macd is None or macd.empty:
                logger.error(f"MACD still empty with {len(df)} candles.")
                return None

            # auto-detect column names
            macd_cols = list(macd.columns)

            macd_col = next((c for c in macd_cols if "MACD_" in c), None)
            sig_col  = next((c for c in macd_cols if "MACDs_" in c), None)
            hist_col = next((c for c in macd_cols if "MACDh_" in c), None)

            if not macd_col or not sig_col or not hist_col:
                logger.error(f"Unexpected MACD columns: {macd_cols}")
                return None

            df["macd"] = macd[macd_col]
            df["macd_signal"] = macd[sig_col]
            df["macd_histogram"] = macd[hist_col]

        # ---- BOLLINGER BANDS ----
        elif indicator.startswith("bbands"):
            bb = ta.bbands(df["Close"], length=20, std=2)
                # Use explicit column names like MACD
            lower_col = [c for c in bb.columns if 'BBL' in c][0]
            mid_col = [c for c in bb.columns if 'BBM' in c][0]
            upper_col = [c for c in bb.columns if 'BBU' in c][0]
            
            df["bbands_lower"] = bb[lower_col]
            df["bbands_middle"] = bb[mid_col]
            df["bbands_upper"] = bb[upper_col]

        # ---- ATR ----
        elif indicator == "atr":
            df[indicator] = ta.atr(df["High"], df["Low"], df["Close"], length=length)

        # ---- ADX ----
        elif indicator == "adx":
            adx = ta.adx(df["High"], df["Low"], df["Close"], length=length)
            df[indicator] = adx[f"ADX_{length}"]

        return df

    except Exception as e:
        logger.error(f"Error calculating {indicator}: {e}")
        return None



# ============================================================================
# OUTPUT FORMATTER
# ============================================================================

def _format_output(symbol, indicator, df, start_date, end_date) -> str:

    # Clean NaN rows
    clean = df[["date", indicator]].dropna()
    if clean.empty:
        return f"No valid {indicator} values found."

    # Build formatted output
    out = "\n" + "=" * 70 + "\n"
    out += f"{indicator.upper()} for {symbol.upper()} ({start_date} → {end_date})\n"
    out += "=" * 70 + "\n\n"

    out += "DATE                VALUE\n"
    out += "-" * 40 + "\n"

    for _, row in clean.tail(20).iterrows():
        out += f"{row['date']:<20} {row[indicator]:>10.4f}\n"

    # Stats
    values = clean[indicator]
    out += "\n" + "-" * 40 + "\n"
    out += f"Latest:      {values.iloc[-1]:.4f}\n"
    out += f"Average:     {values.mean():.4f}\n"
    out += f"Min:         {values.min():.4f}\n"
    out += f"Max:         {values.max():.4f}\n"

    # Description
    out += "\n" + "=" * 70 + "\n"
    out += INDICATOR_DESCRIPTIONS.get(indicator, "No description available.")
    out += "\n" + "=" * 70 + "\n"

    return out


# ============================================================================
# LIST ALL INDICATORS
# ============================================================================

def list_available_indicators():
    msg = "\nAvailable indicators:\n"
    for key, desc in SUPPORTED_INDICATORS.items():
        msg += f"{key:<20} - {desc}\n"
    return msg


# ============================================================================
# TEST MODULE
# ============================================================================

if __name__ == "__main__":

    print("================= TESTING LIST OF INDICATORS =================")

    print(list_available_indicators())

    print("\n================= TESTING INDIVIDUAL INDICATORS =================")    

    print("\nTESTING RSI...")
    print(get_crypto_indicator("BTC", "rsi", "2026-02-01", "2026-03-18"))

    print("\nTESTING MACD...")
    print(get_crypto_indicator("BTC", "macd", "2026-02-01", "2026-03-18"))

    print("\n================= TESTING ALL INDICATORS =================")

    symbol = "BTC"
    start = "2026-02-01"
    end = "2026-03-18"

    tests = [
        "sma_50", "sma_200",
        "ema_10", "ema_21",
        "rsi",
        "macd", "macd_signal", "macd_histogram",
        "bbands_upper", "bbands_middle", "bbands_lower",
        "atr",
        "adx"
    ]

    for ind in tests:
        print(f"\n---- Testing {ind} ----")
        out = get_crypto_indicator(symbol, ind, start, end)
        # print only last 20 lines to keep clean
        print("\n".join(out.splitlines()[-20:]))
    
    print("\n================= TESTING COMPLETE =================")