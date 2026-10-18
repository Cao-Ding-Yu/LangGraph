
from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langchain.messages import HumanMessage
from langchain_ollama import ChatOllama

# ToolNode的基本使用

@tool(parse_docstring=True)
def get_weather(city:str) ->str:
    """
    查询指定城市的当日天气

    Args:
        city:城市名称
    """
    return f"{city} 天气有雨,微风，气温30度"

@tool(parse_docstring=True)
def get_news(home_or_abroad:bool) ->str:
    """
    查询国内外的新闻

    Args:
        home_or_abroad: 查询国内或者国外的新闻
    """
    if home_or_abroad: return "Kimi 新模型发布"
    return "Anthropic 暂停新模型访问"

model_with_tools = ChatOllama(
    model="gpt-oss:20b",
).bind_tools(tools=[get_weather,get_news])

class OverAllState(MessagesState):
    output:str

def llm_node(state:OverAllState) -> OverAllState:
    res = model_with_tools.invoke(state["messages"])
    return {
        "messages":[res],
        "output":res.content
    }

def router(state:OverAllState) -> Literal["tool_node","__end__"]:
    last: AIMessage = state["messages"][-1]
    if last.tool_calls: return "tool_node"
    return END

builder = StateGraph(OverAllState)
builder.add_node("llm_node",llm_node)
builder.add_node("tool_node",ToolNode(tools=[get_weather,get_news]))
builder.add_edge(START,"llm_node")
builder.add_conditional_edges("llm_node",router,path_map=["tool_node",END])
builder.add_edge("tool_node","llm_node")
graph = builder.compile()
with open('1-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

res = graph.invoke({"messages":[HumanMessage("今天北京的天气怎么样?国内有什么新闻?")]})
for msg in res["messages"]: msg.pretty_print()
