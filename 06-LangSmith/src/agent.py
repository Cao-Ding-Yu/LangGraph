from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt

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

graph = builder.compile()