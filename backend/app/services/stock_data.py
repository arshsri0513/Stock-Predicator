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
import requests
from datetime import datetime, timedelta

# Yahoo Finance's free, unofficial endpoints (which yfinance wraps) appear
# to apply stricter rate limiting / blocking to requests that look
# automated -- this affects shared cloud IP ranges (GitHub Actions
# runners, Render's servers) much more than a typical home internet
# connection, since many different automated clients can share the same
# small pool of datacenter IPs. We saw this exact failure mode
# independently in Phase 14 (CI tests) and Phase 15 (live Render
# deployment) -- "Expecting value: line 1 column 1" / "possibly delisted"
# errors for tickers that are obviously real and listed.
#
# This session gives yfinance realistic browser-like headers, which
# sometimes (not guaranteed) helps requests blend in with normal traffic
# rather than being immediately flagged as automated. This is a genuine
# attempt at a workaround, not a guaranteed fix -- if Yahoo's blocking is
# based on IP reputation/volume rather than header inspection, this won't
# help, and that would be an honest limitation of relying on a free,
# unofficial data source from cloud infrastructure.
_session = requests.Session()
_session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
})


def _get_ticker(symbol: str) -> yf.Ticker:
    """
    Single shared place that constructs a yf.Ticker -- every function in
    this file goes through here rather than calling yf.Ticker() directly,
    so the browser-header workaround above applies everywhere consistently.
    """
    return yf.Ticker(symbol, session=_session)


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
    stock = _get_ticker(ticker)
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
    stock = _get_ticker(ticker)
    df = stock.history(start=start, end=end, interval="1d")

    if df.empty:
        raise ValueError(f"No recent data found for ticker '{ticker}'.")

    return df


def fetch_news(ticker: str, limit: int = 10) -> list[dict]:
    """
    Fetch recent news headlines for a ticker via yfinance's built-in news
    property. This is a free, no-extra-API-key data source -- consistent
    with our Phase 1 decision to keep development costs at zero -- but a
    real limitation worth knowing: it's less comprehensive than a dedicated
    news API (NewsAPI, Alpha Vantage News, etc.) and yfinance's exact
    response shape has changed across versions in the past.

    We extract defensively (using .get() with fallbacks) rather than
    assuming a fixed structure, since a malformed or missing field
    shouldn't crash the whole request -- it should just skip that one
    article.

    Returns a list of dicts: [{"title": ..., "publisher": ..., "link": ...,
    "published": ...}, ...]
    """
    stock = _get_ticker(ticker)
    raw_news = stock.news or []

    articles = []
    for item in raw_news[:limit]:
        # yfinance nests article data under a "content" key in newer
        # versions; older versions had fields at the top level. We check
        # both so this keeps working regardless of which version is
        # installed.
        content = item.get("content", item)

        title = content.get("title")
        if not title:
            continue  # skip malformed entries with no headline at all

        articles.append({
            "title": title,
            "publisher": (content.get("provider") or {}).get("displayName", "Unknown"),
            "link": (content.get("canonicalUrl") or {}).get("url", ""),
            "published": content.get("pubDate", ""),
        })

    return articles



def fetch_company_info(ticker: str) -> dict:
    """
    Fetch basic company metadata (name, sector, market cap, etc.).
    Useful for displaying context alongside charts in the frontend.
    """
    stock = _get_ticker(ticker)
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