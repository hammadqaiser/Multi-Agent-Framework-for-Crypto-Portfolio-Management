
def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:

        crypto_of_interest = state["crypto_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""As the Crypto Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three crypto risk analysts—Risky, Neutral, and Safe/Conservative—and determine the best course of action for the crypto trader. Your decision must result in a clear recommendation: Buy, Sell, or Hold the cryptocurrency. Choose Hold only if strongly justified by specific arguments, not as a fallback when all sides seem valid. Strive for clarity and decisiveness in the volatile crypto market.

Guidelines for Decision-Making:
1. **Summarize Key Crypto Arguments**: Extract the strongest points from each analyst, focusing on relevance to cryptocurrency context including volatility, regulation, and technology.
2. **Provide Crypto-Specific Rationale**: Support your recommendation with direct quotes and counterarguments from the debate, considering crypto market uniqueness.
3. **Refine the Crypto Trader's Plan**: Start with the trader's original plan, **{trader_plan}**, and adjust it based on the crypto analysts' insights.
4. **Learn from Past Crypto Mistakes**: Use lessons from **{past_memory_str}** to address prior crypto trading misjudgments and improve the decision you are making now to make sure you don't make a wrong BUY/SELL/HOLD call that loses money in crypto markets.

Deliverables:
- A clear and actionable crypto recommendation: Buy, Sell, or Hold.
- Detailed reasoning anchored in the crypto debate and past crypto trading reflections.

---

**Crypto Analysts Debate History:**  
{history}

---

Focus on actionable crypto insights and continuous improvement. Build on past crypto lessons, critically evaluate all perspectives, and ensure each decision advances better outcomes in cryptocurrency trading."""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node