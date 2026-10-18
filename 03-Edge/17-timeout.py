import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import TimeoutPolicy
from langgraph.errors import NodeTimeoutError

class State(TypedDict):
    result: str

async def slow_node(state: State) -> State:
    await asyncio.sleep(5)
    return {"result": "finished"}

builder = StateGraph(State)
builder.add_node(slow_node, timeout=TimeoutPolicy(run_timeout=3))
builder.add_edge(START, "slow_node")
builder.add_edge("slow_node", END)
graph = builder.compile()

async def main():
    try:
        result = await graph.ainvoke({})
        print("执行成功:", result)
    except NodeTimeoutError as e:
        print(f"超时错误: {e}")

if __name__ == "__main__":
    with open('17-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())
    asyncio.run(main())

