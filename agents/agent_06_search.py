#!/usr/bin/env python3
"""
Code Search Agent - Section 6

A complete coding agent with file operations, bash commands, editing, and code search.
"""

import argparse
import json
import os
import subprocess
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
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"


def list_files(path: str = ".") -> str:
    """
    List all files and directories at the given path recursively.

    Args:
        path: The directory path to list (defaults to current directory)

    Returns:
        JSON array of file and directory paths
    """
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
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
        )

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
            return f"Error creating/appending file: {e}"

    try:
        content = file_path.read_text()
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"

    count = content.count(old_str)
    if count == 0:
        preview = old_str[:50] + "..." if len(old_str) > 50 else old_str
        return f"Error: '{preview}' not found in {path}"
    if count > 1:
        preview = old_str[:50] + "..." if len(old_str) > 50 else old_str
        return f"Error: '{preview}' found {count} times, need exactly 1 match. Include more context to make it unique."

    new_content = content.replace(old_str, new_str, 1)

    try:
        file_path.write_text(new_content)
        return f"Successfully edited {path}"
    except Exception as e:
        return f"Error writing file: {e}"


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
    MAX_MATCHES = 50

    if not pattern:
        return "Error: pattern cannot be empty"

    # Build ripgrep command
    args = ["rg", "--line-number", "--with-filename", "--color=never"]

    if not case_sensitive:
        args.append("--ignore-case")

    if file_type:
        args.extend(["--type", file_type])

    args.append(pattern)
    args.append(path)

    try:
        result = subprocess.run(args, capture_output=True, text=True)

        # Exit code 1 means no matches (not an error)
        if result.returncode == 1:
            return "No matches found"

        # Other non-zero codes are real errors
        if result.returncode != 0:
            return f"Search error: {result.stderr}"

        output = result.stdout.strip()

        if not output:
            return "No matches found"

        # Limit output to prevent overwhelming responses
        lines = output.split("\n")
        if len(lines) > MAX_MATCHES:
            truncated = lines[:MAX_MATCHES]
            return (
                "\n".join(truncated)
                + f"\n\n... (showing first {MAX_MATCHES} of {len(lines)} matches)"
            )

        return output

    except FileNotFoundError:
        return "Error: ripgrep (rg) is not installed. Install it with: brew install ripgrep (macOS) or apt install ripgrep (Ubuntu)"
    except Exception as e:
        return f"Error running search: {e}"


class Agent:
    """A complete coding agent with all tools."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the agent.

        Args:
            verbose: If True, print debug information
        """
        self.client = anthropic.Anthropic()
        self.verbose = verbose
        self.tools = [
            {
                "name": "read_file",
                "description": "Read the contents of a given relative file path. Use this when you need to examine the contents of an existing file.",
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
                "description": "List files and directories at a given path. If no path is provided, lists files in the current directory. Returns a JSON array of file and directory names (directories end with /).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Optional relative path to list. Defaults to current directory if not provided.",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "bash",
                "description": "Execute a bash command and return its output. Use this for running shell commands, scripts, or system utilities.",
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
                "description": "Make edits to a text file by replacing 'old_str' with 'new_str'. The old_str must match exactly once in the file. For creating new files or appending, use an empty old_str.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to edit",
                        },
                        "old_str": {
                            "type": "string",
                            "description": "The text to search for and replace (must match exactly once). Use empty string to create new file or append.",
                        },
                        "new_str": {
                            "type": "string",
                            "description": "The text to replace old_str with",
                        },
                    },
                    "required": ["path", "old_str", "new_str"],
                },
            },
            {
                "name": "code_search",
                "description": "Search for code patterns using ripgrep (rg). Returns matching lines with file names and line numbers. Supports regex patterns.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "The search pattern or regex to find in files",
                        },
                        "path": {
                            "type": "string",
                            "description": "Optional path to search in. Defaults to current directory.",
                        },
                        "file_type": {
                            "type": "string",
                            "description": "Optional file type filter (e.g., 'py', 'js', 'go', 'ts')",
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": "Whether the search should be case-sensitive. Defaults to false.",
                        },
                    },
                    "required": ["pattern"],
                },
            },
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
            path = tool_input.get("path", ".")
            return list_files(path)
        elif name == "bash":
            command = tool_input["command"]
            if self.verbose:
                print(f"[DEBUG] Executing command: {command}")
            return bash(command)
        elif name == "edit_file":
            return edit_file(
                tool_input["path"],
                tool_input["old_str"],
                tool_input["new_str"],
            )
        elif name == "code_search":
            return code_search(
                tool_input["pattern"],
                tool_input.get("path", "."),
                tool_input.get("file_type"),
                tool_input.get("case_sensitive", False),
            )
        return f"Unknown tool: {name}"

    def run(self) -> None:
        """Run the main conversation loop."""
        conversation: list[dict] = []

        print("Chat with Claude - Coding Agent (Ctrl+C to exit)")
        print("-" * 50)

        try:
            while True:
                # Get user input
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue

                # Add user message to conversation
                conversation.append({"role": "user", "content": user_input})

                # Inner loop for tool execution
                while True:
                    if self.verbose:
                        print(f"[DEBUG] Sending {len(conversation)} messages")

                    # Call the API with tools
                    response = self.client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        messages=conversation,
                        tools=self.tools,
                    )

                    if self.verbose:
                        print(f"[DEBUG] Response stop_reason: {response.stop_reason}")

                    # Add assistant response to conversation
                    conversation.append(
                        {"role": "assistant", "content": response.content}
                    )

                    # Check for tool use
                    tool_uses = [b for b in response.content if b.type == "tool_use"]

                    if not tool_uses:
                        # No tools, print text and break to next user input
                        for block in response.content:
                            if hasattr(block, "text"):
                                print(f"\nAssistant: {block.text}")
                        break

                    # Execute tools and collect results
                    tool_results = []
                    for tool_use in tool_uses:
                        if self.verbose:
                            print(f"[DEBUG] Tool call: {tool_use.name}")
                            print(f"[DEBUG] Tool input: {tool_use.input}")

                        result = self.execute_tool(tool_use.name, tool_use.input)

                        if self.verbose:
                            result_preview = (
                                result[:100] + "..."
                                if len(result) > 100
                                else result
                            )
                            print(f"[DEBUG] Tool result: {result_preview}")

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": result,
                            }
                        )

                    # Add tool results to conversation
                    conversation.append({"role": "user", "content": tool_results})

        except KeyboardInterrupt:
            print("\n\nGoodbye!")


def main():
    """Entry point for the coding agent."""
    parser = argparse.ArgumentParser(
        description="Complete coding agent with Claude"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()

    agent = Agent(verbose=args.verbose)
    agent.run()


if __name__ == "__main__":
    main()
