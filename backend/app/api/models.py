"""
Machine learning API routes: /models/train, /models/{ticker}/predict,
/models/{ticker}/evaluate.

Same thin-route pattern as app/api/stocks.py — HTTP concerns only, all real
logic delegated to app.ml.dataset and app.ml.train.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.ml_schemas import (
    TrainRequest, TrainResponse, PredictResponse, EvaluateResponse,
    TrainDLRequest, TrainDLResponse, MultiPredictRequest, MultiPredictResult,
)
from app.ml.dataset import build_ml_dataset, split_features_target, chronological_train_test_split
from app.ml.train import train_model, evaluate_model, save_model, load_model
from app.ml.sequence_dataset import prepare_sequence_dataset
from app.ml.train_dl import train_dl_model, evaluate_dl_model, save_dl_model

router = APIRouter()


@router.post("/train", response_model=TrainResponse)
def train(request: TrainRequest):
    """
    Train a model for a given ticker and save it to disk.

    This is intentionally a SYNCHRONOUS, ON-DEMAND endpoint for now — the
    person clicks "train" and waits for it to finish. Classical ML models
    (Linear Regression, Random Forest, XGBoost) train in seconds to low
    minutes on a few years of daily data, so this is acceptable for now.
    Deep learning training (Phase 6) will be slow enough that we'll need
    a background job queue instead — a genuine future improvement, not
    yet built in this project.

    Example: POST /models/train
    {"ticker": "AAPL", "model_type": "random_forest", "period": "5y"}
    """
    try:
        dataset = build_ml_dataset(
            request.ticker, period=request.period, horizon=request.horizon
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if len(dataset) < 100:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Only {len(dataset)} usable rows after cleaning/feature "
                f"engineering — too little data to train reliably. Try a "
                f"longer 'period'."
            ),
        )

    X, y = split_features_target(dataset)
    X_train, X_test, y_train, y_test = chronological_train_test_split(X, y)

    model = train_model(request.model_type, X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)
    model_path = save_model(model, request.ticker, request.model_type)

    return TrainResponse(
        ticker=request.ticker.upper(),
        model_type=request.model_type,
        rows_trained_on=len(X_train),
        metrics=metrics,
        model_path=model_path,
    )


@router.get("/{ticker}/predict", response_model=PredictResponse)
def predict(ticker: str, model_type: str = "random_forest"):
    """
    Generate a prediction for the next trading day's closing price, using
    a previously trained model. Requires /models/train to have been called
    first for this ticker + model_type combination.

    Example: GET /models/AAPL/predict?model_type=random_forest
    """
    try:
        model = load_model(ticker, model_type)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        # Rebuild the dataset to get the most recent row's features — this
        # is what we feed the model to predict TOMORROW (a date with no
        # actual target yet, which is exactly why we need a fresh fetch
        # rather than reusing training data).
        dataset = build_ml_dataset(ticker, period="6mo")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    X, _ = split_features_target(dataset)
    latest_features = X.iloc[[-1]]  # most recent row, kept as a DataFrame (not Series)
    prediction = model.predict(latest_features)[0]

    return PredictResponse(
        ticker=ticker.upper(),
        model_type=model_type,
        predicted_close=round(float(prediction), 2),
        based_on_date=str(X.index[-1].date()),
    )


@router.post("/predict-multi", response_model=list[MultiPredictResult])
def predict_multi(request: MultiPredictRequest):
    """
    Predict next-day close for several tickers in one call.

    Design choice: this NEVER fails the whole request because one ticker
    has a problem (no trained model, invalid symbol, etc.) -- each
    ticker's result independently carries either a prediction or an error
    message. A dashboard showing 8 stocks shouldn't go blank because the
    9th one was never trained; it should show 8 real predictions and one
    clear "not available" message.
    """
    results = []
    for ticker in request.tickers:
        try:
            model = load_model(ticker, request.model_type)
            dataset = build_ml_dataset(ticker, period="6mo")
            X, _ = split_features_target(dataset)
            latest_features = X.iloc[[-1]]
            prediction = model.predict(latest_features)[0]
            results.append(MultiPredictResult(
                ticker=ticker.upper(),
                predicted_close=round(float(prediction), 2),
                based_on_date=str(X.index[-1].date()),
            ))
        except FileNotFoundError:
            results.append(MultiPredictResult(
                ticker=ticker.upper(),
                error=f"No trained '{request.model_type}' model for this ticker yet.",
            ))
        except ValueError as e:
            results.append(MultiPredictResult(ticker=ticker.upper(), error=str(e)))

    return results


@router.post("/{ticker}/retrain", response_model=TrainResponse)
def retrain(ticker: str, model_type: str = "random_forest", period: str = "5y"):
    """
    Explicitly retrain a model that may already exist, using the most
    recent available data. Functionally this calls the same training
    pipeline as POST /models/train -- the distinction is purely about
    INTENT: "train" implies a new model+ticker combination, "retrain"
    implies refreshing an existing one with newer data -- exactly the
    kind of operation an admin panel's "refresh model" button or a
    scheduled job would trigger.

    Saving a model with the same ticker+model_type filename naturally
    overwrites the previous version on disk -- there's no separate
    "delete old model" step needed.
    """
    try:
        dataset = build_ml_dataset(ticker, period=period)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if len(dataset) < 100:
        raise HTTPException(
            status_code=422,
            detail=f"Only {len(dataset)} usable rows -- too little data to retrain reliably.",
        )

    X, y = split_features_target(dataset)
    X_train, X_test, y_train, y_test = chronological_train_test_split(X, y)

    model = train_model(model_type, X_train, y_train)
    metrics = evaluate_model(model, X_test, y_test)
    model_path = save_model(model, ticker, model_type)

    return TrainResponse(
        ticker=ticker.upper(),
        model_type=model_type,
        rows_trained_on=len(X_train),
        metrics=metrics,
        model_path=model_path,
    )


@router.get("/{ticker}/evaluate", response_model=EvaluateResponse)
def evaluate(ticker: str, model_type: str = "random_forest", period: str = "2y"):
    """
    Re-evaluate a previously trained CLASSICAL model (linear_regression,
    random_forest, xgboost) on a fresh chronological test split, without
    retraining it.

    Why this is useful separately from /train: training and evaluating are
    different concerns. A user might want to check "how is this model
    doing lately?" without paying the cost of retraining, or might want to
    evaluate the SAME saved model against a different period than it was
    originally trained on, to see how well it generalizes.

    Note: this re-evaluates against a fresh chronological split of `period`
    -- it does NOT guarantee the same train/test boundary used during the
    original training run, so metrics here may differ slightly from the
    /train response even for the same model and ticker.

    Example: GET /models/AAPL/evaluate?model_type=random_forest&period=2y
    """
    try:
        model = load_model(ticker, model_type)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        dataset = build_ml_dataset(ticker, period=period)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    X, y = split_features_target(dataset)
    _, X_test, _, y_test = chronological_train_test_split(X, y)

    metrics = evaluate_model(model, X_test, y_test)

    return EvaluateResponse(
        ticker=ticker.upper(),
        model_type=model_type,
        rows_evaluated_on=len(X_test),
        metrics=metrics,
        evaluated_on_period=period,
    )


@router.post("/train-dl", response_model=TrainDLResponse)
def train_deep_learning_model(request: TrainDLRequest):
    """
    Train a deep learning model (LSTM, GRU, or Transformer) for a given
    ticker, using a sliding-window sequence approach rather than the flat
    feature table used by classical models in /models/train.

    Note: this endpoint can take significantly longer than /models/train --
    potentially 1-5 minutes depending on data size and how many epochs
    early stopping allows before halting. This is expected for deep
    learning -- a background job queue would be the right long-term fix
    for a slow synchronous endpoint like this, but is not yet built here.

    Example: POST /models/train-dl
    {"ticker": "AAPL", "model_type": "lstm", "period": "5y", "window_size": 60}
    """
    try:
        X_train, X_test, y_train, y_test, scaler = prepare_sequence_dataset(
            request.ticker, period=request.period, window_size=request.window_size
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if len(X_train) < 100:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Only {len(X_train)} usable training sequences -- too few "
                f"to train a deep learning model reliably. Try a longer "
                f"'period' or a smaller 'window_size'."
            ),
        )

    model, epochs_run = train_dl_model(
        request.model_type, X_train, y_train, window_size=request.window_size
    )
    metrics = evaluate_dl_model(model, X_test, y_test, scaler)
    model_path = save_dl_model(model, scaler, request.ticker, request.model_type)

    return TrainDLResponse(
        ticker=request.ticker.upper(),
        model_type=request.model_type,
        epochs_run=epochs_run,
        sequences_trained_on=len(X_train),
        metrics=metrics,
        model_path=model_path,
    )
