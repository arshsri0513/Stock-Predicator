"""
Request/response schemas for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="At least 8 characters")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # lets this schema build directly from a SQLAlchemy User object

    id: str
    email: str
