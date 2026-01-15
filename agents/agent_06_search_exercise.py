#!/usr/bin/env python3
"""
Code Search Agent - Section 6 (Exercise)

Implement the TODOs to create a complete coding agent with search.
"""

import argparse
import json
import logging
import os
import subprocess
from pathlib import Path

import anthropic

logger = logging.getLogger(__name__)


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
    """Edit a file by replacing old_str with new_str."""
    if not path:
        return "Error: path cannot be empty"
    if old_str == new_str:
        return "Error: old_str and new_str cannot be identical"

    file_path = Path(path)

    if old_str == "":
        try:
            if not file_path.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(new_str)
                return f"Created new file: {path}"
            else:
                existing = file_path.read_text()
                file_path.write_text(existing + new_str)
                return f"Appended to file: {path}"
        except Exception as e:
            return f"Error: {e}"

    try:
        content = file_path.read_text()
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error: {e}"

    count = content.count(old_str)
    if count == 0:
        return f"Error: text not found in {path}"
    if count > 1:
        return f"Error: text found {count} times, need exactly 1 match"

    new_content = content.replace(old_str, new_str, 1)
    try:
        file_path.write_text(new_content)
        return f"Successfully edited {path}"
    except Exception as e:
        return f"Error: {e}"


def code_search(
    pattern: str,
    path: str = ".",
    file_type: str | None = None,
    case_sensitive: bool = False,
) -> str:
    """
    Search for code patterns using ripgrep.

    Args:
        pattern: The search pattern or regex
        path: The path to search in (defaults to current directory)
        file_type: Optional file type filter (e.g., 'py', 'js')
        case_sensitive: Whether search is case-sensitive (default False)

    Returns:
        Matching lines with file names and line numbers, or error message
    """
    # TODO: Implement code search using ripgrep
    # Steps:
    # 1. Validate pattern is not empty
    # 2. Build command args: ["rg", "--line-number", "--with-filename", "--color=never"]
    # 3. Add "--ignore-case" if not case_sensitive
    # 4. Add ["--type", file_type] if file_type is provided
    # 5. Append pattern and path to args
    # 6. Run subprocess.run(args, capture_output=True, text=True)
    # 7. Handle exit codes:
    #    - returncode == 1: return "No matches found"
    #    - returncode != 0: return error message
    # 8. Limit output to MAX_MATCHES (50) lines
    #
    # Hints:
    # - args.extend(["--type", file_type])
    # - lines = output.split("\n")
    # - Handle FileNotFoundError for missing ripgrep
    pass


class Agent:
    """A complete coding agent with all tools."""

    def __init__(self):
        """Initialize the agent."""
        self.client = anthropic.Anthropic()

        # TODO: Add the code_search tool to this list
        # It should have:
        # - name: "code_search"
        # - description: explain ripgrep search
        # - input_schema with:
        #   - "pattern" (required)
        #   - "path" (optional)
        #   - "file_type" (optional)
        #   - "case_sensitive" (optional, boolean)
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
                            "description": "Optional path to list.",
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
            {
                "name": "edit_file",
                "description": "Edit a file by replacing old_str with new_str.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "old_str": {"type": "string", "description": "Text to replace"},
                        "new_str": {"type": "string", "description": "Replacement text"},
                    },
                    "required": ["path", "old_str", "new_str"],
                },
            },
            # TODO: Add code_search tool definition here
        ]

    def execute_tool(self, name: str, tool_input: dict) -> str:
        """Execute a tool and return its result."""
        if name == "read_file":
            return read_file(tool_input["path"])
        elif name == "list_files":
            return list_files(tool_input.get("path", "."))
        elif name == "bash":
            return bash(tool_input["command"])
        elif name == "edit_file":
            return edit_file(
                tool_input["path"],
                tool_input["old_str"],
                tool_input["new_str"],
            )
        # TODO: Add handling for "code_search"
        return f"Unknown tool: {name}"

    def run(self) -> None:
        """Run the main conversation loop."""
        conversation: list[dict] = []

        print("Chat with Claude - Coding Agent (Ctrl+C to exit)")
        print("-" * 50)

        try:
            while True:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue

                conversation.append({"role": "user", "content": user_input})

                while True:
                    logger.debug(f"Sending {len(conversation)} messages")

                    response = self.client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        messages=conversation,
                        tools=self.tools,
                    )

                    logger.debug(f"Response stop_reason: {response.stop_reason}")

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
                        logger.debug(f"Tool call: {tool_use.name}")
                        logger.debug(f"Tool input: {tool_use.input}")

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
    """Entry point for the coding agent."""
    parser = argparse.ArgumentParser(description="Complete coding agent with Claude")
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
