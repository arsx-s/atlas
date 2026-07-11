"""Authentication service."""

from __future__ import annotations

import base64
import json
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from atlas_backend.core.config import AtlasSettings
from atlas_backend.persistence import AtlasLocalStore


@dataclass(slots=True)
class AuthTokens:
    access_token: str
    refresh_token: str
    expires_at: str


class AuthService:
    def __init__(self, settings: AtlasSettings, store: AtlasLocalStore) -> None:
        self.settings = settings
        self.store = store
        self._jwt_secret = settings.jwt_secret or secrets.token_urlsafe(48)

    def _hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 210_000)
        return f"pbkdf2_sha256${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        _, salt_b64, digest_b64 = stored_hash.split("$", 2)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 210_000)
        return hmac.compare_digest(expected, actual)

    def register_user(self, email: str, password: str, display_name: str | None = None) -> dict[str, Any]:
        user = {
            "user_id": str(uuid4()),
            "email": email.lower().strip(),
            "password_hash": self._hash_password(password),
            "display_name": display_name or email.split("@", 1)[0],
            "email_verified": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.store.upsert_user(user)
        return user

    def verify_credentials(self, email: str, password: str) -> dict[str, Any] | None:
        user = self.store.get_user_by_email(email.lower().strip())
        if not user or not self._verify_password(password, user["password_hash"]):
            return None
        return user

    def issue_tokens(self, user: dict[str, Any], device_name: str = "Desktop") -> AuthTokens:
        session_id = str(uuid4())
        device_id = str(uuid4())
        refresh_token = secrets.token_urlsafe(48)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        access_token = self._encode_jwt({
            "sub": user["user_id"],
            "email": user["email"],
            "sid": session_id,
            "exp": expires_at.timestamp(),
            "iat": datetime.now(timezone.utc).timestamp(),
        })
        self.store.upsert_device({
            "device_id": device_id,
            "user_id": user["user_id"],
            "name": device_name,
            "last_seen_at": datetime.now(timezone.utc).isoformat(),
            "refresh_token": refresh_token,
            "revoked": 0,
        })
        self.store.upsert_session({
            "session_id": session_id,
            "user_id": user["user_id"],
            "device_id": device_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at.isoformat(),
            "revoked": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return AuthTokens(access_token=access_token, refresh_token=refresh_token, expires_at=expires_at.isoformat())

    def verify_token(self, access_token: str) -> dict[str, Any] | None:
        try:
            parts = access_token.split(".")
            if len(parts) != 3:
                return None
            encoded_header, encoded_payload, signature = parts
            signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
            expected = hmac.new(self._jwt_secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
            actual = self._b64url_decode(signature)
            if not hmac.compare_digest(expected, actual):
                return None
            payload = json.loads(base64.urlsafe_b64decode(encoded_payload + "==").decode("utf-8"))
            if payload.get("exp", 0) < datetime.now(timezone.utc).timestamp():
                return None
            return payload
        except Exception:
            return None

    @staticmethod
    def _b64url_decode(data: str) -> bytes:
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    def _encode_jwt(self, payload: dict[str, Any]) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        encoded_header = self._b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        encoded_payload = self._b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        signature = hmac.new(self._jwt_secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        return f"{encoded_header}.{encoded_payload}.{self._b64url(signature)}"

    @staticmethod
    def _b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    def refresh(self, refresh_token: str) -> AuthTokens | None:
        session = self.store.get_session_by_refresh_token(refresh_token)
        if not session or int(session["revoked"]) == 1:
            return None
        user = self.store.get_user_by_id(session["user_id"])
        if not user:
            return None
        return self.issue_tokens(user)

    def revoke_session(self, refresh_token: str) -> bool:
        session = self.store.get_session_by_refresh_token(refresh_token)
        if not session:
            return False
        self.store.revoke_session(session["session_id"])
        return True
