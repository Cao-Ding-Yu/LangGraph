
import asyncio
from operator import add
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy, TimeoutPolicy
from langgraph.errors import NodeError

class State(TypedDict):
    msg: Annotated[str,add]

async def error_handler(state: State, error: NodeError) -> State:
    return {"msg": f"节点捕获异常：{error}"}

async def node_a(state: State) -> State:
    return {"msg": "执行节点A → "}

async def node_b(state: State) -> State:
    return {"msg": "执行节点B"}

graph = (
    StateGraph(State)
    .set_node_defaults(
        retry_policy=RetryPolicy(max_attempts=3),
        timeout=TimeoutPolicy(run_timeout=3),
        error_handler=error_handler,
    )
    .add_node("node_a",node_a)
    .add_node("node_b",node_b)
    .add_edge(START,"node_a")
    .add_edge("node_a","node_b")
    .add_edge("node_b",END)
).compile()

async def main():
    print(await graph.ainvoke({"msg": "start → "}))

if __name__ == "__main__":
    with open('19-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())
    asyncio.run(main())