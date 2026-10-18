
import os
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

DB = "7-sqlite.db"
config = {"configurable": {"thread_id": "1"}}
if os.path.exists(DB): os.remove(DB)
with SqliteSaver.from_conn_string(DB) as checkpointer:
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)
    with open('7-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())
    print(graph.invoke({"topic":"猫"},config=config))

# 重复执行指定检查点
target_config = None
with SqliteSaver.from_conn_string(DB) as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
    for checkpoint in list(graph.get_state_history(config=config)):
        if checkpoint.next == ('node_poem', 'node_joke'):
            target_config = checkpoint.config; break
    # 实现replay的效果，状态填写None，config为目标检查点的config
    res = graph.invoke(None,config=target_config)
    print(res)

