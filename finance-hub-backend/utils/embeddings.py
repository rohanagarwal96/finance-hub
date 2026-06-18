"""Embeddings via Pinecone Inference API.

Runs on Pinecone's servers using the existing PINECONE_API_KEY — no local
model, no external HTTP calls to domains that Render's free tier can't reach.
Model: multilingual-e5-large (1024 dims). Requires a Pinecone index with
1024 dimensions (cosine metric, serverless).
"""
from __future__ import annotations

import os

from pinecone import Pinecone

_pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"].strip().strip('"'))
_MODEL = "multilingual-e5-large"
_BATCH_SIZE = 32


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return 1024-dim embeddings for a list of passage texts."""
    results: list[list[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i: i + _BATCH_SIZE]
        response = _pc.inference.embed(
            model=_MODEL,
            inputs=batch,
            parameters={"input_type": "passage", "truncate": "END"},
        )
        results.extend([list(e.values) for e in response])
    return results


def embed_single(text: str) -> list[float]:
    """Return 1024-dim embedding for a single query text."""
    response = _pc.inference.embed(
        model=_MODEL,
        inputs=[text],
        parameters={"input_type": "query", "truncate": "END"},
    )
    return list(response[0].values)
