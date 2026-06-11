"""Portfolio Analyzer — Python metrics + Groq commentary."""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.groq_service import groq_complete
from services.market_service import get_stock_price

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class HoldingInput(BaseModel):
    ticker: str
    shares: float
    avg_cost: float


class PortfolioAnalysisRequest(BaseModel):
    holdings: list[HoldingInput]
    risk_tolerance: str = "moderate"  # conservative | moderate | aggressive


@router.post("/analyze")
async def analyze_portfolio(request: PortfolioAnalysisRequest) -> dict:
    """Analyze a portfolio and return metrics + AI commentary."""
    if not request.holdings:
        raise HTTPException(status_code=400, detail="Portfolio must have at least one holding")

    positions = []
    total_value = 0.0
    total_cost = 0.0

    for holding in request.holdings:
        price_data = get_stock_price(holding.ticker)
        current_price = price_data.get("current_price") or holding.avg_cost
        market_value = current_price * holding.shares
        cost_basis = holding.avg_cost * holding.shares
        gain_loss = market_value - cost_basis
        gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0.0

        positions.append(
            {
                "ticker": holding.ticker.upper(),
                "shares": holding.shares,
                "avg_cost": holding.avg_cost,
                "current_price": current_price,
                "market_value": round(market_value, 2),
                "cost_basis": round(cost_basis, 2),
                "gain_loss": round(gain_loss, 2),
                "gain_loss_pct": round(gain_loss_pct, 2),
            }
        )
        total_value += market_value
        total_cost += cost_basis

    # Portfolio-level metrics
    total_gain_loss = total_value - total_cost
    total_return_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0.0

    # Concentration (weight per position)
    for pos in positions:
        pos["weight_pct"] = round((pos["market_value"] / total_value * 100) if total_value > 0 else 0.0, 2)

    # Top winner / loser
    sorted_positions = sorted(positions, key=lambda x: x["gain_loss_pct"], reverse=True)
    top_winner = sorted_positions[0]["ticker"] if sorted_positions else "N/A"
    top_loser = sorted_positions[-1]["ticker"] if sorted_positions else "N/A"

    # Groq commentary
    prompt = (
        f"You are a financial advisor. Analyze this {request.risk_tolerance}-risk portfolio:\n\n"
        f"Holdings:\n{json.dumps(positions, indent=2)}\n\n"
        f"Total Value: ${total_value:,.2f}\n"
        f"Total Return: {total_return_pct:.2f}%\n\n"
        "Provide:\n"
        "1. Portfolio health assessment (2-3 sentences)\n"
        "2. Diversification analysis\n"
        "3. Top 2-3 actionable recommendations\n"
        "4. Risk assessment given the stated risk tolerance\n\n"
        "Be specific and reference actual tickers and numbers."
    )

    commentary = await groq_complete(prompt, max_tokens=600)

    return {
        "positions": positions,
        "summary": {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_gain_loss": round(total_gain_loss, 2),
            "total_return_pct": round(total_return_pct, 2),
            "top_winner": top_winner,
            "top_loser": top_loser,
            "position_count": len(positions),
        },
        "risk_tolerance": request.risk_tolerance,
        "commentary": commentary,
    }
