"""
Application entrypoint.

This file creates the FastAPI app instance and wires up routers (groups of
related API endpoints). Right now it only has a health-check route — in
Phase 8 we'll import and attach the real routers (auth, stocks, predictions,
news, watchlist) here, keeping this file as a thin "assembly point" rather
than where actual logic lives.
"""

from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
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


# Future routers will be included like this (Phase 8):
# from app.api import auth, stocks, predictions
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
