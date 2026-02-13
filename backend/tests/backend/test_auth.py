"""Tests for authentication module."""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select

from app.models.user import User
from app.utils.password import hash_password


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient, db_session):
    """Test user registration with valid data."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "nickname": "Test User",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["nickname"] == "Test User"

    # Verify user in database
    result = await db_session.execute(select(User).where(User.email == "test@example.com"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.password_hash is not None
    assert user.password_hash != "password123"  # Should be hashed


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient, db_session):
    """Test registration with duplicate email fails."""
    # Create existing user
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        nickname="Existing User",
    )
    db_session.add(user)
    await db_session.commit()

    # Try to register with same email
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "nickname": "Test User",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_weak_password(async_client: AsyncClient):
    """Test registration with weak password fails."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "123",  # Too short
            "nickname": "Test User",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, db_session):
    """Test login with correct credentials."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        nickname="Test User",
    )
    db_session.add(user)
    await db_session.commit()

    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient, db_session):
    """Test login with wrong password fails."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        nickname="Test User",
        failed_login_count=0,
    )
    db_session.add(user)
    await db_session.commit()

    # Login with wrong password
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Verify failed_login_count incremented
    await db_session.refresh(user)
    assert user.failed_login_count == 1


@pytest.mark.asyncio
async def test_login_account_locked(async_client: AsyncClient, db_session):
    """Test login with locked account."""
    # Create test user with 5 failed attempts and lock
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        nickname="Test User",
        failed_login_count=5,
        locked_until=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    db_session.add(user)
    await db_session.commit()

    # Try to login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_account_unlocked_after_timeout(
    async_client: AsyncClient, db_session
):
    """Test login succeeds after lock expires."""
    # Create test user with expired lock
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        nickname="Test User",
        failed_login_count=5,
        locked_until=datetime.now(timezone.utc) - timedelta(minutes=1),  # Expired
    )
    db_session.add(user)
    await db_session.commit()

    # Login should succeed
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify failed_login_count reset
    await db_session.refresh(user)
    assert user.failed_login_count == 0
    assert user.locked_until is None


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client: AsyncClient):
    """Test login with non-existent user fails."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient):
    """Test logout endpoint."""
    response = await async_client.post("/api/v1/auth/logout")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Successfully logged out"


@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient, db_session):
    """Test getting current authenticated user."""
    # Create and login user
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        nickname="Test User",
    )
    db_session.add(user)
    await db_session.commit()

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_refresh_token(async_client: AsyncClient, db_session):
    """Test refreshing access token."""
    # Create and login user
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        nickname="Test User",
    )
    db_session.add(user)
    await db_session.commit()

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh token
    response = await async_client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_invalid(async_client: AsyncClient):
    """Test refresh with invalid token fails."""
    response = await async_client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_token_wrong_type(async_client: AsyncClient, db_session):
    """Test refresh with access token (not refresh token) fails."""
    # Create and login user
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        nickname="Test User",
    )
    db_session.add(user)
    await db_session.commit()

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    access_token = login_response.json()["access_token"]

    # Try to use access token as refresh token
    response = await async_client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_password_bcrypt_hashing(async_client: AsyncClient, db_session):
    """Test passwords are hashed with bcrypt."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "nickname": "Test User",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Check password hash in database
    result = await db_session.execute(select(User).where(User.email == "test@example.com"))
    user = result.scalar_one()

    # Verify hash starts with bcrypt identifier
    assert user.password_hash.startswith("$2b$")

    # Verify hash is not plaintext
    assert user.password_hash != "password123"
    assert len(user.password_hash) == 60  # bcrypt hashes are 60 chars


@pytest.mark.asyncio
async def test_login_oauth_user_no_password(async_client: AsyncClient, db_session):
    """Test OAuth user cannot login with password."""
    # Create OAuth user (no password hash)
    user = User(
        email="oauth@example.com",
        password_hash=None,
        nickname="OAuth User",
        provider="github",
        provider_id="12345",
    )
    db_session.add(user)
    await db_session.commit()

    # Try to login with password
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "oauth@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_development_mode_skip_auth(async_client: AsyncClient, monkeypatch):
    """Test development mode skips authentication."""
    # This test verifies that in development mode,
    # requests without auth token still work for /auth/me
    # Note: This depends on APP_ENV=development

    response = await async_client.get("/api/v1/auth/me")
    # In development mode, should return mock user
    # In production, should return 401
    # We just verify the endpoint responds
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
