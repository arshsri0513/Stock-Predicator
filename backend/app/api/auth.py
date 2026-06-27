"""
Authentication API routes: /auth/signup, /auth/login, /auth/me.

Same thin-route pattern as the rest of the project. Password hashing and
JWT logic live in app.core.security; database queries use the session
dependency from app.core.database (Phase 9).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.models.user import User
from app.schemas.auth_schemas import SignupRequest, LoginRequest, TokenResponse, UserResponse

router = APIRouter()

# HTTPBearer (rather than OAuth2PasswordBearer) gives /docs a simple
# "paste your token" Authorize dialog instead of a username/password form.
#
# Why the change: OAuth2PasswordBearer's built-in docs form submits
# credentials as form-encoded data with a field literally named
# "username" -- but our /auth/login endpoint expects JSON matching our
# LoginRequest schema ({"email": ..., "password": ...}). Those two never
# matched, which is why login-through-the-docs-form silently failed even
# though the same credentials worked perfectly through POST /auth/login
# directly. HTTPBearer sidesteps the mismatch entirely: you log in via
# the real endpoint, copy the real token, and paste it directly -- exactly
# what our actual frontend will do later, so this is also more
# representative of real usage, not just a docs-UI workaround.
bearer_scheme = HTTPBearer()



@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account. The password is hashed before storage --
    we never store or log the plain-text password anywhere, even
    temporarily.
    """
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = User(email=request.email, hashed_password=hash_password(request.password))
    db.add(user)
    db.commit()
    db.refresh(user)  # populates the auto-generated id/created_at from the database

    return UserResponse(id=str(user.id), email=user.email)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Verify credentials and issue a JWT. We return the SAME generic error
    message whether the email doesn't exist OR the password is wrong --
    revealing "that email isn't registered" vs "wrong password" would let
    an attacker enumerate which emails have accounts on this system, a
    real information leak even though it seems like a minor convenience.
    """
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = create_access_token(user_id=str(user.id))
    return TokenResponse(access_token=token)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: extracts and validates the JWT from the
    Authorization header, then loads the corresponding user from the
    database. Any route that needs "who is making this request" depends
    on this function -- e.g. Depends(get_current_user) -- rather than
    re-implementing token checking in every protected route.
    """
    token = credentials.credentials
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists.")

    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user's info. This is also our
    first PROTECTED route -- it requires a valid token to access at all,
    demonstrating the get_current_user dependency in action. Phase 13's
    watchlist routes will use this same pattern.
    """
    return UserResponse(id=str(current_user.id), email=current_user.email)
