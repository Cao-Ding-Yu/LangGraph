
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain.messages import HumanMessage
from langchain_ollama import ChatOllama

# 流式输出 messages

model = ChatOllama(
    model="gpt-oss:20b",
)

def llm_node(state: MessagesState) -> MessagesState:
    response = model.invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node("llm_node", llm_node)
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", END)
graph = builder.compile()
with open('2-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

for chunk in graph.stream(
    {"messages":[HumanMessage(content="你好")]},
    stream_mode=["messages"],
): print(chunk)