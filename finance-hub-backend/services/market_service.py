"""Market data via FMP stable API + yfinance fast_info fallback.

FMP /v3/ endpoints were retired August 31, 2025. All calls now use the
/stable/ API. yfinance fast_info is tried first for price data (no auth
needed), falling back to FMP quote if Yahoo Finance blocks the request.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx
import requests
import yfinance as yf

logger = logging.getLogger(__name__)

_FMP_KEY = os.environ.get("FMP_API_KEY", "").strip()
_FMP_BASE = "https://financialmodelingprep.com/stable"

if not _FMP_KEY:
    logger.warning("FMP_API_KEY not set — market data will be limited")


def _fmp(path: str, **params) -> Any:
    """GET a FMP stable endpoint, returning parsed JSON or None on error."""
    try:
        resp = requests.get(
            f"{_FMP_BASE}/{path}",
            params={"apikey": _FMP_KEY, **params},
            timeout=10,
        )
        logger.warning("FMP /%s params=%s status=%d body=%s", path, params, resp.status_code, resp.text[:300])
        if resp.status_code == 200:
            return resp.json()
    except Exception as exc:
        logger.warning("FMP /%s error: %s", path, exc)
    return None


def get_stock_price(ticker: str) -> dict[str, Any]:
    """Return current price, volume, and market cap.

    Tries yfinance fast_info first (no auth); falls back to FMP quote.
    """
    try:
        fi = yf.Ticker(ticker).fast_info
        price = fi.last_price
        if price:
            return {
                "ticker": ticker.upper(),
                "current_price": price,
                "volume": fi.last_volume,
                "market_cap": fi.market_cap,
                "currency": fi.currency,
            }
    except Exception:
        pass

    # yfinance blocked — use FMP quote
    if _FMP_KEY:
        data = _fmp("quote", symbol=ticker)
        if data and isinstance(data, list) and data:
            q = data[0]
            return {
                "ticker": ticker.upper(),
                "current_price": q.get("price"),
                "volume": q.get("volume"),
                "market_cap": q.get("marketCap"),
                "currency": "USD",
            }

    return {"ticker": ticker.upper(), "error": "price data unavailable"}


def get_financials(ticker: str) -> dict[str, Any]:
    """Return key financial metrics from FMP stable API."""
    if not _FMP_KEY:
        logger.warning("FMP_API_KEY missing — skipping fundamentals for %s", ticker)
        return {"ticker": ticker.upper(), "company_name": ticker}

    base: dict[str, Any] = {"ticker": ticker.upper(), "company_name": ticker}

    profile = _fmp("profile", symbol=ticker)
    if profile and isinstance(profile, list) and profile:
        p = profile[0]
        base.update({
            "company_name": p.get("companyName", ticker),
            "sector": p.get("sector"),
            "industry": p.get("industry"),
            "description": (p.get("description") or "")[:500],
        })

    metrics = _fmp("key-metrics-ttm", symbol=ticker)
    if metrics and isinstance(metrics, list) and metrics:
        m = metrics[0]
        base.update({
            "pe_ratio": m.get("peRatioTTM"),
            "ev_ebitda": m.get("evToEbitdaTTM") or m.get("enterpriseValueOverEBITDATTM"),
            "gross_margin": m.get("grossProfitMarginTTM"),
            "revenue_growth_yoy": m.get("revenueGrowthTTM"),
        })

    return base


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
