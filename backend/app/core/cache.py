"""
Redis caching layer.

Why caching matters specifically here: fetching historical data and
computing technical indicators (Phases 3-4) hits yfinance's live servers
every single time, even if ten different users ask about AAPL within the
same minute. Caching the result for a short window means the 2nd through
Nth request in that window gets an instant response from memory instead
of a fresh network round-trip -- exactly the kind of optimization the
Phase 1 architecture diagram anticipated with its "Redis cache, hot data"
node, which we're now actually implementing.

We connect lazily (on first use, not at import time) so the app still
starts up fine even if Redis is temporarily unreachable -- caching is a
performance optimization, not a hard dependency; a cache failure should
degrade to "slightly slower" (fetch live every time), never to "broken."
"""

import json
import redis
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis | None:
    """
    Returns a shared Redis connection, or None if Redis is unreachable.
    Callers must handle the None case gracefully (skip caching, don't crash).
    """
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            _redis_client.ping()  # fail fast here if Redis genuinely isn't reachable
        except redis.RedisError:
            logger.warning("Redis unreachable -- caching disabled, falling back to live fetches.")
            _redis_client = None
    return _redis_client


def cache_get(key: str):
    """Returns the cached value for `key`, or None on a cache miss OR if
    Redis itself is unavailable -- both cases look identical to the
    caller, which simply proceeds to fetch fresh data either way."""
    client = get_redis_client()
    if client is None:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw is not None else None
    except redis.RedisError:
        return None


def cache_set(key: str, value, ttl_seconds: int = 300):
    """
    Stores `value` (JSON-serialized) under `key`, expiring automatically
    after `ttl_seconds`. Default 300s (5 minutes) -- short enough that
    stock data never feels meaningfully stale, long enough to absorb
    bursts of repeated requests for the same popular ticker.

    Failures here are swallowed deliberately (logged, not raised) --
    a caching failure should never break the actual feature being served.
    """
    client = get_redis_client()
    if client is None:
        return
    try:
        client.set(key, json.dumps(value), ex=ttl_seconds)
    except redis.RedisError as e:
        logger.warning(f"Failed to write cache key '{key}': {e}")
