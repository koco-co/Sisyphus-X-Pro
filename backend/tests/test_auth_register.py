"""测试用户注册功能."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.password import verify_password


class TestUserRegister:
    """测试用户注册 API."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功注册新用户."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "nickname": "测试用户",
            },
        )

        assert response.status_code == 201
        data = response.json()

        # 验证返回的数据结构
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["nickname"] == "测试用户"
        assert data["user"]["provider"] == "email"
        assert "id" in data["user"]
        assert "password_hash" not in data["user"]  # 不返回密码哈希

        # 验证数据库中的用户
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == "test@example.com"
        assert user.nickname == "测试用户"
        assert user.provider == "email"
        assert user.is_active is True
        assert verify_password("password123", user.password_hash)

    @pytest.mark.asyncio
    async def test_register_email_already_exists(self, client: AsyncClient, db: AsyncSession):
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
        assert "Email already registered" in response.json()["detail"]

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

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """测试使用过短密码注册."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",  # 少于8位
                "nickname": "测试用户",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        """测试缺少必填字段."""
        # 缺少 nickname
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 422  # Validation error
