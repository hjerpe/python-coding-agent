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

## Using the Decorator Pattern

This tutorial continues using the decorator-based tool registration system from Section 3. If you need a refresher on how `@tool`, Pydantic models, and the registry system work, review the "Scalable Tool Registration with Decorators" section in TUTORIAL_04_bash.md or TUTORIAL_03_list_files.md (starting at line 92).

**Key point:** The exercise file has all infrastructure pre-written. Your job is to implement the `edit_file()` function body only.

---

## What You'll Do

In this exercise, you'll implement the `edit_file()` tool to modify files programmatically:

1. **Implement string-replacement file editing** (old_str → new_str)
2. **Handle edge cases:** file creation, appending, ambiguous matches
3. **Validate inputs** and provide clear error messages
4. **Test your agent** by editing files through Claude

**Note:** The decorator infrastructure (`@tool`, Pydantic models, Agent class) is already complete. You only need to implement the function body marked with `TODO`.

---

## Exercise Instructions

### Step 1: Review What's Already Done

Open `agent_05_edit_exercise.py` and observe:

1. **Tool Registry System** (lines 26-93): Complete decorator infrastructure
2. **Pydantic Models** (lines 96-122): Includes `EditFileInput` with all three fields
3. **Completed Tools** (lines 127-178): `read_file`, `list_files`, `bash` all implemented
4. **TODO Tool** (lines 181-216): The `edit_file()` function needs implementation

The `edit_file` function already has its decorator:

```python
@tool(
    name="edit_file",
    description="Make edits to a text file by replacing 'old_str'...",
    input_model=EditFileInput,
)
def edit_file(path: str, old_str: str, new_str: str) -> str:
    # TODO: Your implementation here
    pass
```

### Step 2: Implement edit_file()

**Signature:** `def edit_file(path: str, old_str: str, new_str: str) -> str:`

**Requirements:**

1. **Input Validation:**
   - If `path` is empty, return `"Error: path cannot be empty"`
   - If `old_str == new_str`, return `"Error: old_str and new_str cannot be identical"`

2. **New File Creation (when old_str is empty):**
   - If file doesn't exist: create it with `new_str` as content
     - Use `file_path.parent.mkdir(parents=True, exist_ok=True)` to create directories
     - Return `f"Created new file: {path}"`
   - If file exists: append `new_str` to existing content
     - Return `f"Appended to file: {path}"`

3. **Normal Edit (when old_str is not empty):**
   - Read file content
   - Count occurrences of `old_str`:
     - If `count == 0`: return error with preview of what wasn't found
     - If `count > 1`: return error saying "found X times, need exactly 1 match"
     - If `count == 1`: perform replacement
   - Use `content.replace(old_str, new_str, 1)` to replace only first match
   - Write back to file
   - Return `f"Successfully edited {path}"`

4. **Error Handling:**
   - Wrap file operations in try/except blocks
   - Return descriptive error messages

**Implementation hints:**
```python
file_path = Path(path)

# For counting matches
count = content.count(old_str)

# For previews in error messages
preview = old_str[:50] + "..." if len(old_str) > 50 else old_str
```

### Step 3: Test Your Implementation

Run the agent:

```bash
python agent_05_edit_exercise.py --verbose
```

**Test cases:**

1. **Create new file:**
   ```
   You: Create a new file called test.txt with content "Hello World"
   Expected: File created successfully
   ```

2. **Edit existing content:**
   ```
   You: In test.txt, replace "World" with "Universe"
   Expected: Successfully edited test.txt
   ```

3. **Handle ambiguous matches:**
   ```
   You: In a file with duplicate "foo", replace "foo" with "bar"
   Expected: Error about multiple matches, needs more context
   ```

4. **Append to file:**
   ```
   You: Add a new line to test.txt with content "\nGoodbye"
   Expected: Appended to file
   ```

### Step 4: Compare with Solution

Check `agent_05_edit.py` to see the complete implementation. Notice how the decorator pattern kept your focus on business logic rather than plumbing.

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
