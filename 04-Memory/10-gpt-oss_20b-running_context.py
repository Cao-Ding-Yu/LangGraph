
from dataclasses import dataclass
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph,START,END
from langgraph.runtime import Runtime
from langgraph.graph.message import MessagesState
from langchain_ollama import ChatOllama

model = ChatOllama(
    model="gpt-oss:20b",
)

@dataclass
class UserContext:
    username: str
    level: str

class OverAllState(MessagesState):
    user_input: str
    output: str

def llm_node(state:OverAllState,runtime:Runtime[UserContext]) -> OverAllState:
    system_prompt = f"你是普通客户助理,友好简洁回复问题"
    context = runtime.context
    if context:
        level = context.level
        username = context.username
        print(f"当前用户:{username},会员等级:{level}")
        if level == "VIP": system_prompt = f"你是高级客户助理,当前VIP用户是{username},请使用尊称'您',回复末尾加上'VIP🏅服务'"
    messages = [SystemMessage(content=system_prompt)] + [HumanMessage(content=state["user_input"])]
    response = model.invoke(messages)
    return {
        "messages": messages + [response],
        "output": response.content,
    }

builder = StateGraph(
    state_schema=OverAllState,
    context_schema=UserContext,
)
builder.add_node("llm_node",llm_node)
builder.add_edge(START,"llm_node")
builder.add_edge("llm_node",END)
graph = builder.compile()

with open('10-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

res = graph.invoke(
    {"user_input":"帮我查一下最近的优惠活动"},
    context=UserContext(username="Alice", level="VIP")
)['output']
print(res)

res = graph.invoke(
    {"user_input":"帮我查一下最近的优惠活动"},
    context=UserContext(username="Alice", level="普通用户")
)['output']
print(res)


