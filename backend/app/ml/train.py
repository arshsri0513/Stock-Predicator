"""
Classical ML model training and evaluation.

We train three model types on the same data and compare them fairly using
identical train/test splits and identical metrics. This module doesn't fetch
data itself (that's app.ml.dataset's job) — it only trains/evaluates models
on data it's given. This separation means we can unit test this module with
fake data, without needing a network call to Yahoo Finance every time.
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor


# Where trained model files get saved, matching our Phase 1 folder structure
SAVED_MODELS_DIR = Path(__file__).parent / "saved_models"


def get_model(model_type: str):
    """
    Factory function: given a model type name, return a fresh, untrained
    model instance with sensible hyperparameters.

    Why centralize hyperparameters here instead of scattering them?
    So that when we want to tune them later (or expose them as
    user-configurable training options in Phase 13's "model retraining"
    feature), there's exactly one place to change.
    """
    if model_type == "linear_regression":
        # No hyperparameters to tune here — Linear Regression is our
        # deliberately simple baseline. Every other model should beat this,
        # or it's not earning its complexity.
        return LinearRegression()

    elif model_type == "random_forest":
        return RandomForestRegressor(
            n_estimators=200,      # number of trees — more trees = more
                                    # stable predictions, at the cost of
                                    # training time. 200 is a solid default.
            max_depth=10,           # caps how deep each tree can grow —
                                    # prevents severe overfitting to noise
                                    # in daily price data.
            min_samples_leaf=5,     # each leaf needs at least 5 samples —
                                    # another overfitting guard.
            random_state=42,        # fixes randomness for reproducibility —
                                    # same data in = same model out, every time.
            n_jobs=-1,               # use all available CPU cores
        )

    elif model_type == "xgboost":
        return XGBRegressor(
            n_estimators=200,
            max_depth=5,             # XGBoost trees are usually shallower
                                      # than Random Forest's, since boosting
                                      # builds many weak learners sequentially
                                      # rather than a few strong independent ones.
            learning_rate=0.05,        # how much each new tree corrects the
                                      # previous trees' errors — lower values
                                      # need more trees but generalize better.
            random_state=42,
            n_jobs=-1,
        )

    else:
        raise ValueError(
            f"Unknown model_type '{model_type}'. "
            f"Expected one of: linear_regression, random_forest, xgboost."
        )


def train_model(model_type: str, X_train: pd.DataFrame, y_train: pd.Series):
    """
    Train a model of the given type on the provided training data.
    Returns the fitted model object.
    """
    model = get_model(model_type)
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """
    Evaluate a trained model on held-out test data, returning the four
    standard regression metrics:

    - RMSE (Root Mean Squared Error): average prediction error, in the
      SAME UNITS as the target (dollars, for us). Penalizes large errors
      more heavily than small ones, due to the squaring.
    - MAE (Mean Absolute Error): average absolute prediction error, also
      in dollars. More intuitive than RMSE, less sensitive to rare large
      misses.
    - MAPE (Mean Absolute Percentage Error): average error as a PERCENTAGE
      of the actual price — useful for comparing performance across stocks
      with very different price levels ($50 stock vs $2000 stock).
    - R² Score: fraction of price variance the model explains, from 0 to 1
      (can go negative if the model is worse than just predicting the mean).
      An R² of 0.95 doesn't mean "95% accurate" — it means the model
      explains 95% of the day-to-day price VARIANCE, which for stock prices
      is often dominated by yesterday's price being a very strong predictor
      of today's price (high autocorrelation), not necessarily a sign of
      genuine predictive skill.
    """
    predictions = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
    r2 = r2_score(y_test, predictions)

    return {
        "rmse": round(float(rmse), 4),
        "mae": round(float(mae), 4),
        "mape": round(float(mape), 4),
        "r2_score": round(float(r2), 4),
    }


def save_model(model, ticker: str, model_type: str) -> str:
    """
    Persist a trained model to disk so we don't retrain it on every
    prediction request (this is the "pre-train, don't train live" decision
    from our Phase 1 architecture).

    Filename pattern: {TICKER}_{model_type}.joblib
    e.g. AAPL_random_forest.joblib
    """
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = SAVED_MODELS_DIR / f"{ticker.upper()}_{model_type}.joblib"
    joblib.dump(model, filepath)
    return str(filepath)


def load_model(ticker: str, model_type: str):
    """
    Load a previously trained model from disk.
    Raises FileNotFoundError (with a clear message) if it hasn't been
    trained yet — the API layer will catch this and tell the user to
    train a model first.
    """
    filepath = SAVED_MODELS_DIR / f"{ticker.upper()}_{model_type}.joblib"
    if not filepath.exists():
        raise FileNotFoundError(
            f"No trained '{model_type}' model found for '{ticker}'. "
            f"Train one first via POST /models/train."
        )
    return joblib.load(filepath)
