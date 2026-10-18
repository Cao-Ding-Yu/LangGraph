
from typing import Literal
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt.tool_node import ToolNode, ToolRuntime
from langgraph.runtime import Runtime
from langchain.tools import tool
from langchain.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama

# 自定义流式输出内容

@tool(parse_docstring=True)
def get_weather(city: str, runtime: ToolRuntime) -> str:
    """
    根据城市查询当日天气

    Args:
        runtime: 运行时实例
        city: 城市名称
    """
    runtime.stream_writer(f"正在查询 {city} 今天的天气...")
    return f"{city} 今天天气不错"

model_with_tools = ChatOllama(
    model="gpt-oss:20b",
).bind_tools(tools=[get_weather])

def llm_node(state: MessagesState, runtime: Runtime) -> MessagesState:
    response = model_with_tools.invoke(state["messages"])
    runtime.stream_writer("正在执行 llm_node...")
    return {"messages": [response]}

def router(state:MessagesState) -> Literal["tool_node","__end__"]:
    last: AIMessage = state["messages"][-1]
    if last.tool_calls: return "tool_node"
    return END

builder = StateGraph(state_schema=MessagesState)
builder.add_node("llm_node", llm_node)
builder.add_node("tool_node", ToolNode(tools=[get_weather]))
builder.add_edge(START, "llm_node")
builder.add_conditional_edges("llm_node", router, path_map=["tool_node", END])
builder.add_edge("tool_node", "llm_node")
graph = builder.compile()
with open('6-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

for chunk in graph.stream(
    {"messages": [HumanMessage("今天北京天气如何")]},
    # 用户自定义流式输出要添加custom
    stream_mode=["custom"]
):print(chunk)
