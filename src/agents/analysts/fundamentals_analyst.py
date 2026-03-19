"""
Crypto Fundamentals Analyst
Analyzes on-chain metrics, tokenomics, and market fundamentals

Author: Crypto MAS Project
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage

from .agents.utils.agent_tools import (
    get_crypto_fundamentals,
    get_supply_data,
    get_market_activity,
    get_market_performance,
)

def create_fundamentals_analyst(llm):
    """
    Create fundamentals analyst node for crypto analysis.
    
    Analyzes:
    - On-chain fundamentals (market cap, supply, tokenomics)
    - Supply metrics and distribution
    - Market activity and volume trends
    - Performance metrics and valuations
    """
    
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        crypto = state["crypto_of_interest"] 
        
        # Import crypto tools
        tools = [
            get_crypto_fundamentals,
            get_supply_data,
            get_market_activity,
            get_market_performance,
        ]
        
        system_message = (
            f"You are a cryptocurrency fundamentals analyst tasked with analyzing {crypto}'s on-chain metrics and market fundamentals. "
            "Your role is to provide comprehensive analysis of:\n\n"
            "1. **On-Chain Fundamentals**: Market cap, circulating supply, max supply, tokenomics, ATH/ATL analysis\n"
            "2. **Supply Metrics**: Token distribution, supply inflation/deflation, supply percentage in circulation\n"
            "3. **Market Activity**: 30-day volume trends, price volatility, liquidity analysis\n"
            "4. **Performance Metrics**: Price returns across multiple timeframes (24h, 7d, 30d, 1y), market position\n\n"
            
            "**Available Tools**:\n"
            "- `get_crypto_fundamentals(crypto)`: Get comprehensive on-chain data, market cap, supply, tokenomics, project info\n"
            "- `get_supply_data(crypto)`: Get detailed supply metrics and distribution analysis\n"
            "- `get_market_activity(crypto)`: Get 30-day volume and price activity trends\n"
            "- `get_market_performance(crypto)`: Get performance returns across timeframes\n\n"
            
            "**Analysis Requirements**:\n"
            "- Provide DETAILED, granular insights (not just 'trends are mixed')\n"
            "- Compare current metrics to historical ranges (ATH/ATL)\n"
            "- Analyze tokenomics implications (supply dynamics, inflation rate)\n"
            "- Identify key strengths and weaknesses\n"
            "- Highlight any red flags or bullish indicators\n"
            "- Use specific numbers and percentages\n\n"
            
            "**Output Format**:\n"
            "Write a comprehensive report with:\n"
            "1. Executive Summary\n"
            "2. Detailed analysis sections for each metric category\n"
            "3. Key findings and trading implications\n"
            "4. Append a **Markdown table** at the end summarizing:\n"
            "   - Key Metric | Current Value | Assessment | Implication\n"
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
                "Use the provided tools to analyze {crypto} comprehensively. "
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
            "fundamentals_report": report,
        }
    
    return fundamentals_analyst_node
