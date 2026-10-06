import asyncio
from typing import TypedDict, Annotated
from langchain_google_genai import (ChatGoogleGenerativeAI)
from langchain_core.messages import ( BaseMessage)
from langgraph.graph import ( StateGraph, START, END)
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import ( interrupt, Command)
from langchain_mcp_adapters.client import ( MultiServerMCPClient)
from rag import create_retriever
from os import environ

# ============================================================
# STATE
# ============================================================

class State(TypedDict):

    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]

    employee_id: str


# ============================================================
# MODEL
# ============================================================

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# ============================================================
# RAG
# ============================================================

retriever = create_retriever()


async def search_policy(
    state: State
):

    print("\n[RAG] Searching company leave policy...")

    documents = await retriever.ainvoke(
        " ".join(
            message.content
            for message in state["messages"]
            if isinstance(message.content, str)
        )
    )

    if not documents:

        return {
            "messages": [
                {
                    "role": "system",
                    "content": "No leave policy information found."
                }
            ]
        }

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    return {
        "messages": [
            {
                "role": "system",
                "content": (
                    "Relevant company leave policy:\n\n"
                    + context
                )
            }
        ]
    }


# ============================================================
# EXTRACT EMPLOYEE ID
# ============================================================

def extract_employee_id(
    state: State
):

    employee_id = state.get(
        "employee_id",
        ""
    )

    if employee_id:
        return {}

    for message in state["messages"]:

        if not isinstance(
            message.content,
            str
        ):
            continue

        content = message.content

        words = content.replace(
            ",",
            " "
        ).split()

        for word in words:

            cleaned = (
                word
                .strip(".")
                .strip(",")
                .strip()
                .upper()
            )

            if cleaned.startswith("EMP"):

                return {
                    "employee_id": cleaned
                }

    return {}


# ============================================================
# ASSISTANT NODE
# ============================================================

