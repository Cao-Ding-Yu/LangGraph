
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy, Command
from langgraph.errors import NodeError
from requests import HTTPError

class OverAllState(TypedDict):
    error_message: str

def node(state: OverAllState) -> OverAllState:
    print("node 正在运行")
    raise HTTPError

def solve(state: OverAllState, error: NodeError) -> Command[Literal["recovery_node"]]:
    return Command(
        update={"error_message": str(error)},
        goto="recovery_node"
    )

def recovery_node(state: OverAllState) -> None:
    print(f"recovery_node 执行")

builder = StateGraph(OverAllState)
builder.add_node(
    node,
    error_handler=solve,
)
builder.add_node("recovery_node",recovery_node)
builder.add_edge(START,"node")
builder.add_edge("node",END)
builder.add_edge("recovery_node",END)
graph = builder.compile()

print(graph.invoke({}))

png_bytes = graph.get_graph().draw_mermaid_png()
with open('16-graph.png', "wb") as f:
    f.write(png_bytes)

