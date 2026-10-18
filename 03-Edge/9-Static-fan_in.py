
from typing import TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END

class EmptyState(TypedDict):
    pass

def node_a(state:EmptyState,config:RunnableConfig) -> EmptyState:
    cur_step = config["metadata"]["langgraph_step"]
    print(f"a节点超步: {cur_step}")
    return {}

def node_b(state:EmptyState,config:RunnableConfig) -> EmptyState:
    cur_step = config["metadata"]["langgraph_step"]
    print(f"b节点超步: {cur_step}")
    return {}

def node_c(state:EmptyState,config:RunnableConfig) -> EmptyState:
    cur_step = config["metadata"]["langgraph_step"]
    print(f"c节点超步: {cur_step}")
    return {}

def node_d(state:EmptyState,config:RunnableConfig) -> EmptyState:
    cur_step = config["metadata"]["langgraph_step"]
    print(f"d节点超步: {cur_step}")
    return {}

def node_e(state:EmptyState,config:RunnableConfig) -> EmptyState:
    cur_step = config["metadata"]["langgraph_step"]
    print(f"e节点超步: {cur_step}")
    return {}

# "与"关系：c和d同时执行完成后e开始执行
builder1 = StateGraph(EmptyState)
builder1.add_node("node_a",node_a)
builder1.add_node("node_b",node_b)
builder1.add_node("node_c",node_c)
builder1.add_node("node_d",node_d)
builder1.add_node("node_e",node_e)

builder1.add_edge(START,"node_a")
builder1.add_edge("node_a","node_b")
builder1.add_edge("node_a","node_c")
builder1.add_edge("node_b","node_d")
builder1.add_edge(["node_c","node_d"],"node_e")
builder1.add_edge("node_e",END)
graph1 = builder1.compile()
graph1.invoke({})

png_bytes = graph1.get_graph().draw_mermaid_png()
with open('9-graph-and.png', "wb") as f:
    f.write(png_bytes)
print("="*50)

# "或"关系：c和d其一执行完成后e都开始执行，即e可执行两次
builder2 = StateGraph(EmptyState)
builder2.add_node("node_a",node_a)
builder2.add_node("node_b",node_b)
builder2.add_node("node_c",node_c)
builder2.add_node("node_d",node_d)
builder2.add_node("node_e",node_e)

# "与"关系：c和d同时执行完成后e开始执行
builder2.add_edge(START,"node_a")
builder2.add_edge("node_a","node_b")
builder2.add_edge("node_a","node_c")
builder2.add_edge("node_b","node_d")
builder2.add_edge("node_c","node_e")
builder2.add_edge("node_d","node_e")
builder2.add_edge("node_e",END)
graph2 = builder2.compile()
graph2.invoke({})

png_bytes = graph2.get_graph().draw_mermaid_png()
with open('9-graph-or.png', "wb") as f:
    f.write(png_bytes)



