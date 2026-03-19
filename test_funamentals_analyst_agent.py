from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
from .agents.analysts.fundamentals_analyst import create_fundamentals_analyst
# IMPORTANT: Import the actual tools used by the fundamentals analyst
from .agents.utils.agent_tools import (
    get_crypto_fundamentals,
    get_supply_data,
    get_market_activity,
    get_market_performance,
)

# 1. Setup LLM (Update to a 2025/latest model for better tool use)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    google_api_key=""
)

# 2. Initialize Agent
agent = create_fundamentals_analyst(llm)

# 3. Create a Tool Map (Crucial: keys must match the @tool names exactly)
tools_map = {
    "get_crypto_fundamentals": get_crypto_fundamentals,
    "get_supply_data": get_supply_data,
    "get_market_activity": get_market_activity,
    "get_market_performance": get_market_performance,
}

state = {
    "crypto_of_interest": "BTC",
    "trade_date": "2026-02-16",
    "messages": [],
}

# 4. TOOL EXECUTION LOOP
print("\nSTARTING FUNDAMENTALS ANALYSIS...")

for i in range(5):  # Max 5 turns to prevent infinite loops
    result = agent(state)
    
    # Add the AI's response to the message history
    state["messages"].extend(result["messages"])
    last_msg = result["messages"][-1]

    # CHECK: Did the AI request a tool or give a final report?
    if last_msg.tool_calls:
        print(f" Analyst is calling tools: {[t['name'] for t in last_msg.tool_calls]}")
        
        for tool_call in last_msg.tool_calls:
            # 1. Identify which tool function to run
            tool_func = tools_map.get(tool_call["name"])
            if not tool_func:
                print(f" Error: Tool '{tool_call['name']}' not found in tools_map.")
                continue
                
            # 2. Execute the tool with the AI's provided arguments
            observation = tool_func.invoke(tool_call["args"])
            
            # 3. Add the result back to the messages list
            state["messages"].append(ToolMessage(
                content=str(observation),
                tool_call_id=tool_call["id"]
            ))
    else:
        # If there are NO tool calls, the AI has finished its final analysis
        print("\n FUNDAMENTALS REPORT COMPLETED:\n")
        # Ensure your fundamentals_analyst returns 'fundamentals_report' in its dict
        print(result.get("fundamentals_report", last_msg.content))
        break