from typing import TypedDict, Literal
from langchain_core.runnables import RunnableConfig
from langgraph.managed import RemainingSteps
from langgraph.graph import StateGraph,START,END

class OverAllState(TypedDict):
    # RemainingSteps是框架根据recursion_limit自动计算的剩余步数,逐步递减。
    remaining_steps: RemainingSteps

def loop_node(state:OverAllState,config:RunnableConfig) -> OverAllState:
    cur_step = config["metadata"]["langgraph_step"]
    remaining_steps = state["remaining_steps"]
    print(f"cur_step:{cur_step},remaining_step:{remaining_steps}")

def router(state:OverAllState) -> Literal["loop_node", "__end__"]:
    remaining_steps = state["remaining_steps"]
    if remaining_steps < 3:
        print(f"当前可用超步:{remaining_steps},已不足3步,终止循环")
        return END
    return "loop_node"

builder = StateGraph(OverAllState)
builder.add_node("loop_node",loop_node)
builder.add_edge(START,"loop_node")
builder.add_conditional_edges("loop_node",router)
graph = builder.compile()

graph.invoke({},config={"recursion_limit": 10})

png_bytes = graph.get_graph().draw_mermaid_png()
with open('13-graph.png', "wb") as f:
    f.write(png_bytes)