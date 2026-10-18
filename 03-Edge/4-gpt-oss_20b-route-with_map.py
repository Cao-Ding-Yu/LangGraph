from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(TypedDict):
    topic : str
    type : str
    poem : str
    joke : str

def node_poem(state: OverAllState) -> OverAllState:
    poem = model.invoke([f"写一首关于{state['topic']}主题的诗"]).content
    return {
        "poem": poem
    }

def node_joke(state: OverAllState) -> OverAllState:
    joke = model.invoke([f"写一个关于{state['topic']}主题的笑话"]).content
    return {
        "joke": joke
    }

# 路由选择函数
def route(state: OverAllState) -> Literal["node_poem","node_joke"]:
    if "诗" in state["type"]: return "poem"
    else: return "joke"

builder = StateGraph(OverAllState)
builder.add_node(node_poem)
builder.add_node(node_joke)
builder.add_conditional_edges(START,route,path_map={
    "poem":"node_poem",
    "joke":"node_joke"
})
builder.add_edge("node_joke",END)
builder.add_edge("node_poem",END)
graph = builder.compile()

print(graph.invoke({"topic": "猫咪", "type": "诗"}))
print(graph.get_graph().draw_mermaid())

png_bytes = graph.get_graph().draw_mermaid_png()
with open('4-graph.png', "wb") as f:
    f.write(png_bytes)

