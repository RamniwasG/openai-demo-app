# In this project we will build an AI travel agent that can perform web searches, find popular attractions, 
# check whether conditions and search for flights and hotels using LangGraph.

#  install necessary libraries
#  pip install langchain langgraph langchain_openai tavily-python amadeus python-dotenv gradio langchain_community graphviz


import os
import requests
import operator
from agents import function_tool
from typing_extensions import TypedDict
from typing import Sequence, Annotated, Literal
from datetime import date, datetime
from IPython.display import Markdown, display, Image
from dotenv import load_dotenv

# langchain specific imports
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.tools import tool

# langgraph specific imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from IPython.display import Markdown, display

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
model = os.getenv("MODEL", "gpt-5.2")

def print_markdown(text: str):
    display(Markdown(text))

# Example usage:
def render_display(text: str, type: str = "rich"):
    if type == "markdown":
        print(text)
    elif type == "rich":
        try:
            from rich import print
            from rich.markdown import Markdown
            print(Markdown(text))
        except ImportError:
            print(text)
    else:
        print(text)

render_display(f"### Using model: {model}")
render_display(f"### Using OpenAI API Key: {api_key if api_key else 'No'}")
render_display(f"### Using Tavily API Key: {tavily_api_key if tavily_api_key else 'No'}")


# Tavily Search tool
class TavilySearchParams(TypedDict):
    """Parameters for the Tavily search function."""
    query: str
    max_results: int = 3

@function_tool
def tavily_search(params: TavilySearchParams) -> str:
    """Searches for information using the Tavily API."""

    url = "https://api.tavily.ai/search"

    headers = { 
        "Content-Type": "application/json",
    }
    
    payload = {
        "q": params.query, 
        "key": tavily_api_key
    }
    
    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        return f"Tavily API Error: {resp.json().get('error', 'Unknown error occurred.')}"

    data = resp.json()
    if "results" not in data:
        return "No results found."

    lines = []
    for i, r in enumerate(data["results"][:params.max_results], start=1):
        lines.append(f"{i}. **{r['title']}**: {r['snippet']}")
    return "\n".join(lines)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add ]


tavily_search_tool = TavilySearch(max_results=3)

tool_list_single = [tavily_search_tool]


def make_call_model_with_tools(tools: list):
    # inner function to call the model with tools, this will be used in the graph nodes to execute the model with the provided tools and update the state accordingly. 
    def call_model_with_tools(state: AgentState):
        print("Debug: Entering call_model_with_tools:")
        messages = state.get("messages", [])
   
        llm = ChatOpenAI(model=model, temperature=0.7, openai_api_key=api_key)
   
        model_with_tools = llm.bind_tools(tools)
   
        response = model_with_tools.invoke(messages)
   
        return {
            "messages": [response]
        }
   
    return call_model_with_tools


# lets define our conditional edge function which will help us decide the flow of our graph based on the state of our agent. This function will take the current state as input and return the next node to execute based on the conditions we define.

def should_continue(state: AgentState) -> Literal["action", "__end__"]:
    # This is where we will implement the logic to decide whether to continue with the next action or end the workflow. For now, we will just check if the summary contains the word "continue".
    messages = state.get("messages", [])
    if not messages:
        print("Debug: No messages in state, ending workflow.")
        return "__end__"
    
    last_message = messages[-1]
    # if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls and "continue" in last_message.content.lower():
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("Debug: decision - continue to next action")
        return "action"
    
    print("Debug: decision - end workflow")
    return "__end__"


def build_graph_one_tool(tools_list):
    
    # lets instantiate tool node
    tool_node = ToolNode(tools_list)

    # define call node fn
    call_node_fn = make_call_model_with_tools(tools_list)

    # build the graph with one tool using ToolNode
    graph_one_tool = StateGraph(AgentState)

    graph_one_tool.add_node("agent", call_node_fn)
    graph_one_tool.add_node("action", tool_node)
    
    graph_one_tool.set_entry_point("agent")

    graph_one_tool.add_conditional_edges(
        "agent",
        should_continue, 
        { "action": "action", END: END }
    )

    graph_one_tool.add_edge("action", "agent")

    app = graph_one_tool.compile()

    # visualize the graph
    display(Image(app.get_graph().draw_mermaid_png()))

    return app


def app_call(app, messages):
    print("Debug: Starting app_call with messages:")
    print(messages)
    initial_state = {"messages": [HumanMessage(content=messages)]}

    final_state = app.invoke(initial_state)
    print("Debug: Final state after app invocation:")
    # print(final_state) 
    # for i in final_state["messages"]:
    #     print(f"**{i.type}**: {i.content}\n")

    return final_state["messages"][-1].content, final_state


# build the graph with one tool
# app_one_tool = build_graph_one_tool(tool_list_single)

# messages = input("Enter your query please! \n ")

# history, output = app_call(app_one_tool, messages)

# render_display(f"### Final Output: \n {output}")
# render_display(f"### Final State: \n {history}")

@tool
def get_current_date_tool() -> str:
    """Return the current system date and time."""
    
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

app_current_date = build_graph_one_tool([get_current_date_tool])

# prompt = input("Enter your query please! \n ")
prompt = "What is the current date and time? "

history, output = app_call(app_current_date, prompt)

# render_display(f"### Final Output: \n {output}")
# render_display(f"### Final State: \n {history}")
