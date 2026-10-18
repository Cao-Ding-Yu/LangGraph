
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_ollama import ChatOllama

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(MessagesState):
    output: str

def llm_mode(state:OverAllState) -> OverAllState:
    res = model.invoke(state["messages"])
    return {"messages":[res]}

def output_node(state:OverAllState) -> OverAllState:
    return {"output":state["messages"][-1].content}

builder = StateGraph(OverAllState)
builder.add_node("llm_node",llm_mode)
builder.add_node("output_node",output_node)
builder.add_edge(START,"llm_node")
builder.add_edge("llm_node","output_node")
builder.add_edge("output_node",END)

graph = builder.compile(checkpointer=InMemorySaver())

config = {
    "configurable":{
        "thread_id":"1"
    }
}

print(graph.invoke({"messages": [HumanMessage("我的名字是老王")]}, config=config)["output"])
print(graph.invoke({"messages": [HumanMessage("我的名字是什么")]}, config=config)["output"])

png_bytes = graph.get_graph().draw_mermaid_png()
with open('1-graph.png', "wb") as f:
    f.write(png_bytes)

