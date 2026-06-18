"""Remote embeddings via HuggingFace Inference API.

Replaces the local FastEmbed/ONNX model to eliminate the ~300 MB memory spike
that caused OOM crashes on Render's 512 MB free tier.
The same model (all-MiniLM-L6-v2, 384 dims) is used so existing Pinecone
vectors remain valid and no index rebuild is needed.
"""
from __future__ import annotations

import logging
import os
import time

import httpx

logger = logging.getLogger(__name__)

_HF_TOKEN = os.environ.get("HF_TOKEN", "")
_EMBED_URL = (
    "https://api-inference.huggingface.co/models/"
    "sentence-transformers/all-MiniLM-L6-v2"
)
_BATCH_SIZE = 32  # stay well under HF payload limits


def _headers() -> dict[str, str]:
    if _HF_TOKEN:
        return {"Authorization": f"Bearer {_HF_TOKEN}"}
    return {}


def _post_with_retry(texts: list[str], retries: int = 3) -> list[list[float]]:
    """POST to HF Inference API, retrying on 503 (model cold-starting)."""
    for attempt in range(retries):
        resp = httpx.post(
            _EMBED_URL,
            headers=_headers(),
            json={"inputs": texts},
            timeout=30,
        )
        if resp.status_code == 503:
            wait = min(resp.json().get("estimated_time", 10), 20)
            logger.warning(
                "HF model cold-starting, waiting %.0fs (attempt %d/%d)",
                wait, attempt + 1, retries,
            )
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError("HF Inference API unavailable after retries")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return 384-dim embeddings for a list of texts."""
    results: list[list[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        results.extend(_post_with_retry(texts[i: i + _BATCH_SIZE]))
    return results


def embed_single(text: str) -> list[float]:
    """Return 384-dim embedding for a single text."""
    return embed_texts([text])[0]
