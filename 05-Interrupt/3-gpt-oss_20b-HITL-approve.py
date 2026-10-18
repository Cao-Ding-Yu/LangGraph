
from typing import TypedDict, Literal
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph,START,END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama

# human in the loop --审批模式

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(TypedDict):
    topic:str
    poem:str
    is_approved:bool

def approve_node(state:OverAllState) -> Command[Literal["llm_node","default_node"]]:
    is_approved = interrupt("是否同意调用模型?")
    goto = "llm_node" if is_approved else "default_node"
    return Command(
        goto=goto,
        update={"is_approved":is_approved}
    )

def llm_node(state:OverAllState) -> OverAllState:
    topic = state["topic"]
    res = model.invoke([HumanMessage(content=f"写一首关于{topic}主题的七言绝句")]).content
    return {"poem":res}

def default_node(state:OverAllState) -> OverAllState:
    return {"poem":"请求被拒绝"}


builder = StateGraph(OverAllState)
builder.add_node("approve_node",approve_node)
builder.add_node("llm_node",llm_node)
builder.add_node("default_node",default_node)
builder.add_edge(START,"approve_node")
builder.add_edge("llm_node",END)
builder.add_edge("default_node",END)
graph = builder.compile(checkpointer=InMemorySaver())
with open('3-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

# 触发并打印中断
config = {"configurable":{"thread_id":"1"}}
interrupt_res = graph.invoke({"topic":"菊花"},config=config)

# 执行审批
user_approved = input("是否同意调用模型?(y/else)").strip().lower() == 'y'
print(graph.invoke(Command(resume=user_approved),config=config))



