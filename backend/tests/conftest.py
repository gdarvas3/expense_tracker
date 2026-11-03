"""Shared fixtures: an isolated in-memory database and a test client per test."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api_client import ExpenseApi
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
def session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def db_session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    with session_factory() as session:
        yield session


@pytest.fixture
def app(session_factory: sessionmaker[Session]) -> FastAPI:
    def get_test_db() -> Iterator[Session]:
        with session_factory() as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_db] = get_test_db
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def api(client: TestClient) -> ExpenseApi:
    return ExpenseApi(client)
