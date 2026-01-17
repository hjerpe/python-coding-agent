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

## Scalable Tool Registration with Decorators

In Section 3, we introduced a decorator-based tool registration system that eliminates boilerplate when adding new tools. **All subsequent sections (4-6) use this pattern**, so let's recap how it works.

### The Old Way (Manual)

Previously, adding a tool required three steps:

```python
# Step 1: Write the function
def bash(command: str) -> str:
    return subprocess.run(command, shell=True, ...).stdout

# Step 2: Add tool definition to self.tools list
self.tools = [
    {
        "name": "bash",
        "description": "Execute a bash command...",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string", ...}},
            "required": ["command"]
        }
    }
]

# Step 3: Add dispatch logic to execute_tool()
def execute_tool(self, name, tool_input):
    if name == "bash":
        return bash(tool_input["command"])
```

This approach doesn't scale - each tool requires changes in 3 separate places.

### The New Way (Decorators + Pydantic)

With the decorator pattern, adding a tool requires only:

```python
# 1. Define Pydantic input model
class BashInput(BaseModel):
    command: str = Field(description="The bash command to execute")

# 2. Decorate the function
@tool(
    name="bash",
    description="Execute a bash command and return its output...",
    input_model=BashInput,
)
def bash(command: str) -> str:
    """Execute a bash command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        # ... implementation
    except Exception as e:
        return f"Error executing command: {e}"
```

**That's it!** The decorator automatically:
- Registers the tool in the global `TOOLS` registry
- The `anthropic_tools()` function converts it to Anthropic format
- The `execute_tool()` function validates inputs and dispatches correctly

### Benefits

1. **Less Boilerplate:** One decorator vs. three manual steps
2. **Type Safety:** Pydantic validates inputs automatically
3. **Co-location:** Tool definition lives next to implementation
4. **Consistency:** Same pattern for all tools

### Infrastructure Already Provided

In the exercise file, you'll see this infrastructure is **already written** for you:

```python
# ---------- Tool Registry System ----------
TOOLS: dict[str, dict[str, Any]] = {}

def tool(*, name: str, description: str, input_model: type[BaseModel]):
    """Decorator to register a function as an LLM tool."""
    # ... (already implemented)

def anthropic_tools() -> list[dict[str, Any]]:
    """Convert registered tools to Anthropic's tool format."""
    # ... (already implemented)

def execute_tool(name: str, tool_input: dict[str, Any]) -> str:
    """Execute a registered tool with input validation."""
    # ... (already implemented)
```

And the Agent class is simplified:

```python
class Agent:
    def __init__(self):
        self.client = anthropic.Anthropic()
        # Just use the registry - no manual tool definitions!
        self.tools = anthropic_tools()

    def execute_tool(self, name: str, tool_input: dict) -> str:
        # Just delegate - no if/elif chain!
        return execute_tool(name, tool_input)
```

**Your job:** Implement the tool function body. The infrastructure handles the rest.

---

## What You'll Do

In this exercise, you'll implement the `bash()` tool function to execute shell commands:

1. **Implement bash command execution** using `subprocess.run()`
2. **Handle command output** (stdout/stderr) and exit codes
3. **Test your agent** by running shell commands through Claude

**Note:** The decorator infrastructure, Pydantic models, and Agent class are already complete. You only need to implement the tool function body marked with `TODO`.

---

## Exercise Instructions

### Step 1: Review the Decorator Infrastructure

Open `agent_04_bash_exercise.py` and observe:

1. **Tool Registry System** (lines 26-93): Already implemented
2. **Pydantic Models** (lines 96-113): `ReadFileInput`, `ListFilesInput`, `BashInput` - all defined
3. **Completed Tools** (lines 118-152): `read_file` and `list_files` with `@tool` decorators
4. **TODO Tool** (lines 155-182): The `bash()` function needs implementation

### Step 2: Implement the bash() Function

Find the `bash()` function around line 160. It already has the `@tool` decorator applied:

```python
@tool(
    name="bash",
    description="Execute a bash command and return its output...",
    input_model=BashInput,
)
def bash(command: str) -> str:
    """Execute a bash command and return the output."""
    # TODO: Your implementation here
    pass
```

**Your task:** Replace the `pass` statement with the implementation.

**Requirements:**
1. Use `subprocess.run()` with `shell=True`, `capture_output=True`, `text=True`
2. Combine stdout and stderr into a single output string
3. Check `result.returncode`:
   - If non-zero: return `f"Command failed (exit {result.returncode}):\n{output}"`
   - If zero and output exists: return stripped output
   - If zero and no output: return `"(no output)"`
4. Wrap everything in a try/except block, return error message on exception

**Hints:**
```python
result = subprocess.run(command, shell=True, capture_output=True, text=True)
output = result.stdout + result.stderr
```

### Step 3: Test Your Implementation

Run the agent:

```bash
cd /path/to/agents
uv run python agent_04_bash_exercise.py --verbose
```

**Test cases:**

1. **Basic command:**
   ```
   You: Run the command "echo hello world"
   Expected: Should return "hello world"
   ```

2. **Command with exit code:**
   ```
   You: Run "ls /nonexistent"
   Expected: Should return error with exit code
   ```

3. **File operations:**
   ```
   You: List all Python files in the current directory
   Expected: Should use bash with "ls *.py"
   ```

### Step 4: Understand What You Didn't Have to Do

Compare your exercise file to the solution file (`agent_04_bash.py`). Notice you didn't need to:

- Add tool definition to `self.tools` list
- Update `execute_tool()` if/elif chain
- Write JSON schema manually
- Handle input validation

The decorator system handled all of this automatically!

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
   uv run python agents/agent_04_bash.py --verbose
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
