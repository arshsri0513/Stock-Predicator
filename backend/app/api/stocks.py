"""
Stock data API routes.

Note the pattern: this file is intentionally THIN. It handles HTTP concerns
(request parsing, response formatting, error → HTTP status mapping) and
delegates all real logic to app/services/. This keeps routes easy to read
and means the underlying logic is testable without spinning up a web server.
"""

from fastapi import APIRouter, HTTPException, Query

from app.services.stock_data import fetch_historical_data, fetch_company_info
from app.services.data_cleaning import clean_ohlcv, validate_ohlcv

router = APIRouter()


@router.get("/{ticker}/history")
def get_stock_history(
    ticker: str,
    period: str = Query(default="1y", description="e.g. 1mo, 6mo, 1y, 5y, max"),
    interval: str = Query(default="1d", description="e.g. 1d, 1wk, 1mo"),
):
    """
    Returns cleaned historical OHLCV data for a given ticker.

    Example: GET /stocks/AAPL/history?period=6mo&interval=1d
    """
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

    return {
        "ticker": ticker.upper(),
        "period": period,
        "interval": interval,
        "rows": len(records),
        "warnings": warnings,
        "data": records.to_dict(orient="records"),
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
