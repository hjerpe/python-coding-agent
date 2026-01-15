# Section 0: Project Setup

## Learning Objectives

After completing this section, you will:

- Understand the project structure for a Python-based coding agent
- Have `uv` installed as your Python package manager
- Have the Anthropic Python SDK and `python-dotenv` installed
- Have test files ready for use throughout the tutorial
- Know how to set up your API key using a `.env` file
- Be ready to start building your first agent

---

## Key Concepts

### Project Structure

A clean project structure helps organize your code as you build increasingly complex agents:

```
python-coding-agent/
├── agents/                    # Your agent implementations
│   ├── agent_01_chat.py
│   ├── agent_02_read.py
│   └── ...
├── tutorial_materials/        # Learning materials (this folder)
├── test_files/               # Files to test your agent with
│   ├── fizzbuzz.js
│   └── riddle.txt
├── .env                      # API key (not committed to git)
├── .gitignore                # Git ignore file
└── requirements.txt          # Python dependencies
```

### The Anthropic Python SDK

The `anthropic` package provides a clean Python interface to Claude:

```python
from dotenv import load_dotenv
import anthropic

load_dotenv()  # Load API key from .env file

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY from environment
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Environment Variables

Your API key should be stored in a `.env` file for security:

```
ANTHROPIC_API_KEY=your-api-key-here
```

The `python-dotenv` package loads this file automatically when you call `load_dotenv()`.

---

## Implementation Outline

### Step 1: Create the Project Directory

Create a new directory for your project. This keeps your tutorial code separate from other projects.

```bash
mkdir ~/python-coding-agent
cd ~/python-coding-agent
```

### Step 2: Create the Directory Structure

Set up the folder hierarchy:

```bash
mkdir -p agents tutorial_materials test_files
```

### Step 3: Create requirements.txt

Create a `requirements.txt` file with the required dependencies:

```
anthropic>=0.39.0
python-dotenv>=1.0.0
```

### Step 4: Install Dependencies

Install `uv` if you haven't already (a fast Python package manager):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create a virtual environment and install the required packages:

```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
uv pip install -r requirements.txt
```

### Step 5: Set Up Your API Key

Get your API key from [console.anthropic.com](https://console.anthropic.com) and create a `.env` file:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

**Important**: Add `.env` to your `.gitignore` to avoid committing your API key:
```bash
echo ".env" >> .gitignore
```

### Step 6: Create Test Files

Create two test files that you'll use throughout the tutorial:

**test_files/fizzbuzz.js**:
```javascript
function fizzbuzz(n) {
    for (let i = 1; i <= n; i++) {
        if (i % 3 === 0 && i % 5 === 0) {
            console.log("FizzBuzz");
        } else if (i % 3 === 0) {
            console.log("Fizz");
        } else if (i % 5 === 0) {
            console.log("Buzz");
        } else {
            console.log(i);
        }
    }
}

fizzbuzz(100);
```

**test_files/riddle.txt**:
```
I speak without a mouth and hear without ears.
I have no body, but I come alive with the wind.
What am I?

Answer: An echo.
```

### Step 7: Verify Installation

Test that everything is working:

```bash
python -c "from dotenv import load_dotenv; import anthropic; load_dotenv(); print('Setup complete!')"
```

---

## Verification Checklist

Before moving to Section 1, verify:

- [ ] Project directory exists at `~/python-coding-agent`
- [ ] Directory structure is correct (`agents/`, `tutorial_materials/`, `test_files/`)
- [ ] `requirements.txt` contains `anthropic>=0.39.0` and `python-dotenv>=1.0.0`
- [ ] Anthropic SDK is installed (`uv pip list | grep anthropic`)
- [ ] `.env` file exists with `ANTHROPIC_API_KEY`
- [ ] `.env` is in `.gitignore`
- [ ] Test files exist (`fizzbuzz.js`, `riddle.txt`)

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

Install the SDK:
```bash
uv pip install anthropic
```

### "ModuleNotFoundError: No module named 'dotenv'"

Install python-dotenv:
```bash
uv pip install python-dotenv
```

### "Invalid API Key"

1. Check if the `.env` file exists and contains your key: `cat .env`
2. Verify the key format starts with `sk-ant-`
3. Make sure you're calling `load_dotenv()` before creating the client
4. Check your quota at [console.anthropic.com](https://console.anthropic.com)

### Python Version Issues

This tutorial requires Python 3.10+. Check your version:
```bash
python --version
```

If you have an older version, consider using `uv` to install a newer one:
```bash
uv python install 3.12
```

---

## Next Steps

You're ready to move on to **Section 1: Basic Chat**, where you'll build your first agent that can have a conversation with Claude!
