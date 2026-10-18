
from operator import add
from langgraph.types import Send
from typing import TypedDict, Annotated, Sequence
from langgraph.constants import START,END
from langgraph.graph import StateGraph

class OverAllState(TypedDict):
    input_texts: list[str]      # 待处理数据
    entries: Annotated[list[tuple[str,int]],add]  # list(tuple[text,1])
    word_counts: dict[str,int]   # 词频统计结果

class InputState(TypedDict):
    input_texts: list[str]

class SplitState(TypedDict):
    input_text: str

class EntryState(TypedDict):
    entries: Annotated[list[tuple[str,int]],add]

class OutputState(TypedDict):
    word_counts: dict[str,int]

# 将每一条文本分发给一个mapper_node
def router_node(state:InputState)-> Sequence[Send]:
    task = list()
    for text in state["input_texts"]:
        task.append(Send("mapper_node",{"input_text":text}))
    return task

# 按空格切分文本中的单词，拼接成元组列表
def mapper_node(state:SplitState) -> EntryState:
    entries = list()
    words = state["input_text"].split(" ")
    for word in words: entries.append((word,1))
    return {"entries":entries}

# 聚合各mapper_node返回的元组列表
def reducer_node(state:OverAllState) -> OutputState:
    shuffle_dict = dict()   # {word:[1,1,1]}
    reduce_dict = dict()    # {word:3}
    for k,v in state["entries"]:
        if k not in shuffle_dict: shuffle_dict[k] = [v]
        else: shuffle_dict[k].append(v)
    for k,v in shuffle_dict.items():
        reduce_dict[k] = sum(v)
    return {"word_counts":reduce_dict}

builder = StateGraph(
    state_schema=OverAllState,
    input_schema=InputState,
    output_schema=OutputState,
)
builder.add_node("mapper_node",mapper_node)
builder.add_node("reducer_node",reducer_node)
builder.add_conditional_edges(START,router_node,path_map=["mapper_node"])
builder.add_edge("mapper_node","reducer_node")
builder.add_edge("reducer_node",END)
graph = builder.compile()

print(graph.invoke({"input_texts":["hello world","hello cdy","hello llm","hello agent"]}))

png_bytes = graph.get_graph().draw_mermaid_png()
with open('10-graph.png', "wb") as f:
    f.write(png_bytes)

