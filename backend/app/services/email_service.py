"""
Email alert service -- sends notification emails via Gmail SMTP.

Uses Python's built-in smtplib/email modules rather than a third-party
email library -- for simple plain-text/HTML notification emails like
these, the standard library is fully sufficient and adds zero new
dependencies.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def send_email_alert(to_email: str, subject: str, body: str) -> bool:
    """
    Send a plain-text email alert.

    Returns True on success, False on failure -- callers (e.g. a price
    alert checker) should treat a failed email as a non-fatal event to
    log/skip, not something that should crash a background job processing
    many users' alerts.

    Requires SMTP_USERNAME and SMTP_PASSWORD to be set in .env (see Phase
    13 notes on generating a Gmail "App Password" -- a regular Gmail
    password will NOT work here and Google will reject the login attempt).
    """
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        return False  # not configured -- fail quietly rather than crash

    message = MIMEMultipart()
    message["From"] = settings.SMTP_USERNAME
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # upgrade to an encrypted connection -- required by Gmail
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
        return True
    except Exception:
        return False


def format_price_alert_email(ticker: str, current_price: float, threshold: float, direction: str) -> tuple[str, str]:
    """
    Builds a subject/body pair for a price threshold alert.
    Returns (subject, body).
    """
    subject = f"Price Alert: {ticker} is now ${current_price:.2f}"
    body = (
        f"{ticker} has crossed your alert threshold.\n\n"
        f"Current price: ${current_price:.2f}\n"
        f"Your threshold: ${threshold:.2f} ({direction})\n\n"
        f"-- Stock Predictor"
    )
    return subject, body
