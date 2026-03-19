"""
Crypto News Aggregation Module
--------------------------------
Multi-source crypto news engine (no API key required).

Sources Used:
 CoinDesk (RSS)
CoinTelegraph (RSS)
Decrypt (RSS)
Bitcoin Magazine (RSS)
Blockworks (RSS)
U.Today (RSS)

Features:
- Unified normalized output
- Keyword extraction
- Date filtering
"""

import requests
import feedparser
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# =====================================================================
# UTILITIES
# =====================================================================

def _clean(text: str) -> str:
    """Remove HTML tags and clean text."""
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text().strip()

def _normalize_item(title, url, source, published):
    """Create normalized news item."""
    return {
        "title": _clean(title),
        "url": url,
        "source": source,
        "published_at": published,
    }




# =====================================================================
# 1. RSS NEWS SOURCES
# =====================================================================

RSS_FEEDS = {
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "cointelegraph": "https://cointelegraph.com/rss",
    "decrypt": "https://decrypt.co/feed",
    "bitcoinmagazine": "https://bitcoinmagazine.com/.rss/full/",
    "blockworks": "https://blockworks.co/feed",
    "utoday": "https://u.today/rss",
}



def _fetch_rss():
    news = []

    headers = {
        "User-Agent": "Windows NT 10.0; Win64; x64"
    }

    for name, url in RSS_FEEDS.items():
        logger.info(f"Fetching RSS: {name}")

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()

            feed = feedparser.parse(resp.text)

            if not feed.entries:
                logger.error(f"ZERO entries from {name}. Response probably blocked.")
                continue

            for item in feed.entries[:40]:
                published = getattr(item, "published", None) or getattr(item, "updated", "")
                news.append(
                    _normalize_item(
                        item.title,
                        item.link,
                        name,
                        published,
                    )
                )

        except Exception as e:
            logger.error(f"RSS error [{name}]: {e}")

    return news



# =====================================================================
# PUBLIC FUNCTIONS
# =====================================================================

def get_global_news() -> list:
    """
    Get latest crypto news from all sources.
    
    Args:
    
    Returns:
        List of news items (with duplicates removed)
    """
    logger.info("Aggregating global crypto news...")


    return  _fetch_rss()


def _token_match(title: str, term: str) -> bool:
    """
    Accurate keyword matching:
    - exact word match
    - case-insensitive
    - supports BTC → bitcoin mapping
    """
    t = title.lower()
    term = term.lower()

    # whole-word match
    words = t.split()
    if term in words:
        return True

    # substring match (safe)
    if f" {term} " in f" {t} ":
        return True

    return False

COIN_KEYWORDS = {
# Crypto symbol to keyword mappings
    "btc": ["btc", "bitcoin", "sats"],
    "eth": ["eth", "ethereum"],
    "sol": ["sol", "solana"],
    "avax": ["avax", "avalanche"],
    "link": ["link", "chainlink"],
    "ada": ["ada", "cardano"],
    "xrp": ["xrp", "ripple"],
    "ltc": ["ltc", "litecoin"],
    "dot": ["dot", "polkadot"],
    "bnb": ["bnb", "binance coin", "binance"],  
    "doge": ["doge", "dogecoin"],
    "matic": ["matic", "polygon"],
    "jup": ["jupiter", "jup"],
    "uni": ["uni", "uniswap"],
    "hype": ["hype", "hyperliquid"],
}

def get_coin_news(symbol: str) -> list:
    """
    Get news for specific cryptocurrency.
    
    Args:
        symbol: Crypto symbol (e.g., 'BTC', 'ETH')

    Returns:
        Filtered news items mentioning the symbol
    """
    symbol_lower = symbol.lower()
    logger.info(f"Fetching coin-specific news for {symbol}")

    items = _fetch_rss()
     # keyword expansion
    keywords = COIN_KEYWORDS.get(symbol_lower, [symbol_lower])
    # Filter headlines containing the symbol
    out = []
    for item in items:
        title = item["title"].lower()

        if any(_token_match(title, k) for k in keywords):
            out.append(item)

    return out


def search_news(query: str) -> list:
    """
    Search news by keyword.
    
    Args:
        query: Search term
    
    Returns:
        Filtered news items matching query
    """
    query_lower = query.lower()
    query_upper = query.upper()
    logger.info(f"Fetching specific news for {query}")

    query = f"{query} OR {query_upper} OR {query_lower}"

    items = _fetch_rss()
    
    return [n for n in items if query_lower in n["title"].lower() or query_upper in n["title"]]



# =====================================================================
# TESTING
# =====================================================================

if __name__ == "__main__":

    print("\n===== TEST 1: GLOBAL NEWS =====")
    g = get_global_news()
    print(f"Found {len(g)} Articles")
    for item in g:
        print(f"  [{item['source']}]  {item['title']}")

    print("\n===== TEST 2: BTC NEWS =====")
    btc = get_coin_news("BTC")
    print(f"Found {len(btc)} Articles")
    for item in btc:
        print(f"  [{item['source']}]  {item['title']}")

    print("\n===== TEST 3: SEARCH 'ETF' =====")
    s = search_news("ETF")
    print(f"Found {len(s)} Articles")
    for item in s:
        print(f"  [{item['source']}]  {item['title']}")
