"""LLM text generation via HF Inference API — rohan1324/phi3-mini-finance-merged."""
import asyncio
import logging
import os

import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

logger = logging.getLogger(__name__)

_MODEL_ID = "rohan1324/phi3-mini-finance-merged"
_API_URL = f"https://router.huggingface.co/hf-inference/models/{_MODEL_ID}"
_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN", "").strip().strip('"')
_HEADERS = {"Authorization": f"Bearer {_TOKEN}"}


def _run_inference(prompt: str, max_tokens: int, temperature: float) -> str:
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": max(temperature, 0.01),
            "do_sample": temperature > 0,
            "return_full_text": False,
        },
    }
    resp = requests.post(_API_URL, headers=_HEADERS, json=payload, timeout=120)
    logger.info("HF API status: %d | body: %s", resp.status_code, resp.text[:500])
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list) and data:
        return data[0].get("generated_text", "")
    raise RuntimeError(f"Unexpected HF API response: {data}")


async def llm_generate(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Generate text via HF Inference API. Raises HTTPException(503) on failure."""
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _run_inference, prompt, max_tokens, temperature)
    except Exception as exc:
        logger.error("HF Inference API error: %s", exc)
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {exc}")
