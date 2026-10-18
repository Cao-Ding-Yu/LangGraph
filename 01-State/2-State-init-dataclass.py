
from operator import add
from dataclasses import dataclass
from typing import Annotated
from langgraph.graph import StateGraph,START,END

# 1. 定义状态
@dataclass
class OverAllState:
    message : str    # 状态数据信息
    logs : Annotated[list[str],add]  # 定义日志新增方式为追加

# 2. 定义节点
def node_1(state:OverAllState) -> OverAllState:
    pre_message = state.message
    return OverAllState(
        logs=["node_1 运行完毕"],
        message=pre_message + " + node_1_message"
    ) # 返回对象

def node_2(state:OverAllState) -> OverAllState:
    pre_message = state.message
    return {
        "logs": ["node_2 运行完毕"],
        "message": pre_message + " + node_2_message"
    } # Dict参数同样适配

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
result = graph.invoke(OverAllState("start", list()))
# result = graph.invoke({"message":"start"}) # Dict参数同样适配
print(result)

png_bytes = graph.get_graph().draw_mermaid_png()
with open('2-graph.png', "wb") as f:
    f.write(png_bytes)


