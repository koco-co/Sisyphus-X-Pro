"""接口定义模块 API 集成测试."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project
from app.models.interface import Interface
from app.models.interface_folder import InterfaceFolder
from app.utils.password import hash_password


class TestInterfacesList:
    """测试接口列表 API."""

    @pytest.mark.asyncio
    async def test_list_interfaces_empty(self, client: AsyncClient, db: AsyncSession):
        """测试空接口列表."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/interfaces",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_list_interfaces_with_data(self, client: AsyncClient, db: AsyncSession):
        """测试有数据的接口列表."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        interface = Interface(
            name="测试接口",
            method="GET",
            path="/api/test",
            project_id=project.id,
        )
        db.add(interface)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/interfaces",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "测试接口"


class TestInterfacesCreate:
    """测试创建接口 API."""

    @pytest.mark.asyncio
    async def test_create_interface_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功创建接口."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/interfaces",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "用户登录接口",
                "method": "POST",
                "path": "/api/login",
                "project_id": project.id,
                "description": "用户登录",
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "用户登录接口"
        assert data["method"] == "POST"
        assert data["path"] == "/api/login"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_interface_missing_fields(self, client: AsyncClient, db: AsyncSession):
        """测试缺少必填字段."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/interfaces",
            headers={"Authorization": f"Bearer {token}"},
            json={"description": "不完整的接口"}
        )

        assert response.status_code == 422


class TestInterfacesUpdate:
    """测试更新接口 API."""

    @pytest.mark.asyncio
    async def test_update_interface_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功更新接口."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        interface = Interface(
            name="旧名称",
            method="GET",
            path="/api/old",
            project_id=project.id,
        )
        db.add(interface)
        await db.commit()
        await db.refresh(interface)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            f"/api/v1/interfaces/{interface.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "新名称",
                "path": "/api/new",
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "新名称"
        assert data["path"] == "/api/new"

    @pytest.mark.asyncio
    async def test_update_interface_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试更新不存在的接口."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            "/api/v1/interfaces/99999",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "新名称"}
        )

        assert response.status_code == 404


class TestInterfacesDelete:
    """测试删除接口 API."""

    @pytest.mark.asyncio
    async def test_delete_interface_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功删除接口."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        interface = Interface(
            name="待删除接口",
            method="GET",
            path="/api/delete",
            project_id=project.id,
        )
        db.add(interface)
        await db.commit()
        await db.refresh(interface)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            f"/api/v1/interfaces/{interface.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # 验证接口已被删除
        result = await db.execute(select(Interface).where(Interface.id == interface.id))
        interface = result.scalar_one_or_none()
        assert interface is None

    @pytest.mark.asyncio
    async def test_delete_interface_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试删除不存在的接口."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            "/api/v1/interfaces/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestInterfacesParseCurl:
    """测试解析 cURL 命令 API."""

    @pytest.mark.asyncio
    async def test_parse_curl_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功解析 cURL 命令."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        curl_command = '''curl -X POST https://api.example.com/login \\
  -H 'Content-Type: application/json' \\
  -d '{"email":"test@example.com","password":"123456"}"
'''

        response = await client.post(
            "/api/v1/interfaces/parse-curl",
            headers={"Authorization": f"Bearer {token}"},
            json={"curl": curl_command}
        )

        assert response.status_code == 200
        data = response.json()

        assert "method" in data
        assert "path" in data
        assert "headers" in data

    @pytest.mark.asyncio
    async def test_parse_curl_invalid(self, client: AsyncClient, db: AsyncSession):
        """测试解析无效的 cURL 命令."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/interfaces/parse-curl",
            headers={"Authorization": f"Bearer {token}"},
            json={"curl": "not a curl command"}
        )

        # 应该返回错误或部分解析结果
        assert response.status_code in [200, 400]


class TestInterfaceFolders:
    """测试接口文件夹 API."""

    @pytest.mark.asyncio
    async def test_create_folder(self, client: AsyncClient, db: AsyncSession):
        """测试创建文件夹."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/interfaces/folders",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "用户管理",
                "project_id": project.id,
            }
        )

        assert response.status_code in [200, 201]
        data = response.json()

        assert data["name"] == "用户管理"

    @pytest.mark.asyncio
    async def test_list_folders(self, client: AsyncClient, db: AsyncSession):
        """测试获取文件夹列表."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        # 创建文件夹
        folder = InterfaceFolder(
            name="测试文件夹",
            project_id=project.id,
        )
        db.add(folder)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            f"/api/v1/interfaces/folders?project_id={project.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["name"] == "测试文件夹"

    @pytest.mark.asyncio
    async def test_delete_folder(self, client: AsyncClient, db: AsyncSession):
        """测试删除文件夹."""
        user = User(
            email="interface@example.com",
            password_hash=hash_password("password123"),
            nickname="接口用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        folder = InterfaceFolder(
            name="待删除文件夹",
            project_id=project.id,
        )
        db.add(folder)
        await db.commit()
        await db.refresh(folder)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            f"/api/v1/interfaces/folders/{folder.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # 验证文件夹已被删除
        result = await db.execute(select(InterfaceFolder).where(InterfaceFolder.id == folder.id))
        folder = result.scalar_one_or_none()
        assert folder is None
