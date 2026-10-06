from typing import TypedDict, Annotated
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
from langgraph.graph import (StateGraph,START,END)
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from os import environ

# ============================================================
# 1. TOOL
# ============================================================

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# ============================================================
# 2. STATE
# ============================================================

class State(TypedDict):
    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]

# ============================================================
# 3. MODEL
# ============================================================

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

# ============================================================
# 4. TOOLS
# ============================================================

tools = [add]


# Tell Gemini which tools are available
model_with_tools = model.bind_tools(tools)


# Create LangGraph ToolNode
# ToolNode is responsible for actually executing the Python tool.
tool_node = ToolNode(tools)

# ============================================================
# 5. ASSISTANT NODE
# ============================================================

async def assistant(state: State):

    # Get all messages from the state
    messages = state["messages"]

    # Send the conversation to Gemini
    response = await model_with_tools.ainvoke(
        messages
    )

    # Add Gemini's response to the state
    return {
        "messages": [response]
    }

# ============================================================
# 6. ROUTER
# ============================================================

def route_after_assistant(state: State):

    # --------------------------------------------------------
    # Get the messages list
    # --------------------------------------------------------
    messages = state["messages"]

    # Example:
    #
    # messages = [
    #     HumanMessage("What is 25 + 17?"),
    #     AIMessage(
    #         tool_calls=[
    #             {
    #                 "name": "add",
    #                 "args": {
    #                     "a": 25,
    #                     "b": 17
    #                 }
    #             }
    #         ]
    #     )
    # ]
    #
    #
    # [-1] means:
    #
    # "Give me the LAST item in the list"
    #
    # So:
    #
    # messages[-1]
    #
    # gives us the latest Gemini message.

    last_message = messages[-1]

    # --------------------------------------------------------
    # Check whether Gemini requested a tool
    # --------------------------------------------------------

    # tool_calls is a property of an AIMessage.

    if last_message.tool_calls:

        # Gemini wants to use a tool
        return "tools"

    # Gemini does not want to use a tool
    return END


# ============================================================
# 7. CREATE GRAPH
# ============================================================

builder = StateGraph(State)


# ============================================================
# 8. ADD NODES
# ============================================================

# Gemini / LLM node
builder.add_node(
    "assistant",
    assistant
)


# Tool execution node
builder.add_node(
    "tools",
    tool_node
)

# ============================================================
# 9. GRAPH EDGES
# ============================================================

# START → ASSISTANT
builder.add_edge(
    START,
    "assistant"
)

# ASSISTANT → ROUTER
#
# The router decides:
#
#     "tools" → go to ToolNode
#
#     END    → finish
#
builder.add_conditional_edges(
    "assistant",
    route_after_assistant
)

# TOOLS → ASSISTANT
#
# After the tool executes,
# send the result back to Gemini.
#
builder.add_edge(
    "tools",
    "assistant"
)


# ============================================================
# 10. COMPILE GRAPH
# ============================================================

app = builder.compile()

# ============================================================
# 11. RUN GRAPH
# ============================================================

async def main():

    result = await app.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What is 25 + 17?"
                }
            ]
        }
    )

    # Get the final message
    final_message = result["messages"][-1]

    print(final_message.content)


# ============================================================
# 12. START PROGRAM
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())