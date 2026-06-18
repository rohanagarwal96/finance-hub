"""Finance Hub FastAPI application entry point."""
import asyncio
import logging
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.database import DATABASE_URL
from routers import chat, document_qa, portfolio, research, sentiment, study, summarizer
from utils.embeddings import _get_model

logger = logging.getLogger(__name__)

DDL = """
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS title TEXT DEFAULT '';
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    namespace TEXT NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS namespace TEXT DEFAULT '';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS chunk_count INTEGER DEFAULT 0;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
CREATE TABLE IF NOT EXISTS study_questions (
    id TEXT PRIMARY KEY,
    document_id TEXT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    topic TEXT DEFAULT 'General',
    difficulty TEXT DEFAULT 'medium',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS study_attempts (
    id TEXT PRIMARY KEY,
    question_id TEXT REFERENCES study_questions(id) ON DELETE CASCADE,
    user_answer TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    score INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm the embedding model so it's in memory before the first upload
    # request arrives. Without this, the lazy load + PDF processing happen
    # concurrently on the first request and push the process past the 512 MB limit.
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _get_model)
        logger.info("Embedding model warmed up.")
    except Exception as exc:
        logger.warning("Embedding model pre-warm failed: %s", exc)

    # Create tables on startup (idempotent — IF NOT EXISTS)
    try:
        asyncpg_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(asyncpg_url)
        await conn.execute(DDL)
        await conn.close()
        logger.info("Database tables ready.")
    except Exception as exc:
        logger.warning("DB init skipped: %s", exc)
    yield


app = FastAPI(
    title="Finance Hub API",
    description="AI-powered financial research platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
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


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "finance-hub-api", "version": "1.0.0"}
