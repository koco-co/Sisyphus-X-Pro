"""数据库配置模块 API 集成测试."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project
from app.models.database_config import DatabaseConfig
from app.utils.password import hash_password


class TestDBConfigsList:
    """测试数据库配置列表 API."""

    @pytest.mark.asyncio
    async def test_list_db_configs_empty(self, client: AsyncClient, db: AsyncSession):
        """测试空数据库配置列表."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/db-configs",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_list_db_configs_with_data(self, client: AsyncClient, db: AsyncSession):
        """测试有数据的数据库配置列表."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        config = DatabaseConfig(
            name="测试数据库",
            db_type="mysql",
            host="localhost",
            port=3306,
            database="test_db",
            username="root",
            password="password",
            project_id=project.id,
        )
        db.add(config)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/db-configs",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "测试数据库"


class TestDBConfigsCreate:
    """测试创建数据库配置 API."""

    @pytest.mark.asyncio
    async def test_create_db_config_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功创建数据库配置."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
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
            "/api/v1/db-configs",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "生产数据库",
                "db_type": "mysql",
                "host": "prod.example.com",
                "port": 3306,
                "database": "prod_db",
                "username": "dbuser",
                "password": "dbpass",
                "project_id": project.id,
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "生产数据库"
        assert data["db_type"] == "mysql"
        assert data["host"] == "prod.example.com"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_db_config_missing_fields(self, client: AsyncClient, db: AsyncSession):
        """测试缺少必填字段."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/db-configs",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "不完整的配置"}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_db_config_invalid_type(self, client: AsyncClient, db: AsyncSession):
        """测试无效的数据库类型."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
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
            "/api/v1/db-configs",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "无效数据库",
                "db_type": "mongodb",  # 不支持的类型
                "host": "localhost",
                "port": 27017,
                "database": "test",
                "username": "user",
                "password": "pass",
                "project_id": project.id,
            }
        )

        assert response.status_code == 422


class TestDBConfigsUpdate:
    """测试更新数据库配置 API."""

    @pytest.mark.asyncio
    async def test_update_db_config_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功更新数据库配置."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        config = DatabaseConfig(
            name="旧配置",
            db_type="mysql",
            host="old.example.com",
            port=3306,
            database="old_db",
            username="root",
            password="password",
            project_id=project.id,
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            f"/api/v1/db-configs/{config.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "新配置",
                "host": "new.example.com",
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "新配置"
        assert data["host"] == "new.example.com"

    @pytest.mark.asyncio
    async def test_update_db_config_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试更新不存在的数据库配置."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.put(
            "/api/v1/db-configs/99999",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "新名称"}
        )

        assert response.status_code == 404


class TestDBConfigsDelete:
    """测试删除数据库配置 API."""

    @pytest.mark.asyncio
    async def test_delete_db_config_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功删除数据库配置."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        config = DatabaseConfig(
            name="待删除配置",
            db_type="mysql",
            host="localhost",
            port=3306,
            database="test",
            username="root",
            password="password",
            project_id=project.id,
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            f"/api/v1/db-configs/{config.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # 验证配置已被删除
        result = await db.execute(select(DatabaseConfig).where(DatabaseConfig.id == config.id))
        config = result.scalar_one_or_none()
        assert config is None

    @pytest.mark.asyncio
    async def test_delete_db_config_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试删除不存在的数据库配置."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            "/api/v1/db-configs/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestDBConfigsTest:
    """测试数据库连接 API."""

    @pytest.mark.asyncio
    async def test_db_connection(self, client: AsyncClient, db: AsyncSession):
        """测试数据库连接."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        config = DatabaseConfig(
            name="测试配置",
            db_type="mysql",
            host="nonexistent.example.com",  # 不存在的主机
            port=3306,
            database="test",
            username="root",
            password="password",
            project_id=project.id,
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            f"/api/v1/db-configs/{config.id}/test",
            headers={"Authorization": f"Bearer {token}"}
        )

        # 应该返回测试结果 (成功或失败)
        assert response.status_code == 200
        data = response.json()

        assert "success" in data
        assert "message" in data

    @pytest.mark.asyncio
    async def test_db_connection_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试不存在的配置连接."""
        user = User(
            email="dbconfig@example.com",
            password_hash=hash_password("password123"),
            nickname="数据库配置用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/db-configs/99999/test",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
