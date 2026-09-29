"""Chatbot: conversation memory + automatic key/provider fallback."""
from .providers import BaseProvider, LLMError


class Chatbot:
    def __init__(self, providers: dict[str, BaseProvider],
                 system_prompt: str = "You are a helpful assistant.",
                 max_history: int = 20):
        self.providers = providers
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.history: list[dict] = []

    def _order(self, preferred: str | None) -> list[BaseProvider]:
        """preferred can be a type ("groq") or one key ("groq-2")."""
        items = list(self.providers.values())
        if preferred:
            first = [p for p in items if preferred in (p.name, p.label)]
            if not first:
                raise ValueError(f"Unknown provider '{preferred}'. Use: "
                                 f"{sorted({p.name for p in items} | set(self.providers))}")
            items = first + [p for p in items if p not in first]
        # keys in cooldown (recently rate-limited) go last, order otherwise kept
        return sorted(items, key=lambda p: not p.available)

    def ask(self, text: str, provider: str | None = None) -> dict:
        if not text.strip():
            raise ValueError("Message is empty")

        user_msg = {"role": "user", "content": text}
        messages = ([{"role": "system", "content": self.system_prompt}]
                    + self.history[-self.max_history:] + [user_msg])

        errors = {}
        for p in self._order(provider):
            try:
                reply = p.chat(messages)
            except LLMError as e:       # includes RateLimitError -> next key
                errors[p.label] = str(e)
                continue
            self.history += [user_msg, {"role": "assistant", "content": reply}]
            return {"provider": p.label, "reply": reply, "skipped": errors}

        raise LLMError(f"All keys failed: {errors}")

    def reset(self):
        self.history.clear()
