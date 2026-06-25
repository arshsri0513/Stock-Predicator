"""
One-time script to create all tables in PostgreSQL based on our SQLAlchemy
models. Run this once after the database container is up, and again any
time you add a brand new table (for actual schema CHANGES to existing
tables later, we'll use Alembic migrations instead of this blunt approach).

Usage (from the backend/ folder, with venv activated):
    python create_tables.py
"""

from app.core.database import engine, Base
from app.models import User, Stock, MLModel, Prediction, NewsArticle, Watchlist

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Done. Tables created:", list(Base.metadata.tables.keys()))
