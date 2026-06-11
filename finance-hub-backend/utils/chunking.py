"""PDF text extraction and recursive character text splitting."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import fitz  # PyMuPDF


@dataclass
class Chunk:
    text: str
    page_num: int
    section: str
    chunk_index: int


def extract_text_from_pdf(pdf_bytes: bytes) -> list[tuple[int, str]]:
    """Return list of (page_num, text) tuples (1-indexed pages)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        if text.strip():
            pages.append((i + 1, text))
    doc.close()
    return pages


def _detect_section(text: str) -> str:
    """Heuristically detect section header from the start of a text block."""
    lines = text.strip().split("\n")
    for line in lines[:3]:
        line = line.strip()
        if line and len(line) < 80 and line[0].isupper():
            return line[:60]
    return "Body"


def chunk_pages(
    pages: list[tuple[int, str]],
    chunk_size: int = 512,
    overlap: int = 50,
) -> list[Chunk]:
    """Split page text into overlapping chunks of ~chunk_size characters."""
    chunks: list[Chunk] = []
    idx = 0
    for page_num, text in pages:
        section = _detect_section(text)
        text = re.sub(r"\s+", " ", text).strip()
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            if chunk_text.strip():
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        page_num=page_num,
                        section=section,
                        chunk_index=idx,
                    )
                )
                idx += 1
            start += chunk_size - overlap
    return chunks
