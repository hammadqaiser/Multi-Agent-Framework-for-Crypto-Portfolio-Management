from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
from .agents.analysts.news_analyst import create_news_analyst
# Import your actual tool functions for execution
from .agents.utils.agent_tools import get_coin_news, search_crypto_news, get_global_crypto_news

# 1. Setup
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key="")
agent = create_news_analyst(llm)

# Create a map so the script knows which function to run for each tool name
tools_map = {
    "get_coin_news": get_coin_news,
    "search_crypto_news": search_crypto_news,
    "get_global_crypto_news": get_global_crypto_news,
}

state = {
    "crypto_of_interest": "BTC",
    "trade_date": "2026-03-17",
    "messages": [],
}

# 2. RUN LOOP
for i in range(3):  # Limit to 3 turns to prevent infinite loops
    print(f"\n--- Turn {i+1} ---")
    result = agent(state)
    
    # Update our state with the message from the analyst
    state["messages"].extend(result["messages"])
    last_msg = result["messages"][-1]

    # CHECK: Did the model give a final answer or call a tool?
    if last_msg.tool_calls:
        print(f" Analyst is calling: {[t['name'] for t in last_msg.tool_calls]}")
        
        for tool_call in last_msg.tool_calls:
            tool_func = tools_map[tool_call["name"]]
            # Execute the actual Python function
            observation = tool_func.invoke(tool_call["args"])
            
            # Create a ToolMessage to send the data back to the LLM
            state["messages"].append(ToolMessage(
                content=str(observation),
                tool_call_id=tool_call["id"]
            ))
    else:
        # No tool calls means the model has finished its analysis!
        print("\n FINAL News ANALYST REPORT:\n")
        print(result["news_report"])
        break