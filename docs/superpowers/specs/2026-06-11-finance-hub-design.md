# Finance Hub — Design Spec
**Date:** 2026-06-11  
**Status:** Approved

---

## 1. Project Overview

Finance Hub is a full-stack AI-powered financial research platform. Every feature is backed by a fine-tuned Phi-3 Mini language model (hosted on HuggingFace Spaces) and/or Groq Llama 3.1 70B for complex reasoning tasks. The application has 7 distinct financial AI modules, persistent storage, and authentication.

**Live model:** `rohan1324/phi3-mini-finance-qlora`  
**HF Space URL:** `https://rohan1324-finance-hub-api.hf.space`  
**GitHub repo:** `github.com/rohanagarwal96/finance-hub`

---

## 2. Repository Layout

```
C:\Rohan\finance-hub\               ← main GitHub repo (monorepo)
├── finance-hub-backend/            ← Render deploys from this subdirectory
├── finance-hub-frontend/           ← Vercel deploys from this subdirectory
├── docs/superpowers/specs/         ← design specs
├── README.md
├── .env                            ← backend secrets (gitignored)
└── .env.local                      ← frontend secrets (gitignored)

C:\Rohan\finance-hub-api\           ← HF Space repo (separate git, pushes to HF only)
├── Dockerfile
├── requirements.txt
└── app.py
```

---

## 3. Infrastructure

| Service | Purpose | Provider |
|---------|---------|----------|
| Frontend hosting | Next.js app | Vercel |
| Backend API | FastAPI server | Render (free tier) |
| Database | PostgreSQL | Supabase |
| Vector store | Embeddings (384-dim, cosine) | Pinecone (`finance-hub` index, us-east-1) |
| Cache | Redis | Upstash |
| Model server | Fine-tuned Phi-3 Mini inference | HuggingFace Spaces |
| Fast LLM | Complex reasoning (Llama 3.1 70B) | Groq |
| Stock data | Prices, financials, filings | yfinance + SEC EDGAR |
| News | Headlines + sentiment | GNews API + Reuters RSS |

---

## 4. Database Schema (already exists in Supabase)

```sql
users           (id, email, name, created_at)
conversations   (id, user_id, title, created_at)
messages        (id, conversation_id, role, content, created_at)
documents       (id, user_id, filename, pinecone_namespace, uploaded_at)
study_attempts  (id, user_id, topic, exam_type, correct, question, user_answer, attempted_at)
portfolios      (id, user_id, ticker, shares, cost_basis, added_at)
```

RLS is disabled. All indexes already created.

---

## 5. Phase 1 — HuggingFace Space Model Server

**Location:** Cloned to `C:\Rohan\finance-hub-api\` (sibling of main repo)

### Files

**`Dockerfile`**
- Base: `python:3.11-slim`
- Exposes port 7860 (HF Spaces requirement)
- Installs dependencies, copies app files, runs uvicorn

**`requirements.txt`**
- `fastapi`, `uvicorn`, `transformers`, `peft`, `torch` (CPU), `bitsandbytes`, `accelerate`, `sentencepiece`, `protobuf`, `huggingface_hub`

**`app.py`**
- FastAPI server, CORS configured for `*.render.com` and `*.vercel.app`
- Model loaded once at startup: Phi-3 Mini base + LoRA adapter via `peft`, 4-bit quantization via `bitsandbytes` for CPU memory efficiency
- `GET /health` → `{"status": "ok", "model": "loaded"}`
- `POST /generate` → accepts `{"prompt": str, "max_tokens": int, "temperature": float}`, returns `{"generated_text": str}`
- No authentication on Space (Render backend is only caller)

### Constraints
- HF free CPU tier: ~16GB RAM — 4-bit quantized Phi-3 Mini fits
- Cold start: 60-120s — frontend must show warm-up indicator
- Inference latency: 30-60s per request — frontend must never appear frozen

---

## 6. Phase 2 — FastAPI Backend

**Location:** `finance-hub-backend/`  
**Render root directory:** `finance-hub-backend`  
**Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Architecture Decisions
- **Async throughout:** `asyncpg` for DB connections, `httpx.AsyncClient` for HF Space calls, async news fetching
- **No ORM for reads:** Raw SQL via asyncpg for list/history endpoints; SQLAlchemy only for schema definition
- **Groq used only for Modules 3, 5, 6** to stay within free tier (14,400 req/day)
- **Pinecone namespaced** by `{user_id}/{doc_id}` for multi-user isolation; free tier 100k vector limit
- **Redis cache keys and TTLs:**
  - `sentiment:{query}` — 1 hour
  - `research:{ticker}` — 30 minutes
  - `stock_price:{ticker}` — 5 minutes

### Directory Structure

```
finance-hub-backend/
├── main.py
├── requirements.txt
│                               (local dev loads ../.env via python-dotenv; Render uses dashboard env vars)
├── render.yaml
├── routers/
│   ├── document_qa.py          POST /api/document/upload
│   │                           POST /api/document/query
│   │                           GET  /api/document/list
│   ├── summarizer.py           POST /api/summarize/earnings  (SSE streaming)
│   ├── research.py             GET  /api/research/{ticker}
│   ├── study.py                GET  /api/study/question
│   │                           POST /api/study/attempt
│   │                           GET  /api/study/performance/{user_id}
│   ├── portfolio.py            POST /api/portfolio/holdings
│   │                           GET  /api/portfolio/analysis/{user_id}
│   ├── sentiment.py            GET  /api/sentiment/{query}
│   └── chat.py                 POST /api/chat/message
│                               GET  /api/chat/history/{conversation_id}
│                               GET  /api/chat/conversations/{user_id}
├── services/
│   ├── llm_service.py          HF Space async HTTP wrapper, retry + backoff
│   ├── groq_service.py         Groq SDK wrapper, streaming support
│   ├── rag_service.py          LangChain + Pinecone RAG pipeline
│   ├── market_service.py       yfinance + SEC EDGAR
│   ├── news_service.py         GNews + Reuters RSS via feedparser
│   └── cache_service.py        Upstash Redis REST client
├── models/
│   ├── database.py             SQLAlchemy async engine + session
│   └── schemas.py              Pydantic v2 request/response models
└── utils/
    ├── chunking.py             PDF parsing (PyMuPDF) + recursive text splitting
    ├── embeddings.py           sentence-transformers all-MiniLM-L6-v2 (384 dims)
    └── context_window.py       Token counting (tiktoken) + sliding window summarization
