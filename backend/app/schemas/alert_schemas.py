"""
Request/response schemas for price alert endpoints.
"""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class AlertCreateRequest(BaseModel):
    ticker: str
    threshold_price: float = Field(..., gt=0)
    direction: Literal["above", "below"]
    notify_email: str | None = None
    telegram_chat_id: str | None = None


class AlertResponse(BaseModel):
    id: str
    ticker: str
    threshold_price: float
    direction: str
    notify_email: str | None
    telegram_chat_id: str | None
    is_active: str
    created_at: datetime


class AlertCheckResult(BaseModel):
    ticker: str
    current_price: float
    threshold_price: float
    direction: str
    triggered: bool
    email_sent: bool
    telegram_sent: bool
