"""Groq API client for Llama 3.1 70B — used for Modules 3, 5, 6."""
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import HTTPException
from groq import AsyncGroq

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

_client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"].strip().strip('"'))
_MODEL = "llama-3.1-70b-versatile"


async def groq_complete(
    prompt: str,
    system_prompt: str = "You are a professional financial analyst.",
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> str:
    """Single-turn Groq completion. Returns full response text."""
    try:
        response = await _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Groq API error: {exc}")


async def groq_complete_with_history(
    messages: list[dict],
    system_prompt: str = "You are a professional financial analyst.",
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> str:
    """Multi-turn Groq completion with full message history."""
    try:
        response = await _client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Groq API error: {exc}")
