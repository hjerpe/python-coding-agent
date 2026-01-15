#!/usr/bin/env python3
"""
Read File Agent - Section 2 (Exercise)

Implement the TODOs to create a file-reading agent.
"""

import argparse
import logging
from pathlib import Path

import anthropic

logger = logging.getLogger(__name__)


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
    try:
        file_path = Path(path)
        content = file_path.read_text()
        return content
    except Exception as e:
        return f"Error reading file: {e}"


class Agent:
    """A chat agent that can read files."""

    def __init__(self):
        """Initialize the agent."""
        self.client = anthropic.Anthropic()

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
        read_file_tool = {
            "name": "read_file",
            "description": (
                "Reads the contents of a given relative file path."
                " Use this when you need to examine the contents of a file."
                ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The relative path to the file to read"
                        }
                    },
                "required": ["path"]
            }
        }
        self.tools = [read_file_tool]  # Replace with tool definition

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
        if name == "read_file":
            path = tool_input.get("path", "")
            return read_file(path)
        else:
            return f"Unknown tool: {name}"

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
