
from typing import TypedDict,Annotated
from operator import add
from langgraph.graph import StateGraph,START,END

class OverAllState(TypedDict):
    logs : Annotated[list[str],add]
    place : str

def node_1(state:OverAllState) -> OverAllState:
    # 在节点中读取状态
    for k,v in state.items():
        print(f"key:{k} value:{v}")
    return {
        "place":"node_1"
    }

builder = StateGraph(OverAllState)
builder.add_node(node_1)
builder.add_edge(START,"node_1")
builder.add_edge("node_1",END)
graph = builder.compile()

result = graph.invoke({"logs":["start_log"],"place":"start"})
print(result)

png_bytes = graph.get_graph().draw_mermaid_png()
with open('2-graph.png', "wb") as f:
    f.write(png_bytes)