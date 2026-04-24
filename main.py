from core.agent import MultiMemoryAgent
import os
from dotenv import load_dotenv

# Load environment variables (OPENAI_API_KEY, REDIS_HOST, etc.)
load_dotenv()

def main():
    # Initialize Agent for a specific user
    user_id = "user_456"
    agent = MultiMemoryAgent(user_id=user_id)

    print("--- Multi-Memory AI Agent ---")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("User: ")
        if query.lower() in ["exit", "quit"]:
            break

        # Get response
        response = agent.chat(query)
        print(f"Agent: {response}\n")

if __name__ == "__main__":
    main()
