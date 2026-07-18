"""
Database configuration for the AI Trip Planner Agent.

Sets up the SQLAlchemy engine, session factory, and declarative base.
Supports both SQLite (local dev) and PostgreSQL (production on Render).
Provides a FastAPI dependency for per-request DB sessions.
"""

import logging
import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

logger = logging.getLogger(__name__)

# Resolve DB path relative to this file so it works regardless of CWD
BASE_DIR = Path(__file__).resolve().parent

# On serverless environments (Vercel, AWS Lambda), write to the writable /tmp path
if os.getenv("VERCEL") == "1" or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    DEFAULT_DB_PATH = Path("/tmp") / "trip_planner.db"
else:
    DEFAULT_DB_PATH = BASE_DIR / "trip_planner.db"

# Prefer DATABASE_URL from environment (e.g. Render); fall back to local SQLite
_raw_url = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# Render (and some PaaS providers) expose postgres:// which SQLAlchemy 2.x rejects.
# Automatically upgrade the scheme to postgresql://.
DATABASE_URL: str = _raw_url.replace("postgres://", "postgresql://", 1)

if DATABASE_URL != _raw_url:
    logger.info("DATABASE_URL scheme normalised: postgres:// → postgresql://")

# SQLite needs check_same_thread=False when used with FastAPI's async workers
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

# expire_on_commit=False keeps attributes usable after commit (handy for responses)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


def get_db():
    """
    FastAPI dependency that yields a database session.

    Ensures the session is always closed, and rolls back on unhandled errors.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _migrate_add_column(column_def: str, table: str, column: str) -> None:
    """
    Safely add a column to an existing table if it does not already exist.
    Uses a raw SQL approach compatible with both SQLite and PostgreSQL.
    """
    with engine.connect() as conn:
        try:
            # Check if column exists by trying to select it
            conn.execute(text(f"SELECT {column} FROM {table} LIMIT 1"))
        except Exception:
            # Column missing — add it
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_def}"))
                conn.commit()
                logger.info("Migration: added column '%s' to '%s'", column, table)
            except Exception as exc:
                logger.warning("Migration skipped (%s.%s): %s", table, column, exc)


def init_db() -> None:
    """Create all tables and run lightweight column migrations. Safe to call on every startup."""
    # Import models so they register with Base.metadata before create_all
    from models import SavedTrip, Trip, User  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Migrate: add columns that may be missing in existing databases
    _migrations = [
        ("currency VARCHAR(10) DEFAULT 'INR'", "trips", "currency"),
        ("hotel_recommendations_json TEXT", "trips", "hotel_recommendations_json"),
        ("restaurant_suggestions_json TEXT", "trips", "restaurant_suggestions_json"),
    ]
    for col_def, table, col_name in _migrations:
        _migrate_add_column(col_def, table, col_name)
