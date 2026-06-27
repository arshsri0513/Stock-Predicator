"""
Request/response schemas for portfolio tracker endpoints.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class HoldingAddRequest(BaseModel):
    ticker: str
    quantity: float = Field(..., gt=0)
    purchase_price: float = Field(..., gt=0)


class HoldingResponse(BaseModel):
    id: str
    ticker: str
    quantity: float
    purchase_price: float
    purchased_at: datetime
    current_price: float | None = None
    market_value: float | None = None
    gain_loss: float | None = None
    gain_loss_percent: float | None = None
