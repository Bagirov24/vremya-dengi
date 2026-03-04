"""Authentication utilities: JWT token management and password hashing."""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from app.config import settings


# --- Password Hashing ---

def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# --- JWT Token Management ---

def create_access_token(user_id: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    """Create a short-lived JWT access token."""
    return _create_token(
        user_id=user_id,
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
        token_type="access",
        extra_claims=extra_claims,
    )


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived JWT refresh token."""
    return _create_token(
        user_id=user_id,
        expires_delta=timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
        token_type="refresh",
    )


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token. Raises jwt exceptions on failure."""
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )


def _create_token(
    user_id: str,
    expires_delta: timedelta,
    token_type: str = "access",
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Internal helper to create a JWT token."""
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + expires_delta,
        "type": token_type,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


# --- Token Verification Helpers ---

def verify_access_token(token: str) -> Optional[str]:
    """Verify an access token and return user_id or None."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def verify_refresh_token(token: str) -> Optional[str]:
    """Verify a refresh token and return user_id or None."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return None
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def generate_password_reset_token(user_id: str) -> str:
    """Generate a short-lived token for password reset."""
    return _create_token(
        user_id=user_id,
        expires_delta=timedelta(hours=1),
        token_type="password_reset",
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token and return user_id or None."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def generate_email_verification_token(user_id: str) -> str:
    """Generate a token for email verification."""
    return _create_token(
        user_id=user_id,
        expires_delta=timedelta(days=7),
        token_type="email_verify",
    )


def verify_email_verification_token(token: str) -> Optional[str]:
    """Verify an email verification token and return user_id or None."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "email_verify":
            return None
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
