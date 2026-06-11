# Finance Hub — Implementation Plan (Phase 1 & 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the HuggingFace Space model server (Phase 1) and the complete FastAPI backend (Phase 2).

**Architecture:** HF Space runs fine-tuned Phi-3 Mini on CPU via FastAPI on port 7860. FastAPI backend (Render) calls the Space for LLM inference, uses Groq for complex reasoning tasks, Pinecone for vector search, Upstash Redis for caching, and Supabase PostgreSQL for persistence.

**Tech Stack:** Python 3.11, FastAPI, asyncpg, SQLAlchemy, LangChain, Pinecone, sentence-transformers, yfinance, Groq SDK, httpx, PyMuPDF, tiktoken, feedparser, python-dotenv

---

## PHASE 1: HuggingFace Space Model Server

### Task 1: Clone HF Space repo

**Files:**
- Working directory: `C:\Rohan\` (parent of finance-hub)

- [ ] **Step 1: Verify git identity**

```powershell
cd C:\Rohan\finance-hub
git config user.name
git config user.email
```
Expected output:
```
rohanagarwal96
rohanagarwal1324@gmail.com
```

- [ ] **Step 2: Clone the HF Space repo as a sibling directory**

```powershell
cd C:\Rohan
git clone https://huggingface.co/spaces/rohan1324/finance-hub-api
```
Expected: directory `C:\Rohan\finance-hub-api\` created.

- [ ] **Step 3: Verify clone succeeded**

```powershell
ls C:\Rohan\finance-hub-api
```
Expected: `.git` folder present, possibly a README.

---

### Task 2: Create Dockerfile and requirements.txt

**Files:**
- Create: `C:\Rohan\finance-hub-api\Dockerfile`
- Create: `C:\Rohan\finance-hub-api\requirements.txt`

- [ ] **Step 1: Create Dockerfile**

Create `C:\Rohan\finance-hub-api\Dockerfile` with this exact content:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

- [ ] **Step 2: Create requirements.txt**

Create `C:\Rohan\finance-hub-api\requirements.txt` with this exact content:

```
fastapi==0.109.2
uvicorn==0.27.1
transformers==4.40.1
peft==0.10.0
torch==2.2.1
accelerate==0.28.0
sentencepiece==0.2.0
protobuf==4.25.3
huggingface_hub==0.22.2
```

---

### Task 3: Create app.py model server

**Files:**
- Create: `C:\Rohan\finance-hub-api\app.py`

- [ ] **Step 1: Create app.py**

Create `C:\Rohan\finance-hub-api\app.py` with this exact content:

```python
import logging
import os
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from peft import PeftModel
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_model = None
_tokenizer = None

BASE_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
ADAPTER_ID = "rohan1324/phi3-mini-finance-qlora"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model, _tokenizer
    logger.info("Loading tokenizer...")
    _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, trust_remote_code=True)

    logger.info("Loading base model in float16 on CPU...")
    base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=torch.float16,
        device_map="cpu",
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    logger.info("Applying LoRA adapter...")
    _model = PeftModel.from_pretrained(base, ADAPTER_ID)
    _model.eval()
    logger.info("Model ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(title="Finance Hub Model Server", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.render.com",
        "https://*.vercel.app",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7


class GenerateResponse(BaseModel):
    generated_text: str


@app.get("/health")
async def health() -> dict:
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ok", "model": "loaded"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    inputs = _tokenizer(request.prompt, return_tensors="pt")
    input_len = inputs.input_ids.shape[1]

    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            do_sample=request.temperature > 0,
            pad_token_id=_tokenizer.eos_token_id,
        )

    new_tokens = outputs[0][input_len:]
    generated = _tokenizer.decode(new_tokens, skip_special_tokens=True)
    return GenerateResponse(generated_text=generated.strip())
```

---

### Task 4: Push to HuggingFace and verify

**Files:** (no new files, just git operations in `C:\Rohan\finance-hub-api\`)

- [ ] **Step 1: Stage and commit all files**

```powershell
cd C:\Rohan\finance-hub-api
git add Dockerfile requirements.txt app.py
git commit -m "feat: add Finance Hub model server"
```

- [ ] **Step 2: Push to HuggingFace**

```powershell
git push
```
Expected: push succeeds, HF Space build starts (visible at huggingface.co/spaces/rohan1324/finance-hub-api).

- [ ] **Step 3: Wait for build and verify /health**

The Space build takes 5-10 minutes. Once the Space shows "Running" status, verify:

```powershell
curl https://rohan1324-finance-hub-api.hf.space/health
```
Expected:
```json
{"status": "ok", "model": "loaded"}
```

> ⚠️ **STOP HERE.** Confirm the /health endpoint returns 200 before proceeding to Phase 2. Tell the user: "Phase 1 complete. Please verify https://rohan1324-finance-hub-api.hf.space/health returns {status: ok} before I proceed to Phase 2."

---

## PHASE 2: FastAPI Backend

### Task 5: Create backend directory structure and requirements.txt

**Files:**
- Create: `finance-hub-backend/` directory tree
- Create: `finance-hub-backend/requirements.txt`

- [ ] **Step 1: Create all directories**

```powershell
cd C:\Rohan\finance-hub
mkdir finance-hub-backend
mkdir finance-hub-backend\routers
mkdir finance-hub-backend\services
mkdir finance-hub-backend\models
mkdir finance-hub-backend\utils
```

- [ ] **Step 2: Create __init__.py files**

Create empty `finance-hub-backend/routers/__init__.py`, `finance-hub-backend/services/__init__.py`, `finance-hub-backend/models/__init__.py`, `finance-hub-backend/utils/__init__.py`.

Each file should be empty (0 bytes).

- [ ] **Step 3: Create requirements.txt**

Create `finance-hub-backend/requirements.txt`:

```
fastapi==0.109.2
uvicorn==0.27.1
asyncpg==0.29.0
sqlalchemy[asyncio]==2.0.28
pydantic==2.6.3
pydantic-settings==2.2.1
python-dotenv==1.0.1
httpx==0.27.0
pinecone==3.2.2
sentence-transformers==2.6.1
groq==0.5.0
langchain==0.1.13
langchain-community==0.0.29
PyMuPDF==1.24.0
tiktoken==0.6.0
yfinance==0.2.37
feedparser==6.0.11
python-multipart==0.0.9
aiohttp==3.9.3
numpy==1.26.4
pandas==2.2.1
scipy==1.12.0
```

- [ ] **Step 4: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/
git commit -m "feat: scaffold backend directory structure"
```

---

### Task 6: Create models/database.py and models/schemas.py

**Files:**
- Create: `finance-hub-backend/models/database.py`
- Create: `finance-hub-backend/models/schemas.py`

- [ ] **Step 1: Create models/database.py**

