"""
Portfolio tracker API routes: GET/POST/DELETE /portfolio.

Same protected-route pattern as watchlist (Depends(get_current_user)).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.portfolio_schemas import HoldingAddRequest, HoldingResponse
from app.services.portfolio_service import add_holding, remove_holding, get_portfolio_with_gains

router = APIRouter()


@router.get("", response_model=list[HoldingResponse])
def list_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns the authenticated user's full portfolio, with live current
    prices and computed gain/loss per holding.
    """
    return get_portfolio_with_gains(db, str(current_user.id))


@router.post("", response_model=HoldingResponse, status_code=201)
def add_portfolio_holding(
    request: HoldingAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Records a new holding (a purchase) for the authenticated user."""
    holding = add_holding(
        db, str(current_user.id), request.ticker, request.quantity, request.purchase_price
    )
    return HoldingResponse(
        id=str(holding.id),
        ticker=request.ticker.upper(),
        quantity=holding.quantity,
        purchase_price=holding.purchase_price,
        purchased_at=holding.purchased_at,
    )


@router.delete("/{holding_id}", status_code=204)
def remove_portfolio_holding(
    holding_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Removes a specific holding by its ID."""
    removed = remove_holding(db, str(current_user.id), holding_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Holding not found.")
    return None
