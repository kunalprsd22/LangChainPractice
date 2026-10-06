from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    number: int
    result: str


def check_positive(state: State):
    if state["number"] >= 0:
        return {"result": "positive"}
    else:
        return {"result": "negative"}

def route(state: State):
    if state["result"] == "positive":
        return "positive_node"

    return "negative_node"

def positive_node(state: State):
    return {
        "result": "The number is positive."
    }


def negative_node(state: State):
    return {
        "result": "The number is negative."
    }


graph = StateGraph(State)

graph.add_node("check", check_positive)
graph.add_node("positive_node", positive_node)
graph.add_node("negative_node", negative_node)

graph.add_edge(START, "check")

graph.add_conditional_edges(
    "check",
    route
)

graph.add_edge("positive_node", END)
graph.add_edge("negative_node", END)

app = graph.compile()


result = app.invoke({
    "number": 10
})

print(result)