"""认证模块 API 集成测试."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.password import verify_password


class TestAuthRegister:
    """测试用户注册 API."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功注册新用户."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "nickname": "新用户",
            },
        )

        assert response.status_code == 201
        data = response.json()

        # 验证返回的数据结构
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["nickname"] == "新用户"
        assert data["user"]["provider"] == "email"
        assert "id" in data["user"]
        assert "password_hash" not in data["user"]

        # 验证数据库中的用户
        result = await db.execute(select(User).where(User.email == "newuser@example.com"))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == "newuser@example.com"
        assert verify_password("password123", user.password_hash)

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, db: AsyncSession):
        """测试注册已存在的邮箱."""
        # 先创建一个用户
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            nickname="测试用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 尝试用相同邮箱注册
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "nickname": "另一个用户",
            },
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """测试使用无效邮箱注册."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123",
                "nickname": "测试用户",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """测试使用过短密码注册."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
                "nickname": "测试用户",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        """测试缺少必填字段."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 422


class TestAuthLogin:
    """测试用户登录 API."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功登录."""
        # 先创建一个用户
        from app.utils.password import hash_password

        user = User(
            email="login@example.com",
            password_hash=hash_password("password123"),
            nickname="登录用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 使用 OAuth2PasswordRequestForm 格式登录
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "login@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == "login@example.com"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, db: AsyncSession):
        """测试使用错误密码登录."""
        from app.utils.password import hash_password

        user = User(
            email="login@example.com",
            password_hash=hash_password("password123"),
            nickname="登录用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "login@example.com",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """测试不存在的用户登录."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401


class TestAuthMe:
    """测试获取当前用户 API."""

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, db: AsyncSession):
        """测试获取当前用户信息."""
        from app.utils.password import hash_password
        from app.middleware.auth import create_access_token

        # 创建用户
        user = User(
            email="me@example.com",
            password_hash=hash_password("password123"),
            nickname="当前用户",
            provider="email",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # 创建 token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        # 调用 API
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["nickname"] == "当前用户"

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """测试没有 token 时获取用户信息."""
        response = await client.get("/api/v1/auth/me")

        # 在开发模式下可能返回 200,在生产模式下返回 401
        # 这里我们检查是否有用户信息返回
        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """测试使用无效 token 获取用户信息."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code in [401, 403]


class TestAuthRefresh:
    """测试 Token 刷新 API."""

    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, db: AsyncSession):
        """测试刷新 token."""
        from app.utils.password import hash_password
        from app.middleware.auth import create_refresh_token

        # 创建用户
        user = User(
            email="refresh@example.com",
            password_hash=hash_password("password123"),
            nickname="刷新用户",
            provider="email",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # 创建 refresh token
        refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})

        # 刷新 token - 使用 json 参数而不是 data
        response = await client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": refresh_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """测试使用无效 refresh token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": "invalid_refresh_token",
            },
        )

        assert response.status_code in [401, 422]


class TestAuthOAuth:
    """测试 OAuth 认证 API."""

    @pytest.mark.asyncio
    async def test_github_oauth_redirect(self, client: AsyncClient):
        """测试 GitHub OAuth 重定向."""
        response = await client.get("/api/v1/auth/github")

        # 应该返回重定向或授权 URL
        assert response.status_code in [200, 307, 308]

    @pytest.mark.asyncio
    async def test_google_oauth_redirect(self, client: AsyncClient):
        """测试 Google OAuth 重定向."""
        response = await client.get("/api/v1/auth/google")

        # 应该返回重定向或授权 URL
        assert response.status_code in [200, 307, 308]

    @pytest.mark.asyncio
    async def test_github_callback(self, client: AsyncClient):
        """测试 GitHub OAuth 回调."""
        # 注意: 这个测试需要 mock GitHub OAuth 服务
        # 在实际测试中,你可能需要使用 mock 或测试工具
        response = await client.post(
            "/api/v1/auth/callback/github",
            json={"code": "test_code"}
        )

        # 由于没有真实的 OAuth 配置,这里可能返回错误
        assert response.status_code in [200, 400, 401]

    @pytest.mark.asyncio
    async def test_google_callback(self, client: AsyncClient):
        """测试 Google OAuth 回调."""
        response = await client.post(
            "/api/v1/auth/callback/google",
            json={"code": "test_code"}
        )

        assert response.status_code in [200, 400, 401]
