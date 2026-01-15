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
