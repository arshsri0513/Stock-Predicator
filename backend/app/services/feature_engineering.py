"""
Feature engineering for classical ML models (Phase 5: Linear Regression,
Random Forest, XGBoost).

These models take a flat table of numeric features per row and predict a
target value — they have no inherent concept of "time" or "sequence" unless
we explicitly encode recent history as columns. That's what this module does:
turn a plain price history into a feature-rich table.

Deep learning models (Phase 6) will use a DIFFERENT preparation approach
(sliding windows of raw sequences) — we'll build that separately when we
reach Phase 6, since LSTMs/GRUs/Transformers learn temporal patterns
directly rather than needing hand-crafted lag features.
"""

import pandas as pd


def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add core derived features to a cleaned OHLCV DataFrame.

    New columns added:
    - daily_return: percentage change in Close from the previous day
    - close_lag_1, close_lag_2, close_lag_3: Close price from 1/2/3 days ago
    - rolling_volatility_5: standard deviation of daily returns over the
      trailing 5 days (a measure of how "jumpy" the stock has recently been)
    - day_of_week: 0=Monday ... 4=Friday (captures mild weekly patterns,
      e.g. some assets behave slightly differently on Mondays vs Fridays)

    Why lag features specifically? A model predicting tomorrow's price
    benefits from knowing not just today's price, but the recent trajectory.
    Without lag columns, a Random Forest has no way to "see" that the price
    has been rising for 3 straight days — each row would look independent.
    """
    out = df.copy()

    out["daily_return"] = out["Close"].pct_change()

    for lag in [1, 2, 3]:
        out[f"close_lag_{lag}"] = out["Close"].shift(lag)

    out["rolling_volatility_5"] = out["daily_return"].rolling(window=5).std()

    out["day_of_week"] = out.index.dayofweek

    return out


def add_target_column(df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    """
    Add the prediction TARGET column — what the model is trying to learn to
    predict. This is the next day's (or next N days') closing price.

    Args:
        horizon: how many days into the future to predict. horizon=1 means
                 "predict tomorrow's close using today's features."

    Why shift(-horizon) and not shift(horizon)?
    shift(1) moves values DOWN (yesterday's value lands on today's row).
    shift(-1) moves values UP (tomorrow's value lands on today's row) —
    which is exactly what we want: each row should pair TODAY's features
    with TOMORROW's actual closing price, so the model learns
    "given what I see today, predict what happens next."
    """
    out = df.copy()
    out["target"] = out["Close"].shift(-horizon)
    return out


def prepare_ml_dataset(df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    """
    Full pipeline: clean → add features → add target → drop rows with
    any remaining NaN (lag features create NaNs at the start of the series;
    the target column creates NaNs at the very end, since there's no
    "tomorrow" for the last row).

    Returns a DataFrame ready to be split into X (features) and y (target)
    for model training in Phase 5.
    """
    out = add_basic_features(df)
    out = add_target_column(out, horizon=horizon)
    out = out.dropna()
    return out
