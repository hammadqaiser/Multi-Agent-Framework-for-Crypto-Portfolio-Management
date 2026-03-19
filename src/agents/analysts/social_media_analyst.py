"""
Crypto Social Media & Sentiment Analyst
Analyzes social media discussions and community sentiment

Author: Crypto MAS Project
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage

from .agents.utils.agent_tools import (
    get_coin_news,
    search_crypto_news,
)

def create_social_media_analyst(llm):
    """
    Create social media analyst node for crypto sentiment analysis.
    
    Analyzes:
    - Social media discussions (Twitter, Reddit via news)
    - Community sentiment
    - Trending topics and narratives
    - Influencer opinions
    """
    
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        crypto = state["crypto_of_interest"]
        
        # Import crypto tools
        
        tools = [
            get_coin_news,
            search_crypto_news,
        ]
        
        system_message = (
            f"You are a cryptocurrency social media and sentiment analyst tasked with analyzing "
            f"community discussions, social sentiment, and public perception around {crypto}.\n\n"
            
            "**Data Sources** (via news aggregation):\n"
            "- Crypto news sites often aggregate social media sentiment\n"
            "- News articles about community reactions\n"
            "- Public sentiment indicators\n"
            "- Trending narratives in crypto media\n\n"
            
            "**Available Tools**:\n"
            "- `get_coin_news(symbol)`: Get news and discussions about the cryptocurrency\n"
            "- `search_news(query)`: Search for specific sentiment keywords\n"
            "  (e.g., 'bullish', 'bearish', 'FUD', 'FOMO', 'adoption')\n\n"
            
            "**Analysis Focus Areas**:\n"
            "1. **Sentiment Trends**: Overall bullish/bearish sentiment shifts\n"
            "2. **Community Engagement**: Level of discussion, activity patterns\n"
            "3. **Narrative Analysis**: What stories are dominating?\n"
            "4. **Fear/Greed Indicators**: FUD vs FOMO dynamics\n"
            "5. **Influencer Impact**: Notable opinions from crypto influencers\n"
            "6. **Controversy Detection**: Scams, hacks, disputes\n"
            "7. **Adoption Signals**: Real-world use cases, partnerships\n\n"
            
            "**Analysis Requirements**:\n"
            "- Provide DETAILED sentiment analysis (not generic statements)\n"
            "- Distinguish between NOISE and SIGNAL\n"
            "- Identify sentiment shifts over time\n"
            "- Assess credibility of sentiment sources\n"
            "- Look for divergence between sentiment and price\n"
            "- Note viral moments or trending topics\n"
            "- Analyze community health and engagement\n\n"
            
            "**Red Flags to Watch For**:\n"
            "- Coordinated pump/dump campaigns\n"
            "- Sudden negative sentiment spikes\n"
            "- Exit scam warnings\n"
            "- Regulatory concerns going viral\n"
            "- Community fragmentation\n\n"
            
            "**Output Format**:\n"
            "1. Overall sentiment summary (bullish/neutral/bearish)\n"
            "2. Key discussion themes\n"
            "3. Sentiment trend analysis (improving/declining)\n"
            "4. Notable voices and opinions\n"
            "5. Community health assessment\n"
            "6. Trading implications\n"
            "7. Append **Markdown table** summarizing:\n"
            "   - Sentiment Aspect | Current Status | Trend | Impact\n"
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
                "Use the provided tools to analyze social sentiment for {crypto}. "
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
            "sentiment_report": report,
        }
    
    return social_media_analyst_node