```python
"""Async SQLAlchemy engine and session factory for Supabase PostgreSQL."""
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

_raw_url = os.environ["DATABASE_URL"].strip().strip('"')
DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=5, max_overflow=10)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session
```

- [ ] **Step 2: Create models/schemas.py**

```python
"""Pydantic v2 request and response schemas for all API endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatMessageRequest(BaseModel):
    conversation_id: Optional[str] = None
    user_id: str
    content: str


class ChatMessageResponse(BaseModel):
    conversation_id: str
    message_id: str
    role: str
    content: str
    created_at: datetime


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime


class MessageItem(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


# ── Document Q&A ──────────────────────────────────────────────────────────────

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    namespace: str


class DocumentQueryRequest(BaseModel):
    document_id: str
    user_id: str
    question: str


class Citation(BaseModel):
    page: int
    section: str
    text: str
    score: float


class DocumentQueryResponse(BaseModel):
    answer: str
    citations: list[Citation]


class DocumentListItem(BaseModel):
    id: str
    filename: str
    uploaded_at: datetime


# ── Earnings Summarizer ───────────────────────────────────────────────────────

class SummaryRequest(BaseModel):
    transcript: str = Field(..., min_length=100)


# ── Stock Research ────────────────────────────────────────────────────────────

class KeyMetrics(BaseModel):
    pe_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    gross_margin: Optional[float] = None
    revenue_growth_yoy: Optional[float] = None
    market_cap: Optional[float] = None
    current_price: Optional[float] = None


class ResearchReport(BaseModel):
    ticker: str
    company_name: str
    overview: str
    financial_performance: str
    key_metrics: KeyMetrics
    recent_news: list[str]
    bull_case: list[str]
    bear_case: list[str]
    key_risks: str


# ── Study Assistant ───────────────────────────────────────────────────────────

class StudyQuestionRequest(BaseModel):
    user_id: str
    exam_type: str  # CFA, Series7, FRM, CPA
    topic: str
    mode: str  # flashcard, practice, weakspot


class StudyQuestion(BaseModel):
    question: str
    options: Optional[list[str]] = None  # None for flashcard
    correct_answer: str
    explanation: str
    topic: str
    exam_type: str


class StudyAttemptRequest(BaseModel):
    user_id: str
    topic: str
    exam_type: str
    question: str
    user_answer: str
    correct_answer: str


class StudyAttemptResponse(BaseModel):
    correct: bool
    explanation: str


class TopicPerformance(BaseModel):
    topic: str
    correct: int
    total: int
    accuracy: float


class StudyPerformanceResponse(BaseModel):
    user_id: str
    exam_type: Optional[str]
    topics: list[TopicPerformance]


# ── Portfolio ─────────────────────────────────────────────────────────────────

class Holding(BaseModel):
    ticker: str
    shares: float
    cost_basis: float  # per share


class PortfolioRequest(BaseModel):
    user_id: str
    holdings: list[Holding]


class PositionAnalysis(BaseModel):
    ticker: str
    shares: float
    cost_basis: float
    current_price: float
    current_value: float
    pnl_dollar: float
    pnl_percent: float
    sector: Optional[str] = None
    weight: float


class PortfolioAnalysisResponse(BaseModel):
    total_value: float
    total_cost: float
    total_pnl_dollar: float
    total_pnl_percent: float
    positions: list[PositionAnalysis]
    sector_allocation: dict[str, float]
    herfindahl_index: float
    correlation_matrix: dict[str, dict[str, float]]
    commentary: str


# ── Sentiment ─────────────────────────────────────────────────────────────────

class ArticleSentiment(BaseModel):
    title: str
    url: str
    published_at: str
    sentiment: str  # bullish, neutral, bearish
    confidence: float
    summary: Optional[str] = None


class SentimentResponse(BaseModel):
    query: str
    overall_score: float  # -1.0 to 1.0
    overall_label: str
    article_count: int
    articles: list[ArticleSentiment]
    cached: bool = False
```

- [ ] **Step 3: Verify schemas import cleanly**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
python -c "from models.schemas import ChatMessageRequest, ResearchReport, PortfolioAnalysisResponse; print('OK')"
```
Expected: `OK`

- [ ] **Step 4: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/models/
git commit -m "feat: add database engine and Pydantic schemas"
```

---

### Task 7: Create services/cache_service.py

**Files:**
- Create: `finance-hub-backend/services/cache_service.py`

- [ ] **Step 1: Create cache_service.py**

```python
"""Upstash Redis REST client for caching API responses."""
import json
import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

_REDIS_URL = os.environ["UPSTASH_REDIS_REST_URL"].strip().strip('"')
_REDIS_TOKEN = os.environ["UPSTASH_REDIS_REST_TOKEN"].strip().strip('"')
_HEADERS = {"Authorization": f"Bearer {_REDIS_TOKEN}"}


async def cache_get(key: str) -> Optional[Any]:
    """Return the cached value for key, or None if missing/expired."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{_REDIS_URL}/get/{key}", headers=_HEADERS)
        data = resp.json()
        if data.get("result") is None:
            return None
        return json.loads(data["result"])


async def cache_set(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    """Store value as JSON under key with a TTL."""
    serialized = json.dumps(value)
    async with httpx.AsyncClient() as client:
        await client.get(
            f"{_REDIS_URL}/set/{key}/{serialized}/EX/{ttl_seconds}",
            headers=_HEADERS,
        )


async def cache_delete(key: str) -> None:
    """Remove a cache key."""
    async with httpx.AsyncClient() as client:
        await client.get(f"{_REDIS_URL}/del/{key}", headers=_HEADERS)
```

- [ ] **Step 2: Smoke-test cache (requires .env to be readable)**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
python -c "
import asyncio
from services.cache_service import cache_set, cache_get, cache_delete

async def test():
    await cache_set('test_key', {'hello': 'world'}, ttl_seconds=60)
    result = await cache_get('test_key')
    assert result == {'hello': 'world'}, f'Got {result}'
    await cache_delete('test_key')
    print('cache_service OK')

asyncio.run(test())
"
```
Expected: `cache_service OK`

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/services/cache_service.py
git commit -m "feat: add Upstash Redis cache service"
```

---

### Task 8: Create services/llm_service.py

**Files:**
- Create: `finance-hub-backend/services/llm_service.py`

- [ ] **Step 1: Create llm_service.py**

```python
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
```

- [ ] **Step 2: Verify import**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
python -c "from services.llm_service import llm_generate; print('llm_service OK')"
```
Expected: `llm_service OK`

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/services/llm_service.py
git commit -m "feat: add HF Space LLM service with retry backoff"
```

---

### Task 9: Create services/groq_service.py

**Files:**
- Create: `finance-hub-backend/services/groq_service.py`

