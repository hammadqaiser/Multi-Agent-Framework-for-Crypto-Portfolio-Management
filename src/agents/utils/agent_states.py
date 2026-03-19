"""
Crypto MAS – Agent State Definitions
------------------------------------

Shared state schema for all agents participating in:
- Crypto research
- Bull/Bear debate
- Risk evaluation
- Trading decision-making

Designed for:
- LangGraph workflows
- Gemini-based agents
- Multi-agent ReAct reasoning

"""

from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import MessagesState


# ================================================================
# 1. RESEARCHER TEAM – BULL vs BEAR DEBATE (Investment Thesis)
# ================================================================
class InvestDebateState(TypedDict):
    bull_history: Annotated[str, "Conversation history from the Bull analyst"]
    bear_history: Annotated[str, "Conversation history from the Bear analyst"]
    history: Annotated[str, "Full debate transcript between Bull and Bear"]
    current_response: Annotated[str, "Most recent debate message"]
    judge_decision: Annotated[str, "Final Buy/Sell/Hold decision"]
    count: Annotated[int, "Message count in debate"]


# ================================================================
# 2. RISK MANAGEMENT TEAM – RISKY / SAFE / NEUTRAL Debate
# ================================================================
class RiskDebateState(TypedDict):
    risky_history: Annotated[str, "Risk-Taker analyst arguments"]
    safe_history: Annotated[str, "Conservative analyst arguments"]
    neutral_history: Annotated[str, "Neutral analyst arguments"]
    history: Annotated[str, "Full risk debate transcript"]

    latest_speaker: Annotated[str, "Name of the last analyst who spoke"]

    current_risky_response: Annotated[str, "Last risky analyst message"]
    current_safe_response: Annotated[str, "Last conservative analyst message"]
    current_neutral_response: Annotated[str, "Last neutral analyst message"]

    judge_decision: Annotated[str, "Risk Manager's final Buy/Sell/Hold decision"]
    count: Annotated[int, "Message count in the risk debate"]


# ================================================================
# 3. MAIN AGENT STATE – (Shared Across Entire Workflow)
# ================================================================
class AgentState(MessagesState):
    # -------- CORE CONTEXT --------
    crypto_of_interest: Annotated[str, "Crypto asset being analyzed (BTC, ETH, SOL, etc.)"]
    trade_date: Annotated[str, "Trading date (YYYY-MM-DD)"]
    sender: Annotated[str, "Name of the agent who produced last message"]

    # -------- RESEARCH OUTPUTS --------
    market_report: Annotated[str, "OHLCV + technical indicators market analysis"]
    sentiment_report: Annotated[str, "Social media sentiment + crypto community insight"]
    news_report: Annotated[str, "Macro + global crypto news summary"]
    fundamentals_report: Annotated[str, "On-chain + tokenomics fundamentals report"]


    # -------- BULL/BEAR DEBATE OUTPUT --------
    crypto_debate_state: Annotated[
        InvestDebateState,
        "Bull vs Bear debate for investment thesis"
    ]
    investment_plan: Annotated[str, "Final research manager investment plan"]

    # -------- TRADER OUTPUT --------
    trader_investment_plan: Annotated[str, "Trader’s final investment strategy"]

    # -------- RISK DEBATE SYSTEM OUTPUT --------
    risk_debate_state: Annotated[
        RiskDebateState,
        "Risk-adjusted debate before final execution decision"
    ]
    final_trade_decision: Annotated[str, "Final Buy/Sell/Hold decision"]
