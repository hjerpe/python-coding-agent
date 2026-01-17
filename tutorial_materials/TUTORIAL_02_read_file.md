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
   uv run python agents/agent_02_read.py --verbose
   ```
   Then: "Read test_files/fizzbuzz.js"
   Expected: See debug output showing tool calls and results.

---

## Next Steps

In **Section 3: List Files Tool**, you'll add directory listing so Claude can explore the filesystem!