- [ ] **Step 1: Create groq_service.py**

```python
"""Groq API client for Llama 3.1 70B — used for Modules 3, 5, 6."""
import os
from typing import AsyncIterator, Optional

from dotenv import load_dotenv
from fastapi import HTTPException
from groq import AsyncGroq

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

_client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"].strip().strip('"'))
_MODEL = "llama-3.1-70b-versatile"


async def groq_complete(
    prompt: str,
    system_prompt: str = "You are a professional financial analyst.",
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> str:
    """Single-turn Groq completion. Returns full response text."""
    try:
        response = await _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Groq API error: {exc}")


async def groq_complete_with_history(
    messages: list[dict],
    system_prompt: str = "You are a professional financial analyst.",
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> str:
    """Multi-turn Groq completion with full message history."""
    try:
        response = await _client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Groq API error: {exc}")
```

- [ ] **Step 2: Verify import**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
python -c "from services.groq_service import groq_complete; print('groq_service OK')"
```
Expected: `groq_service OK`

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/services/groq_service.py
git commit -m "feat: add Groq LLM service"
```

---

### Task 10: Create utils/chunking.py and utils/embeddings.py

**Files:**
- Create: `finance-hub-backend/utils/chunking.py`
- Create: `finance-hub-backend/utils/embeddings.py`

- [ ] **Step 1: Create utils/chunking.py**

```python
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
```

- [ ] **Step 2: Create utils/embeddings.py**

```python
"""Sentence-transformers embedding model (all-MiniLM-L6-v2, 384 dims)."""
from __future__ import annotations

import numpy as np
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
```

- [ ] **Step 3: Verify chunking works**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
python -c "
from utils.chunking import chunk_pages
pages = [(1, 'This is a test document. ' * 50)]
chunks = chunk_pages(pages)
assert len(chunks) > 0
assert chunks[0].page_num == 1
print(f'chunking OK — {len(chunks)} chunks')
"
```
Expected: `chunking OK — N chunks`

- [ ] **Step 4: Verify embeddings work**

```powershell
python -c "
from utils.embeddings import embed_single
v = embed_single('test text')
assert len(v) == 384
print('embeddings OK')
"
```
Expected: `embeddings OK`

- [ ] **Step 5: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/utils/chunking.py finance-hub-backend/utils/embeddings.py
git commit -m "feat: add PDF chunking and sentence-transformers embeddings"
```

---

### Task 11: Create utils/context_window.py

**Files:**
- Create: `finance-hub-backend/utils/context_window.py`

- [ ] **Step 1: Create context_window.py**

```python
"""Sliding context window management for chat conversations."""
from __future__ import annotations

import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")
_MAX_TOKENS = 3000


def count_tokens(text: str) -> int:
    """Count tokens in a string using cl100k_base encoding."""
    return len(_ENCODING.encode(text))


def messages_token_count(messages: list[dict]) -> int:
    """Count total tokens across a list of {role, content} dicts."""
    return sum(count_tokens(m["content"]) for m in messages)


def trim_messages_to_window(
    messages: list[dict],
    summary: str = "",
) -> tuple[list[dict], str]:
    """Return messages trimmed to fit within _MAX_TOKENS.

    When the history exceeds the limit, the oldest messages are dropped
    and a summary string is returned to be prepended as context.
    The summary is passed in from a prior summarization call.
    Returns (trimmed_messages, existing_summary).
    """
    if messages_token_count(messages) <= _MAX_TOKENS:
        return messages, summary

    # Drop oldest messages until we're under the limit
    trimmed = list(messages)
    while trimmed and messages_token_count(trimmed) > _MAX_TOKENS:
        trimmed.pop(0)

    return trimmed, summary


def build_context_prompt(messages: list[dict], summary: str = "") -> str:
    """Build a prompt string from message history with optional summary prefix."""
    parts = []
    if summary:
        parts.append(f"[Earlier conversation summary: {summary}]\n")
    for m in messages:
        role = m["role"].capitalize()
        parts.append(f"{role}: {m['content']}")
    return "\n".join(parts)
```

- [ ] **Step 2: Verify**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
python -c "
from utils.context_window import count_tokens, trim_messages_to_window
msgs = [{'role': 'user', 'content': 'hello'}, {'role': 'assistant', 'content': 'hi'}]
trimmed, summary = trim_messages_to_window(msgs)
assert trimmed == msgs
print('context_window OK')
"
```
Expected: `context_window OK`

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/utils/context_window.py
git commit -m "feat: add sliding context window utility"
```

---

### Task 12: Create services/rag_service.py

**Files:**
- Create: `finance-hub-backend/services/rag_service.py`

- [ ] **Step 1: Create rag_service.py**

```python
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
```

- [ ] **Step 2: Verify import**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
python -c "from services.rag_service import upsert_chunks, query_document; print('rag_service OK')"
```
Expected: `rag_service OK`

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/services/rag_service.py
git commit -m "feat: add Pinecone RAG service"
```

---

### Task 13: Create services/market_service.py

**Files:**
- Create: `finance-hub-backend/services/market_service.py`

- [ ] **Step 1: Create market_service.py**

```python
"""yfinance wrapper for stock prices, financials, and SEC EDGAR filings."""
from __future__ import annotations

from typing import Any, Optional

import httpx
import yfinance as yf


def get_stock_price(ticker: str) -> dict[str, Any]:
    """Return current price, volume, and market cap for a ticker."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "ticker": ticker.upper(),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "volume": info.get("volume"),
            "market_cap": info.get("marketCap"),
            "currency": info.get("currency", "USD"),
        }
    except Exception as exc:
        return {"ticker": ticker.upper(), "error": str(exc)}


def get_financials(ticker: str) -> dict[str, Any]:
    """Return key financial metrics for a ticker."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "ticker": ticker.upper(),
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "pe_ratio": info.get("trailingPE"),
            "ev_ebitda": info.get("enterpriseToEbitda"),
            "gross_margin": info.get("grossMargins"),
            "revenue_growth_yoy": info.get("revenueGrowth"),
            "total_revenue": info.get("totalRevenue"),
            "net_income": info.get("netIncomeToCommon"),
            "description": info.get("longBusinessSummary", "")[:500],
        }
    except Exception as exc:
        return {"ticker": ticker.upper(), "error": str(exc)}


async def get_sec_filings(ticker: str) -> list[dict[str, str]]:
    """Return most recent 10-K and 10-Q filing dates and links from SEC EDGAR."""
    try:
        t = yf.Ticker(ticker)
        cik = None

        # Try to get CIK from yfinance info
        info = t.info
        # SEC EDGAR full-text search
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom"
                f"&startdt=2023-01-01&forms=10-K,10-Q",
                headers={"User-Agent": "FinanceHub research@financelub.com"},
            )
            if resp.status_code == 200:
                data = resp.json()
                hits = data.get("hits", {}).get("hits", [])[:4]
                return [
                    {
                        "form": h.get("_source", {}).get("form_type", ""),
                        "filed": h.get("_source", {}).get("file_date", ""),
                        "url": f"https://www.sec.gov/Archives/edgar/data/{h.get('_source',{}).get('entity_id','')}/",
                    }
                    for h in hits
                ]
    except Exception:
        pass
    return []
```

