"""
Request/response schemas for watchlist endpoints.
"""

from datetime import datetime
from pydantic import BaseModel


class WatchlistAddRequest(BaseModel):
    ticker: str


class WatchlistItem(BaseModel):
    id: str
    ticker: str
    added_at: datetime

    class Config:
        from_attributes = True
