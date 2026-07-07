"""
Application entrypoint.

This file creates the FastAPI app instance and wires up routers (groups of
related API endpoints). /stocks (Phase 3-4), /models (Phase 5-6), /news
(Phase 7), /auth (Phase 12), /watchlist and /market/movers (Phase 13) are
wired in below, keeping this file a thin "assembly point" rather than
where actual logic lives.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.limiter import limiter
from app.api import stocks, models, news, auth, watchlist, market, portfolio, alerts, admin
from app.core.database import engine, Base
import app.models
from app.api import predictions

setup_logging()
logger = get_logger(__name__)

logger.info(f"ALLOWED_ORIGINS={settings.ALLOWED_ORIGINS}")
logger.info(f"ALLOWED_ORIGINS_LIST={settings.allowed_origins_list}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Auto-creating database tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# CORS (Cross-Origin Resource Sharing): by default, browsers block
# JavaScript on one origin from calling an API on a different origin.
# settings.ALLOWED_ORIGINS is a comma-separated list read from the
# environment (see app/core/config.py) -- this defaults to localhost for
# local development, but in production (Phase 15) gets set to the real
# deployed frontend URL via an environment variable on Render, rather
# than being hardcoded here. Never leave this as "*" (allow everything)
# in a real production deployment -- that defeats the purpose of CORS
# entirely.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(news.router, prefix="/news", tags=["news"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
app.include_router(market.router, prefix="/market/movers", tags=["market"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(
    predictions.router,
    prefix="/predictions",
    tags=["Predictions"],
)

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

    We now LOG the real exception (Phase 15) before returning the generic
    client-facing message -- exc_info=True includes the full traceback in
    the log output, so in production we can actually diagnose what went
    wrong via the platform's log viewer, even though the client never
    sees those details.
    """
    logger.error(f"Unhandled exception on {request.method} {request.url.path}", exc_info=exc)
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

