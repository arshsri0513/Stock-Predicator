"""
SQLAlchemy models: Users and Stocks.

Each class here maps directly to a database table. The class attributes
become columns. This file matches the ER diagram from Phase 9.2 -- two of
the six tables; the other four (Models, Predictions, News, Watchlists) live
in app/models/financial.py since they're more closely related to each
other and depend on these two existing first (via foreign keys).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """
    A registered user of the application. Password hashing (Phase 12) means
    we NEVER store plain-text passwords -- hashed_password holds a one-way
    hash, not the actual password.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # One user can have many watchlist entries and many predictions.
    # cascade="all, delete-orphan" means: if a user is deleted, their
    # watchlist entries and predictions are deleted too, rather than being
    # left behind as orphaned rows pointing at a user that no longer exists.
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    portfolio_holdings = relationship("PortfolioHolding", back_populates="user", cascade="all, delete-orphan")


class Stock(Base):
    """
    A stock ticker the system knows about. We don't pre-populate this with
    every possible ticker -- rows get created the first time a ticker is
    referenced (e.g. the first time someone trains a model or adds it to a
    watchlist), to avoid maintaining a giant static list ourselves.
    """
    __tablename__ = "stocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String, unique=True, nullable=False, index=True)
    company_name = Column(String, nullable=True)
    sector = Column(String, nullable=True)

    models = relationship("MLModel", back_populates="stock", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="stock", cascade="all, delete-orphan")
    news = relationship("NewsArticle", back_populates="stock", cascade="all, delete-orphan")
    watchlists = relationship("Watchlist", back_populates="stock", cascade="all, delete-orphan")
    portfolio_holdings = relationship("PortfolioHolding", back_populates="stock", cascade="all, delete-orphan")
