
import random
from dataclasses import dataclass
from typing import Literal
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langchain.messages import HumanMessage,ToolMessage, AIMessage
from langchain_ollama import ChatOllama

# wrap_tool_call的使用

@tool(parse_docstring=True)
def get_weather(city:str)->str:
    """
    查询指定城市的当日天气

    Args:
        city:城市名称
    """
    rand_int = random.randint(1,10)
    if rand_int <= 7:
        raise ConnectionError("工具重试失败")
    return f"{city}天气多云,微风，10度"

model_with_tool = ChatOllama(
    model="gpt-oss:20b",
).bind_tools(tools=[get_weather])

@dataclass
class UserContext:
    max_attempts: int

def llm_node(state:MessagesState) -> MessagesState:
    res = model_with_tool.invoke(state["messages"])
    return {"messages":[res]}

def router(state:MessagesState) -> Literal["tool_node","__end__"]:
    last: AIMessage = state["messages"][-1]
    if last.tool_calls: return "tool_node"
    return END

# 定义工具调用包装器
# request: 固定参数 => 可以调用runtime
# execute: 执行 => 控制工具调用
def wrap_tool_call(request, execute):
    max_attempts = request.runtime.context.max_attempts
    tool_call_id = request.runtime.tool_call_id
    tool_msg = None
    for i in range(max_attempts):
        try:
            print(f"第{i+1}次工具调用")
            tool_msg = execute(request)
            break
        except ConnectionError as e:
            print("工具调用失败")
    if tool_msg is None:
        tool_msg = ToolMessage(
            tool_call_id = tool_call_id,
            content="调用次数达到上限"
        )
    return tool_msg


builder = StateGraph(
    state_schema=MessagesState,
    context_schema=UserContext,
)

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
with open('3-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

res = graph.invoke(
    {"messages":[HumanMessage(content="今天北京的天气怎么样")]},
    context=UserContext(max_attempts=5)
)
for msg in res["messages"]: msg.pretty_print()

