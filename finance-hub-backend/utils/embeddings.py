"""Sentence-transformers embedding model (all-MiniLM-L6-v2, 384 dims)."""
from __future__ import annotations

from sentence_transformers import SentenceTransformer

_MODEL: SentenceTransformer | None = None
_MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(_MODEL_NAME)
    return _MODEL


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return 384-dim embeddings for a list of texts."""
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return vectors.tolist()


def embed_single(text: str) -> list[float]:
    """Return 384-dim embedding for a single text."""
    return embed_texts([text])[0]
