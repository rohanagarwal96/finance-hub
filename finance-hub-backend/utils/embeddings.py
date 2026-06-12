"""fastembed embedding model (all-MiniLM-L6-v2, 384 dims, ONNX-based)."""
from __future__ import annotations

from fastembed import TextEmbedding

_MODEL: TextEmbedding | None = None
_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _get_model() -> TextEmbedding:
    global _MODEL
    if _MODEL is None:
        _MODEL = TextEmbedding(_MODEL_NAME)
    return _MODEL


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return 384-dim embeddings for a list of texts."""
    model = _get_model()
    return [emb.tolist() for emb in model.embed(texts)]


def embed_single(text: str) -> list[float]:
    """Return 384-dim embedding for a single text."""
    return embed_texts([text])[0]
