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
