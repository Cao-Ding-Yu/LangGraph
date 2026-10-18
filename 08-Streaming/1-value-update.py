
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# 流式打印状态与更新

class OverAllState(TypedDict):
    initial_state: str
    node_a_output: str
    node_b_output: str

def node_a(state: OverAllState) -> OverAllState:
    return {"node_a_output": "节点A的输出"}

def node_b(state: OverAllState) -> OverAllState:
    return {"node_b_output": "节点B的输出"}

builder = StateGraph(OverAllState)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)
graph = builder.compile()
with open('1-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

for chunk in graph.stream(
    {"init_state": "初始状态"},
    stream_mode=["updates","values"],
    version="v1"
): print(chunk)

print()

for chunk in graph.stream(
    {"init_state": "初始状态"},
    stream_mode=["updates","values"],
    version="v2"
): print(chunk)

