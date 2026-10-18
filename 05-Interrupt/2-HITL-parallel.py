
from time import sleep
from typing import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

# human in the loop --parallel

class OverAllState(TypedDict):
    username:str
    age:int

def node_a(state:OverAllState) -> OverAllState:
    username = interrupt("输入姓名:")
    return {"username":username}

def node_b(state:OverAllState) -> OverAllState:
    sleep(1)
    age = interrupt("输入年龄:")
    return {"age":age}


builder = StateGraph(OverAllState)
builder.add_node("node_a",node_a)
builder.add_node("node_b",node_b)
builder.add_edge(START,"node_a")
builder.add_edge(START,"node_b")
builder.add_edge("node_a",END)
builder.add_edge("node_b",END)
graph = builder.compile(checkpointer = InMemorySaver())
with open('2-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

# 触发与查看 interrupt
config = {"configurable":{"thread_id":"1"}}
interrupt_res = graph.invoke({},config=config)
print(interrupt_res)

# 回复执行
resume_map = dict()
for i in interrupt_res['__interrupt__']:
    user_input = input(f"{i.value}")
    resume_map[i.id] = user_input
print(graph.invoke(Command(resume=resume_map),config=config))

