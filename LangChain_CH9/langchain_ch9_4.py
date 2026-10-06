from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    number: int


def increment(state: State):
    return {
        "number": state["number"] + 1
    }


def should_continue(state: State):
    if state["number"] < 5:
        return "increment"

    return END


graph = StateGraph(State)

graph.add_node("increment", increment)

graph.add_edge(START, "increment")

graph.add_conditional_edges(
    "increment",
    should_continue
)

app = graph.compile()

result = app.invoke({
    "number": 0
})

print(result)