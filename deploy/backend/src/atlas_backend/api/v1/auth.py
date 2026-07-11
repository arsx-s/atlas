"""Authentication routes."""

from __future__ import annotations

from typing import Any

from atlas_backend.core.errors import AtlasErrorCode, AtlasException
from atlas_backend.core.responses import create_success_response
from atlas_backend.auth.service import AuthService
from atlas_backend.persistence import AtlasLocalStore


def create_auth_router(settings: Any, store: AtlasLocalStore | None = None) -> Any:
    try:
        from fastapi import APIRouter, Depends, Response
    except ImportError as error:
        raise RuntimeError("FastAPI is required to create Atlas API routers.") from error

    service = AuthService(settings, store or AtlasLocalStore(settings.sqlite_path or "atlas-local.db"))
    router = APIRouter(tags=["auth"])

    from atlas_backend.api.dependencies import get_current_user
    from atlas_backend.core.security import RequestPrincipal

    @router.post("/auth/register")
    async def register(payload: dict[str, Any]) -> Any:
        if not payload.get("email") or not payload.get("password"):
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "Email and password are required.")
        existing = service.store.get_user_by_email(payload["email"].lower().strip())
        if existing:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "Email already registered.")
        user = service.register_user(payload["email"], payload["password"], payload.get("display_name"))
        return create_success_response({"user_id": user["user_id"], "email": user["email"], "status": "registered"})

    @router.post("/auth/login")
    async def login(payload: dict[str, Any], response: Response) -> Any:
        user = service.verify_credentials(payload.get("email", ""), payload.get("password", ""))
        if not user:
            raise AtlasException(AtlasErrorCode.UNAUTHORIZED, "Invalid email or password.")
        tokens = service.issue_tokens(user, payload.get("device_name", "Desktop"))
        response.set_cookie(
            "atlas_refresh_token", tokens.refresh_token,
            httponly=True, secure=bool(settings.https_only),
            samesite="lax", max_age=2592000,
        )
        return create_success_response({"access_token": tokens.access_token, "expires_at": tokens.expires_at})

    @router.post("/auth/refresh")
    async def refresh(payload: dict[str, Any], response: Response) -> Any:
        token = payload.get("refresh_token", "")
        if not token:
            raise AtlasException(AtlasErrorCode.VALIDATION_ERROR, "Refresh token is required.")
        tokens = service.refresh(token)
        if not tokens:
            raise AtlasException(AtlasErrorCode.UNAUTHORIZED, "Invalid or expired refresh token.")
        response.set_cookie(
            "atlas_refresh_token", tokens.refresh_token,
            httponly=True, secure=bool(settings.https_only),
            samesite="lax", max_age=2592000,
        )
        return create_success_response({"access_token": tokens.access_token, "expires_at": tokens.expires_at})

    @router.post("/auth/logout")
    async def logout(payload: dict[str, Any]) -> Any:
        token = payload.get("refresh_token", "")
        if token:
            service.revoke_session(token)
        return create_success_response({"status": "logged_out"})

    @router.get("/auth/me")
    async def me(principal: RequestPrincipal = Depends(get_current_user)) -> Any:
        if principal.kind.value == "local_device":
            return create_success_response({"authenticated": False, "principal": "anonymous"})
        user = service.store.get_user_by_id(principal.principal_id)
        if not user:
            raise AtlasException(AtlasErrorCode.NOT_FOUND, "User not found.")
        return create_success_response({
            "authenticated": True,
            "user_id": user["user_id"],
            "email": user["email"],
            "display_name": user.get("display_name", ""),
        })

    return router
