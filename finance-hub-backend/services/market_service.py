"""Market data via FMP stable API (free tier) + yfinance fast_info fallback.

FMP free tier provides: /stable/profile, /stable/income-statement, /stable/key-metrics.
Profile contains price, marketCap, sector, industry, companyName.
P/E and gross margin are calculated from income statement + profile price.
EV/EBITDA is fetched from FMP key-metrics (enterpriseValueOverEBITDA), with a
yfinance .info fallback if that endpoint returns nothing.
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
        logger.warning("FMP /%s status=%d body=%s", path, resp.status_code, resp.text[:300])
        if resp.status_code == 200:
            return resp.json()
    except Exception as exc:
        logger.warning("FMP /%s error: %s", path, exc)
    return None


def _fmp_profile(ticker: str) -> dict | None:
    """Fetch FMP profile for a ticker, return the first item or None."""
    data = _fmp("profile", symbol=ticker)
    if data and isinstance(data, list) and data:
        return data[0]
    return None


def get_stock_price(ticker: str) -> dict[str, Any]:
    """Return current price, volume, and market cap.

    Tries yfinance fast_info first; falls back to FMP profile on failure.
    Both are blocked for some tickers on cloud IPs; FMP profile is reliable.
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

    if _FMP_KEY:
        p = _fmp_profile(ticker)
        if p:
            return {
                "ticker": ticker.upper(),
                "current_price": p.get("price"),
                "volume": p.get("volume"),
                "market_cap": p.get("marketCap"),
                "currency": p.get("currency", "USD"),
            }

    return {"ticker": ticker.upper(), "error": "price data unavailable"}


def get_financials(ticker: str) -> dict[str, Any]:
    """Return key financial metrics from FMP stable (free tier).

    P/E is calculated as price / diluted EPS from the income statement.
    Gross margin is grossProfit / revenue.
    EV/EBITDA comes from FMP key-metrics, with a yfinance .info fallback.
    """
    if not _FMP_KEY:
        logger.warning("FMP_API_KEY missing — skipping fundamentals for %s", ticker)
        return {"ticker": ticker.upper(), "company_name": ticker}

    base: dict[str, Any] = {"ticker": ticker.upper(), "company_name": ticker}

    # Profile: company info + current price (used to calculate P/E)
    p = _fmp_profile(ticker)
    price = None
    if p:
        price = p.get("price")
        base.update({
            "company_name": p.get("companyName", ticker),
            "sector": p.get("sector"),
            "industry": p.get("industry"),
            "description": (p.get("description") or "")[:500],
        })

    market_cap = p.get("marketCap") if p else None

    # Income statement: derive P/E, gross margin, operating margin, P/S, revenue growth YoY
    stmts = _fmp("income-statement", symbol=ticker, limit=2)
    if stmts and isinstance(stmts, list) and stmts:
        latest = stmts[0]
        revenue = latest.get("revenue")
        gross_profit = latest.get("grossProfit")
        operating_income = latest.get("operatingIncome")
        eps = latest.get("epsdiluted") or latest.get("eps")

        if price and eps and float(eps) > 0:
            base["pe_ratio"] = round(float(price) / float(eps), 2)

        if revenue and gross_profit and float(revenue) > 0:
            base["gross_margin"] = round(float(gross_profit) / float(revenue), 4)

        if revenue and operating_income and float(revenue) > 0:
            base["operating_margin"] = round(float(operating_income) / float(revenue), 4)

        if market_cap and revenue and float(revenue) > 0:
            base["ps_ratio"] = round(float(market_cap) / float(revenue), 2)

        if len(stmts) >= 2 and revenue:
            prev_revenue = stmts[1].get("revenue")
            if prev_revenue and float(prev_revenue) > 0:
                base["revenue_growth_yoy"] = round(
                    (float(revenue) - float(prev_revenue)) / float(prev_revenue), 4
                )

    # EV/EBITDA: try FMP key-metrics first, fall back to yfinance
    km = _fmp("key-metrics", symbol=ticker, limit=1)
    if km and isinstance(km, list) and km:
        ev_ebitda = km[0].get("enterpriseValueOverEBITDA")
        if ev_ebitda is not None:
            try:
                base["ev_ebitda"] = round(float(ev_ebitda), 2)
            except (TypeError, ValueError):
                pass

    if "ev_ebitda" not in base:
        try:
            info = yf.Ticker(ticker).info
            ev_ebitda = info.get("enterpriseToEbitda")
            if ev_ebitda is not None:
                base["ev_ebitda"] = round(float(ev_ebitda), 2)
        except Exception as exc:
            logger.warning("yfinance EV/EBITDA fallback failed for %s: %s", ticker, exc)

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
