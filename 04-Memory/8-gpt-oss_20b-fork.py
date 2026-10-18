
from langchain_ollama import ChatOllama
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph,START,END

class OverAllState(TypedDict):
    user_input: str
    output: str

class StructuredOutputState(TypedDict):
    topic: Annotated[str,"创作主题"]
    mode: Annotated[Literal["poem","joke"],"创作类型"]

model = ChatOllama(
    model="gpt-oss:20b",
).with_structured_output(schema=StructuredOutputState)

def router_node(state:OverAllState) -> StructuredOutputState:
    return model.invoke([HumanMessage(state["user_input"])])

def router(state:StructuredOutputState) -> Literal["node_poem","node_joke","node_default"]:
    if state["mode"] == "poem": return "node_poem"
    elif state["mode"] == "joke": return "node_joke"
    return "node_default"

def node_poem(state:StructuredOutputState) -> OverAllState:
    poem = model.invoke([HumanMessage(f"写一首关于{state["topic"]}主题的七言绝句").content])
    return {"output":poem}

def node_joke(state:StructuredOutputState) -> OverAllState:
    joke = model.invoke([HumanMessage(f"写一首关于{state["topic"]}主题的笑话").content])
    return {"output":joke}

def node_default(state:StructuredOutputState) -> OverAllState:
    return {"output":"无法处理的任务类型"}

builder = StateGraph(OverAllState)
builder.add_node("router_node",router_node)
builder.add_node("node_poem",node_poem)
builder.add_node("node_joke",node_joke)
builder.add_node("node_default",node_default)
builder.add_edge(START,"router_node")
builder.add_conditional_edges("router_node",router,path_map=["node_poem","node_joke","node_default"])
builder.add_edge("node_poem",END)
builder.add_edge("node_joke",END)
builder.add_edge("node_default",END)
graph = builder.compile(checkpointer=InMemorySaver())
with open('8-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())

config={"configurable":{"thread_id":"1"}}

print(graph.invoke(input={"user_input":"写一个关于小猫的诗"}, config=config))

# 方法1：修改父节点状态config
target_checkpoint = next(h for h in list(graph.get_state_history(config=config)) if h.next == ('router_node',))
start_config = graph.update_state(
    config=target_checkpoint.config,
    values={"user_input":"帮我写一个大狗的诗"},
    as_node=START
)
print(graph.invoke(None,config=start_config))

# 方法2：修改节点本身状态config
router_config = graph.update_state(
    config=target_checkpoint.config,
    values={"topic":"荷花","mode":"joke"},
    as_node="router_node"
)
print(graph.invoke(None,config=router_config))


