import functools

def create_trader(llm, memory):
    def trader_node(state, name):
        crypto_of_interest = state["crypto_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past crypto trading memories found."

        context = {
            "role": "user",
            "content": f"Based on a comprehensive analysis by a team of crypto analysts, here is an investment plan tailored for {crypto_of_interest}. This plan incorporates insights from current crypto market trends, on-chain metrics, regulatory developments, and social media sentiment. Use this plan as a foundation for evaluating your next crypto trading decision.\n\nProposed Crypto Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision in the cryptocurrency market.",
        }

        messages = [
            {
                "role": "system",
                "content": f"""You are a cryptocurrency trading agent analyzing crypto market data to make investment decisions. Based on your analysis, provide a specific recommendation to buy, sell, or hold the cryptocurrency. Consider factors like volatility, liquidity, regulatory environment, and technological developments. End with a firm decision and always conclude your response with 'FINAL CRYPTO TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation. Do not forget to utilize lessons from past crypto trading decisions to learn from your mistakes. Here is some reflections from similar crypto trading situations and the lessons learned: {past_memory_str}""",
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="CryptoTrader")