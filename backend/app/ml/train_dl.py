"""
Deep learning model training, with early stopping, and evaluation using the
SAME metrics (RMSE, MAE, MAPE, R2) as Phase 5's classical models -- this is
deliberate, so results are directly comparable across both phases.
"""

import numpy as np
from tensorflow import keras
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pathlib import Path

from app.ml.dl_models import get_dl_model

SAVED_MODELS_DIR = Path(__file__).parent / "saved_models"


def train_dl_model(
    model_type: str,
    X_train, y_train,
    window_size: int = 60,
    epochs: int = 100,
    batch_size: int = 32,
):
    """
    Train a deep learning model with early stopping.

    Args:
        epochs: maximum number of training passes -- set deliberately HIGH
                (100) because early stopping will halt training well before
                this if the model stops improving. Think of this as a safety
                ceiling, not a target.
        batch_size: how many sequences the model processes before each
                    internal weight update. 32 is a common, reasonable
                    default -- smaller batches update more often (slower but
                    sometimes more precise), larger batches are faster per
                    epoch but update less frequently.

    Early stopping configuration:
        - monitor="val_loss": watch the loss on a held-out validation split
          (carved out of X_train automatically by Keras, NOT the final test
          set -- the test set stays completely untouched until evaluation)
        - patience=10: stop if val_loss hasn't improved for 10 consecutive
          epochs (gives the model some room to push through a temporary
          plateau before giving up)
        - restore_best_weights=True: critical -- this rolls the model back
          to whichever epoch had the BEST validation loss, not just the
          last epoch before stopping (which could already be a few epochs
          into overfitting).
    """
    model = get_dl_model(model_type, window_size)

    early_stopping = keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=10,
        restore_best_weights=True,
    )

    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,   # carve 10% of TRAINING data for validation
        callbacks=[early_stopping],
        verbose=0,                # silent -- the API response will report results,
                                   # not a scrolling training log
    )

    epochs_actually_run = len(history.history["loss"])
    return model, epochs_actually_run


def evaluate_dl_model(model, X_test, y_test, scaler) -> dict:
    """
    Evaluate a trained DL model, un-scaling predictions back to real dollar
    amounts first (since the model was trained on 0-1 scaled values, our
    metrics need to be in actual price terms to mean anything to a human,
    and to be comparable with Phase 5's classical model metrics).
    """
    scaled_predictions = model.predict(X_test, verbose=0).flatten()

    # Inverse-transform back to real prices. MinMaxScaler expects a 2D
    # array shaped (n_samples, n_features), hence the reshape.
    predictions = scaler.inverse_transform(scaled_predictions.reshape(-1, 1)).flatten()
    actuals = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

    rmse = np.sqrt(mean_squared_error(actuals, predictions))
    mae = mean_absolute_error(actuals, predictions)
    mape = np.mean(np.abs((actuals - predictions) / actuals)) * 100
    r2 = r2_score(actuals, predictions)

    return {
        "rmse": round(float(rmse), 4),
        "mae": round(float(mae), 4),
        "mape": round(float(mape), 4),
        "r2_score": round(float(r2), 4),
    }


def save_dl_model(model, scaler, ticker: str, model_type: str) -> str:
    """
    Save both the trained model AND its fitted scaler. We need the scaler
    again at prediction time to un-scale future predictions back to dollar
    amounts -- without it, predictions would be meaningless numbers between
    0 and 1.
    """
    import joblib

    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = SAVED_MODELS_DIR / f"{ticker.upper()}_{model_type}.keras"
    scaler_path = SAVED_MODELS_DIR / f"{ticker.upper()}_{model_type}_scaler.joblib"

    model.save(model_path)
    joblib.dump(scaler, scaler_path)

    return str(model_path)


def load_dl_model(ticker: str, model_type: str):
    """Load a previously trained DL model and its scaler."""
    import joblib

    model_path = SAVED_MODELS_DIR / f"{ticker.upper()}_{model_type}.keras"
    scaler_path = SAVED_MODELS_DIR / f"{ticker.upper()}_{model_type}_scaler.joblib"

    if not model_path.exists():
        raise FileNotFoundError(
            f"No trained '{model_type}' deep learning model found for "
            f"'{ticker}'. Train one first via POST /models/train-dl."
        )

    model = keras.models.load_model(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler
