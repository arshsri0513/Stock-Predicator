"""
Application entrypoint.

This file creates the FastAPI app instance and wires up routers (groups of
related API endpoints). /stocks (Phase 3-4), /models (Phase 5-6), and /news
(Phase 7) are wired in below. Watchlist (Phase 8) and auth (Phase 12) will
be added the same way, keeping this file a thin "assembly point" rather
than where actual logic lives.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api import stocks, models, news

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(news.router, prefix="/news", tags=["news"])


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Safety net for any error we didn't explicitly anticipate with a
    try/except in a route. Without this, an unexpected error (a bug, a
    library raising something unusual, etc.) would leak a raw Python
    traceback to the client -- unprofessional, and a minor information
    leak (file paths, library versions). This catches anything that slips
    through and returns a clean, consistent JSON error instead.

    Note: this does NOT replace the specific try/except blocks already in
    each route (e.g. catching ValueError for an invalid ticker) -- those
    stay because they give much more helpful, specific error messages.
    This is purely a backstop for the unexpected.
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please try again or contact support.",
        },
    )


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
# Phase 9: watchlist (after the database exists to store it)
# Phase 12: auth
