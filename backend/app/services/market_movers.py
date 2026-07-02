"""
Market movers service using Finnhub.
"""

import requests

from app.core.config import settings

WATCHLIST_BASKET = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "AMD",
    "NFLX",
    "INTC",
    "ORCL",
    "CRM",
    "ADBE",
    "PYPL",
    "UBER",
]


def get_quote(symbol: str):
    """
    Fetch a single quote from Finnhub.
    """

    response = requests.get(
        "https://finnhub.io/api/v1/quote",
        params={
            "symbol": symbol,
            "token": settings.FINNHUB_API_KEY,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()

def get_market_indices():
    """
    Fetch major US market indices using Finnhub.
    """

    indices = {
        "sp500": "^GSPC",
        "nasdaq": "^IXIC",
        "dow": "^DJI",
        "vix": "^VIX",
    }

    result = {}

    for name, symbol in indices.items():
        try:
            data = get_quote(symbol)

            current = data.get("c")
            previous = data.get("pc")

            if current is None or previous is None or previous == 0:
                continue

            result[name] = {
                "price": round(float(current), 2),
                "change_percent": round(
                    ((current - previous) / previous) * 100,
                    2,
                ),
            }

        except Exception as e:
            print(f"{symbol}: {e}")

    return result


def get_top_movers(limit: int = 5) -> dict:
    """
    Fetch market movers using Finnhub quotes.
    """

    movers = []

    for ticker in WATCHLIST_BASKET:
        try:
            data = get_quote(ticker)

            current = data.get("c")
            previous = data.get("pc")

            if current is None or previous is None or previous == 0:
                continue

            change_percent = ((current - previous) / previous) * 100

            movers.append(
                {
                    "ticker": ticker,
                    "price": round(float(current), 2),
                    "change_percent": round(float(change_percent), 2),
                }
            )

        except Exception as e:
            print(f"{ticker}: {e}")
            continue

    movers.sort(
        key=lambda item: item["change_percent"],
        reverse=True,
    )

    gainers = [
        stock
        for stock in movers
        if stock["change_percent"] > 0
    ]

    losers = [
        stock
        for stock in movers
        if stock["change_percent"] < 0
    ]

    return {
        "gainers": gainers[:limit],
        "losers": losers[:limit],
    }