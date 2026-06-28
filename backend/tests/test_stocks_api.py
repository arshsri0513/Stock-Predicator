"""
API-level tests using FastAPI's TestClient.

Unlike the unit tests in this folder, these exercise the FULL request
pipeline -- routing, Pydantic validation, our error handlers -- by
calling the real FastAPI app object directly, in-process, with no actual
network socket or running server needed. TestClient does this by
wrapping the app and simulating requests against it directly.

Note: tests that hit /stocks or /models genuinely call out to yfinance
(no mocking yet) -- this is intentional for now: it proves the real
integration works, at the cost of these specific tests needing network
access and being slower than pure unit tests. A more advanced setup
would mock yfinance for these tests too; we keep it real here so the
tests double as regression checks against actual external behavior,
matching the project's overall philosophy of verifying with real data
wherever feasible.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_stock_history_valid_ticker():
    response = client.get("/stocks/AAPL/history?period=1mo")
    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["rows"] > 0
    assert "data" in body


def test_stock_history_invalid_ticker_returns_404():
    response = client.get("/stocks/ZZZZINVALIDTICKER/history")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_technical_indicators_includes_expected_columns():
    response = client.get("/stocks/AAPL/technical-indicators?period=6mo")
    assert response.status_code == 200
    body = response.json()
    first_row = body["data"][0]
    for column in ["sma_20", "rsi_14", "macd_line", "bb_upper", "atr_14", "obv"]:
        assert column in first_row
