from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama

# human in the loop --编辑模型工作提示词

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(TypedDict):
    topic: str
    poem: str
    reviewed_poem: str

def llm_node(state: OverAllState) -> OverAllState:
    topic = interrupt("主题:")
    poem = model.invoke([HumanMessage(content=f"写一首关于 {topic} 的七言绝句")]).content
    return {
        "topic": topic,
        "poem": poem,
    }

def review_node(state: OverAllState) -> OverAllState:
    reviewed_poem = interrupt("评价生成的七言绝句:")
    return {"reviewed_poem": reviewed_poem}

builder = StateGraph(OverAllState)
builder.add_node("llm_node", llm_node)
builder.add_node("review_node", review_node)
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", "review_node")
builder.add_edge("review_node", END)
graph = builder.compile(checkpointer=InMemorySaver())
with open('4-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

# 原始输出
config = {"configurable": {"thread_id": "1"}}
interrupted_res = graph.invoke({}, config=config)
topic = input(interrupted_res['__interrupt__'][0].value)
res = graph.invoke(Command(resume=topic), config=config)
print(res["poem"])

# 添加审核
user_review = input(res['__interrupt__'][0].value)
reviewed_res = graph.invoke(Command(resume=user_review), config=config)
print(reviewed_res)

