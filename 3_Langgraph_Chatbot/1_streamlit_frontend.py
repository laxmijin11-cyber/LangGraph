import streamlit as st
# pip install streamlit
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

config={"configurable":{"thread_id":"1"}}
# reset when enter press->dictionary reset ho rahi every time
# message_history=[]

# aisi dictionery jo enter press karne pe reset naa hoti jab tak khud page reset naa karo or start a new conversation naa karo
# st.session_state->dict
if "message_history" not in st.session_state:
    st.session_state["message_history"]=[]

# loading the conversation history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

# message history--->current user msg-->assistant msg

# loading the conversation history
# for message in message_history:
#     with st.chat_message(message["role"]):
#         st.text(message["content"])



# {"role":"user","content":"Hi"}
# {"role":"assistant","content":"Hi-ello"}

# with st.chat_message("user"):
#     st.text("Hi")
    
# with st.chat_message("assistant"):
#     st.text("Hey! How can I help you?")
    
# with st.chat_message("user"):
#     st.text("My name is Laxmi")
    
user_input=st.chat_input("Type here:")
if user_input:
    
    # first add message to message history
    st.session_state["message_history"].append({"role":"user","content":user_input})
    # box create of chat_message
    with st.chat_message("user"):
        # display in box
        st.text(user_input)
        
        
    response=chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config=config)
    ai_message=response["messages"][-1].content
        
    st.session_state["message_history"].append({"role":"assistant","content":ai_message})
    with st.chat_message("assistant"):
        st.text(ai_message)
        
# every enter press,script re execute hogi!
# purana conversation history delete ho raha

# if i will not add config it will forget prev ques ans?
# **Yes — without `config={"configurable":{"thread_id":"1"}}`, the chatbot will forget all previous messages** because LangGraph won't know which conversation thread to load the memory from.

# Without `thread_id`, each `invoke()` call starts fresh — no checkpointer memory is retrieved.