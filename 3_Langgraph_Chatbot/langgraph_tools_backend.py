from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

# pip install langgraph-checkpoint-sqlite
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()
import sqlite3
import requests
from langchain_groq import ChatGroq

# LLM
llm = ChatGroq(
    model="qwen/qwen3.8-27b", api_key=os.getenv("GROQ_API_KEY"), max_tokens=100
)

# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

search_tool = DuckDuckGoSearchRun(region="us-en")  # Note: 'region' not 'regions'


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform basic arithmetic operations on two numbers.
    Supported operations: add, sub, mul, div.
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation in ["div", "divide"]:  # Added 'divide' for safety
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num  # <--- INDENTED CORRECTLY NOW
        else:
            return {"error": f"Unsupported operation '{operation}'"}

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}


# The newer version of the duckduckgo-search library requires the ddgs package, but it wasn't installed automatically.
# pip install -U ddgs duckduckgo-search


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock prices for a given symbol(eg:AAPL,TSLA) using Alpha Vantage with API key in the list
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=BSY6ZFJQFQVO0N8F"
    r = requests.get(url)
    return r.json()


tools = [search_tool, calculator, get_stock_price]

llm_with_tools = llm.bind_tools(tools)


# State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# Nodes
def chat_node(state: ChatState):
    """
    LLLM node that may answer or request a tool call.
    """
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools)

# Checkpointer
conn = sqlite3.connect(database="chatbot1.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# Graph
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")
chatbot = graph.compile(checkpointer=checkpointer)


# Helper
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)


"""
**`checkpointer.list(None)`** fetches the **history of all previous states** (checkpoints) for the conversation, starting from `None` (the beginning).

**One-Line Summary:** *"It retrieves the full saved history (checkpoints) of the graph's execution."* 😊🚀
"""
