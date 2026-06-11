"""Finance Hub FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import chat, document_qa, portfolio, research, sentiment, study, summarizer

app = FastAPI(
    title="Finance Hub API",
    description="AI-powered financial research platform",
    version="1.0.0",
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


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "finance-hub-api", "version": "1.0.0"}