async def assistant(
    state: State
):

    print("\n[Gemini] Thinking...")

    system_prompt = """
You are an Employee HR Assistant.

You can help employees with:

- leave balances
- leave policies
- leave applications
- employee HR questions

Important rules:

1. Never invent employee information.

2. If the employee asks about current leave balance,
   use the HR MCP tools.

3. If the employee asks about company leave policy,
   use the RAG policy information when available.

4. If the employee wants to APPLY, CANCEL or otherwise
   modify leave records, the action requires human approval.

5. Be concise and clear.

6. The employee ID may already be available in the
   application state or previous conversation.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(
        state["messages"]
    )

    response = await model_with_tools.ainvoke(
        messages
    )

    return {
        "messages": [response]
    }


# ============================================================
# HITL NODE
# ============================================================

def human_approval(
    state: State
):

    last_message = state["messages"][-1]

    if not getattr(
        last_message,
        "tool_calls",
        None
    ):
        return {}


    for tool_call in last_message.tool_calls:

        if tool_call["name"] != "apply_leave":
            continue

        args = tool_call["args"]

        approval = interrupt(
            {
                "type": "leave_approval",
                "message": "Human approval required",
                "employee_id": args.get(
                    "employee_id"
                ),
                "leave_type": args.get(
                    "leave_type"
                ),
                "days": args.get(
                    "days"
                )
            }
        )

        if approval is True:

            return {
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Human approved the "
                            "leave application."
                        )
                    }
                ]
            }

        return {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Human rejected the "
                        "leave application. "
                        "Do not execute the apply_leave tool."
                    )
                }
            ]
        }

    return {}


# ============================================================
# ROUTING
# ============================================================

def route_after_assistant(
    state: State
):

    last_message = state["messages"][-1]

    tool_calls = getattr(
        last_message,
        "tool_calls",
        []
    )

    if not tool_calls:
        return END

    for tool_call in tool_calls:

        if tool_call["name"] == "apply_leave":

            return "human_approval"

    return "tools"


def route_after_approval(
    state: State
):

    last_message = state["messages"][-1]

    if (
        isinstance(
            last_message.content,
            str
        )
        and "rejected" in last_message.content.lower()
    ):
        return "assistant"

    return "tools"


# ============================================================
# MAIN
# ============================================================

async def main():

    # --------------------------------------------------------
    # Connect to MCP
    # --------------------------------------------------------

    client = MultiServerMCPClient(
        {
            "hr_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        }
    )

    mcp_tools = await client.get_tools()

    print("\n========================================")
    print("MCP TOOLS")
    print("========================================")

    for tool in mcp_tools:
        print("-", tool.name)


    # --------------------------------------------------------
    # Find important MCP tools
    # --------------------------------------------------------

    get_leave_balance = next(
        (
            tool
            for tool in mcp_tools
            if tool.name == "get_leave_balance"
        ),
        None
    )

    apply_leave = next(
        (
            tool
            for tool in mcp_tools
            if tool.name == "apply_leave"
        ),
        None
    )

    if get_leave_balance is None:

        raise RuntimeError(
            "get_leave_balance MCP tool not found"
        )

    if apply_leave is None:

        raise RuntimeError(
            "apply_leave MCP tool not found"
        )


    # --------------------------------------------------------
    # Add RAG tool
    # --------------------------------------------------------

    from langchain_core.tools import tool


    @tool
    async def search_leave_policy_tool(
        question: str
    ) -> str:
        """
        Search the company leave policy.

        Use this when the user asks about:

        - leave rules
        - casual leave
        - sick leave
        - earned leave
        - carry forward
        - leave eligibility
        - company leave policy
        """

        documents = await retriever.ainvoke(
            question
        )

        if not documents:

            return (
                "No relevant company leave "
                "policy was found."
            )

        return "\n\n".join(
            document.page_content
            for document in documents
        )


    # --------------------------------------------------------
    # All tools
    # --------------------------------------------------------

    tools = [
        get_leave_balance,
        apply_leave,
        search_leave_policy_tool
    ]


    # --------------------------------------------------------
    # Bind tools to Gemini
    # --------------------------------------------------------

    global model_with_tools

    model_with_tools = model.bind_tools(
        tools
    )


    # --------------------------------------------------------
    # Tool Node
    # --------------------------------------------------------

    tool_node = ToolNode(
        tools
    )


    # --------------------------------------------------------
    # Build graph
    # --------------------------------------------------------

    builder = StateGraph(
        State
    )

    builder.add_node(
        "extract_employee_id",
        extract_employee_id
    )

    builder.add_node(
        "assistant",
        assistant
    )

    builder.add_node(
        "human_approval",
        human_approval
    )

    builder.add_node(
        "tools",
        tool_node
    )


    # --------------------------------------------------------
    # Graph edges
    # --------------------------------------------------------

    builder.add_edge(
        START,
        "extract_employee_id"
    )

    builder.add_edge(
        "extract_employee_id",
        "assistant"
    )

    builder.add_conditional_edges(
        "assistant",
        route_after_assistant
    )

    builder.add_conditional_edges(
        "human_approval",
        route_after_approval
    )

    builder.add_edge(
        "tools",
        "assistant"
    )


    # --------------------------------------------------------
    # Checkpointing
    # --------------------------------------------------------

    checkpointer = InMemorySaver()

    app = builder.compile(
        checkpointer=checkpointer
    )


    # --------------------------------------------------------
    # Conversation
    # --------------------------------------------------------

    thread_id = "employee_chat_001"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }


    print("\n========================================")
    print("EMPLOYEE AI ASSISTANT")
    print("========================================")

    print(
        "\nType 'exit' to quit."
    )


    while True:

        user_input = input(
            "\nYou: "
        ).strip()


        if user_input.lower() == "exit":

            print(
                "\nGoodbye!"
            )

            break


        if not user_input:

            continue


        try:

            result = await app.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ]
                },
                config=config
            )


            # ------------------------------------------------
            # Human approval required
            # ------------------------------------------------

            if "__interrupt__" in result:

                interrupt_data = (
                    result["__interrupt__"]
                )

                request = interrupt_data[0].value


                print(
                    "\n========================================"
                )

                print(
                    "HUMAN APPROVAL REQUIRED"
                )

                print(
                    "========================================"
                )

                print(
                    f"Employee ID : "
                    f"{request['employee_id']}"
                )

                print(
                    f"Leave Type  : "
                    f"{request['leave_type']}"
                )

                print(
                    f"Days        : "
                    f"{request['days']}"
                )


                answer = input(
                    "\nApprove? (yes/no): "
                ).strip().lower()


                approved = (
                    answer == "yes"
                )


                result = await app.ainvoke(
                    Command(
                        resume=approved
                    ),
                    config=config
                )


            # ------------------------------------------------
            # Print final response
            # ------------------------------------------------

            messages = result.get(
                "messages",
                []
            )

            if messages:

                last_message = messages[-1]

                content = (
                    last_message.content
                )

                if isinstance(
                    content,
                    list
                ):

                    text_parts = []

                    for item in content:

                        if (
                            isinstance(
                                item,
                                dict
                            )
                            and item.get("type")
                            == "text"
                        ):

                            text_parts.append(
                                item["text"]
                            )

                    content = "\n".join(
                        text_parts
                    )

                print(
                    f"\nAI: {content}"
                )


        except Exception as error:

            print(
                "\nERROR:"
            )

            print(
                error
            )


if __name__ == "__main__":

    asyncio.run(main())