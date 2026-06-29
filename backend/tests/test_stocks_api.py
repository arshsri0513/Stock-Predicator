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

KNOWN LIMITATION (Phase 15): Yahoo Finance frequently rate-limits or
blocks requests from shared cloud/datacenter IP ranges -- exactly what
GitHub Actions runners use. The two tests below that genuinely fetch
live data from yfinance are skipped specifically when running in GitHub
Actions (detected via the GITHUB_ACTIONS environment variable, which
GitHub sets automatically on every run) -- they still run normally on a
real developer machine, where this blocking doesn't occur. This is a
real, common, well-documented constraint of relying on yfinance for CI,
not something we're hiding: skipping is the honest choice here, since a
red CI run caused by Yahoo's rate limiting looks identical to a red CI
run caused by an actual bug, and conflating the two erodes trust in what
CI is telling you.
"""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

running_in_ci = os.environ.get("GITHUB_ACTIONS") == "true"
skip_reason = (
    "Skipped in CI: Yahoo Finance commonly blocks/rate-limits requests "
    "from GitHub Actions' shared IP ranges. This test runs normally on "
    "a real developer machine."
)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.skipif(running_in_ci, reason=skip_reason)
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


@pytest.mark.skipif(running_in_ci, reason=skip_reason)
def test_technical_indicators_includes_expected_columns():
    response = client.get("/stocks/AAPL/technical-indicators?period=6mo")
    assert response.status_code == 200
    body = response.json()
    first_row = body["data"][0]
    for column in ["sma_20", "rsi_14", "macd_line", "bb_upper", "atr_14", "obv"]:
        assert column in first_row
