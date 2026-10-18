
from langgraph.types import Command
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(TypedDict):
    topic: str  # 创作主题
    content_type: Literal["poem","joke"]  # 创作类型
    content_description: str  # 创作内容描述
    poem: str   # 创作的诗词内容
    joke: str   # 创作的笑话内容

def router(state:OverAllState) -> Command[Literal["poem_node","joke_node","__end__"]]:
    topic = state["topic"]
    if state["content_type"] == "poem":
        return Command(
            update={"content_description": "关于{}的诗词".format(state["topic"])},
            goto="poem_node"
        )
    elif state["content_type"] == "joke":
        return Command(
            update={"content_description": f"关于{state["topic"]}的笑话"},
            goto="joke_node"
        )
    else: return Command(goto=END)

def poem_node(state:OverAllState) -> OverAllState:
    return {"poem": model.invoke([f"写一个{state['content_description']}"]).content}


def joke_node(state:OverAllState) -> OverAllState:
    return {"joke": model.invoke([f"写一个{state['content_description']}"]).content}

builder = StateGraph(OverAllState)
builder.add_node("router",router)
builder.add_node("poem_node",poem_node)
builder.add_node("joke_node",joke_node)
builder.add_edge(START,"router")
builder.add_edge("poem_node",END)
builder.add_edge("joke_node",END)
graph = builder.compile()

print(graph.invoke({"topic": "莲花","content_type": "poem"}))
print(graph.invoke({"topic": "猫咪","content_type": "joke"}))
print(graph.invoke({"topic": "猫咪","content_type": "xxx"}))

png_bytes = graph.get_graph().draw_mermaid_png()
with open('8-graph.png', "wb") as f:
    f.write(png_bytes)
