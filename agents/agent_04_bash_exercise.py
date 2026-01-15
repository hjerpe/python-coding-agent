#!/usr/bin/env python3
"""
Bash Agent - Section 4 (Exercise)

Implement the TODOs to create a command-running agent.
"""

import argparse
import json
import os
import subprocess
from pathlib import Path

import anthropic


def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"


def list_files(path: str = ".") -> str:
    """List all files and directories at the given path recursively."""
    try:
        entries = []
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for name in dirs:
                rel_path = os.path.relpath(os.path.join(root, name), path)
                entries.append(rel_path + "/")
            for name in files:
                if name.startswith("."):
                    continue
                rel_path = os.path.relpath(os.path.join(root, name), path)
                entries.append(rel_path)
        return json.dumps(sorted(entries), indent=2)
    except Exception as e:
        return f"Error listing files: {e}"


def bash(command: str) -> str:
    """
    Execute a bash command and return the output.

    Args:
        command: The bash command to execute

    Returns:
        The command output or an error message
    """
    # TODO: Implement bash command execution
    # Steps:
    # 1. Use subprocess.run() with shell=True, capture_output=True, text=True
    # 2. Combine stdout and stderr
    # 3. Check returncode - if non-zero, return error message with exit code
    # 4. Return stripped output, or "(no output)" if empty
    # 5. Wrap in try/except and return error message on failure
    #
    # Hints:
    # - result = subprocess.run(command, shell=True, capture_output=True, text=True)
    # - result.returncode, result.stdout, result.stderr
    pass


class Agent:
    """A chat agent that can read files, list directories, and run commands."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the agent.

        Args:
            verbose: If True, print debug information
        """
        self.client = anthropic.Anthropic()
        self.verbose = verbose

        # TODO: Add the bash tool to this list
        # It should have:
        # - name: "bash"
        # - description: explain what it does
        # - input_schema with required "command" parameter
        self.tools = [
            {
                "name": "read_file",
                "description": "Read the contents of a given relative file path.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The relative path of a file to read",
                        }
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "list_files",
                "description": "List files and directories at a given path.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Optional path to list. Defaults to current directory.",
                        }
                    },
                    "required": [],
                },
            },
            # TODO: Add bash tool definition here
        ]

    def execute_tool(self, name: str, tool_input: dict) -> str:
        """
        Execute a tool and return its result.

        Args:
            name: The name of the tool to execute
            tool_input: The input parameters for the tool

        Returns:
            The tool's output as a string
        """
        if name == "read_file":
            return read_file(tool_input["path"])
        elif name == "list_files":
            return list_files(tool_input.get("path", "."))
        # TODO: Add handling for "bash"
        return f"Unknown tool: {name}"

    def run(self) -> None:
        """Run the main conversation loop."""
        conversation: list[dict] = []

        print("Chat with Claude - Command Runner (Ctrl+C to exit)")
        print("-" * 50)

        try:
            while True:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue

                conversation.append({"role": "user", "content": user_input})

                while True:
                    if self.verbose:
                        print(f"[DEBUG] Sending {len(conversation)} messages")

                    response = self.client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        messages=conversation,
                        tools=self.tools,
                    )

                    if self.verbose:
                        print(f"[DEBUG] Response stop_reason: {response.stop_reason}")

                    conversation.append(
                        {"role": "assistant", "content": response.content}
                    )

                    tool_uses = [b for b in response.content if b.type == "tool_use"]

                    if not tool_uses:
                        for block in response.content:
                            if hasattr(block, "text"):
                                print(f"\nAssistant: {block.text}")
                        break

                    tool_results = []
                    for tool_use in tool_uses:
                        if self.verbose:
                            print(f"[DEBUG] Tool call: {tool_use.name}")
                            print(f"[DEBUG] Tool input: {tool_use.input}")

                        result = self.execute_tool(tool_use.name, tool_use.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": result,
                            }
                        )

                    conversation.append({"role": "user", "content": tool_results})

        except KeyboardInterrupt:
            print("\n\nGoodbye!")


def main():
    """Entry point for the command runner agent."""
    parser = argparse.ArgumentParser(
        description="Chat agent with file operations and bash command capability"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()

    agent = Agent(verbose=args.verbose)
    agent.run()


if __name__ == "__main__":
    main()
