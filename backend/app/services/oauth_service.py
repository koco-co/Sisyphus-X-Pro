"""OAuth authentication service for GitHub and Google."""

import secrets
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User


class OAuthService:
    """Service for handling OAuth authentication flows."""

    def __init__(self, provider: str, client_id: str, client_secret: str):
        """Initialize OAuth service.

        Args:
            provider: OAuth provider name (github or google)
            client_id: OAuth client ID
            client_secret: OAuth client secret
        """
        self.provider = provider
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(self, redirect_uri: str, scope: str | None = None) -> tuple[str, str]:
        """Generate OAuth authorization URL with state parameter.

        Args:
            redirect_uri: Callback URL after authorization
            scope: OAuth permissions scope

        Returns:
            Tuple of (authorization_url, state_token)
        """
        # Generate secure state token for CSRF protection
        state = secrets.token_urlsafe(32)

        if self.provider == "github":
            auth_url = "https://github.com/login/oauth/authorize"
            params = {
                "client_id": self.client_id,
                "redirect_uri": redirect_uri,
                "scope": scope or "user:email",
                "state": state,
            }
        elif self.provider == "google":
            auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
            params = {
                "client_id": self.client_id,
                "redirect_uri": redirect_uri,
                "scope": scope or "openid email profile",
                "response_type": "code",
                "state": state,
            }
        else:
            raise ValueError(f"Unsupported OAuth provider: {self.provider}")

        url = f"{auth_url}?{urlencode(params)}"
        return url, state

    async def get_access_token(self, code: str, redirect_uri: str) -> str:
        """Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Callback URL used in authorization

        Returns:
            Access token string

        Raises:
            HTTPException: If token exchange fails
        """
        if self.provider == "github":
            token_url = "https://github.com/login/oauth/access_token"
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            }
            headers = {"Accept": "application/json"}
        elif self.provider == "google":
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
        else:
            raise ValueError(f"Unsupported OAuth provider: {self.provider}")

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()

        if self.provider == "github":
            return token_data["access_token"]
        else:  # google
            return token_data["access_token"]

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """Fetch user information using access token.

        Args:
            access_token: OAuth access token

        Returns:
            Dictionary with user information (email, name, avatar, etc.)

        Raises:
            HTTPException: If user info request fails
        """
        if self.provider == "github":
            user_url = "https://api.github.com/user"
            headers = {"Authorization": f"Bearer {access_token}"}
        elif self.provider == "google":
            user_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            raise ValueError(f"Unsupported OAuth provider: {self.provider}")

        async with httpx.AsyncClient() as client:
            response = await client.get(user_url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_or_create_user(
        self, user_info: dict[str, Any], db: AsyncSession
    ) -> User:
        """Get existing user or create new one from OAuth info.

        Args:
            user_info: User information from OAuth provider
            db: Database session

        Returns:
            User instance
        """
        # Extract provider-specific user ID and email
        if self.provider == "github":
            provider_id = str(user_info.get("id"))
            email = user_info.get("email")
            name = user_info.get("name") or user_info.get("login")
            avatar = user_info.get("avatar_url")
        elif self.provider == "google":
            provider_id = user_info.get("id")
            email = user_info.get("email")
            name = user_info.get("name")
            avatar = user_info.get("picture")
        else:
            raise ValueError(f"Unsupported OAuth provider: {self.provider}")

        # Check if user exists by provider_id
        result = await db.execute(
            select(User).where(
                User.provider == self.provider, User.provider_id == provider_id
            )
        )
        user = result.scalar_one_or_none()

        if user:
            # Update last login
            user.last_login_at = datetime.now(timezone.utc)
        else:
            # Check if email already exists with different provider
            if email:
                result = await db.execute(select(User).where(User.email == email))
                existing_email_user = result.scalar_one_or_none()
                if existing_email_user:
                    # Link OAuth to existing account
                    user = existing_email_user
                    user.provider = self.provider
                    user.provider_id = provider_id
                    user.last_login_at = datetime.now(timezone.utc)
                    if avatar and not user.avatar:
                        user.avatar = avatar
                else:
                    # Create new user
                    user = User(
                        email=email or f"{self.provider}_{provider_id}@placeholder",
                        nickname=name or f"{self.provider}_user",
                        avatar=avatar,
                        provider=self.provider,
                        provider_id=provider_id,
                        password_hash=None,  # OAuth users don't have password
                        is_active=True,
                    )
                    db.add(user)

        await db.commit()
        await db.refresh(user)
        # User is guaranteed to exist after this method (either found or created)
        assert user is not None  # Type guard for Pyright
        return user


def get_github_oauth_service() -> OAuthService:
    """Get GitHub OAuth service instance.

    Returns:
        OAuthService configured for GitHub

    Raises:
        ValueError: If GitHub OAuth credentials not configured
    """
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise ValueError("GitHub OAuth credentials not configured")
    return OAuthService(
        provider="github",
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
    )


def get_google_oauth_service() -> OAuthService:
    """Get Google OAuth service instance.

    Returns:
        OAuthService configured for Google

    Raises:
        ValueError: If Google OAuth credentials not configured
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise ValueError("Google OAuth credentials not configured")
    return OAuthService(
        provider="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    )
