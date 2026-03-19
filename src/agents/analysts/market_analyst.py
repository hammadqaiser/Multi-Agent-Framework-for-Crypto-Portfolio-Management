"""
Crypto Market Analyst (Technical Analysis)
Analyzes price action and technical indicators

Author: Crypto MAS Project
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from .agents.utils.agent_tools import (
    get_crypto_ohlcv,
    get_crypto_indicator,
    get_current_price,
)


def create_market_analyst(llm):
    """
    Create market analyst node for crypto technical analysis.
    
    Analyzes:
    - OHLCV price data
    - Technical indicators (RSI, MACD, Bollinger Bands, etc.)
    - Trend identification
    - Support/resistance levels
    """
    
    def market_analyst_node(state):
        current_date = state["trade_date"]
        crypto = state["crypto_of_interest"]
        
        # Import crypto tools
        
        tools = [
            get_crypto_ohlcv,
            get_crypto_indicator,
            get_current_price,
        ]
        
        system_message = (
            f"You are a cryptocurrency technical analyst tasked with analyzing {crypto}'s price action and technical indicators. "
            "Your role is to select the **most relevant indicators** for the current market condition.\n\n"
            
            "**Available Indicators** (choose up to 8 complementary indicators):\n\n"
            
            "**Moving Averages**:\n"
            "- sma_50: Medium-term trend (50-day SMA)\n"
            "- sma_200: Long-term trend benchmark (200-day SMA)\n"
            "- ema_10: Short-term responsive average (10-day EMA)\n"
            "- ema_21: Swing trading favorite (21-day EMA)\n\n"
            
            "**Momentum Indicators**:\n"
            "- rsi: Relative Strength Index (overbought >70, oversold <30)\n"
            "- macd: MACD line (trend + momentum)\n"
            "- macd_signal: MACD signal line (crossover triggers)\n"
            "- macd_histogram: MACD histogram (momentum strength)\n\n"
            
            "**Volatility Indicators**:\n"
            "- bbands_upper: Bollinger Upper Band (volatility breakout zone)\n"
            "- bbands_middle: Bollinger Middle Band (20 SMA baseline)\n"
            "- bbands_lower: Bollinger Lower Band (oversold signal)\n"
            "- atr: Average True Range (volatility measurement)\n\n"
            
            "**Trend Strength**:\n"
            "- adx: Average Directional Index (trend strength, >25 = strong)\n\n"
            
            "**Analysis Workflow**:\n"
            "1. First, call `get_crypto_ohlcv(crypto, start_date, end_date)` to get price data\n"
            "2. Then, call `get_crypto_indicator(crypto, indicator_name, start_date, end_date)` for each selected indicator\n"
            "3. Analyze trends, crossovers, divergences, and key levels\n\n"
            
            "**Selection Strategy**:\n"
            "- Avoid redundancy (don't use both sma_50 and sma_200 unless comparing)\n"
            "- Choose indicators that complement each other (e.g., RSI + MACD + Bollinger)\n"
            "- Consider current market conditions (trending vs ranging)\n"
            "- Provide brief rationale for your indicator choices\n\n"
            
            "**Analysis Requirements**:\n"
            "- Provide DETAILED, granular analysis (not just 'trends are mixed')\n"
            "- Identify specific support/resistance levels\n"
            "- Note bullish/bearish divergences\n"
            "- Analyze crossovers and breakouts\n"
            "- Consider timeframe context (short vs long-term signals)\n"
            "- Use specific values and percentages\n\n"
            
            "**Output Format**:\n"
            "1. Indicator selection rationale\n"
            "2. Detailed technical analysis for each indicator\n"
            "3. Overall market structure assessment\n"
            "4. Key levels to watch (support/resistance)\n"
            "5. Append **Markdown table** summarizing:\n"
            "   - Indicator | Current Value | Signal | Interpretation\n"
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
                "Use the provided tools to analyze {crypto}'s technical indicators. "
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
            "market_report": report,
        }
    
    return market_analyst_node
