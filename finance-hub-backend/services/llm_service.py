"""Async HTTP wrapper for the HuggingFace Space /generate endpoint."""
import asyncio
import logging
import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

logger = logging.getLogger(__name__)

_SPACE_URL = os.environ["HUGGINGFACE_SPACE_URL"].strip().strip('"').rstrip("/")
_TIMEOUT = 180.0  # HF free spaces need up to 60s to wake from sleep
_MAX_RETRIES = 5


async def _wake_space() -> None:
    """Ping the space root to trigger wake-up before the actual request."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.get(_SPACE_URL)
    except Exception:
        pass  # Wake ping is best-effort


async def llm_generate(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Call the HF Space /generate endpoint with retry + exponential backoff.

    Free-tier spaces sleep after inactivity and need ~60s to cold-start.
    This function pings the space to trigger wake-up, then retries patiently.
    """
    payload = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}

    await _wake_space()

    for attempt in range(_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(f"{_SPACE_URL}/generate", json=payload)
                resp.raise_for_status()
                return resp.json()["generated_text"]
        except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.ConnectError) as exc:
            logger.warning("HF Space attempt %d/%d failed: %s", attempt + 1, _MAX_RETRIES, exc)
            if attempt == _MAX_RETRIES - 1:
                raise HTTPException(
                    status_code=503,
                    detail=f"LLM service unavailable after {_MAX_RETRIES} retries: {exc}",
                )
            wait = min(2 ** attempt * 5, 60)  # 5s, 10s, 20s, 40s, 60s
            await asyncio.sleep(wait)

    raise HTTPException(status_code=503, detail="LLM service unavailable")
