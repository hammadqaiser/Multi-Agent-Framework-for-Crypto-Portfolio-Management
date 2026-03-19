
def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        history = state["crypto_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        crypto_debate_state = state["crypto_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""As the crypto portfolio manager and debate facilitator, your role is to critically evaluate this round of crypto debate and make a definitive decision: align with the bear analyst, the bull analyst, or choose Hold only if it is strongly justified based on the arguments presented for the cryptocurrency.

Summarize the key points from both sides concisely, focusing on the most compelling crypto-specific evidence or reasoning. Your recommendation—Buy, Sell, or Hold—must be clear and actionable for cryptocurrency trading. Avoid defaulting to Hold simply because both sides have valid points; commit to a stance grounded in the debate's strongest crypto arguments.

Additionally, develop a detailed crypto investment plan for the trader. This should include:

Your Crypto Recommendation: A decisive stance supported by the most convincing crypto arguments.
Crypto-Specific Rationale: An explanation of why these arguments lead to your conclusion in the cryptocurrency context.
Strategic Crypto Actions: Concrete steps for implementing the recommendation in crypto markets.
Take into account your past crypto trading mistakes in similar situations. Use these insights to refine your crypto decision-making and ensure you are learning and improving. Present your crypto analysis conversationally, as if speaking naturally, without special formatting. 

Here are your past reflections on crypto trading mistakes:
\"{past_memory_str}\"

Here is the crypto debate:
Crypto Debate History:
{history}"""

        response = llm.invoke(prompt)

        new_crypto_debate_state = {
            "judge_decision": response.content,
            "history": crypto_debate_state.get("history", ""),
            "bear_history": crypto_debate_state.get("bear_history", ""),
            "bull_history": crypto_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": crypto_debate_state["count"],
        }

        return {
            "crypto_debate_state": new_crypto_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node