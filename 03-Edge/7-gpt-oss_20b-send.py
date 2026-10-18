
from langchain.messages import HumanMessage
from langgraph.types import Send
from typing import TypedDict, Sequence
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(TypedDict):
    topic: str
    poem: str
    joke: str

class inputState(TypedDict):
    topic: str

class workerState(TypedDict):
    form: str
    topic: str

class outputState(TypedDict):
    poem: str
    joke: str

def worker_node(state:workerState) -> outputState:
    form = state["form"]
    topic = state["topic"]
    prompt = "生成一个关于{}的{}".format(topic, form)
    return {form: model.invoke([HumanMessage(prompt)]).content}

def router(state:inputState) -> Sequence[Send]:
    topic = state["topic"]
    return [
        Send(
            node="worker_node",
            arg={"form": "poem", "topic": topic}
        ),
        Send(
            node="worker_node",
            arg={"form": "joke", "topic": topic}
        ),
    ]

builder = StateGraph(
    state_schema=OverAllState,
    input_schema=inputState,
    output_schema=outputState
)
builder.add_node("worker_node", worker_node)
builder.add_conditional_edges(START, router, path_map=["worker_node"])
builder.add_edge("worker_node",END)
graph = builder.compile()

print(graph.invoke({"topic": "莲花"}))

png_bytes = graph.get_graph().draw_mermaid_png()
with open('7-graph.png', "wb") as f:
    f.write(png_bytes)

