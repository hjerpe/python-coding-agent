#!/usr/bin/env python3
"""
Basic Chat Agent - Section 1 (Exercise)

Implement the TODOs to create a basic chatbot.
"""

import argparse
import logging

import anthropic

logger = logging.getLogger(__name__)


class Agent:
    """A basic chat agent that maintains conversation history."""

    def __init__(self):
        """Initialize the agent."""
        # TODO: Initialize the Anthropic client
        # Hint: Use anthropic.Anthropic()
        self.client = anthropic.Anthropic()

    def run(self) -> None:
        """Run the main conversation loop."""
        # TODO: Initialize an empty conversation list
        conversation = []

        print("Chat with Claude (Ctrl+C to exit)")
        print("-" * 40)

        try:
            while True:
                # TODO: Get user input using input() and strip whitespace
                user_input = input("You: ").strip()

                # TODO: Skip empty input
                # Hint: Use 'continue' if user_input is empty
                if not user_input:
                    continue

                # TODO: Add user message to conversation
                # Hint: Append a dict with "role" and "content" keys
                conversation.append({"role": "user", "content": user_input})

                logger.debug(f"Sending {len(conversation)} messages")

                # TODO: Call the API using self.client.messages.create()
                # Required parameters:
                # - model: "claude-sonnet-4-20250514"
                # - max_tokens: 1024
                # - messages: conversation
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=conversation
                )

                logger.debug(f"Response stop_reason: {response.stop_reason}")

                # TODO: Add assistant response to conversation
                # Hint: The response content is in response.content
                conversation.append({"role": "assistant", "content": response.content})

                # TODO: Print the response text
                # Hint: Loop through response.content and check for text attribute
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
    print(args)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="[%(levelname)s] %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)

    agent = Agent()
    agent.run()


if __name__ == "__main__":
    main()
