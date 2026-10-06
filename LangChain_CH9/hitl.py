from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


class State(TypedDict):
    employee_name: str
    leave_days: int
    approved: bool | None
    message: str


def prepare_leave(state: State):
    print("Preparing leave request...")

    return {
        "message": (
            f"Leave request prepared for "
            f"{state['employee_name']} "
            f"for {state['leave_days']} days."
        )
    }


def human_approval(state: State):

    decision = interrupt({
        "question": "Do you approve this leave request?",
        "employee": state["employee_name"],
        "days": state["leave_days"]
    })

    return {
        "approved": decision
    }


def submit_leave(state: State):

    if state["approved"]:
        return {
            "message": (
                f"Leave submitted successfully for "
                f"{state['employee_name']} "
                f"for {state['leave_days']} days."
            )
        }

    return {
        "message": "Leave request rejected."
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("prepare_leave", prepare_leave)
builder.add_node("human_approval", human_approval)
builder.add_node("submit_leave", submit_leave)

builder.add_edge(START, "prepare_leave")
builder.add_edge("prepare_leave", "human_approval")
builder.add_edge("human_approval", "submit_leave")
builder.add_edge("submit_leave", END)


# -------------------------
# Checkpointing
# -------------------------

checkpointer = InMemorySaver()

app = builder.compile(
    checkpointer=checkpointer
)


# -------------------------
# Thread
# -------------------------

config = {
    "configurable": {
        "thread_id": "employee_EMP001"
    }
}


# -------------------------
# First execution
# -------------------------

result = app.invoke(
    {
        "employee_name": "Jacky",
        "leave_days": 2,
        "approved": None,
        "message": ""
    },
    config=config
)

result = app.invoke(
    Command(resume=True),
    config=config
)

print("\nFIRST RESULT:")
print(result)

print("\nINTERRUPT:")
#print(result["__interrupt__"])