"""Standard Atlas API response envelopes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field


DataT = TypeVar("DataT")


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class AtlasSuccessResponse(BaseModel, Generic[DataT]):
    """Standard successful API response envelope."""

    success: Literal[True] = True
    data: DataT
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utc_now)


class AtlasErrorResponse(BaseModel):
    """Standard failed API response envelope."""

    success: Literal[False] = False
    error: str
    details: dict[str, Any] | list[dict[str, Any]] | str | None = None
    code: int
    timestamp: datetime = Field(default_factory=utc_now)


def create_success_response(data: DataT, meta: dict[str, Any] | None = None) -> AtlasSuccessResponse[DataT]:
    """Create a standard successful API response."""

    return AtlasSuccessResponse[DataT](data=data, meta=meta or {})
