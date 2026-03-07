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
    translation_summary: str
    sentiment: str


# ---------------------------------------------
# Lets define the key node, which represents the function that perform specific tasks. Each node will have a name, a description, and a function that takes in the current state and returns an updated state. This will allow us to modularize our code and make it easier to understand and maintain.
# Each node will represent a specific action or task that the agent can perform, such as searching the web, finding popular attractions, checking weather conditions, searching for flights and hotels etc. The function
# associated with each node will take in the current state of the agent, perform the necessary actions, and return an updated state with the new information gathered. This will allow us to build a workflow where the agent can make informed decisions based on the information it has gathered so far and determine the next steps to take in order to achieve its goal of planning a trip for the user.
def summarize_step(state: AgentState) -> AgentState:
    print("Summarizing, Please wait... \n")
    
    llm = ChatOpenAI(model=model, temperature=0.7, openai_api_key=api_key)
    prompt = f"Summarize the following information: {state['input_text']}"

    result = llm.invoke(prompt)
    # messages = [
    #     SystemMessage(content="You are a helpful assistant that summarizes information."),
    #     HumanMessage(content=f"Summarize the following information: {state['input_text']}")
    # ]
    # response = llm(messages)
    
    state["summary"] = result.content

    return {
        **state,
        "summary": result.content
    }

def translate_step(state: AgentState) -> AgentState:
    print("Translating, Please wait... \n")

    llm = ChatOpenAI(model=model, temperature=0.7, openai_api_key=api_key)
    prompt = f"Translate the following information from English to Hindi: {state['input_text']}"

    result = llm.invoke(prompt)

    state["translation_summary"] = result.content

    return {
        **state, # **state is used to unpack the existing key-value pairs in the state dictionary and include them in the new dictionary that we are returning. 
        "translation_summary": result.content
    }


def sentiment_step(state: AgentState) -> AgentState:
    print("Analyzing sentiment, Please wait... \n")

    llm = ChatOpenAI(model=model, temperature=0.7, openai_api_key=api_key)
    prompt = f"Analyze the sentiment of the following text: {state['input_text']}"

    result = llm.invoke(prompt)

    state["sentiment"] = result.content.strip()

    return {
        **state, # **state is used to unpack the existing key-value pairs in the state dictionary and include them in the new dictionary that we are returning. 
        "sentiment": result.content
    }


# Lets define a state graph which is fundamental building block of langgraph
# it manage the flow of information between different nodes/components
# it manage the state throughout the execution of your workflow 

# WORKFLOW: summarize -> translate -> sentiment -> END

workflow = StateGraph(AgentState)

workflow.add_node("summarize", summarize_step)
workflow.add_node("translate", translate_step)
workflow.add_node("analyse_sentiment", sentiment_step)

workflow.add_edge("summarize", "translate")
workflow.add_edge("translate", "analyse_sentiment")

# workflow.add_edge("translate", END) # used when only one node exists

workflow.set_entry_point("summarize")

graph = workflow.compile()

text = """
    Electric cars are becoming increasingly popular as the world looks for cleaner and more sustainable transportation options. Unlike traditional gasoline vehicles, 
    electric cars run on electricity stored in rechargeable batteries. This helps reduce air pollution and greenhouse gas emissions, which contribute to climate change. 
    Many governments are encouraging the use of electric vehicles by offering incentives such as tax benefits and subsidies. Additionally, advancements in battery 
    technology are improving driving range and reducing charging time. However, challenges remain, including the availability of charging infrastructure and the higher 
    upfront cost of electric vehicles. As technology continues to evolve, electric cars are expected to play a major role in the future of transportation.
"""

