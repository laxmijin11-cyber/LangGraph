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

load_dotenv()
import os
llm=ChatGroq(model="qwen/qwen3.8-27b",max_tokens=50,api_key=os.getenv("GROQ_API_KEY"))

@tool
def calculator(first_num: float, second_num: float, operation: str) -> str:
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
        return f"The result of {operation} is {result}"
    except Exception as e:
        return {"error": str(e)}
            
# MCP CLIENT WORKS WITH ASYNCHRONOUS CODE
            
tools=[calculator]
llm_with_tools=llm.bind_tools(tools)

# state
class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    
def build_graph():
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
    chatbot=build_graph()
    result=await chatbot.ainvoke({"messages":HumanMessage(content="Find the modulus of 123456 and give aswer like cricket commentator")})
    print(result["messages"][-1].content)
    
if __name__=='__main__':
    asyncio.run(main())