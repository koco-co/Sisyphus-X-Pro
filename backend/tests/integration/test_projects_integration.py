"""项目管理模块 API 集成测试."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project
from app.utils.password import hash_password


class TestProjectsList:
    """测试项目列表 API."""

    @pytest.mark.asyncio
    async def test_list_projects_empty(self, client: AsyncClient, db: AsyncSession):
        """测试空项目列表."""
        # 创建用户并获取 token
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_projects_with_data(self, client: AsyncClient, db: AsyncSession):
        """测试有数据的项目列表."""
        # 创建用户和项目
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(
            name="测试项目",
            description="测试描述",
            creator_id=user.id,
        )
        db.add(project)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["name"] == "测试项目"

    @pytest.mark.asyncio
    async def test_list_projects_pagination(self, client: AsyncClient, db: AsyncSession):
        """测试项目列表分页."""
        # 创建用户
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建多个项目
        for i in range(15):
            project = Project(
                name=f"项目 {i}",
                description=f"描述 {i}",
                creator_id=user.id,
            )
            db.add(project)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        # 测试第一页
        response = await client.get(
            "/api/v1/projects?page=1&pageSize=10",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_list_projects_search(self, client: AsyncClient, db: AsyncSession):
        """测试项目搜索."""
        # 创建用户
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建项目
        project1 = Project(name="用户管理", description="用户管理模块", creator_id=user.id)
        project2 = Project(name="订单管理", description="订单管理模块", creator_id=user.id)
        db.add_all([project1, project2])
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        # 搜索"用户"
        response = await client.get(
            "/api/v1/projects?name=用户",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert "用户" in data["items"][0]["name"]


class TestProjectsCreate:
    """测试创建项目 API."""

    @pytest.mark.asyncio
    async def test_create_project_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功创建项目."""
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "新项目",
                "description": "新项目描述",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "新项目"
        assert data["description"] == "新项目描述"
        assert "id" in data

        # 验证数据库
        result = await db.execute(select(Project).where(Project.name == "新项目"))
        project = result.scalar_one_or_none()
        assert project is not None

    @pytest.mark.asyncio
    async def test_create_project_duplicate_name(self, client: AsyncClient, db: AsyncSession):
        """测试创建重名项目."""
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 先创建一个项目
        project = Project(name="重复项目", creator_id=user.id)
        db.add(project)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        # 尝试创建同名项目
        response = await client.post(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "重复项目",
                "description": "描述",
            }
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_project_missing_name(self, client: AsyncClient, db: AsyncSession):
        """测试缺少项目名称."""
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
            json={"description": "描述"}
        )

        assert response.status_code == 422


class TestProjectsGet:
    """测试获取项目详情 API."""

    @pytest.mark.asyncio
    async def test_get_project_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功获取项目详情."""
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
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

        response = await client.get(
            f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project.id
        assert data["name"] == "测试项目"

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试获取不存在的项目."""
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/projects/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestProjectsUpdate:
    """测试更新项目 API."""

    @pytest.mark.asyncio
    async def test_update_project_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功更新项目."""
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="旧名称", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "新名称",
                "description": "新描述",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新名称"
        assert data["description"] == "新描述"

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试更新不存在的项目."""
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            "/api/v1/projects/99999",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "新名称"}
        )

        assert response.status_code == 404


class TestProjectsDelete:
    """测试删除项目 API."""

    @pytest.mark.asyncio
    async def test_delete_project_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功删除项目."""
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="待删除项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # 验证项目已被删除
        result = await db.execute(select(Project).where(Project.id == project.id))
        project = result.scalar_one_or_none()
        assert project is None

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试删除不存在的项目."""
        user = User(
            email="project@example.com",
            password_hash=hash_password("password123"),
            nickname="项目用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            "/api/v1/projects/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
