"""
Lightweight security utilities for GeoSpark.

Provides minimal authentication, token validation, and input sanitization
so the API can run without full security infrastructure.
"""

from __future__ import annotations

import re
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


_bearer = HTTPBearer(auto_error=False)


class SecurityManager:
    """Minimal security manager for demo/runtime purposes."""

    def __init__(self) -> None:
        self.security_policies: Dict[str, Dict[str, Any]] = {
            "input_validation": {"enabled": True},
            "authentication": {"enabled": True},
        }
        self._active_tokens: Dict[str, Dict[str, Any]] = {}

    def sanitize_input(self, input_text: Optional[str]) -> str:
        """Basic sanitization: strip control chars and trim whitespace."""
        if input_text is None:
            return ""
        # Remove null bytes and control characters (except whitespace)
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", str(input_text))
        return sanitized.strip()

    async def scan_input(
        self, input_text: str, input_type: str, client_ip: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Lightweight scan for obvious malicious patterns."""
        sanitized = self.sanitize_input(input_text)

        patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b",
        ]

        for pattern in patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                return False, "", {
                    "status": "blocked",
                    "reason": "malicious_pattern",
                    "input_type": input_type,
                }

        return True, sanitized, {"status": "clean", "input_type": input_type}

    async def authenticate_user(
        self, credentials: Dict[str, Any], client_ip: str
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Accept any non-empty credentials and issue a short-lived token."""
        username = credentials.get("username")
        password = credentials.get("password")

        if not username or not password:
            return False, None, {"error": "Missing credentials"}

        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        self._active_tokens[token] = {
            "user_id": username,
            "expires_at": expires_at,
            "client_ip": client_ip,
        }
        return True, token, {"user_id": username, "expires_at": expires_at.isoformat()}

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate token and return user context if valid."""
        if not token:
            return None

        record = self._active_tokens.get(token)
        if not record:
            return None

        expires_at = record.get("expires_at")
        if isinstance(expires_at, datetime) and expires_at < datetime.utcnow():
            self._active_tokens.pop(token, None)
            return None

        return {
            "user_id": record.get("user_id"),
            "role": "user",
            "expires_at": expires_at.isoformat() if isinstance(expires_at, datetime) else None,
        }


security_manager = SecurityManager()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Dict[str, Any]:
    """FastAPI dependency for retrieving the current user."""
    if credentials is None or not credentials.credentials:
        return {"user_id": "anonymous", "role": "guest"}

    user = security_manager.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user
