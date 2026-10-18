
from time import sleep
from typing import TypedDict,Annotated
from operator import add
from langgraph.graph import StateGraph,START,END

class OverAllState(TypedDict):
    # 若出现并行子节点同时更新状态并向下游节点传递，必须有reducer，否则报错
    cur_id : Annotated[str,add]
    logs : Annotated[list[str],add]

def node_1(state:OverAllState) -> OverAllState:
    for k,v in state.items():
        print(f"1key:{k} value:{v}")
    return {
        "logs":["node_1 运行完毕"]
    }

def node_2(state:OverAllState) -> OverAllState:
    for k,v in state.items():
        print(f"2key:{k} value:{v}")
    return {
        "logs":["node_2 运行完毕"],
        "cur_id":"node2"
    }

def node_3(state:OverAllState) -> OverAllState:
    sleep(1) # 异步效果
    for k,v in state.items():
        print(f"3key:{k} value:{v}")
    return {
        "logs":["node_3 运行完毕"],
        "cur_id":"node3"
    }

def node_4(state:OverAllState) -> OverAllState:
    for k,v in state.items():
        print(f"4key:{k} value:{v}")
    return {
        "logs":["node_4 运行完毕"]
    }

# node节点的添加顺序会决定下层node中谁的补充先被添加
builder = StateGraph(OverAllState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
builder.add_node("node_4", node_4)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")
builder.add_edge("node_2", "node_4")
builder.add_edge("node_3", "node_4")
builder.add_edge("node_4", END)
graph = builder.compile()

result = graph.invoke({"logs": ["start"], "cur_id": "start"})
print('\n' + '=' * 30, '-> result <-', '=' * 30 + '\n' + str(result))

png_bytes = graph.get_graph().draw_mermaid_png()
with open('4-graph.png', "wb") as f:
    f.write(png_bytes)