- [ ] **Step 2: Verify import**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
python -c "from services.market_service import get_stock_price; print('market_service OK')"
```
Expected: `market_service OK`

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/services/market_service.py
git commit -m "feat: add yfinance and SEC EDGAR market service"
```

---

### Task 14: Create services/news_service.py

**Files:**
- Create: `finance-hub-backend/services/news_service.py`

- [ ] **Step 1: Create news_service.py**

```python
"""News fetching via GNews API and Reuters RSS feed."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import feedparser
import httpx
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

_GNEWS_KEY = os.environ["GNEWS_API_KEY"].strip().strip('"')
_REUTERS_RSS = "https://feeds.reuters.com/reuters/businessNews"


async def fetch_news(query: str, days: int = 30, max_articles: int = 30) -> list[dict[str, Any]]:
    """Fetch news articles from GNews and Reuters RSS, deduplicated by title."""
    articles: list[dict] = []
    seen_titles: set[str] = set()

    from_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # GNews
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://gnews.io/api/v4/search",
                params={
                    "q": query,
                    "token": _GNEWS_KEY,
                    "lang": "en",
                    "max": 20,
                    "from": from_date,
                },
            )
            if resp.status_code == 200:
                for item in resp.json().get("articles", []):
                    title = item.get("title", "")
                    if title not in seen_titles:
                        seen_titles.add(title)
                        articles.append(
                            {
                                "title": title,
                                "summary": item.get("description", ""),
                                "url": item.get("url", ""),
                                "published_at": item.get("publishedAt", ""),
                                "source": "GNews",
                            }
                        )
    except Exception:
        pass

    # Reuters RSS
    try:
        feed = feedparser.parse(_REUTERS_RSS)
        for entry in feed.entries[:15]:
            title = entry.get("title", "")
            if title not in seen_titles and query.lower() in (title + entry.get("summary", "")).lower():
                seen_titles.add(title)
                articles.append(
                    {
                        "title": title,
                        "summary": entry.get("summary", ""),
                        "url": entry.get("link", ""),
                        "published_at": entry.get("published", ""),
                        "source": "Reuters",
                    }
                )
    except Exception:
        pass

    return articles[:max_articles]
```

- [ ] **Step 2: Verify import**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
python -c "from services.news_service import fetch_news; print('news_service OK')"
```
Expected: `news_service OK`

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/services/news_service.py
git commit -m "feat: add GNews and Reuters RSS news service"
```

---

### Task 15: Create routers/chat.py

**Files:**
- Create: `finance-hub-backend/routers/chat.py`

- [ ] **Step 1: Create routers/chat.py**

```python
"""Chat router — persistent conversational interface with sliding context window."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationSummary,
    MessageItem,
)
from services.llm_service import llm_generate
from utils.context_window import build_context_prompt, trim_messages_to_window

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    """Send a message and receive an AI response."""
    conversation_id = request.conversation_id

    # Create conversation if new
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        title = request.content[:60] + ("..." if len(request.content) > 60 else "")
        await db.execute(
            sa.text(
                "INSERT INTO conversations (id, user_id, title, created_at) "
                "VALUES (:id, :user_id, :title, :created_at)"
            ),
            {
                "id": conversation_id,
                "user_id": request.user_id,
                "title": title,
                "created_at": datetime.now(timezone.utc),
            },
        )
        await db.commit()

    # Fetch existing messages
    result = await db.execute(
        sa.text(
            "SELECT role, content FROM messages "
            "WHERE conversation_id = :cid ORDER BY created_at ASC"
        ),
        {"cid": conversation_id},
    )
    history = [{"role": row.role, "content": row.content} for row in result.fetchall()]

    # Save user message
    user_msg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    await db.execute(
        sa.text(
            "INSERT INTO messages (id, conversation_id, role, content, created_at) "
            "VALUES (:id, :cid, :role, :content, :ts)"
        ),
        {
            "id": user_msg_id,
            "cid": conversation_id,
            "role": "user",
            "content": request.content,
            "ts": now,
        },
    )
    await db.commit()

    # Build context and call LLM
    history.append({"role": "user", "content": request.content})
    trimmed, summary = trim_messages_to_window(history)
    prompt = (
        "You are a knowledgeable financial assistant. Answer concisely and accurately.\n\n"
        + build_context_prompt(trimmed, summary)
        + "\nAssistant:"
    )
    answer = await llm_generate(prompt, max_tokens=512)

    # Save assistant message
    assistant_msg_id = str(uuid.uuid4())
    answer_ts = datetime.now(timezone.utc)
    await db.execute(
        sa.text(
            "INSERT INTO messages (id, conversation_id, role, content, created_at) "
            "VALUES (:id, :cid, :role, :content, :ts)"
        ),
        {
            "id": assistant_msg_id,
            "cid": conversation_id,
            "role": "assistant",
            "content": answer,
            "ts": answer_ts,
        },
    )
    await db.commit()

    return ChatMessageResponse(
        conversation_id=conversation_id,
        message_id=assistant_msg_id,
        role="assistant",
        content=answer,
        created_at=answer_ts,
    )


@router.get("/history/{conversation_id}", response_model=list[MessageItem])
async def get_history(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[MessageItem]:
    """Return all messages in a conversation ordered by time."""
    result = await db.execute(
        sa.text(
            "SELECT id, role, content, created_at FROM messages "
            "WHERE conversation_id = :cid ORDER BY created_at ASC"
        ),
        {"cid": conversation_id},
    )
    rows = result.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [
        MessageItem(id=r.id, role=r.role, content=r.content, created_at=r.created_at)
        for r in rows
    ]


@router.get("/conversations/{user_id}", response_model=list[ConversationSummary])
async def get_conversations(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[ConversationSummary]:
    """Return all conversations for a user, newest first."""
    result = await db.execute(
        sa.text(
            "SELECT id, title, created_at FROM conversations "
            "WHERE user_id = :uid ORDER BY created_at DESC LIMIT 50"
        ),
        {"uid": user_id},
    )
    return [
        ConversationSummary(id=r.id, title=r.title, created_at=r.created_at)
        for r in result.fetchall()
    ]
```

- [ ] **Step 2: Verify import**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
python -c "from routers.chat import router; print('chat router OK')"
```
Expected: `chat router OK`

- [ ] **Step 3: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/routers/chat.py
git commit -m "feat: add chat router with sliding context window"
```

