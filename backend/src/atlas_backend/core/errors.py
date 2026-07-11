"""Standard backend errors and error response mapping."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from atlas_backend.core.responses import AtlasErrorResponse


class AtlasErrorCode(StrEnum):
    """Stable API error categories."""

    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


ERROR_STATUS_CODES: dict[AtlasErrorCode, int] = {
    AtlasErrorCode.BAD_REQUEST: 400,
    AtlasErrorCode.UNAUTHORIZED: 401,
    AtlasErrorCode.FORBIDDEN: 403,
    AtlasErrorCode.NOT_FOUND: 404,
    AtlasErrorCode.CONFLICT: 409,
    AtlasErrorCode.VALIDATION_ERROR: 422,
    AtlasErrorCode.RATE_LIMITED: 429,
    AtlasErrorCode.INTERNAL_ERROR: 500,
    AtlasErrorCode.SERVICE_UNAVAILABLE: 503,
}


class AtlasException(Exception):
    """Application exception that maps cleanly to the Atlas response envelope."""

    def __init__(
        self,
        code: AtlasErrorCode,
        message: str,
        details: dict[str, Any] | list[dict[str, Any]] | str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    @property
    def status_code(self) -> int:
        return ERROR_STATUS_CODES[self.code]


def map_exception_to_error_response(exception: AtlasException) -> AtlasErrorResponse:
    """Convert an application exception into the standard API error envelope."""

    return AtlasErrorResponse(
        error=exception.message,
        details=exception.details,
        code=exception.status_code,
    )
