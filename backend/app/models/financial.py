"""
SQLAlchemy models: MLModel, Prediction, NewsArticle, Watchlist.

These four tables all depend on Stock (and some on User) via foreign keys,
which is why they live separately from app/models/user.py -- conceptually,
"here are the things that REFERENCE a user/stock" vs "here are the core
entities themselves."
"""

import uuid
from datetime import datetime, timezone, date

from sqlalchemy import Column, String, DateTime, Date, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class MLModel(Base):
    """
    Metadata about a trained model -- NOT the model file itself (that stays
    on disk as a .joblib/.keras file, same as Phases 5-6). This table lets
    us query "what models have we trained for AAPL, and how well did they
    perform?" without touching the filesystem at all.
    """
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False)
    model_type = Column(String, nullable=False)  # e.g. "random_forest", "lstm"
    file_path = Column(String, nullable=False)
    r2_score = Column(Float, nullable=True)
    trained_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    stock = relationship("Stock", back_populates="models")
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")


class Prediction(Base):
    """
    A single prediction request and its result. Storing these gives us a
    full audit trail: who asked, for what stock, using which model, what
    the model said, and when -- useful for Phase 13's history features and
    for spotting model drift over time (comparing past predictions against
    what actually happened).
    """
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False)
    predicted_close = Column(Float, nullable=False)
    based_on_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="predictions")
    stock = relationship("Stock", back_populates="predictions")
    model = relationship("MLModel", back_populates="predictions")


class NewsArticle(Base):
    """
    A scored news article, persisted so we don't have to re-fetch and
    re-score the same headlines from yfinance/VADER/FinBERT every time
    someone views a stock's news -- this is the caching layer Phase 1's
    architecture diagram anticipated.
    """
    __tablename__ = "news"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False)
    title = Column(String, nullable=False)
    publisher = Column(String, nullable=True)
    vader_compound = Column(Float, nullable=True)
    finbert_label = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    stock = relationship("Stock", back_populates="news")


class Watchlist(Base):
    """
    A join table: which users are tracking which stocks. A user can watch
    many stocks; a stock can be watched by many users -- this table is what
    makes that many-to-many relationship possible without duplicating
    stock data per user.
    """
    __tablename__ = "watchlists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="watchlists")
    stock = relationship("Stock", back_populates="watchlists")


class PortfolioHolding(Base):
    """
    An actual position a user holds -- distinct from Watchlist, which only
    tracks INTEREST in a stock, not ownership. A user can watch a stock
    without owning it, and own shares without it being on their watchlist;
    keeping these as separate tables keeps each one's meaning unambiguous
    rather than overloading Watchlist with ownership-specific fields that
    wouldn't make sense for someone just watching a stock.

    quantity and purchase_price together let us compute real gain/loss
    against the CURRENT price (fetched live, same as everywhere else in
    this project) without storing a duplicate, potentially-stale copy of
    the current price ourselves.
    """
    __tablename__ = "portfolio_holdings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    purchased_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="portfolio_holdings")
    stock = relationship("Stock", back_populates="portfolio_holdings")
