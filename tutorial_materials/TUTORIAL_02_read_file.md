# Section 2: Read File Tool

## Learning Objectives

After completing this section, you will:

- Understand the tool definition structure (name, description, input schema)
- Know how to register tools with the Anthropic API
- Implement the tool execution loop pattern
- Handle tool results and return them to Claude
- Use `pathlib` for file operations in Python

---

## Key Concepts

### Tool Definition Structure

Tools are defined as dictionaries with three key parts:

```python
tools = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to read"
                }
            },
            "required": ["path"]
        }
    }
]
```

### Input Schema (JSON Schema)

The `input_schema` follows JSON Schema format:
- `type`: Always `"object"` for tool inputs
- `properties`: Dictionary of parameter definitions
- `required`: List of required parameter names

### Tool Use in Responses

When Claude wants to use a tool, the response contains `tool_use` blocks:

```python
for block in response.content:
    if block.type == "tool_use":
        print(f"Tool: {block.name}")
        print(f"Input: {block.input}")
        print(f"ID: {block.id}")
```

### Tool Results

Send tool results back to Claude in the conversation:

```python
tool_results = [
    {
        "type": "tool_result",
        "tool_use_id": tool_use.id,
        "content": "File contents here..."
    }
]
conversation.append({"role": "user", "content": tool_results})
```

### The Tool Execution Loop

The key insight: after processing tools, you must call the API again to let Claude continue:

```python
while True:
    response = client.messages.create(...)

    tool_uses = [b for b in response.content if b.type == "tool_use"]

    if not tool_uses:
        # No tools, print text and break to next user input
        break

    # Execute tools, collect results
    # Send results back, loop again
```

---

## Implementation Outline

### Step 1: Define the Tool

Create a tool definition dictionary for `read_file`:

```python
tools = [
    {
        "name": "read_file",
        "description": "Read the contents of a given relative file path. Use this when you need to examine the contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The relative path of a file to read"
                }
            },
            "required": ["path"]
        }
    }
]
```

**Why**: Clear descriptions help Claude know when to use the tool.

### Step 2: Implement the Tool Function

Create a function that reads a file using `pathlib`:

```python
from pathlib import Path

def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"
```

**Why**: Returning errors as strings lets Claude see and handle them.

### Step 3: Create a Tool Dispatcher

Map tool names to functions:

```python
def execute_tool(self, name: str, tool_input: dict) -> str:
    """Execute a tool and return its result."""
    if name == "read_file":
        return read_file(tool_input["path"])
    return f"Unknown tool: {name}"
```

**Why**: This pattern scales well as you add more tools.

### Step 4: Modify the API Call to Include Tools

Add the `tools` parameter to `messages.create()`:

```python
response = self.client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=conversation,
    tools=self.tools  # Add tools here!
)
```

### Step 5: Implement the Inner Tool Loop

After getting a response, check for tool use and loop until done:

```python
while True:
    response = self.client.messages.create(...)
    conversation.append({"role": "assistant", "content": response.content})

    # Check for tool use
    tool_uses = [b for b in response.content if b.type == "tool_use"]

    if not tool_uses:
        # Print text responses and break
        for block in response.content:
            if hasattr(block, "text"):
                print(f"\nAssistant: {block.text}")
        break

    # Execute tools
    tool_results = []
    for tool_use in tool_uses:
        result = self.execute_tool(tool_use.name, tool_use.input)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": tool_use.id,
            "content": result
        })

    conversation.append({"role": "user", "content": tool_results})
```

**Pitfall**: Don't forget to add the assistant's response to the conversation before sending tool results!

### Step 6: Add Verbose Logging for Tools

Log tool execution when verbose mode is enabled:

```python
if self.verbose:
    print(f"[DEBUG] Tool call: {tool_use.name}")
    print(f"[DEBUG] Tool input: {tool_use.input}")
```

---

## Complete Solution

Save this as `agents/agent_02_read.py`:

```python
#!/usr/bin/env python3
"""
Read File Agent - Section 2

A chat agent with the ability to read files from the filesystem.
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
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error reading file: {e}"


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
            }
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
                            print(f"[DEBUG] Tool result: {result[:100]}...")

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
```

---

## Exercise File

Save this as `agents/agent_02_read_exercise.py` and implement the TODOs:

```python
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
```

---

## Test Commands

After implementing, test your agent:

1. **Read the fizzbuzz file**:
   ```
   You: Read test_files/fizzbuzz.js
   ```
   Expected: Claude reads the file and shows you the FizzBuzz code.

2. **Ask about file contents**:
   ```
   You: Read test_files/fizzbuzz.js and explain what it does
   ```
   Expected: Claude reads the file and provides an explanation.

3. **Read the riddle**:
   ```
   You: What's in test_files/riddle.txt?
   ```
   Expected: Claude reads and shows the riddle.

4. **Handle missing file**:
   ```
   You: Read nonexistent.txt
   ```
   Expected: Claude reports that the file doesn't exist.

5. **Verbose mode**:
   ```bash
   python agents/agent_02_read.py --verbose
   ```
   Then: "Read test_files/fizzbuzz.js"
   Expected: See debug output showing tool calls and results.

---

## Next Steps

In **Section 3: List Files Tool**, you'll add directory listing so Claude can explore the filesystem!
