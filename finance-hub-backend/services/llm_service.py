"""Async HTTP wrapper for the HuggingFace Space /generate endpoint."""
import asyncio
import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

_SPACE_URL = os.environ["HUGGINGFACE_SPACE_URL"].strip().strip('"').rstrip("/")
_TIMEOUT = 120.0
_MAX_RETRIES = 3


async def llm_generate(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Call the HF Space /generate endpoint with retry + exponential backoff.

    Returns the generated text string.
    Raises HTTPException(503) if all retries fail.
    """
    payload = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}

    for attempt in range(_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(f"{_SPACE_URL}/generate", json=payload)
                resp.raise_for_status()
                return resp.json()["generated_text"]
        except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.ConnectError) as exc:
            if attempt == _MAX_RETRIES - 1:
                raise HTTPException(
                    status_code=503,
                    detail=f"LLM service unavailable after {_MAX_RETRIES} retries: {exc}",
                )
            wait = 2 ** attempt
            await asyncio.sleep(wait)

    raise HTTPException(status_code=503, detail="LLM service unavailable")
