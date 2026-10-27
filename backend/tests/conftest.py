"""Shared fixtures: an isolated in-memory database and a test client per test."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app


@pytest.fixture
def engine() -> Iterator[Engine]:
    # StaticPool keeps one connection, so the in-memory database survives across sessions.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def app(engine: Engine) -> FastAPI:
    test_session_factory = sessionmaker(bind=engine, autoflush=False)

    def get_test_db() -> Iterator[Session]:
        with test_session_factory() as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_db] = get_test_db
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)
