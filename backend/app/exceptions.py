"""Domain exceptions raised by services; main.py maps them to HTTP status codes."""


class DomainError(Exception):
    """Base class for all business-rule violations."""

    status_code: int = 500


class ValidationError(DomainError):
    """Input breaks a business rule, e.g. percentages not summing to 100% (AC-5)."""

    status_code = 400


class UnauthorizedError(DomainError):
    """The caller could not be identified from the X-User-Id header."""

    status_code = 401


class ForbiddenError(DomainError):
    """The caller is not allowed to access the resource (AC-7)."""

    status_code = 403


class NotFoundError(DomainError):
    """The requested resource does not exist."""

    status_code = 404


class ConflictError(DomainError):
    """The action conflicts with the current state, e.g. removing an indebted member (AC-6)."""

    status_code = 409
