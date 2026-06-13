"""Market data: yfinance fast_info (price/market cap) + FMP (fundamentals).

Yahoo Finance's quoteSummary endpoint (used by yf.Ticker.info) is blocked
by Cloudflare Edge on cloud server IPs. fast_info uses /v8/finance/chart/
which is not restricted the same way and reliably returns price/market cap.

For sector, industry, and financial ratios, Financial Modeling Prep (FMP)
is used when FMP_API_KEY is set. Without it, those fields return None and
the Groq report notes the data is unavailable.
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
_FMP_BASE = "https://financialmodelingprep.com/api/v3"

if _FMP_KEY:
    logger.info("FMP_API_KEY loaded (len=%d)", len(_FMP_KEY))
else:
    logger.warning("FMP_API_KEY not set — fundamental data will be unavailable")


def get_stock_price(ticker: str) -> dict[str, Any]:
    """Return current price, volume, and market cap via yfinance fast_info."""
    try:
        fi = yf.Ticker(ticker).fast_info
        return {
            "ticker": ticker.upper(),
            "current_price": fi.last_price,
            "volume": fi.last_volume,
            "market_cap": fi.market_cap,
            "currency": fi.currency,
        }
    except Exception as exc:
        return {"ticker": ticker.upper(), "error": str(exc)}


def _fmp_get_financials(ticker: str) -> dict[str, Any]:
    """Fetch fundamentals from Financial Modeling Prep (requires FMP_API_KEY)."""
    base = {"ticker": ticker.upper()}
    try:
        profile_resp = requests.get(
            f"{_FMP_BASE}/profile/{ticker}",
            params={"apikey": _FMP_KEY},
            timeout=10,
        )
        logger.info("FMP profile %s: status=%d body=%s", ticker, profile_resp.status_code, profile_resp.text[:200])
        profile = profile_resp.json()
        if profile and isinstance(profile, list):
            p = profile[0]
            base.update({
                "company_name": p.get("companyName", ticker),
                "sector": p.get("sector"),
                "industry": p.get("industry"),
                "description": (p.get("description") or "")[:500],
            })
    except Exception as exc:
        logger.warning("FMP profile error for %s: %s", ticker, exc)

    try:
        ratios_resp = requests.get(
            f"{_FMP_BASE}/ratios-ttm/{ticker}",
            params={"apikey": _FMP_KEY},
            timeout=10,
        )
        logger.info("FMP ratios %s: status=%d body=%s", ticker, ratios_resp.status_code, ratios_resp.text[:200])
        ratios = ratios_resp.json()
        if ratios and isinstance(ratios, list):
            r = ratios[0]
            base.update({
                "pe_ratio": r.get("peRatioTTM"),
                "ev_ebitda": r.get("enterpriseValueMultipleTTM"),
                "gross_margin": r.get("grossProfitMarginTTM"),
                "revenue_growth_yoy": r.get("revenueGrowthTTM"),
            })
    except Exception as exc:
        logger.warning("FMP ratios error for %s: %s", ticker, exc)

    return base


def get_financials(ticker: str) -> dict[str, Any]:
    """Return key financial metrics. Uses FMP if key is set, else returns partial data."""
    if _FMP_KEY:
        return _fmp_get_financials(ticker)

    # No FMP key — return minimal data so Groq report is honest about missing fundamentals
    return {
        "ticker": ticker.upper(),
        "company_name": ticker,
        "note": "Fundamental data unavailable (FMP_API_KEY not configured).",
    }


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
