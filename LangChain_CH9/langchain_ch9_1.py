from langgraph.graph import StateGraph, START, END
from typing import TypedDict


class State(TypedDict):
    message: str


def greeting(state: State):
    return {
        "message": f"Hello, {state['message']}!"
    }


graph = StateGraph(State)

graph.add_node("greeting1", greeting)

graph.add_edge(START, "greeting1")
graph.add_edge("greeting1", END)

app = graph.compile()

result = app.invoke({
    "message": "Jacky"
})

print(result)