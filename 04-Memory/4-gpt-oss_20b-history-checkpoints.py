
from rich import print as rprint
from typing import TypedDict
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama

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
graph = builder.compile(checkpointer=InMemorySaver())

with open('4-graph.png', "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())

config={
    "configurable":{
        "thread_id":"1"
    }
}

graph.invoke(
    input={"topic":"莲花"},
    config=config,
)

# 1. 查看检查点列表
history = list(graph.get_state_history(config=config))
rprint(history)
print("="*50)

# 2. 查看最新检查点(当前状态)
rprint(graph.get_state(config=config))
print("="*50)

# 3. 查看指定检查点(通过id检索)
checkpoint = graph.get_state(config={
    "configurable": {
        "thread_id": config["configurable"]["thread_id"],
        "checkpoint_id": history[-1].config["configurable"]["checkpoint_id"]
    } # 这里指最早检查点
})
rprint(checkpoint)