---

### Task 16: Create routers/document_qa.py

**Files:**
- Create: `finance-hub-backend/routers/document_qa.py`

- [ ] **Step 1: Create routers/document_qa.py**

```python
"""Document Q&A router — PDF upload, chunking, RAG query."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.schemas import (
    Citation,
    DocumentListItem,
    DocumentQueryRequest,
    DocumentQueryResponse,
    DocumentUploadResponse,
)
from services.rag_service import query_document, upsert_chunks
from utils.chunking import chunk_pages, extract_text_from_pdf

router = APIRouter(prefix="/api/document", tags=["document"])

_MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    """Upload a PDF, chunk it, embed chunks, store in Pinecone."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > _MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds 10 MB limit")

    doc_id = str(uuid.uuid4())
    namespace = f"{user_id}/{doc_id}"

    pages = extract_text_from_pdf(pdf_bytes)
    if not pages:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(status_code=400, detail="PDF produced no text chunks")

    chunk_count = upsert_chunks(chunks, namespace)

    await db.execute(
        sa.text(
            "INSERT INTO documents (id, user_id, filename, pinecone_namespace, uploaded_at) "
            "VALUES (:id, :uid, :filename, :ns, :ts)"
        ),
        {
            "id": doc_id,
            "uid": user_id,
            "filename": file.filename,
            "ns": namespace,
            "ts": datetime.now(timezone.utc),
        },
    )
    await db.commit()

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        chunk_count=chunk_count,
        namespace=namespace,
    )


@router.post("/query", response_model=DocumentQueryResponse)
async def query_doc(
    request: DocumentQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> DocumentQueryResponse:
    """Answer a question about an uploaded document with citations."""
    result = await db.execute(
        sa.text(
            "SELECT pinecone_namespace FROM documents WHERE id = :id AND user_id = :uid"
        ),
        {"id": request.document_id, "uid": request.user_id},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    answer, citations = await query_document(request.question, row.pinecone_namespace)
    return DocumentQueryResponse(answer=answer, citations=citations)


@router.get("/list", response_model=list[DocumentListItem])
async def list_documents(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[DocumentListItem]:
    """List all documents uploaded by a user."""
    result = await db.execute(
        sa.text(
            "SELECT id, filename, uploaded_at FROM documents "
            "WHERE user_id = :uid ORDER BY uploaded_at DESC"
        ),
        {"uid": user_id},
    )
    return [
        DocumentListItem(id=r.id, filename=r.filename, uploaded_at=r.uploaded_at)
        for r in result.fetchall()
    ]
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/routers/document_qa.py
git commit -m "feat: add document Q&A router"
```

---

### Task 17: Create routers/summarizer.py

**Files:**
- Create: `finance-hub-backend/routers/summarizer.py`

- [ ] **Step 1: Create routers/summarizer.py**

```python
"""Earnings summarizer router — map-reduce with SSE streaming."""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.schemas import SummaryRequest
from services.llm_service import llm_generate

router = APIRouter(prefix="/api/summarize", tags=["summarizer"])

_SECTIONS = [
    "Revenue and Growth",
    "Gross Margin and Profitability",
    "Guidance and Forward Outlook",
    "Key Risks Mentioned",
    "Management Tone",
    "Top 3 Analyst Q&A Highlights",
]

_CHUNK_SIZE = 4000  # characters per map chunk


def _split_transcript(text: str) -> list[str]:
    """Split transcript into chunks of ~_CHUNK_SIZE characters at sentence boundaries."""
    chunks = []
    while len(text) > _CHUNK_SIZE:
        split_at = text.rfind(". ", 0, _CHUNK_SIZE)
        if split_at == -1:
            split_at = _CHUNK_SIZE
        chunks.append(text[: split_at + 1].strip())
        text = text[split_at + 1 :].strip()
    if text:
        chunks.append(text)
    return chunks


async def _summarize_chunk(chunk: str, chunk_idx: int) -> str:
    """Summarize a single transcript chunk."""
    prompt = (
        f"Summarize this earnings call segment (part {chunk_idx + 1}). "
        f"Focus on financial figures, guidance, and key statements.\n\n{chunk}\n\nSummary:"
    )
    return await llm_generate(prompt, max_tokens=300)


async def _generate_section(section: str, combined_summary: str) -> str:
    """Generate one structured section from the combined summary."""
    prompt = (
        f"Based on this earnings call summary, write the '{section}' section. "
        f"Be specific with numbers and percentages where mentioned. "
        f"Write 2-4 sentences.\n\nSummary:\n{combined_summary}\n\n{section}:"
    )
    return await llm_generate(prompt, max_tokens=256)


@router.post("/earnings")
async def summarize_earnings(request: SummaryRequest) -> StreamingResponse:
    """Summarize an earnings transcript using map-reduce, streaming each section via SSE."""

    async def event_stream():
        # Map phase: summarize chunks in parallel if transcript is long
        chunks = _split_transcript(request.transcript)

        if len(chunks) > 1:
            yield f"data: {json.dumps({'type': 'status', 'message': f'Processing {len(chunks)} sections...'})}\n\n"
            chunk_summaries = await asyncio.gather(
                *[_summarize_chunk(c, i) for i, c in enumerate(chunks)]
            )
            combined = "\n\n".join(chunk_summaries)
        else:
            combined = request.transcript

        # Reduce phase: generate each structured section and stream it
        for section in _SECTIONS:
            yield f"data: {json.dumps({'type': 'status', 'message': f'Writing: {section}...'})}\n\n"
            text = await _generate_section(section, combined[:6000])
            yield f"data: {json.dumps({'type': 'section', 'title': section, 'content': text})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/routers/summarizer.py
git commit -m "feat: add earnings summarizer router with SSE streaming"
```

---

### Task 18: Create routers/research.py

**Files:**
- Create: `finance-hub-backend/routers/research.py`

- [ ] **Step 1: Create routers/research.py**

