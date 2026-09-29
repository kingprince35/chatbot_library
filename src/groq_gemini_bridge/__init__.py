"""groq-gemini-bridge: one chatbot interface for Groq and Gemini with key failover."""
from .chatbot import Chatbot
from .providers import (BaseProvider, GeminiProvider, GroqProvider, LLMError,
                        RateLimitError, build_providers)

__version__ = "0.1.0"
__all__ = ["Chatbot", "BaseProvider", "GroqProvider", "GeminiProvider",
           "LLMError", "RateLimitError", "build_providers"]
