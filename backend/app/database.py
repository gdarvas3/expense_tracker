"""Database engine, session factory and the request-scoped session dependency."""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./expense_tracker.db")

# SQLite connections are thread-bound by default; FastAPI serves requests from a thread pool.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def get_db() -> Iterator[Session]:
    """Yield a database session that is closed after the request."""
    with SessionLocal() as session:
        yield session
