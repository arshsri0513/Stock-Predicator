"""
Request/response schemas for watchlist endpoints.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class WatchlistAddRequest(BaseModel):
    ticker: str


class WatchlistItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticker: str
    added_at: datetime
