"""Create all database tables. Run once: python db_init.py"""
import asyncio
import os

import asyncpg
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.env"))

_raw_url = os.environ["DATABASE_URL"].strip().strip('"')
_asyncpg_url = _raw_url.replace("postgresql://", "").replace("postgresql+asyncpg://", "")


DDL = """
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

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


async def init_db() -> None:
    conn = await asyncpg.connect(_asyncpg_url)
    try:
        await conn.execute(DDL)
        print("All tables created (or already exist).")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_db())
