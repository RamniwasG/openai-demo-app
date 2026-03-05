import os
from openai import OpenAI
from agents import Agent, Runner, SQLiteSession
from dotenv import load_dotenv

load_dotenv()

model = os.getenv("MODEL")

def print_markdown(text):
    """Utility function to print text in markdown format."""
    print(f"\n{text}\n")

session = SQLiteSession("travel conversation")

# set the instruction
travel_plan_instruction = """
    Instruction:
    you are an assistent specilaizing in weekend travel planing. always suggest one sunny(warm) destination for a quick gateway

    Context:
    You are an ***Travel planning Extert***, having many years of experience in providing weekend plan services

    Input:
    the topic provided by the user

"""

# create a agent
travel_plan_agent = Agent(
    name = "travel plan agent",
    instructions = travel_plan_instruction,
    model = model
)

input_text = input("Enter you query")

# run a agent

response = Runner.run_sync(
    starting_agent = travel_plan_agent,
    input = input_text,
    session = session
)

print_markdown(f"## Agent Response ## \n {response.final_output}")


# Enter you query please suggest one 5 hours weekend destination from uttar-pradesh to himachl pradesh?
# Agent Response
# Sunny (warm) weekend getaway (~5 hours) from Uttar Pradesh to Himachal Pradesh:

# Kasauli (Himachal Pradesh)
# Why Kasauli works
# Quick, relaxed hill escape with a milder, often sunny feel compared to higher Himachal towns.
# Great for a 2-day weekend: viewpoints, short walks, cafés, and colonial charm without long travel hours.
# Approx. travel time (around 5 hours, depending on your starting point in UP)
# From Saharanpur / Muzaffarnagar belt (West UP): ~4.5–6 hrs by road
# From Meerut: ~6–7 hrs
# From Noida/Delhi edge: usually ~6–8 hrs (traffic-dependent)
# If you tell me your exact city in Uttar Pradesh, I’ll give the tightest 5-hour route, best departure time, and a simple 2-day itinerary.

# What to do (perfect for a weekend)
# Sunset at Sunset Point / Lover’s Lane
# Mall Road stroll + cafés
# Gilbert Trail (easy, scenic nature walk)
# Manki Point (Hanuman Temple) (check entry timing)
# Best stay areas
# Near Mall Road (walkable, convenient)
# Lower Kasauli (quieter, often better value)
# Ideal quick 2-day plan
# Day 1: Drive in → check-in → Mall Road + sunset
# Day 2: Morning trail/viewpoint → brunch → drive back
# Share your starting city (e.g., Meerut/Noida/Agra/Lucknow) and whether you’re driving or using train+taxi, and I’ll tailor it to stay as close as possible to 5 hours.