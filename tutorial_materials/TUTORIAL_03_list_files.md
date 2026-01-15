# Section 3: List Files Tool

## Learning Objectives

After completing this section, you will:

- Know how to register multiple tools with the API
- Understand directory traversal using `pathlib` and `os.walk`
- Learn to filter hidden directories from results
- Return structured JSON responses from tools
- Handle optional tool parameters

---

## Key Concepts

### Multiple Tool Registration

Simply add more tools to the tools list:

```python
self.tools = [
    {
        "name": "read_file",
        "description": "...",
        "input_schema": {...}
    },
    {
        "name": "list_files",
        "description": "...",
        "input_schema": {...}
    }
]
```

### Optional Parameters

Make a parameter optional by omitting it from `required`:

```python
"input_schema": {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "Optional path to list (defaults to current directory)"
        }
    },
    "required": []  # path is optional
}
```

### Directory Traversal with os.walk

`os.walk()` recursively traverses directories:

```python
import os

for root, dirs, files in os.walk(path):
    # root: current directory path
    # dirs: list of subdirectory names
    # files: list of file names
    for file in files:
        full_path = os.path.join(root, file)
```

### Filtering Hidden Directories

Modify `dirs` in-place to skip directories:

```python
for root, dirs, files in os.walk(path):
    # Skip hidden directories (starting with .)
    dirs[:] = [d for d in dirs if not d.startswith('.')]
```

### JSON Response Format

Return structured data as JSON strings:

```python
import json

def list_files(path: str) -> str:
    files = ["file1.txt", "dir1/", "file2.py"]
    return json.dumps(files, indent=2)
```

---

## Implementation Outline

### Step 1: Add the List Files Tool Definition

Add a second tool to the tools list with an optional `path` parameter:

```python
{
    "name": "list_files",
    "description": "List files and directories at a given path. Returns a JSON array of file/directory names.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Optional path to list. Defaults to current directory."
            }
        },
        "required": []  # path is optional!
    }
}
```

**Why**: Making `path` optional lets Claude use "." as a sensible default.

### Step 2: Implement the List Files Function

Create a function that walks a directory and collects all files:

```python
import os
import json

def list_files(path: str = ".") -> str:
    """List all files and directories at the given path."""
    try:
        entries = []
        for root, dirs, files in os.walk(path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for name in dirs:
                rel_path = os.path.relpath(os.path.join(root, name), path)
                entries.append(rel_path + "/")

            for name in files:
                rel_path = os.path.relpath(os.path.join(root, name), path)
                entries.append(rel_path)

        return json.dumps(sorted(entries), indent=2)
    except Exception as e:
        return f"Error listing files: {e}"
```

**Pitfall**: Remember to add "/" suffix to directories so Claude can distinguish them.

### Step 3: Update the Tool Dispatcher

Add a case for the new tool:

```python
def execute_tool(self, name: str, tool_input: dict) -> str:
    if name == "read_file":
        return read_file(tool_input["path"])
    elif name == "list_files":
        path = tool_input.get("path", ".")  # Default to current dir
        return list_files(path)
    return f"Unknown tool: {name}"
```

**Why**: Using `.get("path", ".")` handles the optional parameter.

### Step 4: Handle Hidden Directory Filtering

Make sure to filter out directories like `.git`, `.devenv`, etc.:

```python
# Inside the walk loop
dirs[:] = [d for d in dirs if not d.startswith('.')]
```

**Why**: Hidden directories often contain large amounts of irrelevant data.

### Step 5: Format Output for Readability

Sort the entries and format as JSON:

```python
return json.dumps(sorted(entries), indent=2)
```

**Why**: Sorted, formatted JSON is easier for Claude (and humans) to read.

---

## Complete Solution

Save this as `agents/agent_03_list_files.py`:

```python
#!/usr/bin/env python3
"""
List Files Agent - Section 3

A chat agent that can read files and list directory contents.
"""

import argparse
import json
import os
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
            # Skip hidden directories
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


class Agent:
    """A chat agent that can read files and list directories."""

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
        return f"Unknown tool: {name}"

    def run(self) -> None:
        """Run the main conversation loop."""
        conversation: list[dict] = []

        print("Chat with Claude - File Explorer (Ctrl+C to exit)")
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
    """Entry point for the file explorer agent."""
    parser = argparse.ArgumentParser(
        description="Chat agent with file reading and listing capability"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()

    agent = Agent(verbose=args.verbose)
    agent.run()


if __name__ == "__main__":
    main()
```

---

## Exercise File

Save this as `agents/agent_03_list_files_exercise.py` and implement the TODOs:

```python
#!/usr/bin/env python3
"""
List Files Agent - Section 3 (Exercise)

Implement the TODOs to create a file explorer agent.
"""

import argparse
import json
import os
from pathlib import Path

import anthropic


def read_file(path: str) -> str:
    """Read and return the contents of a file."""
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

    def __init__(self, verbose: bool = False):
        """
        Initialize the agent.

        Args:
            verbose: If True, print debug information
        """
        self.client = anthropic.Anthropic()
        self.verbose = verbose

        # TODO: Add the list_files tool to this list
        # It should have:
        # - name: "list_files"
        # - description: explain what it does
        # - input_schema with optional "path" parameter (required: [])
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
            # TODO: Add list_files tool definition here
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
        # TODO: Add handling for "list_files"
        # Hint: Use tool_input.get("path", ".") for optional parameter
        return f"Unknown tool: {name}"

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
    """Entry point for the file explorer agent."""
    parser = argparse.ArgumentParser(
        description="Chat agent with file reading and listing capability"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()

    agent = Agent(verbose=args.verbose)
    agent.run()


if __name__ == "__main__":
    main()
```

---

## Test Commands

After implementing, test your agent:

1. **List current directory**:
   ```
   You: What files are in this directory?
   ```
   Expected: Claude lists all files and subdirectories.

2. **List specific directory**:
   ```
   You: List files in test_files
   ```
   Expected: Shows fizzbuzz.js and riddle.txt.

3. **Explore and read**:
   ```
   You: List files in test_files and read the JavaScript file
   ```
   Expected: Claude lists files, then reads fizzbuzz.js.

4. **Find a file**:
   ```
   You: Is there a riddle file somewhere? Read it if you find one.
   ```
   Expected: Claude explores, finds riddle.txt, and reads it.

5. **Verbose mode**:
   ```bash
   python agents/agent_03_list_files.py --verbose
   ```
   Then: "List all files"
   Expected: See debug output for both list_files and any subsequent tool calls.

---

## Next Steps

In **Section 4: Bash Tool**, you'll add the ability to execute shell commands, opening up powerful automation capabilities!
