
# for message_chunk,metadata in chatbot.stream(
#     {"messages":[HumanMessage(content="What is receipe to amke pasta?")]},
#     config={"configurable":{"thread_id":"1"}},
#     stream_mode="messages"
# ):
#     if message_chunk.content:
#         print(message_chunk.content,end=" ",flush=True)


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
        
        
    # response=chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config=config)
    # ai_message=response["messages"][-1].content
        
    # st.session_state["message_history"].append({"role":"assistant","content":ai_message})
    
    with st.chat_message("assistant"):
        
        ai_message=st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
                {"messages":[HumanMessage(content=user_input)]},
                config={
                    "configurable":{"thread_id":"2"}
                },
                stream_mode="messages"
            )
        )
        
    st.session_state["message_history"].append({"role":"assistant","content":ai_message})
    
    
    

# """

# 1. `chatbot.stream(...)` — streams the response token-by-token instead of waiting for the full answer.
# 2. `{"messages":[HumanMessage(content="...")]}` — sends your question as input to the graph.
# 3. `config={"configurable":{"thread_id":"1"}}` — attaches a thread ID so the chatbot remembers this conversation.
# 4. `stream_mode="messages"` — tells LangGraph to yield each message chunk (token) as it's generated.
# 5. `if message_chunk.content: print(...)` — prints each non-empty token immediately, giving a live typing effect.

# **`flush=True`** → forces Python to print immediately (without waiting for buffer to fill).
# **`end=" "`** → replaces the default newline `\n` after each print with a space, so tokens appear on the same line.

# ---

# **Other `stream_mode` values:**

# | Mode | What it yields |
# |------|----------------|
# | `"values"` | Full state after each step |
# | `"updates"` | Only the changed parts after each node |
# | `"messages"` | `(token_chunk, metadata)` tuples — for LLM streaming |
# | `"custom"` | Whatever you emit manually via `get_stream_writer()` |
# | `"debug"` | All internal events (verbose) |

# ---

# **Generator?**
# Yes — `chatbot.stream(...)` returns a **generator**. That's why you can loop over it with `for`. It yields items **one at a time** as they're produced, instead of computing everything upfront.

# **Brief:**
# > It's a lazy iterator — each `next()` call runs the graph until the next token is ready, then pauses. Memory-efficient and enables real-time streaming.
# """
