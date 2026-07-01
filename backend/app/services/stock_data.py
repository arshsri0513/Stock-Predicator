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

from app.core.config import settings

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


_PERIOD_TO_OUTPUTSIZE = {
    # Twelve Data's time_series endpoint takes an outputsize (row count),
    # not a date range, on the free plan -- so we translate each period
    # into roughly how many bars of the given interval that period covers.
    "1d": 1, "5d": 5, "1mo": 22, "3mo": 66, "6mo": 132,
    "1y": 252, "2y": 504, "5y": 1260, "10y": 2520,
    "max": 5000,  # Twelve Data's free-plan cap per request
}

_INTERVAL_TO_TWELVEDATA = {
    "1m": "1min", "5m": "5min", "15m": "15min", "30m": "30min",
    "1h": "1h", "1d": "1day", "1wk": "1week", "1mo": "1month",
}


def _twelvedata_symbol(ticker: str) -> str:
    """
    Map a Yahoo-style ticker to Twelve Data's symbol format.

    Twelve Data's Basic (free) plan covers US equities, forex, and crypto
    using the plain ticker (e.g. "AAPL") -- no suffix needed. We only
    confidently support that here. Tickers carrying a Yahoo-style exchange
    suffix (e.g. "RELIANCE.NS" for NSE) aren't mapped: Twelve Data
    identifies non-US exchanges via a separate `exchange` parameter rather
    than a suffix, the mapping isn't 1:1, and most non-US exchanges sit
    behind Twelve Data's paid tiers anyway -- so guessing here would either
    silently fetch the wrong instrument or just fail, and an explicit error
    is better than either.
    """
    if "." in ticker:
        raise ValueError(
            f"No Twelve Data fallback mapping for '{ticker}' (non-US suffix)."
        )
    return ticker.upper()


