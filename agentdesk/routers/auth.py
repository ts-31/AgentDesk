"""
routers/auth.py — Authentication endpoints for AgentDesk.

Endpoints:
    POST /auth/login    — Verify email + password; issue access + refresh tokens.
    POST /auth/refresh  — Exchange a valid refresh token for a new access token.
    POST /auth/logout   — Stateless: client discards its tokens. No server state.

Design notes:
  - Login errors always return the same 401 message regardless of whether
    the email or password was wrong (prevents user enumeration).
  - Refresh tokens are stateless JWTs. Revocation support (blocklist table)
    can be added in a future phase without changing this interface.
  - Logout is a no-op on the server side for stateless JWTs — the client
    is responsible for discarding the tokens.  The endpoint exists so that
    a future DB-backed revocation layer can be added transparently.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.hashing import verify_password
from auth.jwt_utils import create_access_token, create_refresh_token, decode_token
from database import get_db
from models import User
from schemas.auth import LoginRequest, RefreshRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

# Identical message for all login failures — prevents user enumeration.
_LOGIN_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password.",
    headers={"WWW-Authenticate": "Bearer"},
)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email + password.

    Returns an access token (24 h) and a refresh token (7 days) on success.
    Always returns HTTP 401 on failure, regardless of which field was wrong.
    """
    user = db.query(User).filter(User.email == request.email).first()

    # Check user exists, has a password set, and the password matches.
    if not user or not user.password_hash or not verify_password(request.password, user.password_hash):
        logger.warning("Failed login attempt for email: %s", request.email)
        raise _LOGIN_ERROR

    access_token = create_access_token(
        user_id=str(user.user_id),
        customer_id=str(user.customer_id),
        email=user.email,
        role=user.role,
    )
    refresh_token = create_refresh_token(user_id=str(user.user_id))

    logger.info("Successful login for user_id=%s", user.user_id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a fresh access token.

    The refresh token is decoded and validated (signature + expiry + type).
    The user is re-fetched from the DB so that any role/customer changes are
    reflected in the new access token immediately.
    """
    _token_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(request.refresh_token)

    if payload.get("type") != "refresh":
        raise _token_error

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise _token_error

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise _token_error

    new_access_token = create_access_token(
        user_id=str(user.user_id),
        customer_id=str(user.customer_id),
        email=user.email,
        role=user.role,
    )
    # Reuse the existing refresh token — it retains its original expiry.
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=request.refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    """
    Stateless logout — instructs the client to discard its tokens.

    No server-side state is changed. A future revocation layer can be
    added here without breaking existing clients.
    """
    return None
