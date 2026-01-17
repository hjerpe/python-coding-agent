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

## Scalable Tool Registration System (Decorator Pattern)

As your agent grows to support more tools (3+), manually defining tool schemas becomes repetitive and error-prone. The complete agent file includes a decorator-based registration system that makes adding tools much cleaner. **This system is already implemented in `agent_03_list_files.py`** - you don't need to build it yourself, but understanding how it works will help you extend the agent with new tools.

### Why the Manual Approach Doesn't Scale

Consider adding a third tool with the manual approach:

```python
# Manual approach - lots of repetition!
self.tools = [
    {
        "name": "read_file",
        "description": "...",
        "input_schema": {"type": "object", "properties": {...}, "required": [...]}
    },
    {
        "name": "list_files",
        "description": "...",
        "input_schema": {"type": "object", "properties": {...}, "required": [...]}
    },
    {
        "name": "write_file",
        "description": "...",
        "input_schema": {"type": "object", "properties": {...}, "required": [...]}
    },
]

# Then update execute_tool with more if/elif...
def execute_tool(self, name: str, tool_input: dict) -> str:
    if name == "read_file":
        return read_file(tool_input["path"])
    elif name == "list_files":
        return list_files(tool_input.get("path", "."))
    elif name == "write_file":
        return write_file(tool_input["path"], tool_input["content"])
    return f"Unknown tool: {name}"
```

**Problems:**
- Tool definition is separated from implementation
- Schema is manually written as a dict (no type checking)
- Need to update multiple places to add a tool
- Easy to make mistakes with required fields

### The Tool Registry Pattern

The decorator system uses a central `TOOLS` dictionary to register all tools:

```python
TOOLS: dict[str, dict[str, Any]] = {}
```

Each tool entry stores:
- `name`: The tool identifier
- `description`: What it does
- `model`: A Pydantic model class for input validation
- `fn`: The actual Python function to call

This centralizes all tool information in one place.

### The @tool Decorator

Python decorators are functions that wrap other functions. Our `@tool` decorator automatically registers a function as an LLM tool:

```python
@tool(
    name="read_file",
    description="Read the contents of a given relative file path.",
    input_model=ReadFileInput,
)
def read_file(path: str) -> str:
    return Path(path).read_text()
```

**What happens:**
1. The `@tool` decorator runs when the module loads
2. It adds an entry to the `TOOLS` registry
3. The function itself remains unchanged and callable

**Benefits:**
- Tool metadata lives right above the implementation
- No need to separately maintain a tools list
- Adding a new tool is just adding a decorated function

### Pydantic Input Validation

Instead of manually writing JSON schemas, we use Pydantic models:

```python
from pydantic import BaseModel, Field

class ReadFileInput(BaseModel):
    path: str = Field(description="The relative path of a file to read")

class ListFilesInput(BaseModel):
    path: str = Field(
        default=".",
        description="The relative path of a directory to list"
    )
```

**Advantages:**
- Type-safe: `path: str` ensures it's a string
- Auto-generated JSON schema via `model_json_schema()`
- Default values: `default="."` makes the field optional
- Automatic validation: Pydantic checks types before calling the function
- Better IDE support: autocomplete and type checking

### The anthropic_tools() Converter

This function converts our registry to Anthropic's expected format:

```python
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
```

**Key points:**
- Loops through all registered tools
- Extracts JSON schema from Pydantic models
- Formats it for Anthropic's API
- Called once in `Agent.__init__()`: `self.tools = anthropic_tools()`

### The execute_tool() Function

Instead of a long if/elif chain, we have a generic dispatcher:

```python
def execute_tool(name: str, tool_input: dict[str, Any]) -> str:
    """Execute a tool with automatic input validation."""
    t = TOOLS.get(name)
    if not t:
        return f"Unknown tool: {name}"

    try:
        # Validate input using Pydantic
        parsed = t["model"].model_validate(tool_input)
    except ValidationError as e:
        return f"Invalid input for {name}: {e.errors()}"

    # Convert validated model to kwargs and call function
    kwargs = parsed.model_dump()
    return t["fn"](**kwargs)
```

**How it works:**
1. Look up the tool in the registry
2. Validate the input against the Pydantic model
3. If validation fails, return a helpful error message
4. Convert the validated model to a dict
5. Call the actual function with `**kwargs`

**Benefits:**
- No if/elif chain needed
- Automatic input validation
- Type-safe function calls
- Consistent error handling

### Side-by-Side Comparison

**Manual Approach:**
```python
# Define schema manually
self.tools = [{
    "name": "read_file",
    "description": "...",
    "input_schema": {
        "type": "object",
        "properties": {"path": {"type": "string", "description": "..."}},
        "required": ["path"]
    }
}]

# Separate dispatcher
def execute_tool(self, name: str, tool_input: dict) -> str:
    if name == "read_file":
        return read_file(tool_input["path"])
    return f"Unknown tool: {name}"

# Function definition elsewhere
def read_file(path: str) -> str:
    return Path(path).read_text()
```

**Decorator Approach:**
```python
# Everything together, type-safe
class ReadFileInput(BaseModel):
    path: str = Field(description="...")

@tool(name="read_file", description="...", input_model=ReadFileInput)
def read_file(path: str) -> str:
    return Path(path).read_text()

# Automatic registration, no dispatcher needed
self.tools = anthropic_tools()
```

### Benefits Summary

1. **DRY (Don't Repeat Yourself)**: Write tool definitions once, in one place
2. **Type Safety**: Pydantic validates inputs before they reach your functions
3. **Easier to Add Tools**: Just add a decorated function - no other changes needed
4. **Better Errors**: Pydantic provides detailed validation error messages
5. **IDE Support**: Type hints work properly with Pydantic models
6. **Maintainable**: All tool metadata lives next to the implementation
7. **Scalable**: Adding the 10th tool is as easy as adding the 2nd

### When to Use This Pattern

- **3+ tools**: Manual approach is fine for 1-2 tools, but use decorators beyond that
- **Complex inputs**: When tools have multiple parameters or optional fields
- **Team projects**: When multiple developers are adding tools
- **Long-lived projects**: When you'll be maintaining and extending the code

The decorator system is **already implemented** in the complete `agent_03_list_files.py` file. You can examine the code in lines 22-117 to see how it all fits together. When you're ready to add a new tool, just define a Pydantic model and add a decorated function!

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
   uv run python agents/agent_03_list_files.py --verbose
   ```
   Then: "List all files"
   Expected: See debug output for both list_files and any subsequent tool calls.

---

## Next Steps

In **Section 4: Bash Tool**, you'll add the ability to execute shell commands, opening up powerful automation capabilities!
