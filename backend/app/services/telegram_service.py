"""
Telegram alert service -- sends notification messages via the Telegram
Bot API.

We use `requests` directly against Telegram's HTTP API rather than a
dedicated Telegram library -- the API surface we need (send one text
message) is a single HTTP call, not worth an extra dependency for.
"""

import requests

from app.core.config import settings


def send_telegram_alert(chat_id: str, message: str) -> bool:
    """
    Send a text message via a Telegram bot.

    Requires TELEGRAM_BOT_TOKEN in .env (see Phase 13 notes on creating a
    bot via @BotFather). `chat_id` is specific to the PERSON receiving the
    message (not the bot) -- each user who wants Telegram alerts needs to
    have messaged the bot at least once and provided their own chat_id,
    obtained via the bot's /getUpdates endpoint as described in our setup
    notes.

    Returns True on success, False on failure -- same non-fatal failure
    pattern as send_email_alert, for the same reason (one user's bad
    chat_id shouldn't crash a batch alert job for everyone else).
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        return False

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False


def format_price_alert_message(ticker: str, current_price: float, threshold: float, direction: str) -> str:
    """Builds a Telegram message for a price threshold alert."""
    return (
        f"\U0001F4C8 Price Alert: {ticker}\n\n"
        f"Current price: ${current_price:.2f}\n"
        f"Threshold: ${threshold:.2f} ({direction})"
    )
