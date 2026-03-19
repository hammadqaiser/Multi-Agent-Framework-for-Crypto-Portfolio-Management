"""
Crypto News Analyst
Analyzes cryptocurrency news and market narratives

Author: Crypto MAS Project
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from .agents.utils.agent_tools import (
    get_coin_news,
    get_global_crypto_news,
    search_crypto_news,
)


def create_news_analyst(llm):
    """
    Create news analyst node for crypto news analysis.
    
    Analyzes:
    - Coin-specific news
    - Global crypto market news
    - Regulatory developments
    - Market narratives and sentiment
    """
    
    def news_analyst_node(state):
        current_date = state["trade_date"]
        crypto = state["crypto_of_interest"]
        
        # Import crypto tools

        tools = [
            get_coin_news,
            get_global_crypto_news,
            search_crypto_news,
        ]
        
        system_message = (
            f"You are a cryptocurrency news analyst tasked with analyzing recent news, narratives, and developments "
            f"affecting {crypto} and the broader crypto market.\n\n"
            
            "**Available Tools**:\n"
            "- `get_coin_news(symbol)`: Get news specific to a cryptocurrency (e.g., 'BTC', 'ETH')\n"
            "- `get_global_news()`: Get global crypto market news from all RSS sources\n"
            "- `search_news(query)`: Search for specific keywords (e.g., 'regulation', 'ETF', 'DeFi')\n\n"
            
            "**Analysis Focus Areas**:\n"
            "1. **Coin-Specific News**: Protocol updates, partnerships, adoption news\n"
            "2. **Market Context**: Overall crypto market sentiment and trends\n"
            "3. **Regulatory Environment**: Government actions, legal developments\n"
            "4. **Macroeconomic Factors**: Fed policy, inflation, global events\n"
            "5. **Narratives**: Trending themes (AI, DeFi, Layer 2s, etc.)\n\n"
            
            "**Analysis Requirements**:\n"
            "- Provide DETAILED analysis (not just 'trends are mixed')\n"
            "- Separate FACT from SPECULATION\n"
            "- Assess credibility of sources\n"
            "- Identify conflicting narratives\n"
            "- Analyze potential market impact (bullish/bearish/neutral)\n"
            "- Consider short-term vs long-term implications\n"
            "- Look for correlation with price movements\n\n"
            
            "**Output Format**:\n"
            "1. Executive Summary (key headlines)\n"
            "2. Coin-specific developments\n"
            "3. Broader market context\n"
            "4. Regulatory/macro updates\n"
            "5. Prevailing narratives and sentiment\n"
            "6. Trading implications\n"
            "7. Append **Markdown table** summarizing:\n"
            "   - News Category | Key Development | Market Impact | Timeframe\n"
        )

                        # --- ENSURE AT LEAST ONE HUMAN MESSAGE ---
        if "messages" not in state or len(state["messages"]) == 0:
            state["messages"] = [
                HumanMessage(content=f"Please analyze {crypto}'s market data for {current_date}.")
            ]

        
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a helpful AI assistant, collaborating with other crypto analysts. "
                "Use the provided tools to analyze news for {crypto}. "
                "If you cannot fully answer, another analyst will continue where you left off. "
                "Execute what you can to make progress.\n\n"
                "If you or any other analyst has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**, "
                "prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop.\n\n"
                "Available tools: {tool_names}\n"
                "Current date: {current_date}\n"
                "Cryptocurrency: {crypto}\n\n"
                "{system_message}"
            ),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(crypto=crypto)
        
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        
        report = result.content
        if not report and result.tool_calls:
            # If there's no text yet, it's because the model is requesting tools
            report = f"Analyst Status: Fetching data using {len(result.tool_calls)} tools..."
        
        
        return {
            "messages": [result],
            "news_report": report,
        }
    
    return news_analyst_node
