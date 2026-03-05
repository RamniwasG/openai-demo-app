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
Write short, engaging disease details (<=200 characters).
Requirements:
- Minimum 3 bullet points
- At least one relevant emoji
- Include one hashtag

Context:
You are an OPD Expert with deep medical understanding.
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
# Pretty Output Formatter
# ---------------------------
def print_header(title):
    print("\n" + "=" * 50)
    print(f"{title.center(50)}")
    print("=" * 50)


def print_response(text):
    print("\n" + "-" * 50)
    print(text)
    print("-" * 50 + "\n")


# ---------------------------
# Main CLI Loop
# ---------------------------
async def main():
    session = SQLiteSession("conversation")
    agent = create_agent()

    print_header(f"{agent.name} Initialized Successfully")

    while True:
        print("""
Choose an option:
1. Ask about a disease
2. Ask follow-up question (memory test)
3. Clear conversation memory
4. Quit
""")

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            topic = input("\nEnter disease/topic: ")
            print_header("Checking...")

            response = await Runner.run(
                starting_agent=agent,
                input=topic,
                session=session
            )

            print_header("Agent Response")
            print_response(response.final_output)

        elif choice == "2":
            followup = input("\nEnter follow-up query: ")
            print_header("Checking...")

            response = await Runner.run(
                starting_agent=agent,
                input=followup,
                session=session
            )

            print_header("Agent Response")
            print_response(response.final_output)

        elif choice == "3":
            session = SQLiteSession("conversation")
            print("\nMemory cleared successfully!\n")

        elif choice == "4":
            print("\nThank you for using OPD Bot. Goodbye 👋\n")
            break

        else:
            print("\nInvalid option. Please choose 1-4.\n")


# ---------------------------
# Entry Point
# ---------------------------
if __name__ == "__main__":
    asyncio.run(main())