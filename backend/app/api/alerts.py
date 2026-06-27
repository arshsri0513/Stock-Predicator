"""
Price alert API routes: POST /alerts (create), POST /alerts/{id}/check
(manually trigger a check, sending email/Telegram if conditions are met).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.financial import PriceAlert
from app.schemas.alert_schemas import AlertCreateRequest, AlertResponse, AlertCheckResult
from app.services.alert_service import create_alert, check_and_trigger_alert

router = APIRouter()


@router.post("", response_model=AlertResponse, status_code=201)
def create_price_alert(
    request: AlertCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a price alert rule. At least one of notify_email or
    telegram_chat_id should be set, or there's nowhere for the alert to
    actually go -- we don't hard-require this at the schema level since a
    person might reasonably want to set one now and add the other later.
    """
    alert = create_alert(
        db, str(current_user.id), request.ticker, request.threshold_price,
        request.direction, request.notify_email, request.telegram_chat_id,
    )
    return AlertResponse(
        id=str(alert.id),
        ticker=request.ticker.upper(),
        threshold_price=alert.threshold_price,
        direction=alert.direction,
        notify_email=alert.notify_email,
        telegram_chat_id=alert.telegram_chat_id,
    )


@router.post("/{alert_id}/check", response_model=AlertCheckResult)
def check_price_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Manually trigger a check of one alert against the current price.

    Note: this is an ON-DEMAND check, not an automatic background process
    -- see app.services.alert_service for why (no scheduler is built in
    this project). Calling this repeatedly is exactly what a real
    scheduled job would do automatically; this route lets you test and
    demonstrate the underlying logic without building that scheduler.
    """
    alert = (
        db.query(PriceAlert)
        .filter(PriceAlert.id == alert_id, PriceAlert.user_id == str(current_user.id))
        .first()
    )
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")

    try:
        result = check_and_trigger_alert(db, alert)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return AlertCheckResult(**result)