```

### Module-to-Model Mapping
| Module | Model |
|--------|-------|
| Document Q&A (RAG) | Fine-tuned Phi-3 Mini (HF Space) |
| Earnings Summarizer | Fine-tuned Phi-3 Mini (HF Space) |
| Stock Research Copilot | Groq Llama 3.1 70B |
| Study Assistant | Fine-tuned Phi-3 Mini (HF Space) |
| Portfolio Analyzer (commentary) | Groq Llama 3.1 70B |
| News Sentiment | Fine-tuned Phi-3 Mini (HF Space) |
| Financial Chat | Fine-tuned Phi-3 Mini (HF Space) |

### Key Implementation Details

**Document Q&A:**
- Chunk size: 512 tokens, 50-token overlap
- Embeddings: all-MiniLM-L6-v2 (384 dims)
- Retrieve top-10 from Pinecone, re-rank to top-3 by cosine score
- Response includes page number and section metadata as citations
- PDF upload limit: 10MB enforced client-side before upload

**Earnings Summarizer:**
- Map-reduce for transcripts >4000 tokens
- SSE streaming via `StreamingResponse` with `text/event-stream`
- Output sections: Revenue & Growth, Gross Margin, Guidance, Key Risks, Management Tone, Top 3 Analyst Q&A

**Stock Research (Groq agent with tool calling):**
- Tools: `get_stock_price`, `get_financials`, `get_recent_news`, `get_sec_filings`
- Output sections: Company Overview, Financial Performance, Key Metrics, Recent News, Bull Case (3pts), Bear Case (3pts), Key Risks

**Study Assistant:**
- Exams: CFA Level 1, Series 7, FRM, CPA
- Modes: Flashcard, Practice Exam, Weak Spot Analysis
- Weak spot selection: weighted by (1 - accuracy) per topic from study_attempts table
- All attempts persisted to study_attempts

**Portfolio Analyzer:**
- Python/pandas calculates all metrics (P&L, sector allocation, Herfindahl index, correlation matrix)
- Groq generates narrative commentary only — LLM never touches raw numbers directly

**News Sentiment:**
- Fetch last 30 days via GNews + Reuters RSS
- Phi-3 Mini classifies each article: Bullish/Neutral/Bearish + confidence 0-1
- Redis cache prevents repeat fetching within 1 hour

**Financial Chat:**
- Sliding context window: summarize oldest messages when history exceeds 3000 tokens
- Context summarization uses Phi-3 Mini
- Conversation title auto-generated from first message content

### Error Handling
- 400: bad input, 401: unauthorized, 404: not found, 500: server errors
- Never return raw exceptions to client
- yfinance wrapped in try/except with fallback message
- HF Space calls: 3 retries with exponential backoff, 120s timeout

---

## 7. Phase 3 — Next.js Frontend

**Location:** `finance-hub-frontend/`  
**Vercel root directory:** `finance-hub-frontend`

### Tech Stack
- Next.js 14 (App Router), TypeScript strict mode
- Tailwind CSS + shadcn/ui
- NextAuth.js (email provider; Google OAuth wired but requires credentials)
- React Query for server state
- Recharts for all charts
- react-dropzone for PDF upload
- framer-motion for animations
- axios for API calls
- EventSource (native) for SSE streaming

### Design System
| Token | Value | Usage |
|-------|-------|-------|
| Background | `#0f172a` | Page background |
| Accent | `#3b82f6` | Interactive elements, links |
| Positive | `#10b981` | Gains, bullish signals |
| Warning | `#f59e0b` | Neutral, caution |
| Danger | `#f43f5e` | Losses, bearish signals |
| Font (numbers) | JetBrains Mono | All financial data |
| Font (body) | Inter | UI text |

