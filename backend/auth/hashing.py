"""
hashing.py — bcrypt password hashing and verification for TeamFlow.

Uses passlib's CryptContext so the scheme can be upgraded in the future
(e.g. argon2) without touching call sites.

Public API:
    hash_password(plain: str) -> str
        Returns a bcrypt hash suitable for storing in User.password_hash.

    verify_password(plain: str, hashed: str) -> bool
        Returns True if `plain` matches the stored `hashed` value.
"""

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the stored bcrypt *hashed* value."""
    return _pwd_context.verify(plain, hashed)
