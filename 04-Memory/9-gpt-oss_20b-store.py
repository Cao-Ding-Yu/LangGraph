
import os
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.runtime import Runtime
from typing import Final, Tuple, Literal
from langgraph.store.sqlite import SqliteStore
from langchain_core.messages import SystemMessage,HumanMessage
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import MessagesState

# --------------- 初始数据准备 ---------------

DB = "9-sqlite.db"
USERS_NS: Final[Tuple[str]] = ("users",)
config = {"configurable": {"thread_id": "1"}}

if os.path.exists(DB): os.remove(DB)
with SqliteStore.from_conn_string(DB) as store:
    store.setup()
    # 创建namespace
    namespace1 = (*USERS_NS, "Alice")
    namespace2 = (*USERS_NS, "Bob")
    namespace3 = (*USERS_NS, "Black")
    # 创建key
    PREFERENCES_KEY: Final[str] = "preferences"
    # 创建value
    value1 = {
        "course": "计算机组成原理",
        "sports": "跑步",
        "food": "蒙牛牛奶"
    }
    value2 = {
        "course": "数字电路",
        "sports": "滑雪",
        "food": "糖葫芦"
    }
    value3 = {
        "course": "模拟电路",
        "sports": "羽毛球",
        "food": "伊利酸奶"
    }
    # 写入数据
    store.put(namespace1, PREFERENCES_KEY, value1)
    store.put(namespace2, PREFERENCES_KEY, value2)
    store.put(namespace3, PREFERENCES_KEY, value3)
    # 写入结果查询
    # for item in store.search(USERS_NS): print(item)

# --------------- 长期记忆 ---------------

model = ChatOllama(
    model="gpt-oss:20b",
)

class OverAllState(MessagesState):
    username:str
    user_input:str
    output:str
    preferences:dict[str,str]

# 路由函数，判断是否存有用户长期记忆
def router(state:OverAllState) -> Literal["check_preference_node","llm_node"]:
    if not state.get("preferences"):
        return "check_preference_node"
    return "llm_node"

def check_preference_node(state:OverAllState,runtime:Runtime) -> OverAllState:
    print(f"用户:{state["username"]}")
    namespace = (*USERS_NS, state["username"])
    if runtime.store:
        run_item = runtime.store.get(namespace, PREFERENCES_KEY)
        if run_item:
            print(f"长期记忆中的偏好数据是{run_item.value}")
            return {"preferences":run_item.value}
    print("没有偏好数据")
    return {}

def llm_node(state:OverAllState) -> OverAllState:
    system_prompt = "根据用户偏好解决用户需求"
    human_prompt = f"用户偏好: {state.get("preferences",{})}\n,用户需求:{state["user_input"]}"
    messages = state["messages"] if state.get("messages",[]) else [SystemMessage(content=system_prompt)]
    response = model.invoke(messages + [HumanMessage(content=human_prompt)])
    return {
        "messages":messages+[HumanMessage(content=human_prompt),response],
        "output": response.content,
    }

builder = StateGraph(OverAllState)
builder.add_node("check_preference_node",check_preference_node)
builder.add_node("llm_node",llm_node)
builder.add_conditional_edges(START,router,path_map=["check_preference_node","llm_node"])
builder.add_edge("check_preference_node","llm_node")
builder.add_edge("llm_node",END)

# 构建长期记忆和短期记忆
with SqliteStore.from_conn_string(DB) as store, SqliteSaver.from_conn_string(DB) as checkpointer :
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer, store=store)
    with open('9-graph.png', "wb") as f: f.write(graph.get_graph().draw_mermaid_png())
    print(graph.invoke({"username":"Alice","user_input":"我有点无聊,和我聊聊天吧"},config=config)["messages"][-1].content)
    print(graph.invoke({"username":"Alice","user_input":"推荐一下牛奶"},config=config)["messages"][-1].content)

