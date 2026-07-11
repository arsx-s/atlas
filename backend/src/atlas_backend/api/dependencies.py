"""FastAPI dependencies for authentication and authorization."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, Request, status

from atlas_backend.auth.service import AuthService
from atlas_backend.core.config import AtlasSettings
from atlas_backend.core.errors import AtlasErrorCode, AtlasException
from atlas_backend.core.security import Permission, PrincipalKind, RequestPrincipal
from atlas_backend.persistence import AtlasLocalStore


def get_settings(request: Request) -> AtlasSettings:
    return request.app.state.settings


def get_store(request: Request) -> AtlasLocalStore:
    return request.app.state.store


def get_auth_service(
    settings: AtlasSettings = Depends(get_settings),
    store: AtlasLocalStore = Depends(get_store),
) -> AuthService:
    return AuthService(settings, store)


async def get_current_user(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> RequestPrincipal:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return RequestPrincipal(
            principal_id="anonymous",
            kind=PrincipalKind.LOCAL_DEVICE,
            permissions=frozenset({Permission.READ_SELF, Permission.READ_PROJECT}),
            device_id=None,
        )
    token = auth_header.removeprefix("Bearer ")
    payload = service.verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return RequestPrincipal(
        principal_id=payload.get("sub", "unknown"),
        kind=PrincipalKind.CLOUD_USER,
        permissions=frozenset({
            Permission.READ_SELF, Permission.WRITE_SELF,
            Permission.READ_PROJECT, Permission.WRITE_PROJECT,
            Permission.RUN_RESEARCH, Permission.MANAGE_SETTINGS,
        }),
        device_id=payload.get("sid"),
    )


async def require_user(
    principal: RequestPrincipal = Depends(get_current_user),
) -> RequestPrincipal:
    if principal.kind != PrincipalKind.CLOUD_USER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return principal

