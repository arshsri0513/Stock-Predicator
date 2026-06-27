"""
Top gainers/losers service.

We use a fixed, well-known basket of large-cap tickers rather than
scanning "the whole market" -- yfinance has no efficient bulk "give me
today's movers" endpoint, so building genuine market-wide gainers/losers
would mean hundreds of individual API calls per request, which is slow
and likely to hit rate limits. A curated basket is the honest, practical
choice for a project at this scale -- worth knowing as a real constraint,
not a hidden shortcut.
"""

import yfinance as yf

WATCHLIST_BASKET = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    "AMD", "NFLX", "INTC", "ORCL", "CRM", "ADBE", "PYPL", "UBER",
]


def get_top_movers(limit: int = 5) -> dict:
    """
    Fetch the most recent 2-day close for each ticker in the basket,
    compute % change, and return the top gainers and losers.

    Why 2 days specifically: we need yesterday's close and today's close
    to compute a single day-over-day percentage change -- exactly the
    same "current vs previous" comparison used throughout the project
    (e.g. PredictionCard's "vs last close" framing from Phase 10).
    """
    movers = []

    for ticker in WATCHLIST_BASKET:
        try:
            hist = yf.Ticker(ticker).history(period="5d", interval="1d")
            if len(hist) < 2:
                continue
            prev_close = hist["Close"].iloc[-2]
            latest_close = hist["Close"].iloc[-1]
            pct_change = ((latest_close - prev_close) / prev_close) * 100
            movers.append({
                "ticker": ticker,
                "price": round(float(latest_close), 2),
                "change_percent": round(float(pct_change), 2),
            })
        except Exception:
            # A single ticker failing (delisted, rate-limited, etc.)
            # shouldn't break the whole response -- skip it and continue.
            continue

    movers.sort(key=lambda m: m["change_percent"], reverse=True)

    return {
        "gainers": movers[:limit],
        "losers": movers[-limit:][::-1] if len(movers) >= limit else movers[::-1],
    }
