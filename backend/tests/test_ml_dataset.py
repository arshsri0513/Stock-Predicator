"""
Unit tests for the chronological split (Phase 5) and sequence windowing
(Phase 6) logic -- the two most important correctness guarantees in the
ML pipeline. A bug here wouldn't crash anything; it would silently
produce misleadingly optimistic metrics, which is a much more dangerous
failure mode than a crash. These tests exist specifically to catch that.
"""

import numpy as np
import pandas as pd

from app.ml.dataset import chronological_train_test_split
from app.ml.sequence_dataset import create_sequences


def test_chronological_split_no_overlap():
    """The single most important test in this file: training data must
    never contain dates that come after any test data date."""
    dates = pd.bdate_range("2024-01-01", periods=100)
    X = pd.DataFrame({"feature": range(100)}, index=dates)
    y = pd.Series(range(100), index=dates)

    X_train, X_test, y_train, y_test = chronological_train_test_split(X, y, test_size=0.2)

    assert X_train.index.max() < X_test.index.min(), (
        "Training data overlaps with or comes after test data -- this is "
        "the exact data leakage bug Phase 5 was built specifically to avoid."
    )


def test_chronological_split_respects_test_size():
    dates = pd.bdate_range("2024-01-01", periods=100)
    X = pd.DataFrame({"feature": range(100)}, index=dates)
    y = pd.Series(range(100), index=dates)

    X_train, X_test, y_train, y_test = chronological_train_test_split(X, y, test_size=0.2)

    assert len(X_train) == 80
    assert len(X_test) == 20


def test_chronological_split_x_and_y_stay_aligned():
    """X and y must split at exactly the same index boundary -- a
    misaligned split would silently pair each row's features with the
    WRONG target, corrupting every metric without throwing any error."""
    dates = pd.bdate_range("2024-01-01", periods=50)
    X = pd.DataFrame({"feature": range(50)}, index=dates)
    y = pd.Series(range(50), index=dates)

    X_train, X_test, y_train, y_test = chronological_train_test_split(X, y, test_size=0.3)

    assert X_train.index.equals(y_train.index)
    assert X_test.index.equals(y_test.index)


def test_create_sequences_shapes_and_values():
    """Verifies the exact sliding-window mechanics from Phase 6 -- each
    window of `window_size` values should pair with the very next value
    as its target, matching the docstring's own worked example."""
    values = np.array([10, 11, 12, 13, 14])
    X, y = create_sequences(values, window_size=3)

    assert X.shape == (2, 3)
    assert y.shape == (2,)
    assert np.array_equal(X[0], [10, 11, 12])
    assert y[0] == 13
    assert np.array_equal(X[1], [11, 12, 13])
    assert y[1] == 14


def test_create_sequences_empty_when_too_short():
    """A series shorter than the window size can't produce a single
    valid sequence -- the function should return empty arrays, not crash."""
    values = np.array([1, 2])
    X, y = create_sequences(values, window_size=5)

    assert len(X) == 0
    assert len(y) == 0
