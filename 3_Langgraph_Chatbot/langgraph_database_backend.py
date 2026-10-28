# uv init
# uv add langgraph-checkpoint-sqlite
import sqlite3
from langgraph.graph import START,END,StateGraph
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
load_dotenv()
import os

# database if not there then it will be created
conn=sqlite3.connect(database="chatbot.db",check_same_thread=False)
# single thread pe kaam ni karna,diff conversations
# Checkpointer setup
checkpointer=SqliteSaver(conn=conn)

llm=ChatGroq(model="qwen/qwen3.8-27b",api_key=os.getenv("GROQ_API_KEY"),max_tokens=50)

class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    
def chat_node(state:ChatState):
    messages=state["messages"]
    response=llm.invoke(messages)
    return {
        "messages":[response]
    }
    
# Checkpointer
# checkpointer=SqliteSaver(conn=conn)

graph=StateGraph(ChatState)
graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

chatbot=graph.compile(checkpointer=checkpointer)


print(checkpointer.list(None))
# None matlab saaare checkpoint chahiye not particular threaad kae checkpoints bruhh
# kitne threads mojud hain database mai?
# overall checkpoints or thread specific checkpoints
# getting generator object

for checkpoint in checkpointer.list(None):
    print(checkpoint)


# all_threads=set()
# for checkpoint in checkpointer.list(None):
#     print(checkpoint.config["configurable"]["thread_id"])
#     all_threads.add(checkpoint.config["configurable"]["thread_id"])
    
# print(list(all_threads))
    
# test
# config={"configurable":{"thread_id":"1"}}
# config={"configurable":{"thread_id":"2"}}

# response=chatbot.invoke(
#     {"messages":[HumanMessage(content='Hi my name is laxmi')]},
#     config=config
# )

# print(response)

# messages saved in chatbot.db
# saare messages dikh rahe
# threads based store ho rahe h
# sqlite viewer-extension to see chatbot.db
def retrieve_all_threads():
    all_threads=set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
        
    return list(all_threads)