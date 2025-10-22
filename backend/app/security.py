"""Security helpers for password hashing and JWT handling."""
from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt

from .config import get_settings


_HASH_NAME = "sha256"
_ITERATIONS = 390000
_SALT_SIZE = 16


def _pbkdf2(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(_HASH_NAME, password.encode("utf-8"), salt, _ITERATIONS)


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC."""

    salt = os.urandom(_SALT_SIZE)
    derived = _pbkdf2(password, salt)
    return "$.".join([
        _HASH_NAME,
        str(_ITERATIONS),
        salt.hex(),
        derived.hex(),
    ])


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""

    algo, iterations, salt_hex, hash_hex = stored_hash.split("$.")
    if algo != _HASH_NAME:
        raise ValueError("Unsupported hash algorithm")
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)
    derived = hashlib.pbkdf2_hmac(algo, password.encode("utf-8"), salt, int(iterations))
    return hmac.compare_digest(expected, derived)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Generate a signed JWT access token."""

    settings = get_settings()
    expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload: Dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.access_token_secret, algorithm="HS256")


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""

    settings = get_settings()
    return jwt.decode(token, settings.access_token_secret, algorithms=["HS256"])


__all__ = ["hash_password", "verify_password", "create_access_token", "decode_token"]
