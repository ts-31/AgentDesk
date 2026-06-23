"""
jwt_utils.py — JWT creation and decoding for TeamFlow.

Access token payload:
    {
        "sub":         "<user_id>",
        "customer_id": "<customer_id>",
        "email":       "user@example.com",
        "role":        "Member | Admin | Guest",
        "type":        "access",
        "iat":         <issued-at epoch>,
        "exp":         <expiry epoch>
    }

Refresh token payload (minimal — no sensitive claims):
    {
        "sub":  "<user_id>",
        "type": "refresh",
        "iat":  <issued-at epoch>,
        "exp":  <expiry epoch>
    }

Public API:
    create_access_token(user_id, customer_id, email, role) -> str
    create_refresh_token(user_id) -> str
    decode_token(token) -> dict   — raises HTTPException 401 on any failure
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from fastapi import HTTPException, status

from config import settings


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(
    user_id: str,
    customer_id: str,
    email: str,
    role: str,
) -> str:
    """Encode a signed access JWT with full user claims."""
    now = _utcnow()
    payload = {
        "sub": user_id,
        "customer_id": customer_id,
        "email": email,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    """Encode a signed refresh JWT containing only the user identity."""
    now = _utcnow()
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """
    Validate signature and expiry; return the decoded payload dict.

    Raises:
        HTTPException 401 — on invalid signature, expired token, or any
                            jose decoding error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise credentials_exception
