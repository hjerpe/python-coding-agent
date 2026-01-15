#!/usr/bin/env python3
"""
Read File Agent - Section 2 (Exercise)

Implement the TODOs to create a file-reading agent.
"""

import argparse
from pathlib import Path

import anthropic


def read_file(path: str) -> str:
    """
    Read and return the contents of a file.

    Args:
        path: The path to the file to read

    Returns:
        The file contents or an error message
    """
    # TODO: Implement file reading
    # Hint: Use Path(path).read_text()
    # Hint: Wrap in try/except and return error message on failure
    pass


class Agent:
    """A chat agent that can read files."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the agent.

        Args:
            verbose: If True, print debug information
        """
        self.client = anthropic.Anthropic()
        self.verbose = verbose

        # TODO: Define the read_file tool
        # Hint: Use the structure:
        # {
        #     "name": "read_file",
        #     "description": "...",
        #     "input_schema": {
        #         "type": "object",
        #         "properties": {...},
        #         "required": [...]
        #     }
        # }
        self.tools = []  # Replace with tool definition

    def execute_tool(self, name: str, tool_input: dict) -> str:
        """
        Execute a tool and return its result.

        Args:
            name: The name of the tool to execute
            tool_input: The input parameters for the tool

        Returns:
            The tool's output as a string
        """
        # TODO: Check if name is "read_file" and call the function
        # Hint: Return f"Unknown tool: {name}" for unknown tools
        pass

    def run(self) -> None:
        """Run the main conversation loop."""
        conversation: list[dict] = []

        print("Chat with Claude - File Reader (Ctrl+C to exit)")
        print("-" * 50)

        try:
            while True:
                # Get user input
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue

                conversation.append({"role": "user", "content": user_input})

                # TODO: Implement the inner tool execution loop
                # The pattern is:
                # 1. Call API with tools
                # 2. Add response to conversation
                # 3. Check for tool_use blocks
                # 4. If no tools, print text and break
                # 5. If tools, execute them, add results to conversation, loop again

                while True:
                    # TODO: Call self.client.messages.create() with:
                    # - model="claude-sonnet-4-20250514"
                    # - max_tokens=1024
                    # - messages=conversation
                    # - tools=self.tools
                    response = None  # Replace with API call

                    # TODO: Add assistant response to conversation

                    # TODO: Find tool_use blocks in response.content
                    # Hint: [b for b in response.content if b.type == "tool_use"]
                    tool_uses = []

                    if not tool_uses:
                        # TODO: Print text blocks and break
                        break

                    # TODO: Execute each tool and collect results
                    # Format: {"type": "tool_result", "tool_use_id": ..., "content": ...}
                    tool_results = []

                    # TODO: Add tool_results to conversation as a user message
                    pass

        except KeyboardInterrupt:
            print("\n\nGoodbye!")


def main():
    """Entry point for the file reader agent."""
    parser = argparse.ArgumentParser(
        description="Chat agent with file reading capability"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()

    agent = Agent(verbose=args.verbose)
    agent.run()


if __name__ == "__main__":
    main()
