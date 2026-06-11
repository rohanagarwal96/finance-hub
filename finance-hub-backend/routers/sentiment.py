"""News Sentiment Analyzer — GNews + Reuters + Groq classification."""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from services.cache_service import cache_get, cache_set
from services.groq_service import groq_complete
from services.news_service import fetch_news

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


@router.get("/{ticker}")
async def analyze_sentiment(ticker: str, days: int = 30) -> dict:
    """Analyze news sentiment for a ticker over the past N days."""
    ticker = ticker.upper().strip()
    cache_key = f"sentiment:{ticker}:{days}"

    cached = await cache_get(cache_key)
    if cached:
        return cached

    articles = await fetch_news(f"{ticker} stock", days=days, max_articles=20)
    if not articles:
        raise HTTPException(status_code=404, detail=f"No news found for {ticker}")

    # Build classification prompt
    articles_text = "\n\n".join(
        [f"[{i+1}] {a['title']}: {a['summary'][:200]}" for i, a in enumerate(articles)]
    )
    prompt = (
        f"You are a financial sentiment analyst. Classify the sentiment of these news articles about {ticker}.\n\n"
        f"{articles_text}\n\n"
        "Return a JSON object with:\n"
        '{"overall_sentiment": "bullish|bearish|neutral", "confidence": 0-100, '
        '"bullish_count": N, "bearish_count": N, "neutral_count": N, '
        '"key_themes": ["theme1", "theme2", "theme3"], "summary": "2-3 sentence overview"}\n\n'
        "Return ONLY the JSON."
    )

    raw = await groq_complete(prompt, max_tokens=500)

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        sentiment_data = json.loads(raw[start:end]) if start != -1 else {}
    except Exception:
        sentiment_data = {}

    result = {
        "ticker": ticker,
        "days_analyzed": days,
        "article_count": len(articles),
        "overall_sentiment": sentiment_data.get("overall_sentiment", "neutral"),
        "confidence": sentiment_data.get("confidence", 50),
        "bullish_count": sentiment_data.get("bullish_count", 0),
        "bearish_count": sentiment_data.get("bearish_count", 0),
        "neutral_count": sentiment_data.get("neutral_count", 0),
        "key_themes": sentiment_data.get("key_themes", []),
        "summary": sentiment_data.get("summary", ""),
        "articles": articles[:10],
    }

    await cache_set(cache_key, result, ttl_seconds=3600)  # 1 hour
    return result