long_text = """
    Electric cars, also known as electric vehicles (EVs), are automobiles that are powered entirely or partially by electricity instead of traditional fossil fuels such as gasoline or diesel. Over the past decade, electric vehicles have gained significant attention as governments, companies, and consumers seek more sustainable and environmentally friendly transportation solutions. The growing concerns about climate change, rising fuel prices, and air pollution in major cities have accelerated the shift toward electric mobility.

    One of the main advantages of electric cars is their ability to reduce greenhouse gas emissions. Traditional internal combustion engine vehicles burn fossil fuels, which release carbon dioxide and other harmful pollutants into the atmosphere. Electric cars, on the other hand, produce zero tailpipe emissions. This makes them an attractive option for reducing air pollution in urban areas and lowering the overall carbon footprint of transportation systems. However, the environmental benefits of electric vehicles also depend on how the electricity used to charge them is generated. If the electricity comes from renewable sources such as solar, wind, or hydropower, the environmental impact is significantly lower.

    Technological advancements have played a major role in the growth of electric vehicles. Improvements in lithium-ion battery technology have increased the driving range of electric cars while reducing battery costs. Early electric vehicles often struggled with limited range and long charging times, which made them less convenient for consumers. Modern EVs can now travel hundreds of kilometers on a single charge, and fast-charging stations can recharge batteries much more quickly than before. Some manufacturers are also exploring solid-state batteries, which promise even higher energy density and improved safety.

    Another factor contributing to the rise of electric vehicles is government support. Many countries have introduced policies to encourage EV adoption, including tax credits, purchase subsidies, and incentives for installing charging infrastructure. Some governments have also announced plans to phase out the sale of new gasoline and diesel vehicles in the coming decades. These policies aim to accelerate the transition toward cleaner transportation systems and reduce dependence on fossil fuels.

    Despite their advantages, electric vehicles still face several challenges. One of the most significant barriers is the availability of charging infrastructure. In many regions, charging stations are not yet widespread, which can make long-distance travel difficult for EV owners. Additionally, the upfront cost of electric vehicles can be higher than that of traditional cars, although lower operating and maintenance costs can offset this difference over time. Battery production and disposal also raise environmental and ethical concerns, particularly regarding the mining of raw materials such as lithium, cobalt, and nickel.

    Automobile manufacturers around the world are investing heavily in electric vehicle development. Major companies are launching new EV models across different price ranges and vehicle categories, including sedans, SUVs, and trucks. At the same time, new companies focused entirely on electric mobility are entering the market and driving innovation. Competition in the EV market is pushing manufacturers to improve performance, reduce costs, and develop better battery technologies.

    The future of transportation is likely to include a large share of electric vehicles. As charging infrastructure expands, battery technology improves, and production scales increase, electric cars are expected to become more affordable and convenient for consumers. In combination with renewable energy and smart grid technologies, electric vehicles could play a crucial role in creating a cleaner, more sustainable transportation ecosystem for the coming decades.
"""

summary_text = """
    Mahendra Singh Dhoni, popularly known as MS Dhoni, is one of the most successful and respected cricketers in the history of Indian cricket. Born on July 7, 1981, in Ranchi, Dhoni is widely recognized for his calm leadership, exceptional wicket-keeping skills, and powerful finishing ability as a batsman.

    Dhoni made his international debut for India national cricket team in 2004 and quickly rose to prominence with his aggressive batting style. In 2007, he was appointed captain of the Indian T20 team and led India to victory in the inaugural ICC Men’s T20 World Cup 2007. Under his leadership, India also won the ICC Cricket World Cup 2011, where Dhoni famously hit the winning six in the final, and the ICC Champions Trophy 2013.

    Known for his composed personality and strategic thinking, Dhoni earned the nickname “Captain Cool.” He is considered one of the greatest finishers in limited-overs cricket and has played many match-winning innings for India. Apart from international cricket, he has been the long-time captain of Chennai Super Kings in the Indian Premier League, leading the team to multiple championship titles.

    Dhoni retired from international cricket in 2020, but his legacy continues to inspire millions of cricket fans and aspiring players around the world. His leadership, humility, and consistency have made him one of the most iconic figures in modern cricket. 🏏
"""

initial_state = {
    "input_text": summary_text,
    "summary": "",
    "translation_summary": "",
    "sentiment": ""
}


result = graph.invoke(initial_state)

summary = result["summary"]
translated_text = result["translation_summary"]
sentiment = result["sentiment"]

render_display(f"### Summary: \n{summary}")
render_display(f"### Translation: \n{translated_text}")
render_display(f"### Sentiment: \n{sentiment}")
