#!/usr/bin/env python3
"""
List Files Agent - Section 3 (Exercise)

Implement the TODOs to create a file explorer agent.

This version uses a decorator-based tool registration system with Pydantic
for input validation. This approach scales better as you add more tools.
"""

from __future__ import annotations
import argparse
import json
import logging
import os
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
    """
    List all files and directories at the given path recursively.

    Args:
        path: The directory path to list (defaults to current directory)

    Returns:
        JSON array of file and directory paths
    """
    # TODO: Implement directory listing
    # Steps:
    # 1. Initialize empty entries list
    # 2. Use os.walk(path) to traverse directories
    # 3. Filter out hidden directories (starting with .)
    # 4. Add directories with "/" suffix
    # 5. Add files (skip hidden files)
    # 6. Return json.dumps(sorted(entries), indent=2)
    #
    # Hints:
    # - dirs[:] = [d for d in dirs if not d.startswith('.')]
    # - os.path.relpath(os.path.join(root, name), path)
    pass


class Agent:
    """A chat agent that can read files and list directories."""

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

        print("Chat with Claude - File Explorer (Ctrl+C to exit)")
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
    """Entry point for the file explorer agent."""
    parser = argparse.ArgumentParser(
        description="Chat agent with file reading and listing capability"
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