def _fetch_from_twelvedata(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """
    Free-tier fallback data source (used when yfinance fails).

    Twelve Data (https://twelvedata.com) requires a free API key (no credit
    card) -- unlike our earlier Stooq-based fallback, which broke when
    Stooq started requiring a paid key for CSV downloads in March 2026.
    Twelve Data's Basic plan: 800 requests/day, 8/minute, US equities +
    forex + crypto, data delayed by several hours (not real-time) -- which
    is an honest, acceptable tradeoff for an educational dashboard, not a
    live trading terminal.

    Requires the TWELVE_DATA_API_KEY setting to be configured (see
    app/core/config.py and the README for how to get a free key).
    """
    if not settings.TWELVE_DATA_API_KEY:
        raise ValueError(
            "TWELVE_DATA_API_KEY is not set. Get a free key at "
            "https://twelvedata.com and set it as an environment variable."
        )

    if interval not in _INTERVAL_TO_TWELVEDATA:
        raise ValueError(f"Twelve Data fallback doesn't support interval='{interval}'.")
    td_interval = _INTERVAL_TO_TWELVEDATA[interval]
    symbol = _twelvedata_symbol(ticker)
    outputsize = _PERIOD_TO_OUTPUTSIZE.get(period, 1260)

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": td_interval,
        "outputsize": outputsize,
        "apikey": settings.TWELVE_DATA_API_KEY,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    payload = resp.json()

    # Twelve Data returns HTTP 200 even on logical errors (bad symbol,
    # rate limit hit, invalid key) -- the real status lives inside the
    # JSON body, so we have to check that explicitly.
    if payload.get("status") == "error" or "values" not in payload:
        raise ValueError(
            f"Twelve Data error for '{ticker}': {payload.get('message', payload)}"
        )

    df = pd.DataFrame(payload["values"])
    if df.empty:
        raise ValueError(f"Twelve Data returned no rows for '{ticker}'.")

    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").rename_axis("Date")
    df = df.rename(columns={
        "open": "Open", "high": "High", "low": "Low",
        "close": "Close", "volume": "Volume",
    })
    for col in ("Open", "High", "Low", "Close", "Volume"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Twelve Data doesn't return dividends/splits on the free plan --
    # default to 0 so the shape matches yfinance's output exactly.
    df["Dividends"] = 0
    df["Stock Splits"] = 0

    # Twelve Data returns rows newest-first; flip to chronological order
    # to match yfinance's convention (downstream code assumes ascending).
    df = df.sort_index()

    return df[["Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"]]


def fetch_historical_data(
    ticker: str,
    period: str = "5y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a given stock ticker.

    Tries yfinance (Yahoo Finance) first. If that fails -- which happens
    intermittently from cloud-hosted servers due to Yahoo's unofficial-API
    blocking, see the module docstring -- automatically falls back to
    Twelve Data, a free-tier (API-key-required) data source. The fallback
    is best-effort: it only covers plain US tickers (see
    _twelvedata_symbol) and requires TWELVE_DATA_API_KEY to be set.

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
        ValueError: if the ticker is invalid or no data was returned from
                    either provider.
    """
    yfinance_error = None
    try:
        stock = _get_ticker(ticker)
        df = stock.history(period=period, interval=interval)
        if df.empty:
            raise ValueError(
                f"No data returned for ticker '{ticker}'. "
                f"Check the symbol is correct (e.g. 'AAPL', not 'Apple')."
            )
        # Yahoo Finance sometimes includes a timezone-aware index; we
        # standardize it to plain dates to avoid timezone bugs later in
        # feature engineering.
        df.index = df.index.tz_localize(None) if df.index.tz is not None else df.index
        return df
    except Exception as e:
        yfinance_error = e

    # yfinance failed -- try the free-tier Twelve Data fallback before giving up.
    try:
        return _fetch_from_twelvedata(ticker, period=period, interval=interval)
    except Exception as td_error:
        raise ValueError(
            f"Could not fetch data for '{ticker}' from Yahoo Finance "
            f"({yfinance_error}) or the Twelve Data fallback ({td_error})."
        )


def fetch_recent_data(ticker: str, days: int = 5) -> pd.DataFrame:
    """
    Fetch the most recent N days of data — used for "near real-time" display
    and for generating fresh predictions without re-downloading years of history.

    Note: yfinance data has an inherent delay (typically a few minutes) and
    is NOT a true real-time trading feed. This is appropriate for our
    educational/portfolio project, not for actual trading decisions.

    Falls back to Twelve Data (same as fetch_historical_data) if yfinance fails.
    """
    end = datetime.now()
    start = end - timedelta(days=days)

    yfinance_error = None
    try:
        stock = _get_ticker(ticker)
        df = stock.history(start=start, end=end, interval="1d")
        if df.empty:
            raise ValueError(f"No recent data found for ticker '{ticker}'.")
        return df
    except Exception as e:
        yfinance_error = e

    try:
        period = "1mo" if days <= 22 else "3mo"
        df = _fetch_from_twelvedata(ticker, period=period, interval="1d")
        return df.tail(days)
    except Exception as td_error:
        raise ValueError(
            f"Could not fetch recent data for '{ticker}' from Yahoo Finance "
            f"({yfinance_error}) or the Twelve Data fallback ({td_error})."
        )


import xml.etree.ElementTree as ET

def fetch_news_rss(ticker: str, limit: int = 10) -> list[dict]:
    """
    Fallback news source that fetches headlines from Yahoo Finance's RSS feed
    directly using standard HTTP requests. This feed is rarely blocked by Yahoo's
    automated-request filters and does not require loading yfinance's heavier
    network dependencies, making it reliable for cloud deployments like Render.
    """
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker.upper()}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        
        articles = []
        for item in root.findall(".//item")[:limit]:
            title = item.find("title")
            link = item.find("link")
            pub_date = item.find("pubDate")
            
            articles.append({
                "title": title.text if title is not None else "No Title",
                "publisher": "Yahoo Finance RSS",
                "link": link.text if link is not None else "",
                "published": pub_date.text if pub_date is not None else "",
            })
        return articles
    except Exception as e:
        # If even RSS fallback fails, raise a clear error
        raise ValueError(f"RSS news fallback failed: {str(e)}")


def fetch_news(ticker: str, limit: int = 10) -> list[dict]:
    """
    Fetch recent news headlines for a ticker.
    Tries yfinance first. If that fails (e.g. cloud IP blocking) or returns
    an empty list, automatically falls back to fetching directly from the
    Yahoo Finance RSS feed.
    """
    yfinance_error = None
    try:
        stock = _get_ticker(ticker)
        raw_news = stock.news or []
        if raw_news:
            articles = []
            for item in raw_news[:limit]:
                content = item.get("content", item)
                title = content.get("title")
                if not title:
                    continue
                articles.append({
                    "title": title,
                    "publisher": (content.get("provider") or {}).get("displayName", "Unknown"),
                    "link": (content.get("canonicalUrl") or {}).get("url", ""),
                    "published": content.get("pubDate", ""),
                })
            return articles
    except Exception as e:
        yfinance_error = e

    # Fallback to RSS feed if yfinance failed or returned no news
    try:
        return fetch_news_rss(ticker, limit=limit)
    except Exception as rss_error:
        raise ValueError(
            f"Could not fetch news for '{ticker}' from Yahoo Finance ({yfinance_error}) "
            f"or the RSS fallback ({rss_error})."
        )



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