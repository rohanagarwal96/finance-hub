"""LLM text generation — HF Space (primary) with Groq fallback.

HF Space runs the fine-tuned Phi-3-mini model. On free-tier CPU the timeout
fires on every request in practice, so Groq handles all traffic until the
Space is upgraded to a GPU. Upgrade the Space hardware and this primary path
works with no code changes.
"""
import logging
import os

import httpx
from dotenv import load_dotenv

from services.groq_service import groq_complete

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

logger = logging.getLogger(__name__)

_SPACE_URL = os.environ.get("HUGGINGFACE_SPACE_URL", "").strip().strip('"').rstrip("/")
# 5s: intentionally short on free CPU tier — fires immediately, routing to Groq.
# Raise to 10s+ after upgrading the Space to GPU (inference then takes 2-5s).
_HF_TIMEOUT = 5.0


async def llm_generate(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Generate text. Tries HF Space first, falls back to Groq on any failure."""
    if _SPACE_URL:
        try:
            async with httpx.AsyncClient(timeout=_HF_TIMEOUT) as client:
                resp = await client.post(
                    f"{_SPACE_URL}/generate",
                    json={"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature},
                )
                resp.raise_for_status()
                return resp.json()["generated_text"]
        except Exception as exc:
            logger.info("HF Space unavailable (%s) — using Groq fallback", type(exc).__name__)

    return await groq_complete(
        prompt,
        system_prompt="You are a knowledgeable financial assistant. Answer clearly and concisely.",
        max_tokens=max_tokens,
        temperature=temperature,
    )
