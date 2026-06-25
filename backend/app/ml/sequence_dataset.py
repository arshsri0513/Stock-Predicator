"""
Sequence preparation for deep learning models (LSTM, GRU, Transformer).

This is fundamentally different from app/ml/dataset.py (used for classical
ML in Phase 5). Classical models take one flat row of features per
prediction. Deep learning models here take a SEQUENCE — a window of recent
days — and learn temporal patterns directly from the ordered sequence
itself, rather than from hand-crafted lag/rolling features.

We still reuse data fetching and cleaning from Phases 3-4, but skip most of
the lag/rolling feature engineering from Phase 5 — there's no need for
'close_lag_1' as a column when the model already sees the last 60 raw
values directly, in order.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from app.services.stock_data import fetch_historical_data
from app.services.data_cleaning import clean_ohlcv


def create_sequences(values: np.ndarray, window_size: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Slice a 1D array of values into overlapping windows of `window_size`,
    each paired with the very next value as its target.

    Example with window_size=3 on values [10, 11, 12, 13, 14]:
        X[0] = [10, 11, 12]  ->  y[0] = 13
        X[1] = [11, 12, 13]  ->  y[1] = 14

    Args:
        values: 1D array of (typically scaled) closing prices, oldest first.
        window_size: how many consecutive days the model sees before
                     predicting the next one. 60 is a common default for
                     daily stock data — roughly 3 trading months of context.

    Returns:
        X: shape (num_sequences, window_size) — input windows
        y: shape (num_sequences,) — the target value right after each window
    """
    X, y = [], []
    for i in range(len(values) - window_size):
        X.append(values[i : i + window_size])
        y.append(values[i + window_size])
    return np.array(X), np.array(y)


def prepare_sequence_dataset(
    ticker: str,
    period: str = "5y",
    window_size: int = 60,
):
    """
    Full pipeline: fetch -> clean -> scale -> window -> chronological split.

    WHY WE SCALE (a new concept vs Phase 5):
    Neural networks train far more reliably when input values are in a
    small, consistent range (typically 0 to 1) rather than raw dollar
    amounts that can be in the hundreds. Large raw values can cause unstable
    gradients during training. We use MinMaxScaler, which maps the minimum
    observed price to 0 and the maximum to 1.

    CRITICAL: the scaler is FIT ONLY ON TRAINING DATA, then used to
    TRANSFORM both train and test data. Fitting on the full dataset
    (including test data) would leak future price range information into
    training — the model would implicitly "know" the test set's min/max
    price before ever seeing it, which is a subtle but real form of data
    leakage, similar in spirit to the shuffle-split mistake from Phase 5.

    Returns:
        X_train, X_test, y_train, y_test (all scaled, shape ready for LSTM
        input which expects 3D: [samples, timesteps, features]), plus the
        fitted scaler (needed later to un-scale predictions back to real
        dollar amounts).
    """
    raw = fetch_historical_data(ticker, period=period, interval="1d")
    cleaned = clean_ohlcv(raw)

    closes = cleaned["Close"].values.reshape(-1, 1)

    # Chronological split FIRST, before any scaling — same principle as
    # Phase 5's chronological_train_test_split, applied here at the raw
    # price level instead of the feature-table level.
    split_index = int(len(closes) * 0.8)
    train_closes = closes[:split_index]
    test_closes = closes[split_index:]

    scaler = MinMaxScaler(feature_range=(0, 1))
    train_scaled = scaler.fit_transform(train_closes)   # fit + transform on train only
    test_scaled = scaler.transform(test_closes)          # transform only, using train's fit

    X_train, y_train = create_sequences(train_scaled.flatten(), window_size)
    X_test, y_test = create_sequences(test_scaled.flatten(), window_size)

    # Reshape to 3D: (samples, timesteps, features=1) — the shape Keras's
    # LSTM/GRU layers require, even though we only have one feature (price)
    # per timestep here.
    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    return X_train, X_test, y_train, y_test, scaler
