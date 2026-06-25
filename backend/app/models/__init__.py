"""
Imports every model so they're all registered with Base before anything
tries to create tables or run migrations. Without this, SQLAlchemy
wouldn't know these classes exist if only app.core.database (which defines
Base) were imported on its own -- Python only registers a class with Base
once its module is actually imported somewhere.
"""

from app.models.user import User, Stock
from app.models.financial import MLModel, Prediction, NewsArticle, Watchlist

__all__ = ["User", "Stock", "MLModel", "Prediction", "NewsArticle", "Watchlist"]
