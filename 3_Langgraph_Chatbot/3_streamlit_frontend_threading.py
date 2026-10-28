import streamlit as st
# pip install streamlit
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid
# random thread id generate

# config={"configurable":{"thread_id":"1"}}

# ********************utility function******************
# for New Chat
def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id

# NEW CHAT BUTTON
def reset_chat():
    # generate new thread id
    thread_id=generate_thread_id()
    # save thread id to session state
    st.session_state["thread_id"]=thread_id
    add_thread(st.session_state["thread_id"])
    # reset message history
    st.session_state["message_history"]=[]
    
def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)
        

def load_conversation(thread_id):
    return chatbot.get_state(config=config).values["messages"]
    
# ***************Session Setup**********************
# page load hote hi

if "message_history" not in st.session_state:
    st.session_state["message_history"]=[]
    
# dynamic thread id generate and add in st.session_state
if 'thread_id' not in st.session_state:
    st.session_state["thread_id"]=generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state["chat_threads"]=[]

add_thread(st.session_state["thread_id"])
    
    
config={"configurable":{"thread_id":st.session_state["thread_id"]}}
    
# **********************Sidebar UI******************
    
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button("New Chat"):
    reset_chat()
st.sidebar.header("My Conversations")

# st.sidebar.text(st.session_state["thread_id"])

for thread_id in st.session_state["chat_threads"][::-1]:
    # st.sidebar.text(thread_id)
    if st.sidebar.button(thread_id):
        st.session_state["thread_id"]=thread_id
        messages=load_conversation(thread_id)
        
        temp_messages=[]
        
        for message in messages:
            if isinstance(message,HumanMessage):
                role='user'
            else:
                role='assistant'
        temp_messages.append({'role':role,'content':message})
        
        st.session_state["message_history"]=temp_messages
    

# *************************Man UI***************
# loading the conversation history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])
        


user_input=st.chat_input("Type here:")
if user_input:
    
    # first add message to message history
    st.session_state["message_history"].append({"role":"user","content":user_input})
    # box create of chat_message
    with st.chat_message("user"):
        # display in box
        st.text(user_input)
        
    
    with st.chat_message("assistant"):
        
        ai_message=st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
                {"messages":[HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages"
            )
        )
        
    st.session_state["message_history"].append({"role":"assistant","content":ai_message})


# """
# sidebar title,button,title
# dynamic threads create and add to session
# display thread in sidebar
# *********************
# on clicking new chat feature,
# 1.generate dynamic thread id
# 2.save it to session
# 3.reset message history
# ***********************************
# 1.create a list of thread ids
# 2.Load all the thread ids in the sidebar
# 3.convert side bar text to clickable links
# ********************************************

# """
