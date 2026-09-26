"""
LLM call abstraction. Two providers wired up for MVP:

- ollama (default): free, local, requires Ollama running on the host with
  the model already pulled (`ollama pull llama3.1:8b`). No API key needed.
- openai: hosted, costs money, used if LLM_PROVIDER=openai.

Swapping providers is a .env change only - callers use `generate_answer`.
"""
import httpx

from app.config import settings


def generate_answer(system_prompt: str, user_prompt: str) -> str:
    if settings.llm_provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""

    # ollama
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(
            f"{settings.ollama_base_url}/api/chat",
            json={
                "model": settings.ollama_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")
