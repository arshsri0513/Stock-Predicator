"""
Stock data API routes.

Note the pattern: this file is intentionally THIN. It handles HTTP concerns
(request parsing, response formatting, error → HTTP status mapping) and
delegates all real logic to app/services/. This keeps routes easy to read
and means the underlying logic is testable without spinning up a web server.
"""

import math

from fastapi import APIRouter, HTTPException, Query

from app.services.stock_data import fetch_historical_data, fetch_company_info
from app.services.data_cleaning import clean_ohlcv, validate_ohlcv
from app.services.technical_indicators import add_all_indicators
from app.core.cache import cache_get, cache_set

router = APIRouter()


@router.get("/{ticker}/history")
def get_stock_history(
    ticker: str,
    period: str = Query(default="1y", description="e.g. 1mo, 6mo, 1y, 5y, max"),
    interval: str = Query(default="1d", description="e.g. 1d, 1wk, 1mo"),
):
    """
    Returns cleaned historical OHLCV data for a given ticker.

    Cached in Redis for 5 minutes (Phase 15) -- this is the single most
    frequently-hit endpoint in the project (every Dashboard/Charts page
    load calls it), and stock data genuinely doesn't change meaningfully
    within a 5-minute window for our purposes, so serving a short-lived
    cached copy instead of re-fetching from yfinance every time reduces
    both latency for the user and load on the external API.

    Example: GET /stocks/AAPL/history?period=6mo&interval=1d
    """
    cache_key = f"history:{ticker.upper()}:{period}:{interval}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        raw = fetch_historical_data(ticker, period=period, interval=interval)
        cleaned = clean_ohlcv(raw)
        warnings = validate_ohlcv(cleaned)
    except ValueError as e:
        # A ValueError from our service means "bad input" (invalid ticker),
        # which maps to HTTP 404 — the resource the client asked for doesn't exist.
        raise HTTPException(status_code=404, detail=str(e))

    # Convert the DataFrame to a JSON-friendly list of records before returning.
    # FastAPI can't serialize pandas DataFrames directly.
    records = cleaned.reset_index().rename(columns={"index": "Date"})
    records["Date"] = records["Date"].astype(str)

    response = {
        "ticker": ticker.upper(),
        "period": period,
        "interval": interval,
        "rows": len(records),
        "warnings": warnings,
        "data": records.to_dict(orient="records"),
    }
    cache_set(cache_key, response, ttl_seconds=300)
    return response


@router.get("/{ticker}/technical-indicators")
def get_technical_indicators(
    ticker: str,
    period: str = Query(default="1y", description="e.g. 1mo, 6mo, 1y, 5y, max"),
):
    """
    Returns historical data WITH technical indicators added: SMA, EMA, RSI,
    MACD, Bollinger Bands, ATR, and OBV.

    Note: the first ~26 rows will have NaN/null values for some indicators
    (e.g. MACD needs 26 days of history to warm up) — this is mathematically
    expected, not a bug. We convert NaN to None so the JSON response is valid
    (raw NaN is not valid JSON).

    Example: GET /stocks/AAPL/technical-indicators?period=6mo
    """
    try:
        raw = fetch_historical_data(ticker, period=period, interval="1d")
        cleaned = clean_ohlcv(raw)
        with_indicators = add_all_indicators(cleaned)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    records = with_indicators.reset_index().rename(columns={"index": "Date"})
    records["Date"] = records["Date"].astype(str)

    # Convert to a list of dicts FIRST, then replace NaN with None at the
    # Python level. This is more reliable than pandas' .where()/.fillna(),
    # which can silently leave real float NaN in place depending on each
    # column's dtype — and raw NaN is not valid JSON (only `null` is).
    raw_records = records.to_dict(orient="records")
    clean_records = [
        {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in row.items()}
        for row in raw_records
    ]

    return {
        "ticker": ticker.upper(),
        "period": period,
        "rows": len(clean_records),
        "data": clean_records,
    }



@router.get("/{ticker}/info")
def get_stock_info(ticker: str):
    """
    Returns basic company metadata for a given ticker.

    Example: GET /stocks/AAPL/info
    """
    try:
        info = fetch_company_info(ticker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return info
