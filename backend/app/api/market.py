"""
Market movers (top gainers/losers) API route.
"""

from fastapi import APIRouter, Query
from app.services.market_movers import get_top_movers

router = APIRouter()


@router.get("")
def top_movers(limit: int = Query(default=5, ge=1, le=10)):
    """
    Returns top gainers and losers from a curated basket of large-cap
    tickers (see app.services.market_movers for why a curated basket
    rather than a full market scan).

    Example: GET /market/movers?limit=5
    """
    return get_top_movers(limit=limit)
