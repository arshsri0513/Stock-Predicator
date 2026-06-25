"""
Request/response schemas for the ML training and prediction endpoints.

Why define these explicitly with Pydantic instead of just using raw dicts?
FastAPI uses these to auto-validate incoming requests (e.g. reject a
request where model_type isn't one of our three supported values, before
our code even runs) AND to auto-generate the interactive /docs page with
correct example values and constraints.
"""

from pydantic import BaseModel, Field
from typing import Literal

ModelType = Literal["linear_regression", "random_forest", "xgboost"]


class TrainRequest(BaseModel):
    ticker: str = Field(..., examples=["AAPL"], description="Stock ticker symbol")
    model_type: ModelType = Field(..., description="Which model to train")
    period: str = Field(default="5y", description="History to train on, e.g. 2y, 5y, max")
    horizon: int = Field(default=1, ge=1, le=30, description="Days ahead to predict")


class TrainResponse(BaseModel):
    ticker: str
    model_type: str
    rows_trained_on: int
    metrics: dict
    model_path: str


class TrainDLRequest(BaseModel):
    ticker: str = Field(..., examples=["AAPL"], description="Stock ticker symbol")
    model_type: Literal["lstm", "gru", "transformer"] = Field(
        ..., description="Which deep learning architecture to train"
    )
    period: str = Field(default="5y", description="History to train on")
    window_size: int = Field(default=60, ge=10, le=200, description="Days of context per sequence")


class TrainDLResponse(BaseModel):
    ticker: str
    model_type: str
    epochs_run: int
    sequences_trained_on: int
    metrics: dict
    model_path: str


class PredictResponse(BaseModel):
    ticker: str
    model_type: str
    predicted_close: float
    based_on_date: str


class EvaluateResponse(BaseModel):
    ticker: str
    model_type: str
    rows_evaluated_on: int
    metrics: dict
    evaluated_on_period: str
