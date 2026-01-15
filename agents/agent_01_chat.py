#!/usr/bin/env python3
"""
Basic Chat Agent - Section 1

A simple chatbot that talks to Claude with no tools.
This is the foundation for more advanced agents.
"""

import argparse

import anthropic


class Agent:
    """A basic chat agent that maintains conversation history."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the agent.

        Args:
            verbose: If True, print debug information
        """
        self.client = anthropic.Anthropic()
        self.verbose = verbose

    def run(self) -> None:
        """Run the main conversation loop."""
        conversation: list[dict] = []

        print("Chat with Claude (Ctrl+C to exit)")
        print("-" * 40)

        try:
            while True:
                # Get user input
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue

                # Add user message to conversation
                conversation.append({"role": "user", "content": user_input})

                if self.verbose:
                    print(f"[DEBUG] Sending {len(conversation)} messages")

                # Call the API
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=conversation,
                )

                if self.verbose:
                    print(f"[DEBUG] Response stop_reason: {response.stop_reason}")

                # Add assistant response to conversation
                conversation.append({"role": "assistant", "content": response.content})

                # Print the response
                for block in response.content:
                    if hasattr(block, "text"):
                        print(f"\nAssistant: {block.text}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")


def main():
    """Entry point for the chat agent."""
    parser = argparse.ArgumentParser(description="Basic chat agent using Claude")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()

    agent = Agent(verbose=args.verbose)
    agent.run()


if __name__ == "__main__":
    main()
