
from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.graph.message import MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import tool
from langchain_ollama import ChatOllama

# human in the loop --工具调用审批

@tool(parse_docstring=True)
def get_weather(city: str) -> str:
    """
    查询指定城市的当日天气

    Args:
        city: 城市名称
    """
    is_approved = interrupt({
        "action": "get_weather",
        "question": "是否同意查询天气(y/else): "
    })
    if is_approved: return f"{city} 今天天气有雨，18度"
    else: return "用户拒绝查询天气"

tools_by_name = {"get_weather": get_weather}

model = ChatOllama(
    model="gpt-oss:20b",
)
model_with_tools = model.bind_tools([get_weather])

def llm_node(state: MessagesState) -> MessagesState:
    response = model_with_tools.invoke(state['messages'])
    return {"messages": [response]}

def tool_node(state: MessagesState) -> MessagesState:
    tool_msgs = list()
    last_msg: AIMessage = state['messages'][-1]
    for tool_call in last_msg.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        tool_res = tool.invoke(tool_call["args"])
        tool_msg = ToolMessage(
            name = tool_call["name"],
            content = tool_res,
            tool_call_id = tool_call["id"]
        )
        tool_msgs.append(tool_msg)
    return {"messages": tool_msgs}

def router(state: MessagesState) -> Literal["tool_node", "__end__"]:
    messages: AIMessage = state['messages'][-1]
    if messages.tool_calls: return "tool_node"
    return END

builder = StateGraph(MessagesState)
builder.add_node("llm_node", llm_node)
builder.add_node("tool_node", tool_node)
builder.add_edge(START, "llm_node")
builder.add_conditional_edges("llm_node", router, path_map=["tool_node", END])
builder.add_edge("tool_node", "llm_node")
graph = builder.compile(checkpointer=InMemorySaver())
with open('5-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())


config = {"configurable": {"thread_id": "1"}}
interrupted_res = graph.invoke({"messages": [HumanMessage("今天北京天气如何")]}, config=config)
print(interrupted_res['__interrupt__'])

user_approved = input(interrupted_res['__interrupt__'][0].value["question"]).strip().lower() == 'y'
approved_res = graph.invoke(Command(resume=user_approved), config=config)
for msg in approved_res['messages']: msg.pretty_print()