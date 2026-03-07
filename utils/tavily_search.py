import os
import requests
from dotenv import load_dotenv
from typing_extensions import TypedDict
from agents import function_tool

load_dotenv()
tavily_api_key = os.getenv("TAVILY_API_KEY")

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
