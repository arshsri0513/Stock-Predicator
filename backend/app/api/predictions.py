from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.financial import Prediction

router = APIRouter()


@router.get("")
def get_prediction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    predictions = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )

    return [
        {
            "id": str(p.id),
            "predicted_close": p.predicted_close,
            "based_on_date": p.based_on_date,
            "created_at": p.created_at,
            "stock_id": str(p.stock_id),
            "model_id": str(p.model_id),
        }
        for p in predictions
    ]