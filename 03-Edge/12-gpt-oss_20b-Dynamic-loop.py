
from typing import Literal
from langchain.tools import tool
from langgraph.types import Command
from langchain_ollama import ChatOllama
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState

@tool(parse_docstring=True)
def get_weather(city:str = "北京"):
    """
    查询指定城市当日天气

    Args:
        city: 城市名称
    """
    return f"{city}天气晴朗,23度"

@tool(parse_docstring=True)
def get_news(domain:Literal["AI","食品安全"]):
    """
    查询特定领域的当日热点

    Args:
        domain: 特定领域
    """
    if domain == "AI": return "Anthropic发布的Claude Opus-4.8，通过中文向它发送“你是谁”时，返回的却是Qwen或Deepseek"
    elif domain == "食品安全": return "双汇发展子公司猪肉产品被抽检出抗生素超标37.5倍"
    else: return "未知的新闻领域"

model = ChatOllama(
    model="gpt-oss:20b",
).bind_tools([get_weather,get_news])

class OverAllState(MessagesState):
    user_input:str
    final_output:str

# 将输入文本转换成用户消息
def input_node(state:OverAllState) -> OverAllState:
    return {"messages": [HumanMessage(state["user_input"])]}

# 调用大模型
def llm_node(state:OverAllState) -> Command[Literal["tool_node","output_node"]]:
    response = model.invoke(state["messages"])
    if response.tool_calls: goto = "tool_node"
    else: goto = "output_node"
    return Command(
        update={"messages" : [response]},
        goto=goto
    )

# 工具调用节点
def tool_node(state:OverAllState) -> OverAllState:
    new_message = list()
    messages = state["messages"]
    last: AIMessage = messages[-1]
    tool_calls = last.tool_calls
    for tool_call in tool_calls:
        if tool_call["name"]== "get_weather":
            new_message.append(get_weather.invoke(tool_call))
        elif tool_call["name"] == "get_news":
            new_message.append(get_news.invoke(tool_call))
        else: new_message.append(ToolMessage(content="工具调用失败", tool_call_id=tool_call["id"]))
    return {"messages": new_message} # 没有toolcall,直接返回

# 输出节点
def output_node(state:OverAllState) -> OverAllState:
    return {"final_output":state["messages"][-1].content}

builder = StateGraph(OverAllState)
builder.add_node("input_node",input_node)
builder.add_node("llm_node",llm_node)
builder.add_node("tool_node",tool_node)
builder.add_node("output_node",output_node)
builder.add_edge(START,"input_node")
builder.add_edge("input_node","llm_node")
builder.add_edge("tool_node","llm_node")
builder.add_edge("output_node",END)
graph = builder.compile()

result = graph.invoke({"user_input":"查询今天的上海天气和AI新闻热点"})
for msg in result["messages"]: msg.pretty_print()

png_bytes = graph.get_graph().draw_mermaid_png()
with open('12-graph.png', "wb") as f:
    f.write(png_bytes)

