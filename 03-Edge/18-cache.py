import time
from typing import TypedDict
from langgraph.cache.memory import InMemoryCache
from langgraph.graph import StateGraph,START,END
from langgraph.types import CachePolicy

class OverAllState(TypedDict):
    user: str

def node(state:OverAllState) -> None:
    print(f"node被调用 user:{state["user"]}")

builder = StateGraph(OverAllState)
builder.add_node(node, cache_policy=CachePolicy(ttl=5))
builder.add_edge(START,"node")
builder.add_edge("node",END)
graph = builder.compile(cache= InMemoryCache())

print(f"运行结果 {graph.invoke({"user":"小明"})}")
print(f"运行结果 {graph.invoke({"user":"小明"})}")
print(f"运行结果 {graph.invoke({"user":"小花"})}")
print(f"运行结果 {graph.invoke({"user":"小花"})}")

time.sleep(5)
print(f"运行结果 {graph.invoke({"user":"小花"})}")
print(f"运行结果 {graph.invoke({"user":"小明"})}")

with open('18-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())
