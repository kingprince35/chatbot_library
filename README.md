# chatrelay

Chatbot library for **Groq** and **Gemini**. Give it multiple API keys; when one hits its
rate limit it automatically switches to the next.

## Install
```bash
pip install chatrelay
```

## Setup
Set environment variables (comma-separated keys):
```bash
export GROQ_API_KEYS="groq_key_1,groq_key_2"
export GEMINI_API_KEYS="gemini_key_1,gemini_key_2"
```

## Use in code
```python
from chatrelay import Chatbot, build_providers

bot = Chatbot(build_providers(), system_prompt="You are a helpful assistant.")
result = bot.ask("What is Python?")
print(result["provider"], result["reply"])   # e.g. groq-1 ...

bot.ask("Explain more")                      # remembers the conversation
bot.ask("Hi", provider="gemini")             # prefer a provider ("gemini") or one key ("groq-2")
bot.reset()                                  # clear history
```

## Terminal chat
```bash
pip install "chatrelay[cli]"

chatrelay "What is Python?"    # one-shot: prints the answer and exits
chatrelay                      # interactive mode: /groq /gemini /auto /reset /quit
```

## How failover works
Order: groq-1 -> groq-2 -> gemini-1 -> gemini-2. A key that returns HTTP 429 is skipped
for 60s (or the `Retry-After` time). If all keys fail, `LLMError` is raised.

## REST API example
See `examples/fastapi_app.py` (`pip install "chatrelay[api]"`).
