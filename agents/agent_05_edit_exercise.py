#!/usr/bin/env python3
"""
Edit File Agent - Section 5 (Exercise)

Implement the TODOs to create a file-editing agent.
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
    """Execute a bash command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        if result.returncode != 0:
            return f"Command failed (exit {result.returncode}):\n{output}"
        return output.strip() if output else "(no output)"
    except Exception as e:
        return f"Error executing command: {e}"


def edit_file(path: str, old_str: str, new_str: str) -> str:
    """
    Edit a file by replacing old_str with new_str.

    Args:
        path: The path to the file to edit
        old_str: The text to replace (must match exactly once, empty for new file)
        new_str: The replacement text

    Returns:
        Success message or error description
    """
    # TODO: Implement file editing
    # Steps:
    # 1. Validate inputs (path not empty, old_str != new_str)
    # 2. If old_str is empty:
    #    - If file doesn't exist: create with new_str content
    #    - If file exists: append new_str
    # 3. For normal edits:
    #    - Read file content
    #    - Count occurrences of old_str (must be exactly 1)
    #    - Replace and write back
    #
    # Hints:
    # - file_path.parent.mkdir(parents=True, exist_ok=True)
    # - content.count(old_str) to count occurrences
    # - content.replace(old_str, new_str, 1) to replace first occurrence
    pass


class Agent:
    """A chat agent that can read, list, run commands, and edit files."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the agent.

        Args:
            verbose: If True, print debug information
        """
        self.client = anthropic.Anthropic()
        self.verbose = verbose

        # TODO: Add the edit_file tool to this list
        # It should have:
        # - name: "edit_file"
        # - description: explain find-and-replace behavior
        # - input_schema with "path", "old_str", "new_str" (all required)
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
            {
                "name": "bash",
                "description": "Execute a bash command and return its output.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute",
                        }
                    },
                    "required": ["command"],
                },
            },
            # TODO: Add edit_file tool definition here
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
        elif name == "bash":
            return bash(tool_input["command"])
        # TODO: Add handling for "edit_file"
        return f"Unknown tool: {name}"

    def run(self) -> None:
        """Run the main conversation loop."""
        conversation: list[dict] = []

        print("Chat with Claude - File Editor (Ctrl+C to exit)")
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
    """Entry point for the file editor agent."""
    parser = argparse.ArgumentParser(
        description="Chat agent with full file editing capability"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()

    agent = Agent(verbose=args.verbose)
    agent.run()


if __name__ == "__main__":
    main()
