
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

# human in the loop

class OverAllState(TypedDict):
    username:str

def node_a(state:OverAllState)->OverAllState:
    username = interrupt("输入姓名:")
    return {"username":username}

builder = StateGraph(OverAllState)
builder.add_node("node_a",node_a)
builder.add_edge(START,"node_a")
builder.add_edge("node_a",END)
graph = builder.compile(checkpointer=InMemorySaver())
with open('1-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

# 触发并打印 interrupt
# {'__interrupt__': [Interrupt(value='输入姓名:', id='xxx', response_schema=None)]}
config = {"configurable":{"thread_id":"1"}}
interrupt_res = graph.invoke({},config=config)
print(interrupt_res['__interrupt__'][0].value, end="")

resume_res = graph.invoke(Command(resume=input()),config=config)
print(resume_res)

