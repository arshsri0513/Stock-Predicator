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


def get_top_movers(limit: int = 5) -> dict:
    movers = []

    for ticker in WATCHLIST_BASKET:
        try:
            response = requests.get(
                "https://finnhub.io/api/v1/quote",
                params={
                    "symbol": ticker,
                    "token": settings.FINNHUB_API_KEY,
                },
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            current = data.get("c")
            previous = data.get("pc")

            if not current or not previous:
                continue

            change_percent = ((current - previous) / previous) * 100

            movers.append(
                {
                    "ticker": ticker,
                    "price": round(current, 2),
                    "change_percent": round(change_percent, 2),
                }
            )

        except Exception as e:
            print(f"{ticker}: {e}")
            continue

    movers.sort(
        key=lambda item: item["change_percent"],
        reverse=True,
    )

    return {
        "gainers": movers[:limit],
        "losers": movers[-limit:][::-1],
    }