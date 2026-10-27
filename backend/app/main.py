"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.exceptions import DomainError
from app.routers import health

API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(engine)
    yield


async def handle_domain_error(_request: Request, error: DomainError) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"detail": str(error)})


async def handle_request_validation_error(
    _request: Request, error: RequestValidationError
) -> JSONResponse:
    # AC-5: invalid input must be rejected with 400, not FastAPI's default 422.
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": jsonable_encoder(error.errors())},
    )


def create_app() -> FastAPI:
    """Build the application with its routers and error handlers."""
    app = FastAPI(title="Shared Household Expense Splitter", lifespan=lifespan)
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.include_router(health.router, prefix=API_PREFIX)
    return app


app = create_app()
