
import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

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
with open('7-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

async def main():
    async for chunk in graph.astream_events(
        {"initial_state": "初始状态"},
        version="v2"
    ): print(chunk)

if __name__ == "__main__":
    asyncio.run(main())

