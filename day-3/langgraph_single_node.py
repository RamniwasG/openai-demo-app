# In this project we will build an AI travel agent that can perform web searches, find popular attractions, 
# check whether conditions and search for flights and hotels using LangGraph.

#  install necessary libraries
#  pip install langchain langgraph langchain_openai tavily-python amadeus python-dotenv gradio langchain_community graphviz


import os
import uuid
import getpass
from typing import List, Dict, TypedDict, Annotated, Tuple, Optional, Any, Union, Literal
from datetime import datetime
from IPython.display import Markdown, display, Image
from graphviz import Source
from dotenv import load_dotenv

# langchain specific imports
from langchain_core import messages
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, SystemMessage
from langchain.tools import tool
from pydantic import BaseModel

# langgraph specific imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from IPython.display import Markdown, display

# gradio imports
import gradio as gr

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
model = os.getenv("MODEL", "gpt-5.2")

def print_markdown(text: str):
    display(Markdown(text))

# Example usage:
# print_markdown("# Hello World\nThis is a markdown message.")
def render_display(text: str, type: str = "rich"):
    if type == "markdown":
        print_markdown(text)
    elif type == "rich":
        try:
            from rich import print
            from rich.markdown import Markdown
            print(Markdown(text))
        except ImportError:
            print(text)
    else:
        print(text)

# render_display(f"### Using model: {model}")
# render_display(f"### Using OpenAI API Key: {api_key if api_key else 'No'}")
# render_display(f"### Using Tavily API Key: {tavily_api_key if tavily_api_key else 'No'}")

# ---------------------------------------------
# lets define the state of our agent at any point in time. This will help us keep track of the information we have gathered and the actions we have taken.
# lets define a state that contains two information: the input text from the user and a summary of the information we have gathered so far. This will help us keep track of our progress and make informed decisions about our next steps.
# store is like a container that stores and passes between different parts of our workflow
# Each node recieves and returns a state object, and a state can includes messages, variables, and memory etc
class AgentState(TypedDict):
    input_text: str
    summary: str


# ---------------------------------------------
# Lets define the key node, which represents the function that perform specific tasks. Each node will have a name, a description, and a function that takes in the current state and returns an updated state. This will allow us to modularize our code and make it easier to understand and maintain.
# Each node will represent a specific action or task that the agent can perform, such as searching the web, finding popular attractions, checking weather conditions, searching for flights and hotels etc. The function
# associated with each node will take in the current state of the agent, perform the necessary actions, and return an updated state with the new information gathered. This will allow us to build a workflow where the agent can make informed decisions based on the information it has gathered so far and determine the next steps to take in order to achieve its goal of planning a trip for the user.
def summarize_step(state: AgentState) -> AgentState:
    # This is where we will implement the logic to summarize the information we have gathered so far. For now, we will just return the input text as the summary.
    llm = ChatOpenAI(model=model, temperature=0.7, openai_api_key=api_key)
    prompt = f"Summarize the following information: {state['input_text']}"

    result = llm.invoke(prompt)
    # messages = [
    #     SystemMessage(content="You are a helpful assistant that summarizes information."),
    #     HumanMessage(content=f"Summarize the following information: {state['input_text']}")
    # ]
    # response = llm(messages)
    
    state["summary"] = result.content

    return state

# Lets define a state graph which is fundamental building block of langgraph
# it manage the flow of information between different nodes/components
# it manage the state throughout the execution of your workflow 

workflow = StateGraph(AgentState)

workflow.add_node("summarize", summarize_step)

workflow.add_edge("translate", END)

workflow.set_entry_point("summarize")

graph = workflow.compile()

text = """
    Electric cars are becoming increasingly popular as the world looks for cleaner and more sustainable transportation options. Unlike traditional gasoline vehicles, 
    electric cars run on electricity stored in rechargeable batteries. This helps reduce air pollution and greenhouse gas emissions, which contribute to climate change. 
    Many governments are encouraging the use of electric vehicles by offering incentives such as tax benefits and subsidies. Additionally, advancements in battery 
    technology are improving driving range and reducing charging time. However, challenges remain, including the availability of charging infrastructure and the higher 
    upfront cost of electric vehicles. As technology continues to evolve, electric cars are expected to play a major role in the future of transportation.
"""

initial_state = {
    "input_text": text,
    "summary": ""
}

print("Summarizing, Please wait... \n")

result = graph.invoke(initial_state)

summary = result["summary"]

render_display(f"### Summary: \n{summary}")
