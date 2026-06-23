"""
dependencies.py — FastAPI dependency for authenticated routes.

Provides:
    get_current_user(token, db) -> User
        Decodes the Bearer JWT from the Authorization header, validates the
        token type is "access", looks up the User row, and returns it.
        Raises HTTP 401 on any failure so the error message is always identical
        (prevents user enumeration via timing differences).

Usage in a router:
    from auth.dependencies import get_current_user
    from models import User

    @router.get("/protected")
    def protected(current_user: User = Depends(get_current_user)):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from auth.jwt_utils import decode_token
from database import get_db
from models import User

# tokenUrl points to the login endpoint so FastAPI's OpenAPI UI can drive the
# Authorize flow.  The CLI and future frontend both send the token manually,
# so this is cosmetic for the docs only.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve the Bearer token to a User ORM object.

    Steps:
      1. Decode and validate the JWT (signature + expiry).
      2. Confirm token type is "access" (reject refresh tokens used here).
      3. Look up the user by the "sub" claim (user_id UUID string).
      4. Return the User — or raise 401 if any step fails.
    """
    payload = decode_token(token)

    # Reject refresh tokens presented as access tokens.
    if payload.get("type") != "access":
        raise _CREDENTIALS_EXCEPTION

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise _CREDENTIALS_EXCEPTION

    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise _CREDENTIALS_EXCEPTION

    return user
