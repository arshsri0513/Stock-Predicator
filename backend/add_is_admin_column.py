"""
One-time migration script: adds the is_admin column to the existing
users table.

Why this needs its own script rather than just re-running create_tables.py:
SQLAlchemy's Base.metadata.create_all() only creates tables that don't
exist yet -- it never ALTERS an existing table's columns. Since 'users'
already exists from Phase 9, adding a new column to it requires a real
ALTER TABLE statement. This is exactly the kind of operation a proper
migration tool (Alembic, listed in our Phase 2 requirements.txt) is built
for -- we're using a minimal raw-SQL script here instead of setting up a
full Alembic migration history, which would be disproportionate tooling
for one column addition this late in the project. A real production
project maintained over time would use Alembic for every schema change,
not just this one.

Usage (from backend/, with venv activated):
    python add_is_admin_column.py
"""

from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    conn.execute(text(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE"
    ))
    conn.commit()

print("Done. 'is_admin' column added to 'users' table (or already existed).")
