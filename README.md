# Finance Hub — AI Financial Research Platform

A production-grade full-stack AI financial research platform with 7 specialized modules powered by a fine-tuned Phi-3 Mini model.

## Modules

| Module | Description |
|--------|-------------|
| Document Q&A | Upload PDFs (10-K, earnings releases) and ask questions with citations |
| Earnings Summarizer | Paste any earnings transcript for structured analysis |
| Stock Research | AI-generated research reports with live market data |
| Study Assistant | CFA, Series 7, FRM, CPA exam prep with flashcards and MCQs |
| Portfolio Analyzer | P&L, concentration risk, and AI narrative commentary |
| Sentiment Analyzer | 30-day news sentiment timeline with bullish/bearish classification |
| Financial Chat | Persistent AI chat with sliding context window |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Next.js 14 Frontend (Vercel)                                   │
│  TypeScript · shadcn/ui · React Query · Recharts                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST
┌──────────────────────────▼──────────────────────────────────────┐
│  FastAPI Backend (Render)                                       │
│  Async SQLAlchemy · Pinecone · Upstash Redis · Groq             │
└────────┬──────────────────┬───────────────────────┬────────────┘
         │                  │                       │
┌────────▼───────┐  ┌───────▼──────┐  ┌────────────▼──────────┐
│  HF Space      │  │  Supabase    │  │  Pinecone             │
│  Phi-3 Mini    │  │  PostgreSQL  │  │  Vector Store         │
│  + LoRA        │  │              │  │  384-dim cosine       │
└────────────────┘  └──────────────┘  └───────────────────────┘
```

## Tech Stack

- **Model**: Fine-tuned Phi-3 Mini 4k with LoRA adapter (`rohan1324/phi3-mini-finance-qlora`) on HuggingFace Spaces
- **Backend**: FastAPI, async SQLAlchemy, Pydantic v2
- **LLM**: Phi-3 Mini (custom tasks) + Groq llama-3.1-70b (research, portfolio, sentiment)
- **Vector DB**: Pinecone (384-dim, all-MiniLM-L6-v2 embeddings)
- **Cache**: Upstash Redis (sentiment 1hr, research 30min)
- **Database**: Supabase PostgreSQL (conversations, documents, study)
- **Frontend**: Next.js 14 App Router, TypeScript, Tailwind CSS, shadcn/ui

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- Accounts: Supabase, Pinecone, Upstash, Groq, GNews, HuggingFace

### Backend

```bash
cd finance-hub-backend
pip install -r requirements.txt
python db_init.py          # create database tables (run once)
uvicorn main:app --reload  # starts at http://localhost:8000
```

### Frontend

```bash
cd finance-hub-frontend
cp .env.local.example .env.local
# edit .env.local with your values
npm install
npm run dev                # starts at http://localhost:3000
```

### Environment Variables

Copy `finance-hub-frontend/.env.local.example` and fill in your values. The backend reads from `.env` at the repo root.

## Deployment

### Backend (Render)
1. Connect GitHub repo to Render
2. Set root directory: `finance-hub-backend`
3. Add all environment variables from `.env` to Render dashboard
4. Deploy — Render uses `render.yaml` at repo root

### Frontend (Vercel)
1. Connect GitHub repo to Vercel
2. Set root directory: `finance-hub-frontend`
3. Add environment variables:
   - `NEXTAUTH_URL` = your Vercel URL
   - `NEXTAUTH_SECRET` = `openssl rand -base64 32`
   - `NEXT_PUBLIC_API_URL` = your Render URL

## Project Structure

```
finance-hub/
├── finance-hub-backend/     # FastAPI backend (deploy to Render)
│   ├── models/              # Pydantic schemas + async DB engine
│   ├── routers/             # 7 API routers (chat, documents, etc.)
│   ├── services/            # LLM, RAG, market data, news, cache
│   ├── utils/               # chunking, embeddings, context window
│   ├── main.py              # app entry point
│   └── requirements.txt
├── finance-hub-frontend/    # Next.js 14 frontend (deploy to Vercel)
│   ├── app/                 # App Router pages
│   ├── components/          # Navbar, Sidebar, shadcn/ui
│   ├── lib/                 # API client, auth, utils
│   └── types/               # TypeScript interfaces
├── render.yaml              # Render deployment config
└── .env                     # Backend secrets (gitignored)
```
