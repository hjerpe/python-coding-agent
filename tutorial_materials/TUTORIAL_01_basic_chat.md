# Section 1: Basic Chat

## Learning Objectives

After completing this section, you will:

- Understand how to connect to the Anthropic API using the Python SDK
- Know the message/conversation pattern for multi-turn dialogue
- Be able to build a core event loop that maintains conversation history
- Handle user input/output in a terminal-based chat interface
- Use the `--verbose` flag pattern for debugging

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
class Agent:
    def __init__(self, verbose: bool = False):
        self.client = anthropic.Anthropic()
        self.verbose = verbose

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
import anthropic

def main():
    parser = argparse.ArgumentParser(description="Basic chat agent")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    # ... create and run agent
```

**Why**: Argument parsing lets users enable debugging output when needed.

### Step 2: Create the Agent Class

Define a class to hold the Anthropic client and configuration:

```python
class Agent:
    def __init__(self, verbose: bool = False):
        self.client = anthropic.Anthropic()
        self.verbose = verbose
```

**Why**: Encapsulating state in a class keeps the code organized and extensible.

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

### Step 6: Add Verbose Logging

Add debug output when verbose mode is enabled:

```python
if self.verbose:
    print(f"[DEBUG] Sending {len(conversation)} messages")
    print(f"[DEBUG] Response stop_reason: {response.stop_reason}")
```

**Why**: Verbose logging helps diagnose issues during development.

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

## Complete Solution

Save this as `agents/agent_01_chat.py`:

```python
#!/usr/bin/env python3
"""
Basic Chat Agent - Section 1

A simple chatbot that talks to Claude with no tools.
This is the foundation for more advanced agents.
"""

import argparse

import anthropic


class Agent:
    """A basic chat agent that maintains conversation history."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the agent.

        Args:
            verbose: If True, print debug information
        """
        self.client = anthropic.Anthropic()
        self.verbose = verbose

    def run(self) -> None:
        """Run the main conversation loop."""
        conversation: list[dict] = []

        print("Chat with Claude (Ctrl+C to exit)")
        print("-" * 40)

        try:
            while True:
                # Get user input
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue

                # Add user message to conversation
                conversation.append({"role": "user", "content": user_input})

                if self.verbose:
                    print(f"[DEBUG] Sending {len(conversation)} messages")

                # Call the API
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=conversation,
                )

                if self.verbose:
                    print(f"[DEBUG] Response stop_reason: {response.stop_reason}")

                # Add assistant response to conversation
                conversation.append({"role": "assistant", "content": response.content})

                # Print the response
                for block in response.content:
                    if hasattr(block, "text"):
                        print(f"\nAssistant: {block.text}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")


def main():
    """Entry point for the chat agent."""
    parser = argparse.ArgumentParser(description="Basic chat agent using Claude")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()

    agent = Agent(verbose=args.verbose)
    agent.run()


if __name__ == "__main__":
    main()
```

---

## Exercise File

Save this as `agents/agent_01_chat_exercise.py` and implement the TODOs:

```python
#!/usr/bin/env python3
"""
Basic Chat Agent - Section 1 (Exercise)

Implement the TODOs to create a basic chatbot.
"""

import argparse

import anthropic


class Agent:
    """A basic chat agent that maintains conversation history."""

    def __init__(self, verbose: bool = False):
        """
        Initialize the agent.

        Args:
            verbose: If True, print debug information
        """
        # TODO: Initialize the Anthropic client
        # Hint: Use anthropic.Anthropic()
        self.client = None  # Replace with actual client

        self.verbose = verbose

    def run(self) -> None:
        """Run the main conversation loop."""
        # TODO: Initialize an empty conversation list
        conversation = None  # Replace with actual list

        print("Chat with Claude (Ctrl+C to exit)")
        print("-" * 40)

        try:
            while True:
                # TODO: Get user input using input() and strip whitespace
                user_input = None  # Replace with actual input

                # TODO: Skip empty input
                # Hint: Use 'continue' if user_input is empty

                # TODO: Add user message to conversation
                # Hint: Append a dict with "role" and "content" keys

                if self.verbose:
                    print(f"[DEBUG] Sending {len(conversation)} messages")

                # TODO: Call the API using self.client.messages.create()
                # Required parameters:
                # - model: "claude-sonnet-4-20250514"
                # - max_tokens: 1024
                # - messages: conversation
                response = None  # Replace with actual API call

                if self.verbose:
                    print(f"[DEBUG] Response stop_reason: {response.stop_reason}")

                # TODO: Add assistant response to conversation
                # Hint: The response content is in response.content

                # TODO: Print the response text
                # Hint: Loop through response.content and check for text attribute
                pass

        except KeyboardInterrupt:
            print("\n\nGoodbye!")


def main():
    """Entry point for the chat agent."""
    parser = argparse.ArgumentParser(description="Basic chat agent using Claude")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose debug output"
    )
    args = parser.parse_args()

    agent = Agent(verbose=args.verbose)
    agent.run()


if __name__ == "__main__":
    main()
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
   python agents/agent_01_chat.py --verbose
   ```
   Expected: See debug output showing message counts and stop reasons.

---

## Next Steps

In **Section 2: Read File Tool**, you'll extend this basic chat to give Claude the ability to read files from your filesystem!
