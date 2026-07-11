"""Authentication and authorization boundary contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from atlas_backend.core.errors import AtlasErrorCode, AtlasException


class PrincipalKind(StrEnum):
    """Supported authenticated principal types."""

    LOCAL_DEVICE = "local_device"
    CLOUD_USER = "cloud_user"
    SYSTEM = "system"


class Permission(StrEnum):
    """Initial permission set for API boundary checks."""

    READ_SELF = "read:self"
    WRITE_SELF = "write:self"
    READ_PROJECT = "read:project"
    WRITE_PROJECT = "write:project"
    RUN_RESEARCH = "run:research"
    MANAGE_SETTINGS = "manage:settings"


class RequestPrincipal(BaseModel):
    """Authenticated caller context for local or cloud API requests."""

    principal_id: str
    kind: PrincipalKind
    permissions: frozenset[Permission] = Field(default_factory=frozenset)
    device_id: str | None = None

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions


def require_cloud_user(principal: RequestPrincipal) -> None:
    """Require an authenticated Atlas cloud user for cloud-only features."""

    if principal.kind != PrincipalKind.CLOUD_USER:
        raise AtlasException(
            AtlasErrorCode.UNAUTHORIZED,
            "Cloud authentication is required for this operation.",
        )


def require_permission(principal: RequestPrincipal, permission: Permission) -> None:
    """Require a permission from the authenticated principal."""

    if not principal.has_permission(permission):
        raise AtlasException(
            AtlasErrorCode.FORBIDDEN,
            "The authenticated principal does not have permission for this operation.",
            details={"permission": permission.value},
        )
