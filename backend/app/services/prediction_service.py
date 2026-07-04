from datetime import datetime

from sqlalchemy.orm import Session

from app.models.financial import Prediction, MLModel
from app.services.watchlist_service import get_or_create_stock


def save_prediction(
    db: Session,
    user_id: str | None,
    ticker: str,
    model_type: str,
    predicted_close: float,
    based_on_date: str,
) -> Prediction:
    stock = get_or_create_stock(db, ticker)

    model = (
        db.query(MLModel)
        .filter(
            MLModel.stock_id == stock.id,
            MLModel.model_type == model_type,
        )
        .first()
    )

    if model is None:
        raise ValueError("Model record not found.")

    prediction = Prediction(
        user_id=user_id,
        stock_id=stock.id,
        model_id=model.id,
        predicted_close=predicted_close,
        based_on_date=datetime.strptime(
            based_on_date,
            "%Y-%m-%d",
        ).date(),
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction