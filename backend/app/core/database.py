"""
Database connection setup.

This is the ONLY place that creates the SQLAlchemy engine and session
factory -- every other file that needs database access imports from here,
rather than each file creating its own connection. Centralizing this means
connection pooling, credentials, and configuration live in exactly one spot.

Concepts explained:
- ENGINE: the core object that manages the actual connection(s) to Postgres.
  Created once, reused for the lifetime of the application.
- SESSION: a single "conversation" with the database -- you open one,
  do some queries/inserts, then close it. We create a NEW session per
  request (see get_db() below), never share one session across requests.
- BASE: a special class that all our table models (Phase 9.4) will inherit
  from. SQLAlchemy uses this to know which Python classes correspond to
  database tables.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session to a route, and
    guarantees it gets closed afterward -- even if the route raises an
    error. This pattern (a generator with try/finally) is how FastAPI
    expects dependencies that need cleanup to be written.

    Usage in a route:
        @router.get("/something")
        def my_route(db: Session = Depends(get_db)):
            ...use db here...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
