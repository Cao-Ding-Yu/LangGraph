
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_ollama import ChatOllama

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(MessagesState):
    username : str
    output : str

def node_a(state: OverAllState) -> OverAllState:
    return {
        "messages": [HumanMessage("你好,我是" + state["username"])],
    }

def llm_node(state: OverAllState) -> OverAllState:
    res = model.invoke(state["messages"])
    return {
        "output": res.content
    }

builder = StateGraph(OverAllState)
builder.add_node("node_a", node_a)
builder.add_node("llm_node", llm_node)
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "llm_node")
builder.add_edge("llm_node", END)
graph = builder.compile()

result = graph.invoke({"username": "老王"})
print(result)

png_bytes = graph.get_graph().draw_mermaid_png()
with open('5-graph.png', "wb") as f:
    f.write(png_bytes)

