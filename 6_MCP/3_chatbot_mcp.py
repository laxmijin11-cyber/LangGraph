from langgraph.graph import START,END,StateGraph
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.tools import tool
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
# pip install langchain-mcp-adapters
load_dotenv()
import os
llm=ChatGroq(model="qwen/qwen3.8-27b",max_tokens=50,api_key=os.getenv("GROQ_API_KEY"))

# MCP CLIENT FOR LOCAL FASTMCP SERVER
client=MultiServerMCPClient(
    {
        "arith":{
            "transport":"stdio",
            "command":"python3",
            "args":[r"\users\admin\OneDrive\Desktop\New folder\LangGraph\6_MCP\4_main.py"]
        },
        "expense":{
            "transport":"streamable_http",
            "url":"https://splendid-gold.dingo.fastmcp.app/mcp"
        }
    }
)


# state
class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    
async def build_graph():
    
    tools=await client.get_tools()
    print(tools)
    
    llm_with_tools=llm.bind_tools(tools)
    # nodes
    async def chat_node(state:ChatState):
        messages=state["messages"]
        response=await llm_with_tools.ainvoke(messages)
        return {"messages":[response]}

    tool_node=ToolNode(tools)
    # defining graph and nodes
    graph=StateGraph(ChatState)
    graph.add_node("chat_node",chat_node)
    graph.add_node("tools",tool_node)
    # defining graph connect
    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge("tools","chat_node")

    chatbot=graph.compile() 
    return chatbot

async def main():
    chatbot=await build_graph()
    # result=await chatbot.ainvoke({"messages":HumanMessage(content="Find the modulus of 123456 and give aswer like cricket commentator")})
    # result=await chatbot.ainvoke({"messages":HumanMessage(content="Add an expense of udemy course on 10th Nov")})
    result=await chatbot.ainvoke({"messages":HumanMessage(content="Add an expense of udemy course from 1st nov to 30th Nov")})
    print(result["messages"][-1].content)
    
if __name__=='__main__':
    asyncio.run(main())
    
"""
- **`async`**: A Python keyword that tells the system a function can be paused and resumed later, allowing other tasks to run in the meantime without freezing the program.
- **`await`**: A keyword used inside an `async` function that pauses execution until a slow task (like a network request) finishes, freeing up the system to do other work.
- **`ainvoke`**: The asynchronous version of "invoke" (used in LangChain) that runs an AI model or tool in the background so your app doesn't freeze while waiting for the response.
"""
