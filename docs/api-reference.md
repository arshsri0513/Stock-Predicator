# API Reference

Complete list of every endpoint built so far (Phases 3-8). All endpoints
are auto-documented interactively at `/docs` when the server is running --
this file is a stable, version-controlled reference alongside that.

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Confirms the server is running |

## Stocks (`/stocks`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/stocks/{ticker}/history` | Cleaned historical OHLCV data |
| GET | `/stocks/{ticker}/technical-indicators` | OHLCV + SMA/EMA/RSI/MACD/Bollinger/ATR/OBV |
| GET | `/stocks/{ticker}/info` | Company metadata (name, sector, market cap) |

## Models (`/models`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/models/train` | Train a classical ML model (linear_regression / random_forest / xgboost) |
| GET | `/models/{ticker}/predict` | Predict next day's close using a saved classical model |
| GET | `/models/{ticker}/evaluate` | Re-evaluate a saved classical model on fresh data |
| POST | `/models/train-dl` | Train a deep learning model (lstm / gru / transformer) |

## News (`/news`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/news/{ticker}` | Recent headlines scored with VADER + FinBERT |

## Error response shape

All endpoints return errors in this consistent shape:
```json
{ "detail": "human-readable explanation of what went wrong" }
```

Status codes used, and what each means in this project:
- `404` -- the requested resource doesn't exist (bad ticker, no trained model yet)
- `422` -- the request was understood but the data isn't usable (e.g. too little history to train on)
- `502` -- an upstream dependency (yfinance) failed
- `500` -- an unexpected error we didn't specifically anticipate (caught by the global handler)

## Not yet built (upcoming phases)

- Authentication (Phase 12) -- everything above is currently UNAUTHENTICATED
- Watchlist (Phase 9, after the database exists)
- Admin/retraining endpoints (Phase 13)

## Known limitation: yfinance on cloud hosting (Phase 15)

Endpoints that depend on yfinance (`/stocks/*`, `/models/train`,
`/models/{ticker}/predict`, `/news/{ticker}`, etc.) work correctly on
local development machines and most home/office internet connections,
but currently FAIL when called from this project's live Render
deployment, returning a 404 like:

    "No data returned for ticker 'AAPL'."

This is NOT a bug in our code. Yahoo Finance's free, unofficial endpoints
(which the yfinance library wraps) appear to block or aggressively rate
limit requests originating from shared cloud/datacenter IP ranges --
we independently reproduced the identical failure in two completely
separate environments: GitHub Actions CI runners (Phase 14) and Render's
production servers (Phase 15). A genuine attempt at a workaround (custom
browser-like request headers, see app/services/stock_data.py) did not
resolve it, suggesting Yahoo's blocking is based on IP reputation/volume
rather than anything in the request itself -- something application code
cannot control.

What still works correctly on the live deployment:
- /health
- /auth/* (signup, login, /me) -- no external data dependency
- /watchlist, /portfolio, /alerts CRUD operations that don't require a
  live price lookup at write time

What does NOT currently work on the live deployment:
- Any endpoint that calls yfinance: stock history/indicators/info, model
  training/prediction, news/sentiment, portfolio gain/loss (needs a live
  price), market movers

The honest, real fix for a genuine production deployment would be
switching to a paid, officially-supported market data API (e.g. Alpha
Vantage, Polygon.io, IEX Cloud) with proper API key authentication, which
doesn't suffer from this kind of informal IP-based blocking. That's a
deliberate scope decision left for a future iteration of this project,
not something we implemented here.
