
import json
from dataclasses import dataclass
from typing import Literal
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langchain.messages import HumanMessage,ToolMessage, AIMessage
from langchain_ollama import ChatOllama

# wrap_tool_call设计缓存
global_cache = dict()

@tool(parse_docstring=True)
def get_weather(city:str)->str:
    """
    查询指定城市的当日天气

    Args:
        city:城市名称
    """
    return f"{city}天气多云,微风，10度"

model_with_tool = ChatOllama(
    model="gpt-oss:20b",
).bind_tools(tools=[get_weather])

def llm_node(state:MessagesState) -> MessagesState:
    res = model_with_tool.invoke(state["messages"])
    return {"messages":[res]}

def router(state:MessagesState) -> Literal["tool_node","__end__"]:
    last: AIMessage = state["messages"][-1]
    if last.tool_calls: return "tool_node"
    return END

def wrap_tool_call(request,execute):
    tool_name = request.tool_call["name"]
    tool_args = json.dumps(request.tool_call["args"])
    tool_call_id = request.runtime.tool_call_id

    cache_key = (tool_name,tool_args)
    cache = global_cache.get(cache_key)

    if cache: # 缓存命中
        print("缓存命中")
        tool_msg = ToolMessage(
            tool_call_id = tool_call_id,
            content= cache
        )
    else: # 缓存没有命中
        tool_msg = execute(request)
        global_cache[cache_key] = tool_msg.content
        print("缓存已记录")
    return tool_msg


builder = StateGraph(MessagesState)
builder.add_node("llm_node",llm_node)
builder.add_node(
    "tool_node",
    ToolNode(
        tools=[get_weather],
        wrap_tool_call=wrap_tool_call,
    )
)
builder.add_edge(START,"llm_node")
builder.add_conditional_edges("llm_node",router,path_map=["tool_node",END])
builder.add_edge("tool_node","llm_node")
graph = builder.compile()
with open('4-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

res = graph.invoke({"messages":[HumanMessage(content="今天北京的天气怎么样")]})
for msg in res["messages"]: msg.pretty_print()

print("="*50)

res = graph.invoke({"messages":[HumanMessage(content="今天北京的天气怎么样")]})
for msg in res["messages"]: msg.pretty_print()

