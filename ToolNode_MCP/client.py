import asyncio
from typing import TypedDict, Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from langgraph.graph import (StateGraph,START,END)
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.client import (MultiServerMCPClient)
from os import environ

# ==========================================
# STATE
# ==========================================
class State(TypedDict):

    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]

# ==========================================
# GEMINI
# ==========================================

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

# ==========================================
# MAIN
# ==========================================

async def main():

    # ======================================
    # MCP CLIENT
    # ======================================

    client = MultiServerMCPClient(
        {
            "hr_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        }
    )

    # ======================================
    # GET MCP TOOLS
    # ======================================

    mcp_tools = await client.get_tools()

    print("\nMCP TOOLS:")

    for tool in mcp_tools:
        print("-", tool.name)

    # ======================================
    # GIVE TOOLS TO GEMINI
    # ======================================

    model_with_tools = model.bind_tools(
        mcp_tools
    )

    # ======================================
    # TOOL NODE
    # ======================================

    tool_node = ToolNode(mcp_tools)

    # ======================================
    # ASSISTANT
    # ======================================

    async def assistant(state: State):

        print("\n[Gemini] Thinking...")

        response = await model_with_tools.ainvoke(
            state["messages"]
        )

        return {
            "messages": [response]
        }


    # ======================================
    # ROUTER
    # ======================================
    def route_after_assistant(state: State):
        last_message = state["messages"][-1]

        if last_message.tool_calls:
            print("\n[Router] Tool call detected")
            return "tools"
        print(
            "\n[Router] No tool call"
        )
        return END

    # ======================================
    # GRAPH
    # ======================================

    builder = StateGraph(State)

    builder.add_node(
        "assistant",
        assistant
    )

    builder.add_node(
        "tools",
        tool_node
    )

    builder.add_edge(
        START,
        "assistant"
    )

    builder.add_conditional_edges(
        "assistant",
        route_after_assistant
    )

    builder.add_edge(
        "tools",
        "assistant"
    )

    # ======================================
    # COMPILE
    # ======================================
    app = builder.compile()

    # ======================================
    # USER INPUT
    # ======================================

    user_input = input(
        "\nAsk something: "
    )

    # ======================================
    # RUN
    # ======================================

    result = await app.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }
    )


    # ======================================
    # FINAL RESPONSE
    # ======================================

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================")

    print(
        result["messages"][-1].content
    )


if __name__ == "__main__":

    asyncio.run(main())