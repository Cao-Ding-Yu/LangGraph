
from operator import add
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph,START

class OverAllState(TypedDict):
    message : str    # 状态数据信息
    logs : Annotated[list[str],add]  # 定义日志新增方式为追加

def node_1(state:OverAllState) -> OverAllState:
    pre_message = state["message"]
    return {
        "logs": ["node_1 运行完毕"],
        "message": pre_message + " + node_1_message"
    }

def node_2(state:OverAllState) -> OverAllState:
    pre_message = state["message"]
    return {
        "logs": ["node_2 运行完毕"],
        "message": pre_message + " + node_2_message"
    }


builder = StateGraph(OverAllState)

# 使用add_sequence实现纯线性节点逻辑 → langchain
builder.add_edge(START,"node_1")  # 不可省略，必须要有START
builder.add_sequence([node_1,node_2])
# builder.add_edge("node_2",END)  # 可省略，自动为最后节点添加END

graph = builder.compile()
print(graph.invoke({"message":"start"}))

png_bytes = graph.get_graph().draw_mermaid_png()
with open('1-graph.png', "wb") as f:
    f.write(png_bytes)


