"""REST API example. pip install "groq-gemini-bridge[api]"
Run: uvicorn fastapi_app:app --reload   Docs: http://127.0.0.1:8000/docs"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from groq_gemini_bridge import Chatbot, LLMError, build_providers

app = FastAPI(title="Groq + Gemini Bridge")
PROVIDERS = build_providers()
sessions: dict[str, Chatbot] = {}  # in-memory; use Redis/DB in production


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    provider: str | None = None


@app.post("/chat")
def chat(req: ChatRequest):
    bot = sessions.setdefault(req.session_id, Chatbot(PROVIDERS))
    try:
        return bot.ask(req.message, req.provider)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except LLMError as e:
        raise HTTPException(502, str(e))
