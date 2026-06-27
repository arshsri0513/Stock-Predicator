"""
Admin panel API routes: GET /admin/users, GET /admin/models.

Every route here uses Depends(require_admin) rather than
Depends(get_current_user) -- a regular logged-in user gets a 403
Forbidden if they try these, even with a perfectly valid token, because
being AUTHENTICATED and being AUTHORIZED for admin actions are two
different checks (see app.api.auth.require_admin for why these are kept
as separate dependencies).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import require_admin
from app.models.user import User, Stock
from app.models.financial import MLModel
from app.schemas.admin_schemas import AdminUserView, AdminModelView

router = APIRouter()


@router.get("/users", response_model=list[AdminUserView])
def list_all_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Lists every registered user. Admin-only -- a regular user has no
    legitimate reason to enumerate every other user's email address.
    """
    users = db.query(User).all()
    return [
        AdminUserView(id=str(u.id), email=u.email, is_admin=u.is_admin, created_at=u.created_at)
        for u in users
    ]


@router.get("/models", response_model=list[AdminModelView])
def list_all_trained_models(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Lists every trained model recorded in the database (see Phase 13's
    model_registry.py for how these rows get created) -- gives an admin
    visibility into what's been trained system-wide, across every user,
    without inspecting the filesystem directly.
    """
    records = (
        db.query(MLModel, Stock.ticker)
        .join(Stock, MLModel.stock_id == Stock.id)
        .all()
    )
    return [
        AdminModelView(
            id=str(model.id),
            ticker=ticker,
            model_type=model.model_type,
            r2_score=model.r2_score,
            trained_at=model.trained_at,
        )
        for model, ticker in records
    ]
