# SlashAgents/default_config.py

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

DEFAULT_CONFIG = {
    # =========================================================
    # Project Paths
    # =========================================================
    "project_dir": BASE_DIR,
    "results_dir": os.getenv(
        "SLASHAGENTS_RESULTS_DIR",
        os.path.join(BASE_DIR, "results"),
    ),
    "data_dir": os.getenv(
        "SLASHAGENTS_DATA_DIR",
        os.path.join(BASE_DIR, "data"),
    ),
    "data_cache_dir": os.path.join(
        BASE_DIR,
        "dataflows",
        "data_cache",
    ),

    # =========================================================
    # LLM Configuration (Gemini ONLY)
    # =========================================================
    "llm_provider": "google_gemini",
    "gemini_model": "gemini-2.0-flash",  # or "gemini-1.5-pro"
    "gemini_api_key": "",  # Replace with your actual API key

    # =========================================================
    # Debate & Graph Controls
    # =========================================================
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,

    # =========================================================
    # Crypto Data Vendor Configuration
    # =========================================================
    # Category-level defaults
    "data_vendors": {
        "market_data": "ccxt",          # OHLCV, price
        "technical_indicators": "local",# RSI, MACD, EMA
        "fundamentals": "coingecko",    # supply, mcap, tokenomics
        "news": "crypto_news_api",      # crypto news
        "sentiment": "local",           # heuristics / social tools
    },

    # Tool-level overrides (optional)
    "tool_vendors": {
        # Example:
        # "get_crypto_ohlcv": "binance",
        # "get_coin_news": "cryptopanic",
    },
}
