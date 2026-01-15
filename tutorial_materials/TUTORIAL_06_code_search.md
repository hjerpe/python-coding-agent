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

## Implementation Outline

### Step 1: Add the Code Search Tool Definition

Define the tool with optional parameters:

```python
{
    "name": "code_search",
    "description": "Search for code patterns using ripgrep (rg). Returns matching lines with file names and line numbers.",
    "input_schema": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "The search pattern or regex"
            },
            "path": {
                "type": "string",
                "description": "Optional path to search in. Defaults to current directory."
            },
            "file_type": {
                "type": "string",
                "description": "Optional file type filter (e.g., 'py', 'js', 'go')"
            },
            "case_sensitive": {
                "type": "boolean",
                "description": "Whether search is case-sensitive. Defaults to false."
            }
        },
        "required": ["pattern"]
    }
}
```

### Step 2: Build the Command Arguments

Create a function that builds ripgrep arguments:

```python
def code_search(pattern: str, path: str = ".", file_type: str = None, case_sensitive: bool = False) -> str:
    args = ["rg", "--line-number", "--with-filename", "--color=never"]

    if not case_sensitive:
        args.append("--ignore-case")

    if file_type:
        args.extend(["--type", file_type])

    args.append(pattern)
    args.append(path)
```

**Why these flags**:
- `--line-number`: Show line numbers for each match
- `--with-filename`: Always show filename (even for single file)
- `--color=never`: Plain output (no ANSI codes)
- `--ignore-case`: Case-insensitive by default (friendlier)

### Step 3: Execute and Handle Exit Codes

Run the command and handle ripgrep's exit codes:

```python
result = subprocess.run(args, capture_output=True, text=True)

# Exit code 1 means no matches (not an error)
if result.returncode == 1:
    return "No matches found"

# Other non-zero codes are real errors
if result.returncode != 0:
    return f"Search error: {result.stderr}"

output = result.stdout.strip()
```

**Pitfall**: Don't treat exit code 1 as an error!

### Step 4: Implement Output Limiting

Prevent overwhelming Claude with too many matches:

```python
MAX_MATCHES = 50

if output:
    lines = output.split("\n")
    if len(lines) > MAX_MATCHES:
        truncated = lines[:MAX_MATCHES]
        return "\n".join(truncated) + f"\n\n... (showing first {MAX_MATCHES} of {len(lines)} matches)"

return output if output else "No matches found"
```

### Step 5: Update the Tool Dispatcher

Add the code_search case:

```python
elif name == "code_search":
    return code_search(
        tool_input["pattern"],
        tool_input.get("path", "."),
        tool_input.get("file_type"),
        tool_input.get("case_sensitive", False),
    )
```

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
   python agents/agent_06_search.py --verbose
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
