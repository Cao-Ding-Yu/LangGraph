
from rich import print as rprint
from typing import TypedDict
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(TypedDict):
    topic:str
    poem:str
    joke:str
    output:str

class InputState(TypedDict):
    topic:str

class OutputState(TypedDict):
    output:str

def node_poem(state:InputState) -> OverAllState:
    poem = model.invoke([HumanMessage(f"写一首关于{state["topic"]}的七言绝句")]).content
    return {"poem":poem}

def node_joke(state:InputState) -> OverAllState:
    joke = model.invoke([HumanMessage(f"写一首关于{state["topic"]}的笑话")]).content
    return {"joke":joke}

def node_output(state:OverAllState)->OutputState:
    output = f"关于{state["topic"]}主题的七言绝句:{state["poem"]},\n笑话:{state["joke"]}\n"
    return {"output": output}

builder = StateGraph(
    state_schema=OverAllState,
    input_schema=InputState,
    output_schema=OutputState
)
builder.add_node("node_poem",node_poem)
builder.add_node("node_joke",node_joke)
builder.add_node("node_output",node_output)
builder.add_edge(START,"node_poem")
builder.add_edge(START,"node_joke")
builder.add_edge("node_poem","node_output")
builder.add_edge("node_joke","node_output")
builder.add_edge("node_output",END)

DB = "5-6-sqlite.db"
config = {"configurable": {"thread_id": "1"}}
with SqliteSaver.from_conn_string(DB) as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
    # 报错检查点继续执行时，input需为None，config不变
    print(graph.invoke(None, config=config))
    rprint(list(graph.get_state_history(config=config)))


