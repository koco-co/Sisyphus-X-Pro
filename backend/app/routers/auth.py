"""Authentication router."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from app.services import get_github_oauth_service, get_google_oauth_service
from app.utils.password import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user with email and password.

    自动登录并返回 JWT token。

    Args:
        user_in: User registration data
        db: Database session

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: If email already registered
    """
    # 检查邮箱是否已注册
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # 创建新用户
    user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        nickname=user_in.nickname,
        provider="email",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 自动登录并生成 JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user with email and password.

    Uses OAuth2 password flow for compatibility with OpenAPI documentation.

    Args:
        form_data: OAuth2 password form data (username=email, password)
        db: Database session

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, user=UserResponse.model_validate(user))


@router.post("/login/json", response_model=Token)
async def login_json(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user with email and password (JSON format).

    Alternative login endpoint that accepts JSON instead of form data.

    Args:
        user_in: User login data (email, password)
        db: Database session

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user = await authenticate_user(user_in.email, user_in.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user (from dependency)

    Returns:
        Current user information
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout():
    """Logout current user.

    Note: JWT tokens are stateless. Real logout requires token blacklisting
    with Redis or short token expiration times. This endpoint is a placeholder
    for client-side token deletion.

    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}


# OAuth endpoints


@router.get("/github")
async def github_login():
    """Initiate GitHub OAuth login flow.

    Returns:
        Redirect to GitHub authorization page

    Raises:
        HTTPException: If GitHub OAuth not configured
    """
    try:
        oauth_service = get_github_oauth_service()
        redirect_uri = f"{settings.OAUTH_REDIRECT_URL}/github/callback"
        auth_url, state = oauth_service.get_authorization_url(redirect_uri)

        # In production, store state in Redis with expiration
        # For now, return it in the response (not ideal but works for development)
        return {
            "authorization_url": auth_url,
            "state": state,
            "message": "Redirect to GitHub to authorize",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e),
        ) from e


@router.get("/github/callback")
async def github_callback(
    code: Annotated[str, Query(...)],
    state: Annotated[str, Query(...)],
    db: AsyncSession = Depends(get_db),
):
    """Handle GitHub OAuth callback.

    Args:
        code: Authorization code from GitHub
        state: State parameter for CSRF protection
        db: Database session

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: If authentication fails
    """
    try:
        oauth_service = get_github_oauth_service()
        redirect_uri = f"{settings.OAUTH_REDIRECT_URL}/github/callback"

        # Exchange code for access token
        access_token = await oauth_service.get_access_token(code, redirect_uri)

        # Get user info from GitHub
        user_info = await oauth_service.get_user_info(access_token)

        # Get or create user
        user = await oauth_service.get_or_create_user(user_info, db)

        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires,
        )

        return Token(access_token=jwt_token, user=UserResponse.model_validate(user))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"GitHub authentication failed: {str(e)}",
        ) from e


@router.get("/google")
async def google_login():
    """Initiate Google OAuth login flow.

    Returns:
        Redirect to Google authorization page

    Raises:
        HTTPException: If Google OAuth not configured
    """
    try:
        oauth_service = get_google_oauth_service()
        redirect_uri = f"{settings.OAUTH_REDIRECT_URL}/google/callback"
        auth_url, state = oauth_service.get_authorization_url(redirect_uri)

        return {
            "authorization_url": auth_url,
            "state": state,
            "message": "Redirect to Google to authorize",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e),
        ) from e


@router.get("/google/callback")
async def google_callback(
    code: Annotated[str, Query(...)],
    state: Annotated[str, Query(...)],
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback.

    Args:
        code: Authorization code from Google
        state: State parameter for CSRF protection
        db: Database session

    Returns:
        JWT access token and user information

    Raises:
        HTTPException: If authentication fails
    """
    try:
        oauth_service = get_google_oauth_service()
        redirect_uri = f"{settings.OAUTH_REDIRECT_URL}/google/callback"

        # Exchange code for access token
        access_token = await oauth_service.get_access_token(code, redirect_uri)

        # Get user info from Google
        user_info = await oauth_service.get_user_info(access_token)

        # Get or create user
        user = await oauth_service.get_or_create_user(user_info, db)

        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires,
        )

        return Token(access_token=jwt_token, user=UserResponse.model_validate(user))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {str(e)}",
        ) from e
