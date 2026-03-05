import os
import requests
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

load_dotenv()

model = os.getenv("MODEL")

tavily_api_key = os.getenv("TAVILY_API_KEY")

@function_tool
def tafily_search(query: str) -> str:
    url = "https://api.tavily.ai/search"
    payload = {"q": query, "key": tavily_api_key}
    resp = requests.post(url, json=payload).json()

    if "results" not in resp:
        return "No results found."

    if resp.status_code != 200:
        return f"Tavliy api Error: {resp.get('error', 'Unknown error occurred.')}"

    lines = []
    for i, r in enumerate(resp["results"][:5], start=1):
        lines.append(f"{i}. {r['title']}: {r['snippet']}")
    return "\n".join(lines)


input_query = input("Enter your search query: ")

agent = Agent(
    name="SearchBot",
    instructions="Use tavily_search tool when needed.",
    tools=[tafily_search],
    model = model
)

response = Runner.run_sync(
    starting_agent=agent,
    input=input_query
)

print(response.final_output)

# import json
# from typing_extensions import TypedDict
# from agents import function_tool

# class WeatherInfo(TypedDict):
#     location: str
#     temperature: float
#     condition: str

# @function_tool
# def get_weather(location: str) -> WeatherInfo:
#     """Fetches the current weather information for a given location."""
#     # In a real implementation, this would call an external API.
#     # Here, we return mock data for demonstration purposes.
#     mock_response = {
#         "location": location,
#         "temperature": 25.0,
#         "condition": "Sunny"
#     }
#     return WeatherInfo(**mock_response)

