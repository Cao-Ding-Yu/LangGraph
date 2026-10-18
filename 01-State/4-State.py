
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# 输入状态
class InputState(TypedDict):
    input : str

# 输出状态
class OutputState(TypedDict):
    output: str

# 全局状态
class OverAllState(TypedDict):
    input : str
    output : str
    log : str

# 私有状态
class PrivateState(TypedDict):
    greeting : str

def node_1(state: InputState) -> OverAllState:
    return {
        "log": "Dear " + state["input"]
    }

def node_2(state: OverAllState) -> PrivateState:
    return {
        "greeting": "Hello, " + state["log"]
    }

def node_3(state:PrivateState) -> OutputState:
    return {
        "output": state["greeting"] + " !!! ",
    }

# InputState与OutputState应当是OverAllState的子集
builder = StateGraph(
    state_schema=OverAllState,
    input_schema=InputState,
    output_schema=OutputState,
)

builder.add_node("node_1",node_1)
builder.add_node("node_2",node_2)
builder.add_node("node_3",node_3)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", "node_3")
builder.add_edge("node_3", END)

graph = builder.compile()

print(graph.invoke({"input": "cdy"}))

png_bytes = graph.get_graph().draw_mermaid_png()
with open('4-graph.png', "wb") as f:
    f.write(png_bytes)

