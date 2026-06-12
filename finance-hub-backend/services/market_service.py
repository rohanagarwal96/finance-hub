"""yfinance wrapper for stock prices, financials, and SEC EDGAR filings."""
from __future__ import annotations

from typing import Any

import httpx
import requests
import yfinance as yf


def _yf_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    return session


def get_stock_price(ticker: str) -> dict[str, Any]:
    """Return current price, volume, and market cap for a ticker."""
    try:
        t = yf.Ticker(ticker, session=_yf_session())
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
        t = yf.Ticker(ticker, session=_yf_session())
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
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom"
                f"&startdt=2023-01-01&forms=10-K,10-Q",
                headers={"User-Agent": "FinanceHub research@financehub.app"},
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
