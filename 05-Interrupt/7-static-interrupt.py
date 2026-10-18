
from typing import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph,START,END

# 静态断点，用于调试，恢复时传入None，

class OverAllState(TypedDict):
    result: str

def node_a(state:OverAllState)->OverAllState:
    print("node_a 执行")
    return {"result":"node_a 中间结果"}

def node_b(state:OverAllState)->OverAllState:
    print("node_b 执行")
    return {"result":"node_b 中间结果"}

def node_c(state:OverAllState)->OverAllState:
    print("node_c 执行")
    return {"result":"node_c 中间结果"}

builder = StateGraph(OverAllState)
builder.add_node("node_a",node_a)
builder.add_node("node_b",node_b)
builder.add_node("node_c",node_c)
builder.add_edge(START,"node_a")
builder.add_edge("node_a","node_b")
builder.add_edge("node_b","node_c")
builder.add_edge("node_c",END)
# 最好写入compile里，否则每次invoke都需要传入interrupt_before和interrupt_after参数
# 相邻节点之间即使有多个静态中断，也只中断一次
graph = builder.compile(
    checkpointer=InMemorySaver(),
    interrupt_before=["node_a","node_b"],
    interrupt_after=["node_a","node_b"]
)
with open('7-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

config = {"configurable":{"thread_id":"1"}}

print("==========第一次执行==============")
first_res = graph.invoke({},config=config)
print(f"第一次执行结果:{first_res}")

print("==========第二次执行==============")
second_res = graph.invoke(None,config=config)
print(f"第二次执行结果:{second_res}")

print("==========第三次执行==============")
res3 = graph.invoke(None,config=config)
print(f"第三次执行结果:{res3}")

print("==========第四次执行==============")
res4 = graph.invoke(None,config=config)
print(f"第四次执行结果:{res3}")


