import asyncio
from typing import TypedDict
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


# ==================================================
# STATE
# ==================================================

class LeaveState(TypedDict):
    employee_id: str
    leave_type: str
    days: int

    balance: int | None
    approved: bool | None

    result: str


# ==================================================
# MAIN
# ==================================================

async def main():

    # ----------------------------------------------
    # 1. Connect to MCP Server
    # ----------------------------------------------

    client = MultiServerMCPClient(
        {
            "hr_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        }
    )

    # ----------------------------------------------
    # 2. Get MCP Tools
    # ----------------------------------------------

    mcp_tools = await client.get_tools()

    print("\nMCP TOOLS:")

    for tool in mcp_tools:
        print("-", tool.name)

    # ----------------------------------------------
    # 3. Find required MCP tools
    # ----------------------------------------------

    get_leave_balance = next(
        tool
        for tool in mcp_tools
        if tool.name == "get_leave_balance"
    )

    apply_leave = next(
        tool
        for tool in mcp_tools
        if tool.name == "apply_leave"
    )

    # ==================================================
    # GRAPH NODES
    # ==================================================

    # ----------------------------------------------
    # Node 1: Check Leave Balance
    # ----------------------------------------------

    async def check_balance(state: LeaveState):

        print("\nChecking leave balance...")

        response = await get_leave_balance.ainvoke(
            {
                "employee_id": state["employee_id"]
            }
        )

        print("MCP Response:")
        print(response)

        if not response.get("success"):
            return {
                "balance": 0,
                "result": response["message"]
            }

        balance_key = f"{state['leave_type']}_leave"

        balance = response.get(balance_key, 0)

        return {
            "balance": balance
        }

    # ----------------------------------------------
    # Node 2: Human Approval
    # ----------------------------------------------

    def human_approval(state: LeaveState):

        # ------------------------------------------
        # Safety check
        # ------------------------------------------

        if state["balance"] is None:
            return {
                "approved": False,
                "result": "Leave balance could not be determined."
            }

        if state["days"] > state["balance"]:
            return {
                "approved": False,
                "result": (
                    f"Insufficient leave balance. "
                    f"Available: {state['balance']}, "
                    f"Requested: {state['days']}"
                )
            }

        # ------------------------------------------
        # Pause the graph
        # ------------------------------------------

        decision = interrupt(
            {
                "message": "Human approval required",
                "employee_id": state["employee_id"],
                "leave_type": state["leave_type"],
                "requested_days": state["days"],
                "available_balance": state["balance"]
            }
        )

        return {
            "approved": decision
        }

    # ----------------------------------------------
    # Node 3: Apply Leave
    # ----------------------------------------------

    async def apply_leave_node(state: LeaveState):

        if not state["approved"]:

            print("\nLeave rejected by human.")

            return {
                "result": "Leave request rejected by human."
            }

        print("\nApplying leave through MCP...")

        response = await apply_leave.ainvoke(
            {
                "employee_id": state["employee_id"],
                "leave_type": state["leave_type"],
                "days": state["days"]
            }
        )

        print("\nMCP Apply Leave Response:")
        print(response)

        return {
            "result": str(response)
        }

    # ==================================================
    # BUILD LANGGRAPH
    # ==================================================

    builder = StateGraph(LeaveState)

    builder.add_node(
        "check_balance",
        check_balance
    )

    builder.add_node(
        "human_approval",
        human_approval
    )

    builder.add_node(
        "apply_leave",
        apply_leave_node
    )

    # ----------------------------------------------
    # Edges
    # ----------------------------------------------

    builder.add_edge(
        START,
        "check_balance"
    )

    builder.add_edge(
        "check_balance",
        "human_approval"
    )

    builder.add_edge(
        "human_approval",
        "apply_leave"
    )

    builder.add_edge(
        "apply_leave",
        END
    )

    # ==================================================
    # CHECKPOINT
    # ==================================================

    checkpointer = InMemorySaver()

    app = builder.compile(
        checkpointer=checkpointer
    )

    # ==================================================
    # THREAD
    # ==================================================

    config = {
        "configurable": {
            "thread_id": "leave_request_EMP001_001"
        }
    }

    # ==================================================
    # START WORKFLOW
    # ==================================================

    print("\n========================================")
    print("STARTING LEAVE REQUEST")
    print("========================================")

    result = await app.ainvoke(
        {
            "employee_id": "EMP001",
            "leave_type": "casual",
            "days": 2,
            "balance": None,
            "approved": None,
            "result": ""
        },
        config=config
    )

    # ==================================================
    # CHECK INTERRUPT
    # ==================================================

    if "__interrupt__" in result:

        print("\n========================================")
        print("APPROVAL REQUIRED")
        print("========================================")

        interrupt_data = result["__interrupt__"]

        print(interrupt_data)

        print("\n----------------------------------------")
        print("Leave Approval Request")
        print("----------------------------------------")

        # Usually the first interrupt contains our payload
        request = interrupt_data[0].value

        print(f"Employee ID      : {request['employee_id']}")
        print(f"Leave Type       : {request['leave_type']}")
        print(f"Requested Days   : {request['requested_days']}")
        print(f"Available Balance: {request['available_balance']}")

        print("----------------------------------------")

        # ==================================================
        # HUMAN DECISION
        # ==================================================

        user_input = input(
            "\nApprove leave? (yes/no): "
        ).strip().lower()

        approved = user_input == "yes"

        # ==================================================
        # RESUME GRAPH
        # ==================================================

        result = await app.ainvoke(
            Command(
                resume=approved
            ),
            config=config
        )

    # ==================================================
    # FINAL RESULT
    # ==================================================

    print("\n========================================")
    print("FINAL RESULT")
    print("========================================")

    print(result)

    print("\n========================================")
    print("MESSAGE")
    print("========================================")

    print(result.get("result"))


# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    asyncio.run(main())