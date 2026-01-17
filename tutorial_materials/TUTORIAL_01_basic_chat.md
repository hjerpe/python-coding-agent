# Section 1: Basic Chat

## Learning Objectives

After completing this section, you will:

- Understand how to connect to the Anthropic API using the Python SDK
- Know the message/conversation pattern for multi-turn dialogue
- Be able to build a core event loop that maintains conversation history
- Handle user input/output in a terminal-based chat interface
- Use the logging module for debug output

---

## Key Concepts

### The Anthropic Client

The Anthropic Python SDK provides a simple client that automatically uses your API key:

```python
import anthropic

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var
```

### Message Structure

Claude's API uses a conversation array where each message has a `role` and `content`:

```python
messages = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there! How can I help?"},
    {"role": "user", "content": "What's 2+2?"}
]
```

The roles alternate between `"user"` and `"assistant"`.

### The Messages API

Send messages to Claude with `client.messages.create()`:

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=conversation
)
```

### Response Structure

The response contains a `content` array with content blocks:

```python
for block in response.content:
    if hasattr(block, "text"):
        print(block.text)
```

### The Agent Class Pattern

Encapsulate the client and conversation logic in a class:

```python
import logging

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def run(self):
        # Main conversation loop
        pass
```

---

## Implementation Outline

### Step 1: Set Up Imports and Argument Parsing

Start with the necessary imports and a way to enable verbose mode:

```python
import argparse
import logging
import anthropic

def main():
    parser = argparse.ArgumentParser(description="Basic chat agent")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    # Configure logging based on verbose flag
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="[%(levelname)s] %(message)s",
    )
    # ... create and run agent
```

**Why**: Argument parsing lets users enable debugging output when needed. The logging module provides a professional, standard way to handle debug output.

### Step 2: Create the Agent Class

Define a class to hold the Anthropic client:

```python
logger = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        self.client = anthropic.Anthropic()
```

**Why**: Encapsulating state in a class keeps the code organized and extensible. The module-level logger is created using `__name__` to identify where log messages come from.

### Step 3: Implement the Conversation Loop

Create a `run()` method with an infinite loop that:
1. Prompts for user input
2. Handles empty input (skip)
3. Adds the user message to the conversation
4. Calls the API
5. Adds the assistant response to the conversation
6. Prints the response

```python
def run(self):
    conversation = []

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue

        conversation.append({"role": "user", "content": user_input})
        # ... call API and process response
```

**Pitfall**: Don't forget to strip whitespace from input!

### Step 4: Call the API

Inside the loop, call `client.messages.create()`:

```python
response = self.client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=conversation
)
```

**Why**: We pass the entire conversation history so Claude has context.

### Step 5: Process the Response

Add the response to the conversation and print text blocks:

```python
conversation.append({"role": "assistant", "content": response.content})

for block in response.content:
    if hasattr(block, "text"):
        print(f"\nAssistant: {block.text}")
```

**Why**: The response content is a list of blocks (text, tool_use, etc.).

### Step 6: Add Debug Logging

Add debug output using the logger:

```python
logger.debug(f"Sending {len(conversation)} messages")
logger.debug(f"Response stop_reason: {response.stop_reason}")
```

**Why**: Using Python's logging module provides a professional, standard way to output debug information. The `--verbose` flag controls the log level in main(), so these debug messages only appear when verbose mode is enabled.

### Step 7: Handle Keyboard Interrupt

Wrap the main loop in try/except for clean exit:

```python
try:
    while True:
        # ... conversation loop
except KeyboardInterrupt:
    print("\n\nGoodbye!")
```

---

## Test Commands

After implementing, test your agent with these prompts:

1. **Basic greeting**:
   ```
   You: Hello!
   ```
   Expected: Claude responds with a greeting.

2. **Follow-up question** (tests conversation history):
   ```
   You: My name is Alice.
   You: What's my name?
   ```
   Expected: Claude remembers your name from the previous message.

3. **Multi-turn reasoning**:
   ```
   You: I'm thinking of a number between 1 and 10. It's even.
   You: It's also greater than 5.
   You: What number am I thinking of?
   ```
   Expected: Claude uses context from previous messages.

4. **Verbose mode**:
   ```bash
   uv run python agents/agent_01_chat.py --verbose
   ```
   Expected: See debug output showing message counts and stop reasons.

---

## Next Steps

In **Section 2: Read File Tool**, you'll extend this basic chat to give Claude the ability to read files from your filesystem!
