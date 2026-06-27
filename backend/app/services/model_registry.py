"""
Records trained-model metadata in the database (the MLModel table) --
separate from app.ml.train.save_model(), which only saves the model FILE
to disk and has no database access at all.

Why keep these separate rather than have save_model() write to the
database directly? app/ml/ is deliberately kept free of database
concerns -- it's pure ML logic that's testable without a running
Postgres instance (exactly how we verified dataset.py/train.py's logic in
Phases 5-6, without a database, in the sandboxed environment building
this project). Database recording belongs at the API layer, which
already has a session via Depends(get_db).
"""

from sqlalchemy.orm import Session

from app.models.financial import MLModel
from app.services.watchlist_service import get_or_create_stock


def record_trained_model(db: Session, ticker: str, model_type: str, file_path: str, r2_score: float) -> MLModel:
    """
    Create (or update, if this exact ticker+model_type combination was
    already recorded) a row describing a trained model -- used by the
    admin panel to show what's been trained without inspecting the
    filesystem directly.
    """
    stock = get_or_create_stock(db, ticker)

    existing = (
        db.query(MLModel)
        .filter(MLModel.stock_id == stock.id, MLModel.model_type == model_type)
        .first()
    )

    if existing:
        existing.file_path = file_path
        existing.r2_score = r2_score
        db.commit()
        db.refresh(existing)
        return existing

    record = MLModel(stock_id=stock.id, model_type=model_type, file_path=file_path, r2_score=r2_score)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
