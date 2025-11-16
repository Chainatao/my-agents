from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from IPython.display import Image, display
import gradio as gr
from langgraph.prebuilt import ToolNode, tools_condition
import requests
import os
from langchain.tools import tool
import asyncio
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv(override=True)

class State(TypedDict):
    
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


telegram_token = os.getenv("TELEGRAM_NOTIFICATIONS_TOKEN")
chat_id = os.getenv("TELEGRAM_NOTIFICATIONS_CHAT_ID")

def push(text: str):
    """Send a push notification to the user"""
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    response = requests.post(
        url=url,
        params={'chat_id': chat_id, 'text': f'{text}', 'parse_mode': 'Markdown'}
    )

@tool('send_push_notification')
def tool_push(message: str):
    """Useful for when you want to send a push notification.

    Keyword arguments:
    message -- The message to send.
    """
    return push(message)


# Introducing nest_asyncio
# Python async code only allows for one "event loop" processing aynchronous events.
# The `nest_asyncio` library patches this, and is used for special situations, if you need to run a nested event loop.

import nest_asyncio
nest_asyncio.apply()

from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser

# If you get a NotImplementedError here or later, see the Heads Up at the top of the notebook
async def main():
    async_browser =  create_async_playwright_browser(headless=False)  # headful mode
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
    tools = toolkit.get_tools()

    for tool in tools:
        print(f"{tool.name}={tool}")

    tool_dict = {tool.name:tool for tool in tools}

    navigate_tool = tool_dict.get("navigate_browser")
    extract_text_tool = tool_dict.get("extract_text")

        
    await navigate_tool.arun({"url": "https://www.cnn.com"})
    text = await extract_text_tool.arun({})

    import textwrap
    print(textwrap.fill(text))

    all_tools = tools + [tool_push]

    
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(all_tools)


    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools=all_tools))
    graph_builder.add_conditional_edges( "chatbot", tools_condition, "tools")
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    display(Image(graph.get_graph().draw_mermaid_png()))

    config = {"configurable": {"thread_id": "10"}}

    async def chat(user_input: str, history):
        result = await graph.ainvoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
        return result["messages"][-1].content


    gr.ChatInterface(chat, type="messages").launch()

asyncio.run(main())