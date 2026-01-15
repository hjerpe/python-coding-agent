# Section 5: Edit File Tool

## Learning Objectives

After completing this section, you will:

- Know how to implement string replacement in files
- Understand how to create new files with parent directories
- Learn to validate edits (exactly one match requirement)
- Handle the "append to new file" pattern with empty old_str
- Have a fully capable coding agent that can modify code!

---

## Key Concepts

### String Replacement Pattern

The edit tool uses a find-and-replace pattern:

```python
content = file_path.read_text()
new_content = content.replace(old_str, new_str, 1)  # Replace first occurrence
file_path.write_text(new_content)
```

### Validation: Exactly One Match

To ensure precise edits, require exactly one match:

```python
count = content.count(old_str)
if count == 0:
    return f"Error: '{old_str}' not found in file"
if count > 1:
    return f"Error: '{old_str}' found {count} times, need exactly 1 match"
```

**Why**: Multiple matches could cause unintended changes. Requiring a unique match forces precise edits.

### Creating New Files

When `old_str` is empty and file doesn't exist, create a new file:

```python
if old_str == "":
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_str)
        return f"Created new file: {path}"
    else:
        # Append to existing file
        existing = path.read_text()
        path.write_text(existing + new_str)
        return f"Appended to file: {path}"
```

### Parent Directory Creation

Use `pathlib` to create parent directories:

```python
from pathlib import Path

path = Path("some/nested/file.txt")
path.parent.mkdir(parents=True, exist_ok=True)  # Creates some/nested/
path.write_text(content)
```

---

## Implementation Outline

### Step 1: Add the Edit File Tool Definition

Add the edit tool with three parameters:

```python
{
    "name": "edit_file",
    "description": "Make edits to a text file. Replaces 'old_str' with 'new_str' in the file. For creating new files, use empty old_str.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file to edit"
            },
            "old_str": {
                "type": "string",
                "description": "The text to search for (must match exactly once). Use empty string for new files."
            },
            "new_str": {
                "type": "string",
                "description": "The text to replace old_str with"
            }
        },
        "required": ["path", "old_str", "new_str"]
    }
}
```

### Step 2: Implement Basic Validation

Start with input validation:

```python
def edit_file(path: str, old_str: str, new_str: str) -> str:
    # Validate inputs
    if not path:
        return "Error: path cannot be empty"

    if old_str == new_str:
        return "Error: old_str and new_str cannot be identical"

    file_path = Path(path)
    # ... rest of implementation
```

**Pitfall**: Don't forget the no-op check (old_str == new_str)!

### Step 3: Handle New File Creation

Check for the special case of empty old_str:

```python
if old_str == "":
    if not file_path.exists():
        # Create new file with parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(new_str)
        return f"Created new file: {path}"
    else:
        # Append to existing file
        existing = file_path.read_text()
        file_path.write_text(existing + new_str)
        return f"Appended to file: {path}"
```

### Step 4: Implement Find-and-Replace

For normal edits, validate and replace:

```python
try:
    content = file_path.read_text()
except FileNotFoundError:
    return f"Error: file not found: {path}"

# Check for exactly one match
count = content.count(old_str)
if count == 0:
    return f"Error: '{old_str[:50]}...' not found in {path}"
if count > 1:
    return f"Error: '{old_str[:50]}...' found {count} times, need exactly 1 match"

# Perform the replacement
new_content = content.replace(old_str, new_str, 1)
file_path.write_text(new_content)
return f"Successfully edited {path}"
```

**Tip**: Truncate long strings in error messages for readability.

### Step 5: Update the Tool Dispatcher

Add the edit_file case:

```python
elif name == "edit_file":
    return edit_file(
        tool_input["path"],
        tool_input["old_str"],
        tool_input["new_str"]
    )
```

---

## Test Commands

After implementing, test your agent:

1. **Add a comment**:
   ```
   You: Add a comment at the top of test_files/fizzbuzz.js saying "// FizzBuzz implementation"
   ```
   Expected: Claude reads the file, adds the comment, and confirms the edit.

2. **Create a new file**:
   ```
   You: Create a new file called test_files/hello.txt with the content "Hello, World!"
   ```
   Expected: Claude creates the new file.

3. **Edit existing code**:
   ```
   You: In test_files/fizzbuzz.js, change "FizzBuzz" to "FizzBang"
   ```
   Expected: Claude makes the replacement.

4. **Handle multiple matches**:
   ```
   You: Change "console.log" to "print" in test_files/fizzbuzz.js
   ```
   Expected: Claude reports multiple matches and asks for more context.

5. **Create nested directories**:
   ```
   You: Create a file at test_files/nested/deep/file.txt with content "Nested!"
   ```
   Expected: Claude creates parent directories and the file.

6. **Fix and verify**:
   ```
   You: Read test_files/fizzbuzz.js, fix the FizzBang back to FizzBuzz, then show me the result
   ```
   Expected: Claude reads, edits, and reads again to verify.

7. **Verbose mode**:
   ```bash
   python agents/agent_05_edit.py --verbose
   ```
   Then: Make an edit and observe the debug output.

---

## Important Notes

### The "Exactly One Match" Rule

This is a key design decision that prevents accidents:
- Forces Claude to provide enough context for unique matches
- Prevents accidental bulk changes
- Makes edits predictable and reviewable

### Empty old_str Behavior

When `old_str` is empty:
- **New file**: Creates with `new_str` as content
- **Existing file**: Appends `new_str` to end

This enables both file creation and append operations.

---

## Next Steps

In **Section 6: Code Search Tool**, you'll add ripgrep-powered search to help Claude find code patterns across your entire project!
