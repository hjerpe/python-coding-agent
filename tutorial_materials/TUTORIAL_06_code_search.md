# Section 6: Code Search Tool

## Learning Objectives

After completing this section, you will:

- Know how to integrate ripgrep (`rg`) for powerful pattern searching
- Understand how to build dynamic command-line arguments
- Learn to handle ripgrep's exit codes correctly
- Implement output limiting to prevent overwhelming responses
- Have a complete, fully-featured coding agent!

---

## Key Concepts

### Why Ripgrep?

Ripgrep (`rg`) is a line-oriented search tool that recursively searches directories for regex patterns:
- **Fast**: Much faster than grep for large codebases
- **Smart**: Respects `.gitignore` by default
- **Powerful**: Full regex support with flexible output options

### Building Dynamic Commands

Build ripgrep arguments based on optional parameters:

```python
args = ["rg", "--line-number", "--with-filename", "--color=never"]

if not case_sensitive:
    args.append("--ignore-case")

if file_type:
    args.extend(["--type", file_type])

args.append(pattern)
args.append(path or ".")
```

### Exit Code Handling

Ripgrep's exit codes have specific meanings:
- **0**: Matches found
- **1**: No matches found (not an error!)
- **2**: Actual error (bad regex, file not found, etc.)

```python
result = subprocess.run(args, capture_output=True, text=True)

if result.returncode == 1:
    return "No matches found"
elif result.returncode != 0:
    return f"Error: {result.stderr}"
```

### Output Limiting

Large search results can overwhelm Claude's context. Limit output:

```python
MAX_MATCHES = 50
lines = output.strip().split("\n")
if len(lines) > MAX_MATCHES:
    truncated = lines[:MAX_MATCHES]
    return "\n".join(truncated) + f"\n\n... (showing first {MAX_MATCHES} of {len(lines)} matches)"
return output
```

---

## Architecture Note: Decorator Pattern

This is the final tutorial in the series, and it uses the same decorator-based architecture as Sections 3-5. All infrastructure is pre-written in the exercise file - you only implement the `code_search()` function body.

If you've completed the previous exercises, you're now familiar with this pattern:
1. Pydantic model defines inputs
2. `@tool` decorator registers the function
3. Implementation focuses on core logic only

For a complete explanation of this architecture, see TUTORIAL_03_list_files.md (line 92+) or TUTORIAL_04_bash.md.

---

## What You'll Do

In this final exercise, you'll implement the `code_search()` tool using ripgrep:

1. **Build ripgrep commands** with dynamic arguments (case sensitivity, file types)
2. **Parse ripgrep output** and handle exit codes
3. **Limit results** to prevent overwhelming responses
4. **Test your complete coding agent** with all 5 tools working together

**Note:** All decorator infrastructure is pre-written. You only implement the TODO'd function body.

---

## Exercise Instructions

### Step 1: Review the Complete Architecture

Open `agent_06_search_exercise.py` and observe the full structure:

1. **Tool Registry System** (lines 26-93): Decorator infrastructure
2. **Pydantic Models** (lines 96-139): Five models including `CodeSearchInput` with all fields
3. **Completed Tools** (lines 144-246): `read_file`, `list_files`, `bash`, and `edit_file` all working
4. **TODO Tool** (lines 249-292): The `code_search()` function needs implementation

The function already has its decorator:

```python
@tool(
    name="code_search",
    description="Search for code patterns using ripgrep...",
    input_model=CodeSearchInput,
)
def code_search(
    pattern: str,
    path: str = ".",
    file_type: str | None = None,
    case_sensitive: bool = False,
) -> str:
    # TODO: Your implementation here
    pass
```

### Step 2: Implement code_search()

**Signature:**
```python
def code_search(
    pattern: str,
    path: str = ".",
    file_type: str | None = None,
    case_sensitive: bool = False
) -> str:
```

**Requirements:**

1. **Input Validation:**
   - If `pattern` is empty, return `"Error: pattern cannot be empty"`

2. **Build ripgrep command:**
   ```python
   args = ["rg", "--line-number", "--with-filename", "--color=never"]

   if not case_sensitive:
       args.append("--ignore-case")

   if file_type:
       args.extend(["--type", file_type])

   args.append(pattern)
   args.append(path)
   ```

3. **Execute and handle results:**
   ```python
   result = subprocess.run(args, capture_output=True, text=True)

   # Exit code 1 means no matches (not an error)
   if result.returncode == 1:
       return "No matches found"

   # Other non-zero codes are errors
   if result.returncode != 0:
       return f"Search error: {result.stderr}"
   ```

