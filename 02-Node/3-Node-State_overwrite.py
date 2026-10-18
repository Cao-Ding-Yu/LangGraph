
from operator import add
from typing import TypedDict,Annotated
from langgraph.graph import StateGraph,START,END
from langgraph.types import Overwrite

class OverAllState(TypedDict):
    logs : Annotated[list[str],add]
    data : str

# 2. 定义节点
def node_1(state:OverAllState) -> OverAllState:
    for k,v in state.items():
        print(f"key:{k} value:{v}")
    return {
        "logs":["node_1 运行完毕"],
        "data":"node_1"
    }

def node_2(state:OverAllState) -> OverAllState:
    for k,v in state.items():
        print(f"key:{k} value:{v}")
    return {
        "logs":Overwrite(["node_2 运行完毕"]),
        "data":"node_2"
    } # Overwrite覆盖原数据

def node_3(state:OverAllState) -> OverAllState:
    for k,v in state.items():
        print(f"key:{k} value:{v}")
    return {
        "logs":["node_3 运行完毕"],
        "data":"node_3"
    }

builder = StateGraph(OverAllState)
builder.add_node("node_1",node_1)
builder.add_node("node_2",node_2)
builder.add_node("node_3",node_3)
builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_2","node_3")
builder.add_edge("node_3",END)
graph = builder.compile()

result = graph.invoke({"logs":["start"],"data":"start"})
print(result)

png_bytes = graph.get_graph().draw_mermaid_png()
with open('3-graph.png', "wb") as f:
    f.write(png_bytes)