```python
"""Stock research router — Groq agent with yfinance + news tools."""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from models.schemas import KeyMetrics, ResearchReport
from services.groq_service import groq_complete
from services.market_service import get_financials, get_sec_filings, get_stock_price
from services.news_service import fetch_news

router = APIRouter(prefix="/api/research", tags=["research"])


@router.get("/{ticker}", response_model=ResearchReport)
async def research_ticker(ticker: str) -> ResearchReport:
    """Run a full stock research report using tool calling with Groq."""
    ticker = ticker.upper().strip()

    # Gather tool data in parallel conceptually (sequential here for simplicity)
    price_data = get_stock_price(ticker)
    fin_data = get_financials(ticker)
    news_articles = await fetch_news(fin_data.get("company_name", ticker), days=14, max_articles=10)
    filings = await get_sec_filings(ticker)

    if "error" in price_data and "error" in fin_data:
        raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")

    company_name = fin_data.get("company_name", ticker)
    news_headlines = [a["title"] for a in news_articles[:10]]
    filing_summary = ", ".join(
        f"{f['form']} ({f['filed']})" for f in filings[:3]
    ) or "No recent filings found"

    context = f"""
Company: {company_name} ({ticker})
Current Price: {price_data.get('current_price')}
Market Cap: {price_data.get('market_cap')}
Sector: {fin_data.get('sector')} | Industry: {fin_data.get('industry')}
P/E Ratio: {fin_data.get('pe_ratio')}
EV/EBITDA: {fin_data.get('ev_ebitda')}
Gross Margin: {fin_data.get('gross_margin')}
Revenue Growth YoY: {fin_data.get('revenue_growth_yoy')}
Total Revenue: {fin_data.get('total_revenue')}
Net Income: {fin_data.get('net_income')}
Business Description: {fin_data.get('description', '')}
Recent Headlines: {json.dumps(news_headlines)}
Recent SEC Filings: {filing_summary}
"""

    system_prompt = (
        "You are a senior equity research analyst. Produce structured, fact-based reports. "
        "Use only the provided data. Be specific with numbers."
    )

    report_prompt = f"""
Based on the following data, write a comprehensive research report in valid JSON format with these exact keys:
"overview", "financial_performance", "bull_case" (list of 3 strings), "bear_case" (list of 3 strings), "key_risks"

Data:
{context}

Respond with ONLY valid JSON, no markdown.
"""

    raw = await groq_complete(report_prompt, system_prompt=system_prompt, max_tokens=1500)

    try:
        # Strip markdown code fences if present
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: return raw text in overview
        parsed = {
            "overview": raw,
            "financial_performance": "See overview",
            "bull_case": ["Data available above"],
            "bear_case": ["Data available above"],
            "key_risks": "See overview",
        }

    return ResearchReport(
        ticker=ticker,
        company_name=company_name,
        overview=parsed.get("overview", ""),
        financial_performance=parsed.get("financial_performance", ""),
        key_metrics=KeyMetrics(
            pe_ratio=fin_data.get("pe_ratio"),
            ev_ebitda=fin_data.get("ev_ebitda"),
            gross_margin=fin_data.get("gross_margin"),
            revenue_growth_yoy=fin_data.get("revenue_growth_yoy"),
            market_cap=price_data.get("market_cap"),
            current_price=price_data.get("current_price"),
        ),
        recent_news=news_headlines[:5],
        bull_case=parsed.get("bull_case", [])[:3],
        bear_case=parsed.get("bear_case", [])[:3],
        key_risks=parsed.get("key_risks", ""),
    )
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/routers/research.py
git commit -m "feat: add stock research router with Groq agent"
```

---

### Task 19: Create routers/study.py

**Files:**
- Create: `finance-hub-backend/routers/study.py`

- [ ] **Step 1: Create routers/study.py**

```python
"""Study assistant router — question generation, attempt tracking, performance."""
from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.schemas import (
    StudyAttemptRequest,
    StudyAttemptResponse,
    StudyPerformanceResponse,
    StudyQuestion,
    StudyQuestionRequest,
    TopicPerformance,
)
from services.llm_service import llm_generate

router = APIRouter(prefix="/api/study", tags=["study"])

_TOPICS: dict[str, list[str]] = {
    "CFA": ["Equity Valuation", "Fixed Income", "Derivatives", "Portfolio Management", "Ethics", "Economics"],
    "Series7": ["Equity Securities", "Debt Securities", "Options", "Mutual Funds", "Regulations", "Customer Accounts"],
    "FRM": ["Market Risk", "Credit Risk", "Operational Risk", "Quantitative Analysis", "Valuation"],
    "CPA": ["Financial Accounting", "Auditing", "Taxation", "Business Law", "Regulation"],
}


async def _get_weak_topics(user_id: str, exam_type: str, db: AsyncSession) -> list[str]:
    """Return topics sorted by weakness (lowest accuracy first)."""
    result = await db.execute(
        sa.text(
            "SELECT topic, "
            "SUM(CASE WHEN correct THEN 1 ELSE 0 END) as correct_count, "
            "COUNT(*) as total "
            "FROM study_attempts WHERE user_id = :uid AND exam_type = :et "
            "GROUP BY topic"
        ),
        {"uid": user_id, "et": exam_type},
    )
    rows = result.fetchall()
    if not rows:
        return _TOPICS.get(exam_type, ["General"])

    scored = [(r.topic, r.correct_count / r.total) for r in rows]
    scored.sort(key=lambda x: x[1])
    return [t for t, _ in scored]


@router.get("/question", response_model=StudyQuestion)
async def get_question(
    user_id: str,
    exam_type: str,
    topic: str,
    mode: str = "practice",
    db: AsyncSession = Depends(get_db),
) -> StudyQuestion:
    """Generate a study question for the given exam, topic, and mode."""
    if mode == "weakspot":
        weak_topics = await _get_weak_topics(user_id, exam_type, db)
        topic = weak_topics[0] if weak_topics else topic

    if mode == "flashcard":
        prompt = (
            f"Create one {exam_type} exam flashcard for the topic '{topic}'. "
            f"Respond in JSON with keys: question, correct_answer, explanation. "
            f"No markdown, just valid JSON."
        )
    else:
        prompt = (
            f"Create one {exam_type} multiple choice question for the topic '{topic}'. "
            f"Respond in JSON with keys: question, options (array of 4 strings A-D), "
            f"correct_answer (the full correct option text), explanation. "
            f"No markdown, just valid JSON."
        )

    raw = await llm_generate(prompt, max_tokens=400)

    try:
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Model returned malformed question")

    return StudyQuestion(
        question=parsed.get("question", raw),
        options=parsed.get("options"),
        correct_answer=parsed.get("correct_answer", ""),
        explanation=parsed.get("explanation", ""),
        topic=topic,
        exam_type=exam_type,
    )


@router.post("/attempt", response_model=StudyAttemptResponse)
async def record_attempt(
    request: StudyAttemptRequest,
    db: AsyncSession = Depends(get_db),
) -> StudyAttemptResponse:
    """Record a study attempt and return whether the answer was correct."""
    correct = request.user_answer.strip().lower() == request.correct_answer.strip().lower()

    await db.execute(
        sa.text(
            "INSERT INTO study_attempts "
            "(id, user_id, topic, exam_type, correct, question, user_answer, attempted_at) "
            "VALUES (:id, :uid, :topic, :et, :correct, :q, :ua, :ts)"
        ),
        {
            "id": str(uuid.uuid4()),
            "uid": request.user_id,
            "topic": request.topic,
            "et": request.exam_type,
            "correct": correct,
            "q": request.question[:500],
            "ua": request.user_answer[:200],
            "ts": datetime.now(timezone.utc),
        },
    )
    await db.commit()

    explanation_prompt = (
        f"Question: {request.question}\n"
        f"Correct answer: {request.correct_answer}\n"
        f"Student answered: {request.user_answer}\n"
        f"Briefly explain why the correct answer is right (2-3 sentences):"
    )
    explanation = await llm_generate(explanation_prompt, max_tokens=150)

    return StudyAttemptResponse(correct=correct, explanation=explanation)


@router.get("/performance/{user_id}", response_model=StudyPerformanceResponse)
async def get_performance(
    user_id: str,
    exam_type: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> StudyPerformanceResponse:
    """Return per-topic accuracy breakdown for a user."""
    query = (
        "SELECT topic, exam_type, "
        "SUM(CASE WHEN correct THEN 1 ELSE 0 END) as correct_count, "
        "COUNT(*) as total "
        "FROM study_attempts WHERE user_id = :uid"
    )
    params: dict = {"uid": user_id}
    if exam_type:
        query += " AND exam_type = :et"
        params["et"] = exam_type
    query += " GROUP BY topic, exam_type ORDER BY topic"

    result = await db.execute(sa.text(query), params)
    rows = result.fetchall()

    topics = [
        TopicPerformance(
            topic=r.topic,
            correct=r.correct_count,
            total=r.total,
            accuracy=round(r.correct_count / r.total, 3),
        )
        for r in rows
    ]
    return StudyPerformanceResponse(user_id=user_id, exam_type=exam_type, topics=topics)
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/routers/study.py
git commit -m "feat: add study assistant router"
```

