"""
Full ML dataset preparation pipeline.

This module is the bridge between everything we built in Phases 3-4
(data fetching, cleaning, technical indicators, lag features) and the
actual model training that happens in app/ml/train.py.

It produces a single, clean, fully-numeric DataFrame where:
- Every row is one trading day
- Every column except 'target' is a FEATURE (input to the model)
- 'target' is what we're trying to predict (next day's closing price)
- There are NO NaN values anywhere (models can't handle them)
"""

import pandas as pd

from app.services.stock_data import fetch_historical_data
from app.services.data_cleaning import clean_ohlcv
from app.services.technical_indicators import add_all_indicators
from app.services.feature_engineering import add_basic_features, add_target_column


# Columns that are identifiers/metadata, not predictive features. We keep
# them out of X (the feature matrix) since a model can't learn from a raw
# date string, and Dividends/Stock Splits are mostly zero (sparse, low signal
# for daily price prediction at this stage of the project).
NON_FEATURE_COLUMNS = ["Dividends", "Stock Splits"]


def build_ml_dataset(ticker: str, period: str = "5y", horizon: int = 1) -> pd.DataFrame:

    raw = fetch_historical_data(ticker, period=period, interval="1d")

    print("\n========== RAW DATA ==========")
    print("Latest raw date:", raw.index[-1])
    print(raw.tail())

    cleaned = clean_ohlcv(raw)
    with_indicators = add_all_indicators(cleaned)
    with_lags = add_basic_features(with_indicators)
    with_target = add_target_column(with_lags, horizon=horizon)

    final = with_target.dropna()

    print("\n========== FINAL DATASET ==========")
    print("Latest final date:", final.index[-1])
    print(final.tail())

    final = final.drop(columns=[c for c in NON_FEATURE_COLUMNS if c in final.columns])

    return final


def split_features_target(df: pd.DataFrame):
    """
    Separate a prepared dataset into X (features) and y (target).
    Returns (X, y) as a tuple — X is every column except 'target',
    y is the 'target' column alone.
    """
    X = df.drop(columns=["target"])
    y = df["target"]
    return X, y


def chronological_train_test_split(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
    """
    Split data by TIME, not randomly. The most recent `test_size` fraction
    of rows becomes the test set; everything before it is training data.

    This is the single most important data-handling rule in this entire
    project for time series. See the project notes for why: random shuffling
    would let the model "see" data chronologically surrounding a test point,
    which never happens in real-world prediction (you only ever have the
    past when predicting the future) and would make our evaluation metrics
    falsely optimistic.

    Args:
        X, y: full feature matrix and target series, already in
              chronological order (oldest first — which build_ml_dataset
              guarantees, since clean_ohlcv sorts by date).
        test_size: fraction of rows (from the END, i.e. most recent) to
                   reserve for testing. 0.2 = last 20% of the time range.

    Returns:
        X_train, X_test, y_train, y_test
    """
    split_index = int(len(X) * (1 - test_size))
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
    return X_train, X_test, y_train, y_test
