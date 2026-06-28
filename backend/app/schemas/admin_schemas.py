"""
Request/response schemas for admin-only endpoints.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AdminUserView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    is_admin: bool
    created_at: datetime


class AdminModelView(BaseModel):
    id: str
    ticker: str
    model_type: str
    r2_score: float | None
    trained_at: datetime
