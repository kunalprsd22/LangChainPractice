from langgraph.graph import StateGraph, START, END
from typing import TypedDict


class State(TypedDict):
    message: str


def step_one(state: State):
    return {
        "message": state["message"] + " - Step 1"
    }


def step_two(state: State):
    return {
        "message": state["message"] + " - Step 2"
    }


graph = StateGraph(State)

graph.add_node("step_one", step_one)
graph.add_node("step_two", step_two)

graph.add_edge(START, "step_one")
graph.add_edge("step_one", "step_two")
graph.add_edge("step_two", END)

app = graph.compile()

result = app.invoke({
    "message": "Start"
})

print(result)