
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_ollama import ChatOllama

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(MessagesState):
    output: str

def llm_mode(state:OverAllState) -> OverAllState:
    res = model.invoke(state["messages"])
    return {"messages":[res]}

def output_node(state:OverAllState) -> OverAllState:
    return {"output":state["messages"][-1].content}

builder = StateGraph(OverAllState)
builder.add_node("llm_node",llm_mode)
builder.add_node("output_node",output_node)
builder.add_edge(START,"llm_node")
builder.add_edge("llm_node","output_node")
builder.add_edge("output_node",END)

graph = builder.compile(checkpointer=InMemorySaver())

config = {
    "configurable":{
        "thread_id":"1"
    }
}

# 检查点模式：
#   exit: 只有当正常退出，异常退出，被中断时记录检查点，开销最小，容灾能力最低
#   async: 默认，异步模式，在每个超步后，下一节点运行与检查点记录同时开始，较为均衡
#   sync: 同步模式，在每个超步后，完成检查点记录后再开始下一超步，容灾能力最强，但引入响应延迟
result = graph.invoke(
    {"messages":[HumanMessage("1+1=?")]},
    config=config,
    durability="async", # 检查点模式
)
print(result)

png_bytes = graph.get_graph().draw_mermaid_png()
with open('3-graph.png', "wb") as f:
    f.write(png_bytes)

