from langgraph.graph import START,END,StateGraph
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
load_dotenv()
import os

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
checkpointer=InMemorySaver()

graph=StateGraph(ChatState)
graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

chatbot=graph.compile(checkpointer=checkpointer)

# chatbot.invoke()

# for message_chunk,metadata in chatbot.stream(
#     {"messages":[HumanMessage(content="What is receipe to amke pasta?")]},
#     config={"configurable":{"thread_id":"1"}},
#     stream_mode="messages"
# ):
#     if message_chunk.content:
#         print(message_chunk.content,end=" ",flush=True)


# config={"configurable":{"thread_id":"1"}}

# response=chatbot.invoke(
#     {"messages":[HumanMessage(content="Hi")]},
#     config=config
# )

# print(chatbot.get_state(config=config))
# # StateSnapShot object-values attribute-usme messages hain

# print(chatbot.get_state(config=config).values["messages"])

"""
StateSnapshot(values={'messages': [HumanMessage(content='Hi', additional_kwargs={}, response_metadata={}, id='a8724c42-bfdf-4343-bada-f724eef4c083'), AIMessage(content='Hello! How can I help you today?', additional_kwargs={}, response_metadata={'token_usage': {'completion_tokens': 10, 'prompt_tokens': 13, 'total_tokens': 23, 'completion_time': 0.019144477, 'completion_tokens_details': None, 'prompt_time': 0.000599271, 'prompt_tokens_details': None, 'queue_time': 0.044136468, 'total_time': 0.019743748}, 'model_name': 'qwen/qwen3.8-27b', 'system_fingerprint': 'fp_424cb89518', 'service_tier': 'on_demand', 'finish_reason': 'stop', 'logprobs': None, 'model_provider': 'groq'}, id='lc_run--01a138c8-122e-7450-ad7d-9aa454500a42-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 13, 'output_tokens': 10, 'total_tokens': 23})]}, next=(), config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f1c78c1-b11d-6ec4-8001-b75ec6215dd7'}}, metadata={'source': 'loop', 'step': 1, 'parents': {}}, created_at='2026-10-14T04:59:58.870086+00:00', parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f1c78c1-ac67-66d2-8000-0b55a86e54fc'}}, tasks=(), interrupts=())
"""
