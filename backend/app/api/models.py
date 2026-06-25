"""
Machine learning API routes: /models/train, /models/{ticker}/predict,
/models/{ticker}/evaluate.

Same thin-route pattern as app/api/stocks.py — HTTP concerns only, all real
logic delegated to app.ml.dataset and app.ml.train.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.ml_schemas import TrainRequest, TrainResponse, PredictResponse
from app.ml.dataset import build_ml_dataset, split_features_target, chronological_train_test_split
from app.ml.train import train_model, evaluate_model, save_model, load_model

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
    a background job queue instead — we'll build that properly in Phase 13.

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
