#!/usr/bin/env python3
"""
Code Search Agent - Section 6 (Exercise)

Implement the TODOs to create a complete coding agent.

This version uses a decorator-based tool registration system with Pydantic
for input validation. This approach scales better as you add more tools.
"""

from __future__ import annotations
import argparse
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field, ValidationError
import anthropic

logger = logging.getLogger(__name__)


# ---------- Tool Registry System ----------

TOOLS: dict[str, dict[str, Any]] = {}


def tool(*, name: str, description: str, input_model: type[BaseModel]):
    """
    Decorator to register a function as an LLM tool.

    Args:
        name: The tool name that the LLM will use
        description: Description of what the tool does
        input_model: Pydantic model class for validating inputs

    Returns:
        Decorated function
    """
    def deco(fn: Callable[..., str]):
        TOOLS[name] = {
            "name": name,
            "description": description,
            "model": input_model,
            "fn": fn,
        }
        return fn
    return deco


def anthropic_tools() -> list[dict[str, Any]]:
    """Convert registered tools to Anthropic's tool format."""
    out: list[dict[str, Any]] = []
    for t in TOOLS.values():
        schema = t["model"].model_json_schema()

        out.append({
            "name": t["name"],
            "description": t["description"],
            "input_schema": {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", []),
            },
        })
    return out


def execute_tool(name: str, tool_input: dict[str, Any]) -> str:
    """
    Execute a registered tool with input validation.

    Args:
        name: The name of the tool to execute
        tool_input: Dictionary of input parameters

    Returns:
        The tool's output as a string, or an error message
    """
    t = TOOLS.get(name)
    if not t:
        return f"Unknown tool: {name}"

    try:
        parsed = t["model"].model_validate(tool_input)
    except ValidationError as e:
        return f"Invalid input for {name}: {e.errors()}"

    kwargs = parsed.model_dump()
    return t["fn"](**kwargs)


# ---------- Pydantic Input Models ----------

class ReadFileInput(BaseModel):
    """Input schema for the read_file tool."""
    path: str = Field(description="The relative path of a file to read")


class ListFilesInput(BaseModel):
    """Input schema for the list_files tool."""
    path: str = Field(
        default=".",
        description="The relative path of a directory to list (defaults to current directory)"
    )


class BashInput(BaseModel):
    """Input schema for the bash tool."""
    command: str = Field(description="The bash command to execute")


class EditFileInput(BaseModel):
    """Input schema for the edit_file tool."""
    path: str = Field(description="The path to the file to edit")
    old_str: str = Field(
        description="The text to search for and replace (must match exactly once). Use empty string to create new file or append."
    )
    new_str: str = Field(description="The text to replace old_str with")


class CodeSearchInput(BaseModel):
    """Input schema for the code_search tool."""
    pattern: str = Field(description="The search pattern or regex to find in files")
    path: str = Field(
        default=".",
        description="The path to search in (defaults to current directory)"
    )
    file_type: str | None = Field(
        default=None,
        description="Optional file type filter (e.g., 'py', 'js', 'go', 'ts')"
    )
    case_sensitive: bool = Field(
        default=False,
        description="Whether the search should be case-sensitive (defaults to false)"
    )


# ---------- Tool Implementations ----------

@tool(
    name="read_file",
    description="Read the contents of a given relative file path. Use this when you need to examine the contents of an existing file.",
    input_model=ReadFileInput,
)
def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"


@tool(
    name="list_files",
    description="List files and directories at a given path. If no path is provided, lists files in the current directory. Returns a JSON array of file and directory names (directories end with /).",
    input_model=ListFilesInput,
)
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


@tool(
    name="bash",
    description="Execute a bash command and return its output. Use this for running shell commands, scripts, or system utilities.",
    input_model=BashInput,
)
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


@tool(
    name="edit_file",
    description="Make edits to a text file by replacing 'old_str' with 'new_str'. The old_str must match exactly once in the file. For creating new files or appending, use an empty old_str.",
    input_model=EditFileInput,
)
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


@tool(
    name="code_search",
    description="Search for code patterns using ripgrep (rg). Returns matching lines with file names and line numbers. Supports regex patterns.",
    input_model=CodeSearchInput,
)
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
    # 2. Build ripgrep command with args:
    #    - Base: ["rg", "--line-number", "--with-filename", "--color=never"]
    #    - Add "--ignore-case" if not case_sensitive
    #    - Add ["--type", file_type] if file_type provided
    #    - Add pattern and path
    # 3. Run subprocess.run() with capture_output=True, text=True
    # 4. Handle exit codes:
    #    - Exit code 1 means no matches (return "No matches found")
    #    - Exit code 0 means success
    #    - Other exit codes are errors
    # 5. Limit output to first 50 matches (MAX_MATCHES = 50)
    # 6. Handle FileNotFoundError (ripgrep not installed)
    #
    # Hints:
    # - result.returncode
    # - output.split("\n")
    # - len(lines) > MAX_MATCHES: return truncated with message
    pass


class Agent:
    """A complete coding agent with all tools."""

    def __init__(self):
        """Initialize the agent with registered tools."""
        self.client = anthropic.Anthropic()
        # Use the decorator-based tool registry
        # This automatically includes all tools registered with @tool decorator
        self.tools = anthropic_tools()

    def execute_tool(self, name: str, tool_input: dict) -> str:
        """
        Execute a tool and return its result.

        Args:
            name: The name of the tool to execute
            tool_input: The input parameters for the tool

        Returns:
            The tool's output as a string
        """
        # Delegate to the module-level execute_tool function
        # which handles validation and dispatching
        return execute_tool(name, tool_input)

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
    parser = argparse.ArgumentParser(
        description="Complete coding agent with Claude"
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
