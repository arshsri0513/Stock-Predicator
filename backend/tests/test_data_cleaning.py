"""
Unit tests for app.services.data_cleaning.

These test pure data transformations with no network calls and no
database -- exactly the kind of test that should run in milliseconds and
never flake. We build small, controlled DataFrames by hand rather than
fetching real data, so each test is deterministic and isolated.
"""

import pandas as pd
import numpy as np
import pytest

from app.services.data_cleaning import clean_ohlcv, validate_ohlcv


def make_ohlcv(rows: int = 10) -> pd.DataFrame:
    """Helper: build a small, clean OHLCV DataFrame for use as a test fixture."""
    dates = pd.bdate_range("2024-01-01", periods=rows)
    close = 100 + np.arange(rows, dtype=float)
    return pd.DataFrame({
        "Open": close - 0.5,
        "High": close + 1,
        "Low": close - 1,
        "Close": close,
        "Volume": np.full(rows, 1_000_000),
    }, index=dates)


def test_clean_ohlcv_removes_duplicate_dates():
    df = make_ohlcv(5)
    df = pd.concat([df, df.iloc[[2]]])  # duplicate one row
    assert df.index.duplicated().sum() == 1

    cleaned = clean_ohlcv(df)
    assert cleaned.index.duplicated().sum() == 0
    assert len(cleaned) == 5


def test_clean_ohlcv_forward_fills_nan():
    df = make_ohlcv(5)
    df.iloc[2, df.columns.get_loc("Close")] = np.nan
    expected_fill_value = df.iloc[1]["Close"]  # the last known good value

    cleaned = clean_ohlcv(df)
    assert cleaned.iloc[2]["Close"] == expected_fill_value
    assert cleaned["Close"].isna().sum() == 0


def test_clean_ohlcv_removes_non_positive_prices():
    df = make_ohlcv(5)
    df.iloc[1, df.columns.get_loc("Close")] = -10.0  # invalid, should be dropped

    cleaned = clean_ohlcv(df)
    assert (cleaned["Close"] > 0).all()
    assert len(cleaned) == 4  # one row removed


def test_clean_ohlcv_sorts_chronologically():
    df = make_ohlcv(5)
    shuffled = df.sample(frac=1, random_state=1)  # deliberately scramble row order

    cleaned = clean_ohlcv(shuffled)
    assert cleaned.index.is_monotonic_increasing


def test_validate_ohlcv_flags_high_below_low():
    df = make_ohlcv(5)
    df.iloc[0, df.columns.get_loc("High")] = df.iloc[0]["Low"] - 5  # High < Low, invalid

    warnings = validate_ohlcv(df)
    assert any("High < Low" in w for w in warnings)


def test_validate_ohlcv_no_warnings_on_clean_data():
    df = make_ohlcv(10)
    warnings = validate_ohlcv(df)
    assert warnings == []
