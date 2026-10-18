
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(TypedDict):
    topic : str
    poem : str
    joke : str

def node_poem(state: OverAllState) -> OverAllState:
    poem = model.invoke([f"写一首关于{state['topic']}主题的诗词"]).content
    return {
        "poem": poem
    }

def node_joke(state: OverAllState) -> OverAllState:
    joke = model.invoke([f"写一个关于{state['topic']}主题的笑话"]).content
    return {
        "joke": joke
    }

def delay_node(state: OverAllState) -> OverAllState:
    print(f"诗歌{'已生成' if state['poem'] else '未生成'}")
    print(f"笑话{'已生成' if state['joke'] else '未生成'}")

builder = StateGraph(OverAllState)

builder.add_node(node_poem)
builder.add_node(node_joke)
builder.add_node(delay_node, defer=True)

builder.add_edge(START,"node_poem")
builder.add_edge(START,"node_joke")
builder.add_edge(START,"delay_node")
builder.add_edge("node_poem",END)
builder.add_edge("node_joke",END)
builder.add_edge("delay_node",END)

graph = builder.compile()

print(graph.invoke({"topic": "猫"}))
print(graph.get_graph().draw_mermaid())

png_bytes = graph.get_graph().draw_mermaid_png()
with open('6-graph.png', "wb") as f:
    f.write(png_bytes)

