"""
Stock data fetching service.

This module is the ONLY place in the backend that talks to yfinance directly.
Why centralize this?
- If Yahoo Finance changes its API, or we ever swap to a different data
  provider, we change ONE file, not every place that needed stock data.
- It lets us add caching, retries, and error handling in one consistent spot
  rather than repeating that logic everywhere.

Every function here returns a pandas DataFrame — the standard tabular data
structure in Python's data science ecosystem. Think of it as an in-memory
spreadsheet: rows are dates, columns are Open/High/Low/Close/Volume.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_historical_data(
    ticker: str,
    period: str = "5y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a given stock ticker.

    Args:
        ticker: Stock symbol, e.g. "AAPL", "TSLA", "RELIANCE.NS" (Indian stocks
                need the ".NS" or ".BO" suffix for NSE/BSE listings).
        period: How far back to fetch. Valid values: "1d","5d","1mo","3mo",
                "6mo","1y","2y","5y","10y","ytd","max".
        interval: Candle size. Valid values: "1m","5m","15m","30m","1h","1d",
                  "1wk","1mo". Note: intervals under 1 day only work for
                  periods of 60 days or less (Yahoo Finance limitation, not ours).

    Returns:
        A pandas DataFrame with columns: Open, High, Low, Close, Volume,
        Dividends, Stock Splits — indexed by Date.

    Raises:
        ValueError: if the ticker is invalid or no data was returned.
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)

    if df.empty:
        raise ValueError(
            f"No data returned for ticker '{ticker}'. "
            f"Check the symbol is correct (e.g. 'AAPL', not 'Apple')."
        )

    # Yahoo Finance sometimes includes a timezone-aware index; we standardize
    # it to plain dates to avoid timezone bugs later in feature engineering.
    df.index = df.index.tz_localize(None) if df.index.tz is not None else df.index

    return df


def fetch_recent_data(ticker: str, days: int = 5) -> pd.DataFrame:
    """
    Fetch the most recent N days of data — used for "near real-time" display
    and for generating fresh predictions without re-downloading years of history.

    Note: yfinance data has an inherent delay (typically a few minutes) and
    is NOT a true real-time trading feed. This is appropriate for our
    educational/portfolio project, not for actual trading decisions.
    """
    end = datetime.now()
    start = end - timedelta(days=days)
    stock = yf.Ticker(ticker)
    df = stock.history(start=start, end=end, interval="1d")

    if df.empty:
        raise ValueError(f"No recent data found for ticker '{ticker}'.")

    return df


def fetch_company_info(ticker: str) -> dict:
    """
    Fetch basic company metadata (name, sector, market cap, etc.).
    Useful for displaying context alongside charts in the frontend.
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    if not info or "symbol" not in info:
        raise ValueError(f"Could not retrieve company info for '{ticker}'.")

    return {
        "symbol": info.get("symbol"),
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "currency": info.get("currency"),
    }