---

### Task 20: Create routers/portfolio.py

**Files:**
- Create: `finance-hub-backend/routers/portfolio.py`

- [ ] **Step 1: Create routers/portfolio.py**

```python
"""Portfolio analyzer router — metrics calculated in Python, commentary from Groq."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db
from models.schemas import (
    Holding,
    PortfolioAnalysisResponse,
    PortfolioRequest,
    PositionAnalysis,
)
from services.groq_service import groq_complete
from services.market_service import get_financials, get_stock_price

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


def _compute_herfindahl(weights: list[float]) -> float:
    """Herfindahl-Hirschman Index for portfolio concentration (0=diversified, 1=concentrated)."""
    return float(sum(w**2 for w in weights))


@router.post("/holdings", response_model=PortfolioAnalysisResponse)
async def analyze_holdings(
    request: PortfolioRequest,
    db: AsyncSession = Depends(get_db),
) -> PortfolioAnalysisResponse:
    """Fetch prices, calculate metrics, generate Groq commentary."""
    if not request.holdings:
        raise HTTPException(status_code=400, detail="No holdings provided")

    positions: list[PositionAnalysis] = []
    price_series: dict[str, float] = {}

    for holding in request.holdings:
        price_data = get_stock_price(holding.ticker)
        fin_data = get_financials(holding.ticker)

        current_price = price_data.get("current_price") or 0.0
        current_value = current_price * holding.shares
        cost_total = holding.cost_basis * holding.shares
        pnl_dollar = current_value - cost_total
        pnl_percent = (pnl_dollar / cost_total * 100) if cost_total else 0.0
        price_series[holding.ticker] = current_price

        positions.append(
            PositionAnalysis(
                ticker=holding.ticker.upper(),
                shares=holding.shares,
                cost_basis=holding.cost_basis,
                current_price=current_price,
                current_value=current_value,
                pnl_dollar=round(pnl_dollar, 2),
                pnl_percent=round(pnl_percent, 2),
                sector=fin_data.get("sector"),
                weight=0.0,  # filled below
            )
        )

    # Compute weights
    total_value = sum(p.current_value for p in positions)
    total_cost = sum(p.cost_basis * p.shares for p in positions)
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost else 0.0

    for p in positions:
        p.weight = round(p.current_value / total_value, 4) if total_value else 0.0

    weights = [p.weight for p in positions]
    hhi = _compute_herfindahl(weights)

    # Sector allocation
    sector_alloc: dict[str, float] = {}
    for p in positions:
        sector = p.sector or "Unknown"
        sector_alloc[sector] = round(sector_alloc.get(sector, 0.0) + p.weight, 4)

    # Correlation matrix (use 1.0 on diagonal, 0.0 off-diagonal as placeholder — real correlation needs historical data)
    tickers = [p.ticker for p in positions]
    corr: dict[str, dict[str, float]] = {
        t: {t2: (1.0 if t == t2 else 0.0) for t2 in tickers} for t in tickers
    }

    # Groq commentary
    summary_text = "\n".join(
        f"{p.ticker}: {p.shares} shares @ ${p.cost_basis:.2f} cost, "
        f"now ${p.current_price:.2f}, P&L ${p.pnl_dollar:.2f} ({p.pnl_percent:.1f}%), "
        f"weight {p.weight:.1%}, sector: {p.sector}"
        for p in positions
    )
    commentary_prompt = (
        f"Analyze this portfolio and provide commentary on:\n"
        f"1. Concentration risk (HHI: {hhi:.3f})\n"
        f"2. Sector allocation\n"
        f"3. Suggested rebalancing if needed\n"
        f"4. Brief market context for each position\n\n"
        f"Portfolio:\n{summary_text}\n\n"
        f"Total value: ${total_value:,.2f}, Total P&L: ${total_pnl:,.2f} ({total_pnl_pct:.1f}%)\n"
        f"Sector allocation: {json.dumps(sector_alloc)}\n\n"
        f"Provide 3-4 paragraphs of professional commentary."
    )
    commentary = await groq_complete(commentary_prompt, max_tokens=600)

    # Save holdings to DB
    for holding in request.holdings:
        await db.execute(
            sa.text(
                "INSERT INTO portfolios (id, user_id, ticker, shares, cost_basis, added_at) "
                "VALUES (:id, :uid, :ticker, :shares, :cb, :ts) "
                "ON CONFLICT DO NOTHING"
            ),
            {
                "id": str(uuid.uuid4()),
                "uid": request.user_id,
                "ticker": holding.ticker.upper(),
                "shares": holding.shares,
                "cb": holding.cost_basis,
                "ts": datetime.now(timezone.utc),
            },
        )
    await db.commit()

    return PortfolioAnalysisResponse(
        total_value=round(total_value, 2),
        total_cost=round(total_cost, 2),
        total_pnl_dollar=round(total_pnl, 2),
        total_pnl_percent=round(total_pnl_pct, 2),
        positions=positions,
        sector_allocation=sector_alloc,
        herfindahl_index=round(hhi, 4),
        correlation_matrix=corr,
        commentary=commentary,
    )


@router.get("/analysis/{user_id}", response_model=list[dict])
async def get_saved_portfolio(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Return saved portfolio holdings for a user."""
    result = await db.execute(
        sa.text(
            "SELECT ticker, shares, cost_basis, added_at FROM portfolios "
            "WHERE user_id = :uid ORDER BY added_at DESC"
        ),
        {"uid": user_id},
    )
    return [
        {"ticker": r.ticker, "shares": r.shares, "cost_basis": r.cost_basis, "added_at": str(r.added_at)}
        for r in result.fetchall()
    ]
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/routers/portfolio.py
git commit -m "feat: add portfolio analyzer router"
```

