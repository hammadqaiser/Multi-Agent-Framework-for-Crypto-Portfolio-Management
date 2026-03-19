
def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        crypto_debate_state = state["crypto_debate_state"]
        history = crypto_debate_state.get("history", "")
        bull_history = crypto_debate_state.get("bull_history", "")

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

        prompt = f"""You are a Crypto Bull Analyst advocating for investing in the cryptocurrency. Your task is to build a strong, evidence-based case emphasizing growth potential, technological advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Highlight the cryptocurrency's adoption rate, network growth, developer activity, and scalability solutions.
- Technological Advantages: Emphasize factors like strong security, fast transactions, low fees, active development, and real-world utility.
- Positive Indicators: Use on-chain metrics, trading volume, institutional adoption, and positive regulatory developments as evidence.
- Bear Counterpoints: Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst's points and debating effectively rather than just listing data.

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest crypto news and regulations: {news_report}
On-chain metrics and fundamentals: {fundamentals_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}

Use this information to deliver a compelling bull argument, refute the bear's concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Crypto Bull Analyst: {response.content}"

        new_crypto_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": crypto_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": crypto_debate_state["count"] + 1,
        }

        return {"crypto_debate_state": new_crypto_debate_state}

    return bull_node