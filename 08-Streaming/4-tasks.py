
from typing import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph,END,START

class OverAllState(TypedDict):
    initial_state:str
    parallel_node_a_1:str
    parallel_node_a_2:str
    node_b_output:str

def parallel_node_a_1(state:OverAllState) -> OverAllState:
    return {"parallel_node_a_1":"并行节点A-1的输出"}

def parallel_node_a_2(state:OverAllState) -> OverAllState:
    return {"parallel_node_a_2":"并行节点A-2的输出"}

def node_b(state:OverAllState) -> OverAllState:
    return {"node_b_output":"节点B的输出"}

builder = StateGraph(OverAllState)
builder.add_node("parallel_node_a_1",parallel_node_a_1)
builder.add_node("parallel_node_a_2",parallel_node_a_2)
builder.add_node("node_b",node_b)
builder.add_edge(START,"parallel_node_a_1")
builder.add_edge(START,"parallel_node_a_2")
builder.add_edge(["parallel_node_a_1","parallel_node_a_2"],"node_b")
builder.add_edge("node_b",END)
graph = builder.compile(checkpointer=InMemorySaver())
with open('4-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())


config = {"configurable":{"thread_id":"1"}}
for chunk in graph.stream(
    {"initial_state":"初始状态"},
    config=config,
    stream_mode=["tasks"],
): print(chunk)