### Pages
| Route | Description |
|-------|-------------|
| `/` | Landing: hero, 7-module feature grid, CTA → /login |
| `/login` | NextAuth login (email + Google placeholder) |
| `/dashboard` | 7 module cards + recent activity + quick stats |
| `/document-qa` | PDF upload + citation-grounded Q&A |
| `/earnings-summarizer` | Transcript paste + real-time streaming summary |
| `/stock-research` | Ticker search + structured research report |
| `/study` | Exam/topic/mode selector + flashcard/MCQ/performance |
| `/portfolio` | Holdings input + allocation/P&L/correlation charts + AI commentary |
| `/sentiment` | Query input + sentiment gauge + timeline + article list |
| `/chat` | Persistent chat with conversation history sidebar |
| `/history` | Saved conversations / reports / documents (tabbed) |

### API Client (`lib/api.ts`)
- Typed functions for every backend endpoint
- axios base URL from `NEXT_PUBLIC_API_URL`
- All requests wrapped in try/catch; errors surface as toast notifications
- Loading states on every async operation

### Key Frontend Behaviors
- PDF upload: 10MB limit enforced client-side before any network call
- Earnings summarizer: EventSource reads SSE chunks, renders sections as they arrive
- Backend warm-up: if first response takes >5s, show "Warming up server..." indicator (Render free tier spins down after 15min)
- All charts: Recharts (pie, bar, line, custom heatmap)
- Cross-module: Stock Research "Ask follow-up" button opens /chat with report pre-loaded as context

---

## 8. Phase 4 — Deployment

### Render (`render.yaml` in `finance-hub-backend/`)
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
All backend `.env` variables added manually in Render dashboard.

### Vercel
- Root directory set to `finance-hub-frontend` in Vercel dashboard
- All `.env.local` variables added in Vercel dashboard
- `NEXTAUTH_URL` updated to production Vercel URL
- `NEXT_PUBLIC_API_URL` updated to production Render URL

### HF Space CORS Update
After Render and Vercel URLs are known, update `app.py` CORS origins and push to HF Space.

### End-to-End Verification Checklist
- [ ] Upload PDF, ask question, verify citation appears
- [ ] Paste short earnings transcript, verify all 6 sections stream
- [ ] Research AAPL, verify bull/bear case renders
- [ ] Generate CFA study question, submit answer, check study_attempts in DB
- [ ] Add 1-2 portfolio holdings, verify P&L and charts
- [ ] Check sentiment for a company, verify Redis cache on second request
- [ ] Send chat message, verify saved to messages table

---

## 9. Environment Variables

### Backend (`.env` / Render dashboard)
| Variable | Source |
|----------|--------|
| `DATABASE_URL` | Supabase → Settings → Database → URI |
| `PINECONE_API_KEY` | Pinecone dashboard → API Keys |
| `PINECONE_INDEX_NAME` | `finance-hub` |
| `PINECONE_ENVIRONMENT` | `us-east-1` |
| `UPSTASH_REDIS_REST_URL` | Upstash dashboard |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash dashboard |
| `HUGGINGFACE_API_TOKEN` | HuggingFace → Settings → Tokens |
| `HUGGINGFACE_MODEL_ID` | `rohan1324/phi3-mini-finance-qlora` |
| `HUGGINGFACE_SPACE_URL` | `https://rohan1324-finance-hub-api.hf.space` |
| `GROQ_API_KEY` | Groq console → API Keys |
| `GNEWS_API_KEY` | GNews dashboard |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API → service_role |

### Frontend (`.env.local` / Vercel dashboard)
| Variable | Source |
|----------|--------|
| `NEXTAUTH_URL` | Your Vercel deployment URL |
| `NEXTAUTH_SECRET` | `openssl rand -base64 32` |
| `NEXT_PUBLIC_API_URL` | Your Render deployment URL |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase → Settings → API |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase → Settings → API |

---

## 10. Known Constraints & Mitigations

| Constraint | Mitigation |
|-----------|-----------|
| HF Space CPU inference 30-60s | Frontend loading state, never appear frozen |
| Render free tier 15min spin-down | "Warming up..." indicator if response >5s |
| Pinecone free tier 100k vectors | Namespace by user+doc, prune old docs |
| Upstash free tier 10k req/day | Aggressive caching (sentiment 1hr, research 30min) |
| Groq free tier 14,400 req/day | Only Modules 3, 5, 6 use Groq |
| yfinance flakiness | try/except everywhere, graceful fallback message |
