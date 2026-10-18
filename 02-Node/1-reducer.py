
from langchain.messages import  SystemMessage,HumanMessage,AIMessage
from langgraph.graph.message import add_messages

# 原来有多少钱
left = [
    SystemMessage(content="你是一个专业的翻译",id = '1'),
    HumanMessage(content="你好",id = '2'),
    AIMessage(content="你好，我是专业的翻译",id = '3'),
    HumanMessage(content="你是谁?",id = '4'),
]

# 近期账单
right = [
    HumanMessage(content="我是老王,你是小王",id = '2'),
    AIMessage(content="好的我记住了",id = '3'),
    AIMessage(content="我是小王",id = '5'),
    HumanMessage(content="你是小王吗?",id = '1'),
]

# 现在有多少钱
merged = add_messages(left,right)
print(merged)