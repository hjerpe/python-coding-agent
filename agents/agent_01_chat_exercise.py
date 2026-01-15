#!/usr/bin/env python3
"""
Basic Chat Agent - Section 1 (Exercise)

Implement the TODOs to create a basic chatbot.
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
        # TODO: Initialize the Anthropic client
        # Hint: Use anthropic.Anthropic()
        self.client = None  # Replace with actual client

        self.verbose = verbose

    def run(self) -> None:
        """Run the main conversation loop."""
        # TODO: Initialize an empty conversation list
        conversation = None  # Replace with actual list

        print("Chat with Claude (Ctrl+C to exit)")
        print("-" * 40)

        try:
            while True:
                # TODO: Get user input using input() and strip whitespace
                user_input = None  # Replace with actual input

                # TODO: Skip empty input
                # Hint: Use 'continue' if user_input is empty

                # TODO: Add user message to conversation
                # Hint: Append a dict with "role" and "content" keys

                if self.verbose:
                    print(f"[DEBUG] Sending {len(conversation)} messages")

                # TODO: Call the API using self.client.messages.create()
                # Required parameters:
                # - model: "claude-sonnet-4-20250514"
                # - max_tokens: 1024
                # - messages: conversation
                response = None  # Replace with actual API call

                if self.verbose:
                    print(f"[DEBUG] Response stop_reason: {response.stop_reason}")

                # TODO: Add assistant response to conversation
                # Hint: The response content is in response.content

                # TODO: Print the response text
                # Hint: Loop through response.content and check for text attribute
                pass

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
