"""关键字配置模块 API 集成测试."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.keyword import Keyword
from app.utils.password import hash_password


class TestKeywordsList:
    """测试关键字列表 API."""

    @pytest.mark.asyncio
    async def test_list_keywords(self, client: AsyncClient, db: AsyncSession):
        """测试获取关键字列表."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/keywords",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_list_keywords_filter_by_type(self, client: AsyncClient, db: AsyncSession):
        """测试按类型过滤关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/keywords?type=HTTP",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # 验证所有返回的关键字都是 HTTP 类型
        for keyword in data["items"]:
            assert keyword["type"] == "HTTP"

    @pytest.mark.asyncio
    async def test_list_keywords_filter_builtin(self, client: AsyncClient, db: AsyncSession):
        """测试过滤内置关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/keywords?is_builtin=true",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # 验证所有返回的关键字都是内置的
        for keyword in data["items"]:
            assert keyword["is_builtin"] is True

    @pytest.mark.asyncio
    async def test_list_keywords_pagination(self, client: AsyncClient, db: AsyncSession):
        """测试关键字列表分页."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/keywords?page=1&pageSize=5",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 1
        assert len(data["items"]) <= 5


class TestKeywordsEnabled:
    """测试启用的关键字 API."""

    @pytest.mark.asyncio
    async def test_get_enabled_keywords(self, client: AsyncClient, db: AsyncSession):
        """测试获取所有启用的关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/keywords/enabled",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "keywords" in data
        assert isinstance(data["keywords"], dict)


class TestKeywordsCreate:
    """测试创建关键字 API."""

    @pytest.mark.asyncio
    async def test_create_keyword_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功创建关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/keywords",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "type": "HTTP",
                "name": "自定义请求",
                "method_name": "custom_request",
                "code": "def custom_request(url): pass",
                "params": [
                    {"name": "url", "type": "str", "description": "请求URL"}
                ],
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["type"] == "HTTP"
        assert data["name"] == "自定义请求"
        assert data["is_builtin"] is False
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_keyword_missing_fields(self, client: AsyncClient, db: AsyncSession):
        """测试缺少必填字段."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/keywords",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "type": "HTTP",
                "name": "不完整关键字",
            }
        )

        assert response.status_code == 422


class TestKeywordsUpdate:
    """测试更新关键字 API."""

    @pytest.mark.asyncio
    async def test_update_keyword_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功更新自定义关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建自定义关键字
        keyword = Keyword(
            type="HTTP",
            name="旧名称",
            method_name="old_method",
            code="def old_method(): pass",
            is_builtin=False,
            is_enabled=True,
        )
        db.add(keyword)
        await db.commit()
        await db.refresh(keyword)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            f"/api/v1/keywords/{keyword.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "新名称",
                "code": "def new_method(): pass",
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "新名称"

    @pytest.mark.asyncio
    async def test_update_builtin_keyword_forbidden(self, client: AsyncClient, db: AsyncSession):
        """测试更新内置关键字应该失败."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建内置关键字
        keyword = Keyword(
            type="HTTP",
            name="内置请求",
            method_name="builtin_request",
            code="def builtin_request(): pass",
            is_builtin=True,
            is_enabled=True,
        )
        db.add(keyword)
        await db.commit()
        await db.refresh(keyword)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            f"/api/v1/keywords/{keyword.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "试图修改内置关键字",
            }
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_keyword_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试更新不存在的关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            "/api/v1/keywords/99999",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "新名称"}
        )

        assert response.status_code == 404


class TestKeywordsDelete:
    """测试删除关键字 API."""

    @pytest.mark.asyncio
    async def test_delete_keyword_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功删除自定义关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建自定义关键字
        keyword = Keyword(
            type="HTTP",
            name="待删除关键字",
            method_name="to_delete",
            code="def to_delete(): pass",
            is_builtin=False,
            is_enabled=True,
        )
        db.add(keyword)
        await db.commit()
        await db.refresh(keyword)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            f"/api/v1/keywords/{keyword.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # 验证关键字已被删除
        result = await db.execute(select(Keyword).where(Keyword.id == keyword.id))
        keyword = result.scalar_one_or_none()
        assert keyword is None

    @pytest.mark.asyncio
    async def test_delete_builtin_keyword_forbidden(self, client: AsyncClient, db: AsyncSession):
        """测试删除内置关键字应该失败."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建内置关键字
        keyword = Keyword(
            type="HTTP",
            name="内置关键字",
            method_name="builtin_method",
            code="def builtin_method(): pass",
            is_builtin=True,
            is_enabled=True,
        )
        db.add(keyword)
        await db.commit()
        await db.refresh(keyword)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            f"/api/v1/keywords/{keyword.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_keyword_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试删除不存在的关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            "/api/v1/keywords/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestKeywordsToggle:
    """测试关键字启用/禁用 API."""

    @pytest.mark.asyncio
    async def test_toggle_keyword_enable(self, client: AsyncClient, db: AsyncSession):
        """测试启用关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建禁用的关键字
        keyword = Keyword(
            type="HTTP",
            name="禁用的关键字",
            method_name="disabled_method",
            code="def disabled_method(): pass",
            is_builtin=False,
            is_enabled=False,
        )
        db.add(keyword)
        await db.commit()
        await db.refresh(keyword)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.patch(
            f"/api/v1/keywords/{keyword.id}/toggle?is_enabled=true",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_enabled"] is True

    @pytest.mark.asyncio
    async def test_toggle_keyword_disable(self, client: AsyncClient, db: AsyncSession):
        """测试禁用关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建启用的关键字
        keyword = Keyword(
            type="HTTP",
            name="启用的关键字",
            method_name="enabled_method",
            code="def enabled_method(): pass",
            is_builtin=False,
            is_enabled=True,
        )
        db.add(keyword)
        await db.commit()
        await db.refresh(keyword)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.patch(
            f"/api/v1/keywords/{keyword.id}/toggle?is_enabled=false",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_enabled"] is False

    @pytest.mark.asyncio
    async def test_toggle_keyword_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试切换不存在的关键字."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.patch(
            "/api/v1/keywords/99999/toggle?is_enabled=true",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestKeywordsParse:
    """测试解析代码 docstring API."""

    @pytest.mark.asyncio
    async def test_parse_code_docstring(self, client: AsyncClient, db: AsyncSession):
        """测试解析 Python 代码 docstring."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        code = '''
def send_request(url: str, method: str = "GET"):
    """发送 HTTP 请求

    Args:
        url: 请求地址
        method: 请求方法

    Returns:
        响应对象
    """
    pass
'''

        response = await client.post(
            "/api/v1/keywords/parse",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": code}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["function_name"] == "send_request"
        assert "发送 HTTP 请求" in data["description"]
        assert len(data["params"]) == 2
        assert data["params"][0]["name"] == "url"
        assert data["params"][0]["type"] == "str"
        assert data["params"][1]["name"] == "method"
        assert data["params"][1]["default"] == "GET"

    @pytest.mark.asyncio
    async def test_parse_invalid_code(self, client: AsyncClient, db: AsyncSession):
        """测试解析无效代码."""
        user = User(
            email="keyword@example.com",
            password_hash=hash_password("password123"),
            nickname="关键字用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/keywords/parse",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": "invalid python code <<<<"}
        )

        # 应该返回错误信息
        assert response.status_code == 200
        data = response.json()

        # 可能有 error 字段或者 function_name 为空
        assert "error" in data or not data.get("function_name")
