"""
Price alert business logic: creating alert rules and checking them
against live prices.
"""

from sqlalchemy.orm import Session

from app.models.financial import PriceAlert
from app.services.watchlist_service import get_or_create_stock
from app.services.stock_data import fetch_recent_data
from app.services.email_service import send_email_alert, format_price_alert_email
from app.services.telegram_service import send_telegram_alert, format_price_alert_message


def create_alert(
    db: Session,
    user_id: str,
    ticker: str,
    threshold_price: float,
    direction: str,
    notify_email: str | None,
    telegram_chat_id: str | None,
) -> PriceAlert:
    stock = get_or_create_stock(db, ticker)
    alert = PriceAlert(
        user_id=user_id,
        stock_id=stock.id,
        threshold_price=threshold_price,
        direction=direction,
        notify_email=notify_email,
        telegram_chat_id=telegram_chat_id,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def check_and_trigger_alert(db: Session, alert: PriceAlert) -> dict:
    """
    Check a single alert against the current live price, and send
    notifications if the threshold condition is met.

    This is a manual/on-demand check for now (called by a route a person
    triggers themselves) -- a genuine production version of this feature
    would run on a schedule (e.g. every few minutes via a background job
    or cron), checking every active alert automatically rather than
    waiting for someone to ask. We don't build that scheduler here, but
    this function is exactly the piece such a scheduler would call
    repeatedly.
    """
    ticker = alert.stock.ticker
    recent = fetch_recent_data(ticker, days=5)
    current_price = float(recent["Close"].iloc[-1])

    triggered = (
        (alert.direction == "above" and current_price >= alert.threshold_price)
        or (alert.direction == "below" and current_price <= alert.threshold_price)
    )

    email_sent = False
    telegram_sent = False

    if triggered:
        if alert.notify_email:
            subject, body = format_price_alert_email(
                ticker, current_price, alert.threshold_price, alert.direction
            )
            email_sent = send_email_alert(alert.notify_email, subject, body)

        if alert.telegram_chat_id:
            message = format_price_alert_message(
                ticker, current_price, alert.threshold_price, alert.direction
            )
            telegram_sent = send_telegram_alert(alert.telegram_chat_id, message)

    return {
        "ticker": ticker,
        "current_price": round(current_price, 2),
        "threshold_price": alert.threshold_price,
        "direction": alert.direction,
        "triggered": triggered,
        "email_sent": email_sent,
        "telegram_sent": telegram_sent,
    }
