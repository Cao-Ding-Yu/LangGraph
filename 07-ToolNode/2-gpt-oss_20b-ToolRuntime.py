
from typing import Literal
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain.tools import tool
from langgraph.prebuilt import ToolNode, ToolRuntime
from langgraph.types import Command
from langchain.messages import HumanMessage, ToolMessage, AIMessage
from langchain_ollama import ChatOllama

# ToolRuntime的基本使用

class OverAllState(MessagesState):
    weather_res:str
    new_res:str
    output:str

@tool(parse_docstring=True)
def get_weather(city:str, runtime:ToolRuntime) ->Command:
    """
    查询指定城市的当日天气

    Args:
        city:城市名称
        runtime:ToolRuntime
    """
    res = f"{city} 天气有雨,微风，气温30度"
    tool_msg = ToolMessage(tool_call_id=runtime.tool_call_id,content=res)
    return Command(
        update= {
            "weather_res":res,
            "messages":[tool_msg]
        }
    )

@tool(parse_docstring=True)
def get_news(home_or_abroad:bool, runtime:ToolRuntime) ->Command:
    """
    查询国内外的新闻

    Args:
        home_or_abroad: 查询国内或者国外的新闻
        runtime:ToolRuntime
    """
    if home_or_abroad: res = "Kimi 新模型发布"
    else: res = "Anthropic 暂停新模型访问"
    tool_msg = ToolMessage(tool_call_id=runtime.tool_call_id,content=res)
    return Command(
        update={
            "new_res" :res,
            "messages":[tool_msg]
        }
    )

model_with_tools = ChatOllama(
    model="gpt-oss:20b",
).bind_tools(tools=[get_weather,get_news])

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
with open('2-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

res = graph.invoke({"messages":[HumanMessage("今天北京的天气怎么样?国内有什么新闻?")]})
for msg in res["messages"]: msg.pretty_print()


