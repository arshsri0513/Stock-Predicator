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
