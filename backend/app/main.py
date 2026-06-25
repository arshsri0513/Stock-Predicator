"""
Application entrypoint.

This file creates the FastAPI app instance and wires up routers (groups of
related API endpoints). /stocks (Phase 3-4), /models (Phase 5-6), and /news
(Phase 7) are wired in below. Watchlist (Phase 8) and auth (Phase 12) will
be added the same way, keeping this file a thin "assembly point" rather
than where actual logic lives.
"""

from fastapi import FastAPI
from app.core.config import settings
from app.api import stocks, models, news

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(news.router, prefix="/news", tags=["news"])


@app.get("/health")
def health_check():
    """
    Simple endpoint to verify the server is running and reachable.
    Used by deployment platforms (Render, Docker) to confirm the app is alive
    before sending it real traffic.
    """
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
    }


# More routers will be added here as we build them:
# Phase 8: watchlist
# Phase 12: auth
