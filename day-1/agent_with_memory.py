import asyncio
from agents import Agent, Runner, SQLiteSession
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()


# ---------------------------
# Agent Instructions
# ---------------------------
PATIENT_OPD_INSTRUCTIONS = """
Instruction:
Write short, engaging disease details (<=200 characters) about a given topic.
Details must:
- Be wrapped into minimum three bullet points
- Include at least one relevant emoji
- Include one hashtag

Context:
You are an OPD Expert with deep understanding of medical diseases.

Input:
A topic provided by the user.
"""


# ---------------------------
# Create Agent
# ---------------------------
def create_agent():
    return Agent(
        name="OPD Bot",
        instructions=PATIENT_OPD_INSTRUCTIONS,
        model="gpt-4.1-mini"
    )


# ---------------------------
# Run Conversation
# ---------------------------
async def run_conversation():
    session = SQLiteSession("conversation")
    opd_bot_agent = create_agent()

    print(f"{opd_bot_agent.name} # Agent # created successfully!\n")

    # First Question
    q1 = input("Enter your query please: ")
    print(f"\nYou: '{q1}'")
    print("### Checking... ###\n")

    response = await Runner.run(
        starting_agent=opd_bot_agent,
        input=q1,
        session=session
    )

    print("\n## Agent Response ##")
    print(response.final_output)

    # Follow-up Question
    q2 = input("\nEnter your follow-up query: ")
    print(f"\nYou: '{q2}'")
    print("### Checking... ###\n")

    response2 = await Runner.run(
        starting_agent=opd_bot_agent,
        input=q2,
        session=session
    )

    print("\n## Agent Response ##")
    print(response2.final_output)


# ---------------------------
# Main Entry Point
# ---------------------------
if __name__ == "__main__":
    asyncio.run(run_conversation())