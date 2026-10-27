"""Tests for the application skeleton: health check and error-to-status mapping."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.exceptions import (
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


class PositiveAmount(BaseModel):
    amount: int = Field(gt=0)


def register_probe_routes(app: FastAPI) -> None:
    """Add test-only endpoints that trigger each error path."""

    @app.post("/probe/validate")
    def validate_body(body: PositiveAmount) -> PositiveAmount:
        return body

    @app.get("/probe/raise/{error_name}")
    def raise_domain_error(error_name: str) -> None:
        raise DOMAIN_ERRORS_BY_NAME[error_name]("probe message")


DOMAIN_ERRORS_BY_NAME: dict[str, type[DomainError]] = {
    "validation": ValidationError,
    "unauthorized": UnauthorizedError,
    "forbidden": ForbiddenError,
    "not_found": NotFoundError,
    "conflict": ConflictError,
}


@pytest.fixture
def probe_client(app: FastAPI) -> TestClient:
    register_probe_routes(app)
    return TestClient(app)


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_request_validation_error_returns_400_not_422(probe_client: TestClient) -> None:
    # AC-5 requires 400; FastAPI's default for invalid request bodies is 422.
    response = probe_client.post("/probe/validate", json={"amount": 0})

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("error_name", "expected_status"),
    [
        ("validation", 400),
        ("unauthorized", 401),
        ("forbidden", 403),
        ("not_found", 404),
        ("conflict", 409),
    ],
)
def test_domain_error_maps_to_http_status(
    probe_client: TestClient, error_name: str, expected_status: int
) -> None:
    response = probe_client.get(f"/probe/raise/{error_name}")

    assert response.status_code == expected_status
    assert response.json() == {"detail": "probe message"}
