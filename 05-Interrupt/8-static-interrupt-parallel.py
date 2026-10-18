
from typing import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph,START,END

class OverAllState(TypedDict):
    final_res:str

def node_a(state:OverAllState)->OverAllState:
    print("node_a 执行")
    return {"final_res":"node_a 中间结果"}

def node_b(state:OverAllState)->OverAllState:
    print("node_b 执行")
    return {"final_res":"node_b 中间结果"}

def node_c(state:OverAllState)->OverAllState:
    print("node_c 执行")
    return {"final_res":"node_c 结果"}

def node_d(state:OverAllState)->OverAllState:
    print("node_d被执行")
    return {}

def node_e(state:OverAllState)->OverAllState:
    print("node_e被执行")
    return {}

builder = StateGraph(OverAllState)
builder.add_node("node_a",node_a)
builder.add_node("node_b",node_b)
builder.add_node("node_c",node_c)
builder.add_node("node_d",node_d)
builder.add_node("node_e",node_e)

builder.add_edge(START,"node_a")
builder.add_edge(START,"node_d")
builder.add_edge("node_a","node_b")
builder.add_edge("node_d","node_e")
builder.add_edge("node_b","node_c")
builder.add_edge("node_e","node_c")
builder.add_edge("node_c",END)
graph = builder.compile(
    checkpointer=InMemorySaver(),
    interrupt_before=["node_a","node_b"],
    interrupt_after=["node_a","node_b"]
)
with open('8-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

config = {"configurable":{"thread_id":"1"}}

print("==========第一次执行==============")
first_res = graph.invoke({},config=config)
print(f"第一次执行结果:{first_res}")

print("==========第二次执行==============")
second_res = graph.invoke(None,config=config)
print("第二次执行结果:{}",second_res)

print("==========第三次执行==============")
second_res = graph.invoke(None,config=config)
print("第三次执行结果:{}",second_res)

print("==========第四次执行==============")
second_res = graph.invoke(None,config=config)
print("第四次执行结果:{}",second_res)

