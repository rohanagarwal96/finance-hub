"""LangChain + Pinecone RAG pipeline for Document Q&A."""
from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import HTTPException
from pinecone import Pinecone

from models.schemas import Citation
from services.llm_service import llm_generate
from utils.chunking import Chunk
from utils.embeddings import embed_single, embed_texts

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

_pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"].strip().strip('"'))
_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"].strip().strip('"')
_index = _pc.Index(_INDEX_NAME)


def upsert_chunks(chunks: list[Chunk], namespace: str) -> int:
    """Embed and upsert chunks into Pinecone under the given namespace."""
    texts = [c.text for c in chunks]
    vectors = embed_texts(texts)

    records = []
    for chunk, vector in zip(chunks, vectors):
        records.append(
            {
                "id": f"{namespace}-{chunk.chunk_index}",
                "values": vector,
                "metadata": {
                    "text": chunk.text[:1000],
                    "page_num": chunk.page_num,
                    "section": chunk.section,
                    "namespace": namespace,
                },
            }
        )

    # Upsert in batches of 100
    for i in range(0, len(records), 100):
        _index.upsert(vectors=records[i : i + 100], namespace=namespace)

    return len(records)


async def query_document(
    question: str,
    namespace: str,
    top_k: int = 10,
    rerank_top: int = 3,
) -> tuple[str, list[Citation]]:
    """Retrieve relevant chunks, re-rank, and generate a cited answer."""
    query_vector = embed_single(question)

    results = _index.query(
        vector=query_vector,
        top_k=top_k,
        namespace=namespace,
        include_metadata=True,
    )

    if not results.matches:
        raise HTTPException(status_code=404, detail="No relevant content found in document")

    # Re-rank: already sorted by score, take top rerank_top
    top_matches = results.matches[:rerank_top]

    context_parts = []
    citations: list[Citation] = []
    for match in top_matches:
        meta = match.metadata
        context_parts.append(f"[Page {meta['page_num']}, {meta['section']}]: {meta['text']}")
        citations.append(
            Citation(
                page=int(meta["page_num"]),
                section=meta["section"],
                text=meta["text"][:200],
                score=float(match.score),
            )
        )

    context = "\n\n".join(context_parts)
    prompt = (
        f"You are a financial document analyst. Answer the question using ONLY the provided context. "
        f"Cite page numbers when referencing specific information.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )

    answer = await llm_generate(prompt, max_tokens=512)
    return answer, citations


def delete_namespace(namespace: str) -> None:
    """Delete all vectors in a Pinecone namespace."""
    _index.delete(delete_all=True, namespace=namespace)
