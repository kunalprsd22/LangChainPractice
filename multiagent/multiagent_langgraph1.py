import asyncio
from typing import TypedDict, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import (
    StateGraph,
    START,
    END
)
from os import environ

# ==================================================
# STATE
# ==================================================

class State(TypedDict):
    user_request: str
    route: str
    response: str

# ==================================================
# GEMINI
# ==================================================

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# ==================================================
# SUPERVISOR
# ==================================================

async def supervisor(state: State):

    prompt = f"""
You are a supervisor responsible for routing
user requests to specialized agents.

Available agents:

1. HR
   - employee information
   - leave
   - HR policy
   - attendance

2. Developer
   - Python
   - programming
   - FastAPI
   - LangChain
   - LangGraph
   - software architecture

User request:
{state["user_request"]}

Return ONLY one word:

HR

or

DEVELOPER
"""

    response = await model.ainvoke(prompt)

    route = response.content.strip().upper()

    if "HR" in route:
        route = "hr"
    else:
        route = "developer"

    return {
        "route": route
    }


# ==================================================
# HR AGENT
# ==================================================

async def hr_agent(state: State):

    prompt = f"""
You are an HR specialist.

Answer the user's HR-related question.

User question:
{state["user_request"]}

Be concise and do not invent employee information.
"""

    response = await model.ainvoke(prompt)

    return {
        "response": response.content
    }


# ==================================================
# DEVELOPER AGENT
# ==================================================

async def developer_agent(state: State):

    prompt = f"""
You are a senior Python developer.

Help the user with programming,
Python, FastAPI, LangChain,
LangGraph and software architecture.

User question:
{state["user_request"]}

Explain concepts clearly with examples
when useful.
"""

    response = await model.ainvoke(prompt)

    return {
        "response": response.content
    }


# ==================================================
# ROUTER
# ==================================================

def route_request(
    state: State
) -> Literal["hr_agent", "developer_agent"]:

    if state["route"] == "hr":
        return "hr_agent"

    return "developer_agent"


# ==================================================
# BUILD GRAPH
# ==================================================

builder = StateGraph(State)


builder.add_node(
    "supervisor",
    supervisor
)

builder.add_node(
    "hr_agent",
    hr_agent
)

builder.add_node(
    "developer_agent",
    developer_agent
)


# ==================================================
# EDGES
# ==================================================

builder.add_edge(
    START,
    "supervisor"
)


builder.add_conditional_edges(
    "supervisor",
    route_request
)


builder.add_edge(
    "hr_agent",
    END
)

builder.add_edge(
    "developer_agent",
    END
)


# ==================================================
# COMPILE
# ==================================================

app = builder.compile()

# ==================================================
# MAIN
# ==================================================

async def main():

    user_request = input(
        "Ask something: "
    )

    result = await app.ainvoke(
        {
            "user_request": user_request,
            "route": "",
            "response": ""
        }
    )

    print("\n==============================")
    print("ROUTE")
    print("==============================")

    print(result["route"])

    print("\n==============================")
    print("ANSWER")
    print("==============================")

    print(result["response"])


if __name__ == "__main__":
    asyncio.run(main())