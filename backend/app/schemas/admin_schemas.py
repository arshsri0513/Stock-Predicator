"""
Request/response schemas for admin-only endpoints.
"""

from datetime import datetime
from pydantic import BaseModel


class AdminUserView(BaseModel):
    id: str
    email: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminModelView(BaseModel):
    id: str
    ticker: str
    model_type: str
    r2_score: float | None
    trained_at: datetime
