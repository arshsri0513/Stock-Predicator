"""
Security utilities: password hashing and JWT creation/verification.

Centralized here for the same reason every other cross-cutting concern in
this project lives in one file -- if we ever need to change our hashing
algorithm or token expiry policy, there's exactly one place to do it.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# CryptContext manages the hashing algorithm for us. We specify bcrypt
# explicitly -- it's slow BY DESIGN (a deliberate security property: slow
# hashing makes brute-force password guessing impractically expensive),
# and is the industry-standard choice for password storage.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    One-way hash a plain-text password for storage. The original password
    is never recoverable from the hash -- this is mathematically
    irreversible by design, not just "hard to reverse."
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check whether a plain-text password matches a stored hash, WITHOUT
    ever decrypting the hash (because it can't be decrypted) -- bcrypt
    re-hashes the candidate password the same way and compares the results.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
    """
    Create a signed JWT for a given user ID. The token's payload ("claims")
    contains:
    - sub (subject): the user's ID -- this is what we trust to know "who
      is making this request" on every future call
    - exp (expiry): a timestamp after which the token is no longer valid,
      forcing re-login -- this limits how long a stolen token would remain
      useful if it were ever leaked

    The token is signed with our JWT_SECRET_KEY (from .env, never
    committed to git -- see Phase 2's .env setup). Anyone with that secret
    could forge valid tokens, which is exactly why it must stay private.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """
    Verify a token's signature and expiry, returning the user ID it
    belongs to if valid, or None if the token is invalid/expired/tampered.

    Why return None instead of raising here? This function is a low-level
    utility -- deciding HOW to respond to an invalid token (401 Unauthorized,
    redirect to login, etc.) is the API layer's job, not this one's.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
