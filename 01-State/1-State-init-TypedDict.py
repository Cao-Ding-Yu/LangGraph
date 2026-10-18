
from operator import add
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph,START,END

# 1. 定义简易状态
class OverAllState(TypedDict):
    message : str    # 状态数据信息
    logs : Annotated[list[str],add]  # 定义日志新增方式为追加

# 2. 定义节点
def node_1(state:OverAllState) -> OverAllState:
    pre_message = state["message"]
    # 假设节点操作
    return {
        "logs": ["node_1 运行完毕"],
        "message": pre_message + " + node_1_message"
    }

def node_2(state:OverAllState) -> OverAllState:
    pre_message = state["message"]
    # 假设节点操作
    return {
        "logs": ["node_2 运行完毕"],
        "message": pre_message + " + node_2_message"
    }

# 3. 创建图
builder = StateGraph(OverAllState)

# 4. 添加节点
builder.add_node(node_1)    # 隐式添加节点，节点名与函数名相同
builder.add_node("node_2", node_2)  # 显示添加节点，自定义节点名

# 5. 添加边
builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_2",END)

# 6. 有向图编译
graph = builder.compile()

# 7. 输出结果打印
result = graph.invoke({"message":"start"})
print(result)

# 8. 流程拓扑表
raw_mermaid = graph.get_graph().draw_mermaid()
print(raw_mermaid)

# 9. 保存可视化流程图
png_bytes = graph.get_graph().draw_mermaid_png()
with open('1-graph.png', "wb") as f:
    f.write(png_bytes)