---

### Task 21: Create routers/sentiment.py

**Files:**
- Create: `finance-hub-backend/routers/sentiment.py`

- [ ] **Step 1: Create routers/sentiment.py**

```python
"""News sentiment router — classify articles with Phi-3 Mini, cache with Redis."""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, HTTPException

from models.schemas import ArticleSentiment, SentimentResponse
from services.cache_service import cache_get, cache_set
from services.llm_service import llm_generate
from services.news_service import fetch_news

router = APIRouter(prefix="/api/sentiment", tags=["sentiment"])

_CACHE_TTL = 3600  # 1 hour


async def _classify_article(title: str, summary: str) -> tuple[str, float]:
    """Classify one article as bullish/neutral/bearish with confidence 0-1."""
    prompt = (
        f"Classify this financial news as bullish, neutral, or bearish. "
        f"Reply with exactly: sentiment|confidence (e.g. bullish|0.85)\n\n"
        f"Title: {title}\nSummary: {summary[:300]}\n\nClassification:"
    )
    raw = await llm_generate(prompt, max_tokens=20, temperature=0.1)
    raw = raw.strip().lower()

    for label in ("bullish", "neutral", "bearish"):
        if label in raw:
            try:
                confidence = float(raw.split("|")[1]) if "|" in raw else 0.7
                confidence = max(0.0, min(1.0, confidence))
            except (ValueError, IndexError):
                confidence = 0.7
            return label, confidence

    return "neutral", 0.5


def _compute_overall_score(articles: list[ArticleSentiment]) -> float:
    """Weighted average sentiment score: bullish=1, neutral=0, bearish=-1."""
    if not articles:
        return 0.0
    scores = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}
    total_weight = sum(a.confidence for a in articles)
    if total_weight == 0:
        return 0.0
    weighted_sum = sum(scores[a.sentiment] * a.confidence for a in articles)
    return round(weighted_sum / total_weight, 3)


@router.get("/{query}", response_model=SentimentResponse)
async def get_sentiment(query: str) -> SentimentResponse:
    """Get sentiment analysis for a company/topic query."""
    cache_key = f"sentiment:{query.lower().replace(' ', '_')}"
    cached = await cache_get(cache_key)
    if cached:
        result = SentimentResponse(**cached)
        result.cached = True
        return result

    articles_raw = await fetch_news(query, days=30, max_articles=30)
    if not articles_raw:
        raise HTTPException(status_code=404, detail=f"No news found for '{query}'")

    # Classify all articles concurrently
    classifications = await asyncio.gather(
        *[_classify_article(a["title"], a.get("summary", "")) for a in articles_raw]
    )

    classified: list[ArticleSentiment] = []
    for article, (sentiment, confidence) in zip(articles_raw, classifications):
        classified.append(
            ArticleSentiment(
                title=article["title"],
                url=article["url"],
                published_at=article["published_at"],
                sentiment=sentiment,
                confidence=confidence,
                summary=article.get("summary", "")[:200],
            )
        )

    overall_score = _compute_overall_score(classified)
    if overall_score > 0.2:
        label = "bullish"
    elif overall_score < -0.2:
        label = "bearish"
    else:
        label = "neutral"

    response = SentimentResponse(
        query=query,
        overall_score=overall_score,
        overall_label=label,
        article_count=len(classified),
        articles=classified,
        cached=False,
    )

    await cache_set(cache_key, response.model_dump(mode="json"), ttl_seconds=_CACHE_TTL)
    return response
```

- [ ] **Step 2: Commit**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/routers/sentiment.py
git commit -m "feat: add sentiment analysis router with Redis caching"
```

---

### Task 22: Create main.py and render.yaml

**Files:**
- Create: `finance-hub-backend/main.py`
- Create: `finance-hub-backend/render.yaml`

- [ ] **Step 1: Create main.py**

```python
"""Finance Hub FastAPI application entry point."""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

# Validate required env vars on startup
_REQUIRED = [
    "DATABASE_URL",
    "PINECONE_API_KEY",
    "PINECONE_INDEX_NAME",
    "HUGGINGFACE_SPACE_URL",
    "GROQ_API_KEY",
    "GNEWS_API_KEY",
    "UPSTASH_REDIS_REST_URL",
    "UPSTASH_REDIS_REST_TOKEN",
    "SUPABASE_SERVICE_ROLE_KEY",
]
_missing = [k for k in _REQUIRED if not os.environ.get(k)]
if _missing:
    raise RuntimeError(f"Missing required environment variables: {_missing}")

from routers import chat, document_qa, portfolio, research, sentiment, study, summarizer


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Finance Hub API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(document_qa.router)
app.include_router(summarizer.router)
app.include_router(research.router)
app.include_router(study.router)
app.include_router(portfolio.router)
app.include_router(sentiment.router)


@app.get("/")
async def root() -> dict:
    return {"status": "Finance Hub API is running", "version": "1.0.0"}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
```

- [ ] **Step 2: Create render.yaml**

```yaml
services:
  - type: web
    name: finance-hub-api
    runtime: python
    rootDir: finance-hub-backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

- [ ] **Step 3: Smoke test — verify the app starts**

```powershell
cd C:\Rohan\finance-hub\finance-hub-backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
Expected: `Application startup complete.` — then visit http://localhost:8000/health in browser.
Expected response: `{"status":"ok"}`

Press Ctrl+C to stop.

- [ ] **Step 4: Commit everything**

```powershell
cd C:\Rohan\finance-hub
git add finance-hub-backend/main.py finance-hub-backend/render.yaml
git add finance-hub-backend/routers/__init__.py finance-hub-backend/services/__init__.py
git add finance-hub-backend/models/__init__.py finance-hub-backend/utils/__init__.py
git commit -m "feat: add FastAPI main app and Render deployment config"
git push origin main
```

> ✅ **Phase 2 complete.** Tell the user: "Phase 2 (FastAPI backend) is complete. The backend starts locally at http://localhost:8000. Please verify /health returns OK, then I'll proceed to Phase 3 (Next.js frontend)."
