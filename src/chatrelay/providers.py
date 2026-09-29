"""LLM providers. One instance = one API key. Rate-limited keys get a cooldown."""
import os
import time
from abc import ABC, abstractmethod

import requests


class LLMError(Exception):
    """Any provider failure (network, auth, bad response...)."""


class RateLimitError(LLMError):
    """Key hit its limit (HTTP 429) -> switch to the next key."""


class BaseProvider(ABC):
    name = "base"
    COOLDOWN = 60  # seconds to skip a key after it hits its limit

    def __init__(self, api_key: str | None, model: str, label: str, timeout: int = 30):
        if not api_key:
            raise ValueError(f"{self.name}: API key is missing")
        self.api_key = api_key
        self.model = model
        self.label = label          # e.g. "groq-1", "groq-2"
        self.timeout = timeout
        self.cooldown_until = 0.0

    @property
    def available(self) -> bool:
        return time.time() >= self.cooldown_until

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        ...

    def _post(self, url: str, headers: dict, body: dict) -> dict:
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=self.timeout)
        except requests.RequestException as e:
            raise LLMError(f"{self.label}: network error: {e}") from e

        if resp.status_code == 429:  # limit reached
            wait = resp.headers.get("Retry-After", "")
            self.cooldown_until = time.time() + (int(wait) if wait.isdigit() else self.COOLDOWN)
            raise RateLimitError(f"{self.label}: rate limit hit")
        if resp.status_code != 200:
            raise LLMError(f"{self.label}: HTTP {resp.status_code}: {resp.text[:300]}")
        return resp.json()


class GroqProvider(BaseProvider):
    """OpenAI-compatible API, messages go in as-is."""
    name = "groq"
    URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key, label="groq-1", model=None, timeout=30):
        super().__init__(api_key, model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                         label, timeout)

    def chat(self, messages):
        data = self._post(self.URL,
                          {"Authorization": f"Bearer {self.api_key}"},
                          {"model": self.model, "messages": messages})
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise LLMError(f"{self.label}: unexpected response: {data}") from e


class GeminiProvider(BaseProvider):
    """Own format, so we convert (adapter pattern)."""
    name = "gemini"
    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, api_key, label="gemini-1", model=None, timeout=30):
        super().__init__(api_key, model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                         label, timeout)

    def chat(self, messages):
        system = [m["content"] for m in messages if m["role"] == "system"]
        contents = [
            {"role": "model" if m["role"] == "assistant" else "user",
             "parts": [{"text": m["content"]}]}
            for m in messages if m["role"] != "system"
        ]
        body = {"contents": contents}
        if system:
            body["systemInstruction"] = {"parts": [{"text": "\n".join(system)}]}

        data = self._post(self.URL.format(model=self.model),
                          {"x-goog-api-key": self.api_key}, body)
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise LLMError(f"{self.label}: unexpected response: {data}") from e


def _read_keys(plural: str, singular: str) -> list[str]:
    """GROQ_API_KEYS=k1,k2 (preferred) or GROQ_API_KEY=k1."""
    raw = os.getenv(plural) or os.getenv(singular) or ""
    return [k.strip() for k in raw.split(",") if k.strip()]


def build_providers() -> dict[str, BaseProvider]:
    """One provider per key. Order = try order (groq-1, groq-2, gemini-1, gemini-2)."""
    providers = {}
    for cls, env in ((GroqProvider, "GROQ"), (GeminiProvider, "GEMINI")):
        for i, key in enumerate(_read_keys(f"{env}_API_KEYS", f"{env}_API_KEY"), start=1):
            label = f"{cls.name}-{i}"
            providers[label] = cls(key, label=label)
    if not providers:
        raise RuntimeError("Set GROQ_API_KEYS and/or GEMINI_API_KEYS in .env")
    return providers
