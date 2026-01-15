# Section 4: Bash Tool

## Learning Objectives

After completing this section, you will:

- Know how to run external commands with Python's `subprocess` module
- Understand how to capture stdout and stderr
- Handle command errors gracefully (returning errors as strings for Claude to see)
- Be aware of security considerations when executing shell commands
- Have a fully functional command-execution agent

---

## Key Concepts

### The subprocess Module

Python's `subprocess.run()` executes external commands:

```python
import subprocess

result = subprocess.run(
    "ls -la",
    shell=True,           # Interpret command through shell
    capture_output=True,  # Capture stdout and stderr
    text=True             # Return strings instead of bytes
)

print(result.stdout)      # Standard output
print(result.stderr)      # Standard error
print(result.returncode)  # Exit code (0 = success)
```

### Combined Output

When you don't need to distinguish stdout from stderr:

```python
result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True
)
output = result.stdout + result.stderr
```

### Error Handling Strategy

**Key insight**: Return errors as strings, not exceptions. This lets Claude see and respond to errors:

```python
def bash(command: str) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"Command failed (exit {result.returncode}):\n{result.stderr or result.stdout}"
        return result.stdout
    except Exception as e:
        return f"Error executing command: {e}"
```

### Security Considerations

Running arbitrary shell commands is powerful but potentially dangerous:

1. **Never run untrusted input** - Claude generates commands, but be cautious
2. **Consider sandboxing** - In production, use containers or restricted environments
3. **Log commands** - The verbose flag helps track what's being executed
4. **Review before production** - This tutorial is for learning; add safeguards for real use

---

## Implementation Outline

### Step 1: Add the Bash Tool Definition

Add the bash tool to your tools list:

```python
{
    "name": "bash",
    "description": "Execute a bash command and return its output. Use for running shell commands, scripts, or system utilities.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The bash command to execute"
            }
        },
        "required": ["command"]
    }
}
```

**Why**: A clear description helps Claude know when bash is appropriate vs other tools.

### Step 2: Implement the Bash Function

Create a function using `subprocess.run()`:

```python
import subprocess

def bash(command: str) -> str:
    """Execute a bash command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        # Combine stdout and stderr
        output = result.stdout + result.stderr

        if result.returncode != 0:
            return f"Command failed (exit {result.returncode}):\n{output}"

        return output.strip() if output else "(no output)"
    except Exception as e:
        return f"Error executing command: {e}"
```

**Pitfall**: Don't forget to strip whitespace from output!

### Step 3: Update the Tool Dispatcher

Add the bash case to `execute_tool()`:

```python
def execute_tool(self, name: str, tool_input: dict) -> str:
    if name == "read_file":
        return read_file(tool_input["path"])
    elif name == "list_files":
        return list_files(tool_input.get("path", "."))
    elif name == "bash":
        return bash(tool_input["command"])
    return f"Unknown tool: {name}"
```

### Step 4: Add Command Logging

Log commands when verbose mode is enabled:

```python
def bash(command: str, verbose: bool = False) -> str:
    if verbose:
        print(f"[DEBUG] Executing: {command}")
    # ... rest of function
```

**Why**: Seeing what commands are executed helps debugging and security review.

### Step 5: Handle Edge Cases

Consider what to return for:
- Empty output: Return "(no output)" instead of empty string
- Non-zero exit codes: Include the exit code and error message
- Exceptions: Return the error message as a string

---

## Complete Solution

Save this as `agents/agent_04_bash.py`:

```python
#!/usr/bin/env python3
"""
Bash Agent - Section 4

A chat agent that can read files, list directories, and execute bash commands.
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

        # Combine stdout and stderr
        output = result.stdout + result.stderr

        if result.returncode != 0:
            return f"Command failed (exit {result.returncode}):\n{output}"

        return output.strip() if output else "(no output)"
    except Exception as e:
        return f"Error executing command: {e}"


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
        return f"Unknown tool: {name}"

    def run(self) -> None:
        """Run the main conversation loop."""
        conversation: list[dict] = []

        print("Chat with Claude - Command Runner (Ctrl+C to exit)")
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
```

---

## Exercise File

Save this as `agents/agent_04_bash_exercise.py` and implement the TODOs:

```python
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
```

---

## Test Commands

After implementing, test your agent:

1. **Simple command**:
   ```
   You: Run git status
   ```
   Expected: Claude runs the command and shows git status output.

2. **Check Python version**:
   ```
   You: What Python version is installed?
   ```
   Expected: Claude runs `python --version` and tells you.

3. **List with bash**:
   ```
   You: Use ls -la to show all files including hidden ones
   ```
   Expected: Claude uses bash instead of list_files tool.

4. **Handle errors**:
   ```
   You: Run the command "nonexistent_command_xyz"
   ```
   Expected: Claude reports the command failed with an error message.

5. **Chain commands**:
   ```
   You: Count how many lines are in test_files/fizzbuzz.js
   ```
   Expected: Claude runs `wc -l test_files/fizzbuzz.js`.

6. **Multi-step task**:
   ```
   You: Create a new directory called 'temp', list its contents, then remove it
   ```
   Expected: Claude runs mkdir, ls, and rmdir commands in sequence.

7. **Verbose mode**:
   ```bash
   python agents/agent_04_bash.py --verbose
   ```
   Then: "Run pwd"
   Expected: See debug output including the exact command being executed.

---

## Security Note

The bash tool is powerful but potentially dangerous. For production use, consider:

1. **Command whitelisting** - Only allow specific commands
2. **Sandboxing** - Run in a container or restricted environment
3. **User confirmation** - Ask before running destructive commands
4. **Logging** - Track all commands for audit

For this tutorial, we trust Claude to be reasonable, but always be aware of what commands are being run!

---

## Next Steps

In **Section 5: Edit File Tool**, you'll add the ability to modify files, completing the core functionality of a coding agent!
