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
