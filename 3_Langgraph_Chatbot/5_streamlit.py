import streamlit as st

# pip install streamlit
from langgraph_tools_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

# random thread id generate

# config={"configurable":{"thread_id":"1"}}


# ********************utility function******************
# for New Chat
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id


# NEW CHAT BUTTON
def reset_chat():
    # generate new thread id
    thread_id = generate_thread_id()
    # save thread id to session state
    st.session_state["thread_id"] = thread_id
    add_thread(st.session_state["thread_id"])
    # reset message history
    st.session_state["message_history"] = []


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    cfg = {"configurable": {"thread_id": thread_id}}
    return chatbot.get_state(config=cfg).values["messages"]


# ***************Session Setup**********************
# page load hote hi

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# dynamic thread id generate and add in st.session_state
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

add_thread(st.session_state["thread_id"])


# config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

# adding thread diff conversation in langsmith although its automatic now shayad
config = {
    "configurable": {"thread_id": st.session_state["thread_id"]},
    "metadata": {"thread_id": st.session_state["thread_id"]},
    "run_name": "chat_turn",
}

# **********************Sidebar UI******************

st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button("New Chat"):
    reset_chat()
st.sidebar.header("My Conversations")

# st.sidebar.text(st.session_state["thread_id"])

for thread_id in st.session_state["chat_threads"][::-1]:
    # st.sidebar.text(thread_id)
    if st.sidebar.button(thread_id):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp_messages.append({"role": role, "content": message})

        st.session_state["message_history"] = temp_messages
        st.rerun()


# *************************Man UI***************
# loading the conversation history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


user_input = st.chat_input("Type here:")
if user_input:

    # first add message to message history
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    # box create of chat_message
    with st.chat_message("user"):
        # display in box
        st.text(user_input)

    with st.chat_message("assistant"):

        # use a mutuable holder so that generator can set and modify it!
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages",
            ):
                # Lazily create and update the SAME status container when tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"Using {tool_name}", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"Using {tool_name}", status="running", expanded=True
                        )

                if isinstance(message_chunk, AIMessage):
                    # yield only assistant tokens
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream)

        # ai_message = st.write_stream(
        #     message_chunk.content
        #     for message_chunk, metadata in chatbot.stream(
        #         {"messages": [HumanMessage(content=user_input)]},
        #         config=config,
        #         stream_mode="messages",
        #     )
        # )

    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )


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

"""
what is 2*2?
{"first_num": 2.0, "second_num": 2.0, "operation": "mul", "result": 4.0}2 × 2 = 4

happening bcoz of  ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages",
            )
        )
        
"""
# status container in chat elements in streamlit
# shows tools finished better ui experience

"""
# Streamlit `st.status` Container – Brief Syntax

**`st.status()`** creates a collapsible, interactive box that shows the progress of a long-running task (like an AI agent using tools). 

### ✅ Basic Syntax
```python
with st.status("Label here", expanded=True) as status:
    st.write("Doing task 1...")
    # ... your code ...
    status.update(label="Task Complete!", state="complete", expanded=False)
```

### 🧩 Key Parameters
| **Parameter** | **What It Does** |
|---------------|------------------|
| **`label`** | The text shown in the box (e.g., "Thinking..."). |
| **`expanded`** | `True` keeps it open; `False` keeps it collapsed. |
| **`state`** | Changes the icon. Options: `"running"` (spinner), `"complete"` (checkmark), `"error"` (cross). |

### 🛠️ Methods
*   **`status.update()`**: Changes the label, state, or expanded status *after* the box is created (perfect for showing tool calls step-by-step).
*   **`status.write()`**: Writes text inside the box.

**One-Line Summary:** *"Use `with st.status()` to create a live progress box, and `.update()` to change its label/state as your AI agent works."* 😊🚀
"""
