> **Note**: This is a Python implementation of [How to Build a Coding Agent](https://github.com/ghuntley/how-to-build-a-coding-agent), originally created in Go by [Geoffrey Huntley](https://github.com/ghuntley).

# How to Build a Python Coding Agent

Build your own AI coding agent step-by-step using Python and the Anthropic API.

## Quick Start

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# 3. Set your API key
export ANTHROPIC_API_KEY="your-api-key-here"

# 4. Run the final agent
uv run python agents/agent_06_search.py
```

## Tutorial Structure

```
python-coding-agent/
├── agents/                    # Python implementations
│   ├── agent_01_chat.py       # Basic chat (complete)
│   ├── agent_01_chat_exercise.py
│   ├── agent_02_read.py       # + Read file tool
│   ├── agent_02_read_exercise.py
│   ├── agent_03_list_files.py # + List files tool
│   ├── agent_03_list_files_exercise.py
│   ├── agent_04_bash.py       # + Bash tool
│   ├── agent_04_bash_exercise.py
│   ├── agent_05_edit.py       # + Edit file tool
│   ├── agent_05_edit_exercise.py
│   ├── agent_06_search.py     # + Code search tool (final)
│   └── agent_06_search_exercise.py
├── tutorial_materials/        # Learning materials
│   ├── TUTORIAL_00_setup.md
│   ├── TUTORIAL_01_basic_chat.md
│   ├── TUTORIAL_02_read_file.md
│   ├── TUTORIAL_03_list_files.md
│   ├── TUTORIAL_04_bash.md
│   ├── TUTORIAL_05_edit_file.md
│   └── TUTORIAL_06_code_search.md
├── test_files/               # Test files for the agent
│   ├── fizzbuzz.js
│   └── riddle.txt
└── requirements.txt
```

## Sections

| Section | Topic | Tools Added |
|---------|-------|-------------|
| 0 | Setup | (project setup) |
| 1 | Basic Chat | None (conversation only) |
| 2 | Read File Tool | `read_file` |
| 3 | List Files Tool | `list_files` |
| 4 | Bash Tool | `bash` |
| 5 | Edit File Tool | `edit_file` |
| 6 | Code Search Tool | `code_search` |

## How to Learn

Each section includes:

1. **Learning Objectives** - What you'll understand
2. **Key Concepts** - New patterns and APIs
3. **Implementation Outline** - Step-by-step guide
4. **Complete Solution** - Working reference code
5. **Exercise File** - Skeleton with TODOs
6. **Test Commands** - Verification prompts

**Recommended approach:**
1. Read the learning material in `tutorial_materials/`
2. Try implementing using the exercise file
3. Compare to the complete solution
4. Test with the provided commands

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (fast Python package installer)
- Anthropic API key
- ripgrep (`rg`) for Section 6

## Test Your Agent

After completing all sections:

```bash
uv run python agents/agent_06_search.py
```

Try these prompts:
- "Read test_files/fizzbuzz.js"
- "List all files in this folder"
- "Run git status"
- "Add a comment to the top of test_files/fizzbuzz.js"
- "Find all function definitions"