4. **Limit output:**
   ```python
   output = result.stdout.strip()
   MAX_MATCHES = 50
   lines = output.split("\n")

   if len(lines) > MAX_MATCHES:
       truncated = lines[:MAX_MATCHES]
       return "\n".join(truncated) + f"\n\n... (showing first {MAX_MATCHES} of {len(lines)} matches)"
   ```

5. **Handle missing ripgrep:**
   ```python
   except FileNotFoundError:
       return "Error: ripgrep (rg) is not installed. Install it with: brew install ripgrep"
   ```

### Step 3: Test Your Complete Agent

Run the agent:

```bash
uv run python agent_06_search_exercise.py --verbose
```

**Test cases demonstrating all 5 tools:**

1. **Search for pattern:**
   ```
   You: Search for the word "Agent" in Python files
   Expected: Shows matches with line numbers
   ```

2. **Read file from search results:**
   ```
   You: Read the file agent_03_list_files.py
   Expected: Shows full file content
   ```

3. **Edit code based on search:**
   ```
   You: In test_file.py, replace "old_function" with "new_function"
   Expected: Performs edit
   ```

4. **Verify with bash:**
   ```
   You: Run "git diff test_file.py" to see the changes
   Expected: Shows git diff output
   ```

5. **List directory structure:**
   ```
   You: List all files in the tutorial_materials directory
   Expected: Shows directory tree
   ```

### Step 4: Reflect on the Architecture

You've now built a complete coding agent with 5 tools:
- `read_file`
- `list_files`
- `bash`
- `edit_file`
- `code_search`

Thanks to the decorator pattern:
- Each tool required only **one function** + **one Pydantic model**
- No manual tool registration
- No execute_tool() if/elif chains
- Automatic input validation

Compare this to what it would look like with manual registration - you'd have:
- 5 tool definitions in `self.tools` list (~100 lines of JSON schema)
- 5 branches in `execute_tool()` if/elif chain (~25 lines)
- Manual input validation in each branch (~50 lines)
- Total: ~175 lines of boilerplate

With decorators: **0 lines of boilerplate**. All infrastructure is reusable.

### Next Steps

You now have all the foundational skills to build powerful AI agents:

1. **Tool-based architectures:** Giving LLMs structured capabilities
2. **Agentic loops:** Iterating until task completion
3. **State management:** Maintaining conversation context
4. **Error handling:** Graceful failures and recovery
5. **Scalable patterns:** Decorator-based tool registration

**Extensions to try:**
- Add more tools (git operations, API calls, data processing)
- Implement tool chaining (output of one tool → input of another)
- Add conversation memory/summarization for long sessions
- Build specialized agents (code reviewer, test generator, doc writer)

---

## Test Commands

After implementing, test your complete coding agent:

1. **Basic search**:
   ```
   You: Find all function definitions in test_files
   ```
   Expected: Claude searches for "function" and shows matches.

2. **Regex search**:
   ```
   You: Search for lines containing numbers in test_files/fizzbuzz.js
   ```
   Expected: Claude uses regex like `\d+` to find numbers.

3. **File type filter**:
   ```
   You: Search for "console" only in JavaScript files
   ```
   Expected: Claude uses `--type js` filter.

4. **Case-sensitive search**:
   ```
   You: Search for "FizzBuzz" case-sensitively
   ```
   Expected: Claude uses case-sensitive mode.

5. **Search and read**:
   ```
   You: Find where fizzbuzz is called and show me that file
   ```
   Expected: Claude searches, then reads the file.

6. **Search, edit, verify**:
   ```
   You: Find "fizzbuzz(100)" and change 100 to 50
   ```
   Expected: Claude searches, edits, and confirms.

7. **Complex task**:
   ```
   You: Find all console.log statements and add a comment above each one explaining what it logs
   ```
   Expected: Claude uses search, read, and edit tools in sequence.

8. **Verbose mode**:
   ```bash
   uv run python agents/agent_06_search.py --verbose
   ```
   Then: Run searches and observe the ripgrep commands.

---

## Congratulations!

You've built a complete coding agent with:

- **Read File**: Examine file contents
- **List Files**: Explore directory structure
- **Bash**: Run shell commands
- **Edit File**: Modify and create files
- **Code Search**: Find patterns across the codebase

This is the foundation of powerful AI coding assistants. From here, you could extend it with:

- Git integration (commit, diff, branch)
- LSP integration (go-to-definition, find references)
- Web search capabilities
- Multi-file refactoring
- Test running and coverage

Happy coding!
