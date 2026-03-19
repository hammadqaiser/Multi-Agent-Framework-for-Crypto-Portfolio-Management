
def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        crypto_debate_state = state["crypto_debate_state"]
        history = crypto_debate_state.get("history", "")
        bear_history = crypto_debate_state.get("bear_history", "")

        current_response = crypto_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""You are a Crypto Bear Analyst making the case against investing in the cryptocurrency. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

Key points to focus on:
- Risks and Challenges: Highlight factors like regulatory uncertainty, security vulnerabilities, market manipulation, high volatility, or technological limitations.
- Competitive Weaknesses: Emphasize vulnerabilities such as slow adoption, scalability issues, strong competition, or lack of clear utility.
- Negative Indicators: Use evidence from on-chain data, market trends, negative regulatory news, or security incidents to support your position.
- Bull Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest crypto news and regulations: {news_report}
On-chain metrics and fundamentals: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}

Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the cryptocurrency. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Crypto Bear Analyst: {response.content}"

        new_crypto_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": crypto_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": crypto_debate_state["count"] + 1,
        }

        return {"crypto_debate_state": new_crypto_debate_state}

    return bear_node