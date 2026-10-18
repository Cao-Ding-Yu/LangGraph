
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

# 单个节点的多次中断：后续中断会从缓存中读取前面中断的值，并非从中断处继续

class OverAllState(TypedDict):
    username: str
    age: int
    gender: Literal["male", "female"]

def get_info_node(state: OverAllState) -> OverAllState:
    username = interrupt("输入用户名：")
    age = interrupt("输入年龄：")
    gender = interrupt("输入性别：")
    return {
        "username": username,
        "age": age,
        "gender": gender
    }

builder = StateGraph(OverAllState)
builder.add_node("get_info_node", get_info_node)
builder.add_edge(START, "get_info_node")
builder.add_edge("get_info_node", END)
graph = builder.compile(checkpointer=InMemorySaver())
with open('6-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

config = {"configurable": {"thread_id": "1"}}
interrupted_1 = graph.invoke({}, config=config)

user_name = input(interrupted_1['__interrupt__'][0].value)
interrupted_2 = graph.invoke(Command(resume=user_name), config=config)

user_age = input(interrupted_2['__interrupt__'][0].value)
interrupted_3 = graph.invoke(Command(resume=int(user_age)), config=config)

user_gender = input(interrupted_3['__interrupt__'][0].value)
res = graph.invoke(Command(resume=user_gender), config=config)
print(res)


