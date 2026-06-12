"""Stock Research — Groq agent with market data tools."""
from __future__ import annotations

import json

from fastapi import APIRouter
from pydantic import BaseModel

from services.cache_service import cache_get, cache_set
from services.groq_service import groq_complete
from services.market_service import get_financials, get_sec_filings, get_stock_price

router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    ticker: str
    focus: str = "comprehensive"  # comprehensive | valuation | growth | risks


@router.post("/")
async def research_stock(request: ResearchRequest) -> dict:
    """Generate a full research report for a stock ticker."""
    ticker = request.ticker.upper().strip()
    cache_key = f"research:{ticker}:{request.focus}"

    cached = await cache_get(cache_key)
    if cached:
        return cached

    # Gather market data (errors are non-fatal — Groq can still generate a report)
    price_data = get_stock_price(ticker)
    financial_data = get_financials(ticker)
    filings = await get_sec_filings(ticker)

    company_name = financial_data.get("company_name", ticker)
    prompt = (
        f"You are a senior equity analyst. Write a {request.focus} research report for {company_name} ({ticker}).\n\n"
        f"Market Data:\n{json.dumps(price_data, indent=2)}\n\n"
        f"Financial Metrics:\n{json.dumps(financial_data, indent=2)}\n\n"
        f"Recent SEC Filings: {len(filings)} filings found\n\n"
        "Structure your report with these sections:\n"
        "1. Executive Summary\n"
        "2. Financial Performance\n"
        "3. Valuation Analysis\n"
        "4. Key Risks\n"
        "5. Investment Recommendation\n\n"
        "Be specific, cite numbers, and provide a clear BUY/HOLD/SELL recommendation with rationale."
    )

    report_text = await groq_complete(prompt, max_tokens=1200)

    result = {
        "ticker": ticker,
        "company_name": company_name,
        "focus": request.focus,
        "report": report_text,
        "market_data": price_data,
        "financials": financial_data,
        "sec_filings": filings,
    }

    await cache_set(cache_key, result, ttl_seconds=1800)  # 30 min
    return result
