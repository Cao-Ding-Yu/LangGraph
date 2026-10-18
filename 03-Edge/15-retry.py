
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from requests import HTTPError

class EmptyState(TypedDict):
    pass

def node(state:EmptyState) -> EmptyState:
    print("node 正在运行")
    raise HTTPError

builder = StateGraph(EmptyState)
builder.add_node(
    node,
    retry_policy=RetryPolicy(
        # 以下参数皆为可选配置
        max_attempts=5,  # 最大重试次数
        initial_interval=0.5,  # 首次重试时间间隔
        backoff_factor=2.0,  # 重试时间增长倍数
        max_interval=128.0,  # 单次最大等待时间
        jitter=False,  # 是否添加随机抖动
        retry_on=[HTTPError], # 设置触发重试的错误种类
    )
)

builder.add_edge(START,"node")
builder.add_edge("node",END)
graph = builder.compile()

try: graph.invoke({})
except HTTPError as e:
    print("重试次数耗尽")

png_bytes = graph.get_graph().draw_mermaid_png()
with open('15-graph.png', "wb") as f:
    f.write(png_bytes)

