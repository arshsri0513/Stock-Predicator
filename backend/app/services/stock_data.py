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


_PERIOD_TO_DAYS = {
    "1d": 1, "5d": 5, "1mo": 31, "3mo": 93, "6mo": 186,
    "1y": 365, "2y": 730, "5y": 1825, "10y": 3650,
    "ytd": None,  # handled specially below
    "max": 7300,  # ~20y, stooq's free CSV history rarely goes back further anyway
}


def _stooq_symbol(ticker: str) -> str:
    """
    Map a Yahoo-style ticker to Stooq's symbol format.

    Stooq wants a lowercase symbol with a market suffix, e.g. "aapl.us".
    We only confidently support plain US tickers (no existing suffix) here
    -- that covers the common case (AAPL, TSLA, MSFT, NVDA, ...). Tickers
    that already carry a Yahoo-style suffix (e.g. "RELIANCE.NS" for NSE)
    aren't mapped, since Stooq's suffix scheme for non-US markets doesn't
    line up 1:1 with Yahoo's, and silently guessing wrong would return data
    for the wrong instrument -- worse than no fallback at all.
    """
    if "." in ticker:
        raise ValueError(
            f"No Stooq fallback mapping for '{ticker}' (non-US suffix)."
        )
    return f"{ticker.lower()}.us"


def _fetch_from_stooq(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """
    Free, no-API-key fallback data source.

    Stooq (https://stooq.com) publishes daily/weekly/monthly OHLCV data as
    plain CSV over HTTP, with no API key, no auth, and -- unlike Yahoo's
    unofficial endpoints -- no observed pattern of blocking cloud/datacenter
    IPs. The tradeoff: free + reliable from servers, but EOD data only (no
    intraday candles, and quotes lag by the time CSV is published) and only
    confidently mapped for plain US tickers here. This is exactly the right
    tradeoff for an educational dashboard/prediction app, not for a live
    trading terminal.
    """
    if interval not in ("1d", "1wk", "1mo"):
        raise ValueError(
            f"Stooq fallback only supports daily/weekly/monthly data, not "
            f"interval='{interval}'."
        )
    stooq_interval = {"1d": "d", "1wk": "w", "1mo": "m"}[interval]
    symbol = _stooq_symbol(ticker)

    if period == "ytd":
        start = datetime(datetime.now().year, 1, 1)
    else:
        days = _PERIOD_TO_DAYS.get(period, 1825)
        start = datetime.now() - timedelta(days=days)

    url = "https://stooq.com/q/d/l/"
    params = {
        "s": symbol,
        "d1": start.strftime("%Y%m%d"),
        "d2": datetime.now().strftime("%Y%m%d"),
        "i": stooq_interval,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()

    # Stooq returns the literal text "No data" (not a 4xx) for unknown
    # symbols or symbols with nothing in the requested range -- it's a 200
    # response either way, so we can't rely on status code alone.
    if not resp.text or resp.text.strip().lower().startswith("no data"):
        raise ValueError(f"Stooq returned no data for '{ticker}' ({symbol}).")

    from io import StringIO
    df = pd.read_csv(StringIO(resp.text))
    if df.empty or "Date" not in df.columns:
        raise ValueError(f"Stooq returned an unexpected/empty response for '{ticker}'.")

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    df = df.rename(columns=str.title)  # stooq headers are already title-case, kept for safety

    # Match yfinance's column shape so downstream code (clean_ohlcv,
    # indicators, the /history route) doesn't need to know which provider
    # the data came from.
    for col in ("Dividends", "Stock Splits"):
        if col not in df.columns:
            df[col] = 0

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
    Stooq, a free CSV data source with no API key and no observed
    cloud-IP blocking. The fallback is best-effort: it only covers plain
    US tickers and daily/weekly/monthly intervals (see _fetch_from_stooq).

    Args:
        ticker: Stock symbol, e.g. "AAPL", "TSLA", "RELIANCE.NS" (Indian stocks
                need the ".NS" or ".BO" suffix for NSE/BSE listings).
        period: How far back to fetch. Valid values: "1d","5d","1mo","3mo",
                "6mo","1y","2y","5y","10y","ytd","max".
        interval: Candle size. Valid values: "1m","5m","15m","30m","1h","1d",
                  "1wk","1mo". Note: intervals under 1 day only work for
                  periods of 60 days or less (Yahoo Finance limitation, not ours),
                  and only via the yfinance path -- Stooq has no intraday fallback.

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

    # yfinance failed -- try the free Stooq fallback before giving up.
    try:
        return _fetch_from_stooq(ticker, period=period, interval=interval)
    except Exception as stooq_error:
        raise ValueError(
            f"Could not fetch data for '{ticker}' from Yahoo Finance "
            f"({yfinance_error}) or the Stooq fallback ({stooq_error})."
        )


def fetch_recent_data(ticker: str, days: int = 5) -> pd.DataFrame:
    """
    Fetch the most recent N days of data — used for "near real-time" display
    and for generating fresh predictions without re-downloading years of history.

    Note: yfinance data has an inherent delay (typically a few minutes) and
    is NOT a true real-time trading feed. This is appropriate for our
    educational/portfolio project, not for actual trading decisions.

    Falls back to Stooq (same as fetch_historical_data) if yfinance fails.
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
        period = "1mo" if days <= 31 else "3mo"
        df = _fetch_from_stooq(ticker, period=period, interval="1d")
        return df.tail(days)
    except Exception as stooq_error:
        raise ValueError(
            f"Could not fetch recent data for '{ticker}' from Yahoo Finance "
            f"({yfinance_error}) or the Stooq fallback ({stooq_error})."
        )


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