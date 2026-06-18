"""Pydantic v2 request and response schemas for all API endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatMessageRequest(BaseModel):
    conversation_id: Optional[str] = None
    user_id: str = "anonymous"
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
    operating_margin: Optional[float] = None
    ps_ratio: Optional[float] = None
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
