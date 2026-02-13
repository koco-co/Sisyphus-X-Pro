"""全局参数模块 API 集成测试."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.global_param import GlobalParam
from app.utils.password import hash_password


class TestGlobalParamsList:
    """测试全局参数列表 API."""

    @pytest.mark.asyncio
    async def test_list_global_params_empty(self, client: AsyncClient, db: AsyncSession):
        """测试空全局参数列表."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/global-params",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_list_global_params_with_data(self, client: AsyncClient, db: AsyncSession):
        """测试有数据的全局参数列表."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建全局参数
        param = GlobalParam(
            name="base_url",
            function_name="get_base_url",
            description="获取基础 URL",
            code="def get_base_url(): return 'https://api.example.com'",
            is_enabled=True,
        )
        db.add(param)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/global-params",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "base_url"

    @pytest.mark.asyncio
    async def test_list_global_params_filter_enabled(self, client: AsyncClient, db: AsyncSession):
        """测试过滤启用的全局参数."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建启用的参数
        param1 = GlobalParam(
            name="enabled_param",
            function_name="enabled_func",
            description="启用的参数",
            code="def enabled_func(): pass",
            is_enabled=True,
        )
        # 创建禁用的参数
        param2 = GlobalParam(
            name="disabled_param",
            function_name="disabled_func",
            description="禁用的参数",
            code="def disabled_func(): pass",
            is_enabled=False,
        )
        db.add_all([param1, param2])
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/global-params?is_enabled=true",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # 应该只返回启用的参数
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "enabled_param"
        assert data["items"][0]["is_enabled"] is True


class TestGlobalParamsCreate:
    """测试创建全局参数 API."""

    @pytest.mark.asyncio
    async def test_create_global_param_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功创建全局参数."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/global-params",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "timestamp",
                "function_name": "get_timestamp",
                "description": "获取当前时间戳",
                "code": "import time\ndef get_timestamp(): return int(time.time())",
                "is_enabled": True,
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "timestamp"
        assert data["function_name"] == "get_timestamp"
        assert data["is_enabled"] is True
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_global_param_duplicate_name(self, client: AsyncClient, db: AsyncSession):
        """测试创建重名全局参数."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 先创建一个参数
        param = GlobalParam(
            name="duplicate_param",
            function_name="func1",
            description="第一个参数",
            code="def func1(): pass",
            is_enabled=True,
        )
        db.add(param)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        # 尝试创建同名参数
        response = await client.post(
            "/api/v1/global-params",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "duplicate_param",
                "function_name": "func2",
                "description": "第二个参数",
                "code": "def func2(): pass",
            }
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_global_param_missing_fields(self, client: AsyncClient, db: AsyncSession):
        """测试缺少必填字段."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/global-params",
            headers={"Authorization": f"Bearer {token}"},
            json={"description": "不完整的参数"}
        )

        assert response.status_code == 422


class TestGlobalParamsUpdate:
    """测试更新全局参数 API."""

    @pytest.mark.asyncio
    async def test_update_global_param_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功更新全局参数."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建参数
        param = GlobalParam(
            name="old_name",
            function_name="old_func",
            description="旧描述",
            code="def old_func(): pass",
            is_enabled=True,
        )
        db.add(param)
        await db.commit()
        await db.refresh(param)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            f"/api/v1/global-params/{param.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "new_name",
                "description": "新描述",
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "new_name"
        assert data["description"] == "新描述"

    @pytest.mark.asyncio
    async def test_update_global_param_not_found(self, client: AsyncClient, db:AsyncSession):
        """测试更新不存在的全局参数."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            "/api/v1/global-params/99999",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "新名称"}
        )

        assert response.status_code == 404


class TestGlobalParamsDelete:
    """测试删除全局参数 API."""

    @pytest.mark.asyncio
    async def test_delete_global_param_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功删除全局参数."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建参数
        param = GlobalParam(
            name="to_delete",
            function_name="delete_func",
            description="待删除的参数",
            code="def delete_func(): pass",
            is_enabled=True,
        )
        db.add(param)
        await db.commit()
        await db.refresh(param)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            f"/api/v1/global-params/{param.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # 验证参数已被删除
        result = await db.execute(select(GlobalParam).where(GlobalParam.id == param.id))
        param = result.scalar_one_or_none()
        assert param is None

    @pytest.mark.asyncio
    async def test_delete_global_param_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试删除不存在的全局参数."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            "/api/v1/global-params/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestGlobalParamsToggle:
    """测试全局参数启用/禁用 API."""

    @pytest.mark.asyncio
    async def test_toggle_global_param_enable(self, client: AsyncClient, db: AsyncSession):
        """测试启用全局参数."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建禁用的参数
        param = GlobalParam(
            name="disabled_param",
            function_name="disabled_func",
            description="禁用的参数",
            code="def disabled_func(): pass",
            is_enabled=False,
        )
        db.add(param)
        await db.commit()
        await db.refresh(param)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.patch(
            f"/api/v1/global-params/{param.id}/toggle?is_enabled=true",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_enabled"] is True

    @pytest.mark.asyncio
    async def test_toggle_global_param_disable(self, client: AsyncClient, db: AsyncSession):
        """测试禁用全局参数."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建启用的参数
        param = GlobalParam(
            name="enabled_param",
            function_name="enabled_func",
            description="启用的参数",
            code="def enabled_func(): pass",
            is_enabled=True,
        )
        db.add(param)
        await db.commit()
        await db.refresh(param)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.patch(
            f"/api/v1/global-params/{param.id}/toggle?is_enabled=false",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_enabled"] is False

    @pytest.mark.asyncio
    async def test_toggle_global_param_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试切换不存在的全局参数."""
        user = User(
            email="param@example.com",
            password_hash=hash_password("password123"),
            nickname="参数用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.patch(
            "/api/v1/global-params/99999/toggle?is_enabled=true",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
