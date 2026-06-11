"""Earnings Summarizer — map-reduce summarization with SSE streaming."""
from __future__ import annotations

import json
from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.schemas import SummaryRequest
from services.llm_service import llm_generate

router = APIRouter(prefix="/summarizer", tags=["summarizer"])

_CHUNK_SIZE = 2000  # characters per map chunk


def _split_into_chunks(text: str, size: int = _CHUNK_SIZE) -> list[str]:
    words = text.split()
    chunks, current = [], []
    char_count = 0
    for word in words:
        if char_count + len(word) + 1 > size and current:
            chunks.append(" ".join(current))
            current, char_count = [word], len(word)
        else:
            current.append(word)
            char_count += len(word) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks


async def _stream_transcript_summary(transcript: str) -> AsyncGenerator[str, None]:
    """Stream a map-reduce summary of the provided transcript text."""
    yield f"data: {json.dumps({'status': 'starting'})}\n\n"

    # Map phase: summarize the transcript directly
    chunks = _split_into_chunks(transcript)
    map_summaries = []

    for i, chunk in enumerate(chunks):
        yield f"data: {json.dumps({'status': 'analyzing', 'chunk': i + 1, 'total': len(chunks)})}\n\n"
        map_prompt = (
            "You are analyzing an earnings call transcript. "
            "Provide a concise summary of the key financial results in this excerpt, "
            "including revenue, earnings, guidance, and notable events. "
            "Format as bullet points. Be specific with numbers.\n\n"
            f"Excerpt:\n{chunk}"
        )
        section_summary = await llm_generate(map_prompt, max_tokens=400)
        map_summaries.append(section_summary)

    combined = "\n\n".join(map_summaries)

    # Reduce phase: combine section summaries
    yield f"data: {json.dumps({'status': 'reducing'})}\n\n"
    reduce_prompt = (
        "Combine these section summaries into a single cohesive earnings summary:\n\n"
        f"{combined}\n\n"
        "Provide a final summary with key financial metrics as bullet points."
    )
    map_summary = await llm_generate(reduce_prompt, max_tokens=600)

    # Extract key metrics as JSON
    yield f"data: {json.dumps({'status': 'extracting_metrics'})}\n\n"
    metrics_prompt = (
        f"Based on this earnings summary:\n{map_summary}\n\n"
        "Extract financial metrics and return JSON with these exact keys:\n"
        '{"revenue": "...", "eps": "...", "guidance": "...", "highlights": ["...", "..."]}'
    )
    metrics_raw = await llm_generate(metrics_prompt, max_tokens=400)

    try:
        start = metrics_raw.find("{")
        end = metrics_raw.rfind("}") + 1
        metrics_dict = json.loads(metrics_raw[start:end]) if start != -1 else {}
    except Exception:
        metrics_dict = {}

    yield f"data: {json.dumps({'status': 'complete', 'summary': map_summary, 'metrics': metrics_dict})}\n\n"


@router.post("/stream")
async def stream_summary(
    request: SummaryRequest,
) -> StreamingResponse:
    """Stream an earnings summary using SSE (Server-Sent Events).

    Accepts a SummaryRequest with a `transcript` field containing the earnings
    call text to summarize.
    """
    return StreamingResponse(
        _stream_transcript_summary(request.transcript),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/", response_model=dict)
async def summarize(
    request: SummaryRequest,
) -> dict:
    """Non-streaming summary endpoint.

    Accepts a SummaryRequest with a `transcript` field containing the earnings
    call text to summarize.
    """
    prompt = (
        "Summarize the key financial results from the following earnings call transcript.\n"
        "Include revenue, EPS, guidance, and major highlights. "
        "Be concise and specific.\n\n"
        f"Transcript:\n{request.transcript}"
    )
    summary = await llm_generate(prompt, max_tokens=600)
    return {"summary": summary}
