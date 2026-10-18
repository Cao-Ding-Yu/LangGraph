
from typing import TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START
from langgraph.errors import GraphRecursionError

class EmptyState(TypedDict):
    pass

def loop_node(state:EmptyState,config:RunnableConfig) -> EmptyState:
    cur_step = config["metadata"]["langgraph_step"]
    print(f"cur_step:{cur_step}")

builder = StateGraph(EmptyState)
builder.add_node("loop_node",loop_node)
builder.add_edge(START,"loop_node")
builder.add_edge("loop_node","loop_node")
graph = builder.compile()

try: graph.invoke({},config={"recursion_limit":10})
except GraphRecursionError as e:
    print(f"超步数量达到最大限制,抛出异常:{e}")

png_bytes = graph.get_graph().draw_mermaid_png()
with open('14-graph.png', "wb") as f:
    f.write(png_bytes)

