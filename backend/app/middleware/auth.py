"""JWT authentication middleware and utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.utils.password import verify_password

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,  # Allow optional token for dev mode
)

oauth2_scheme_refresh = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/refresh",
    auto_error=False,
)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token (e.g., {"sub": user_id})
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token.

    Args:
        data: Data to encode in the token (e.g., {"sub": user_id})

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token.

    In development mode (ENVIRONMENT=development), authentication is skipped
    and a mock user is returned for testing purposes.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        Current user object

    Raises:
        HTTPException: If authentication fails or user not found
    """
    # Development mode: Skip authentication
    if settings.ENVIRONMENT == "development":
        # Return a mock user for development
        # In real development, you might want to create a test user in the database
        mock_user = User(
            id=1,
            email="dev@example.com",
            nickname="Dev User",
            provider="email",
            is_active=True,
        )
        return mock_user

    # Production mode: Require authentication
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user ID
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Query user from database
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled"
        )

    return user


async def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Get the current user if authenticated, otherwise return None.

    This is useful for endpoints that work both with and without authentication.

    Args:
        token: JWT token from Authorization header (optional)
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    # Development mode: Return mock user
    if settings.ENVIRONMENT == "development":
        mock_user = User(
            id=1,
            email="dev@example.com",
            nickname="Dev User",
            provider="email",
            is_active=True,
        )
        return mock_user

    # No token provided
    if token is None:
        return None

    # Try to decode token and get user
    try:
        payload = decode_token(token)
        if payload is None:
            return None

        user_id: str | None = payload.get("sub")
        if user_id is None:
            return None

        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        return user
    except (JWTError, ValueError):
        return None


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User | None:
    """Authenticate a user by email and password.

    Args:
        email: User email
        password: Plain text password
        db: Database session

    Returns:
        User object if authentication successful, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not user.password_hash:
        # User registered via OAuth, no password set
        return None

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        # Account is still locked
        return None

    # Verify password
    if not verify_password(password, user.password_hash):
        # Increment failed login count
        user.failed_login_count = (user.failed_login_count or 0) + 1

        # Lock account after 5 failed attempts
        if user.failed_login_count >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)

        await db.commit()
        return None

    # Successful login - reset failed login count and lock
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    return user
