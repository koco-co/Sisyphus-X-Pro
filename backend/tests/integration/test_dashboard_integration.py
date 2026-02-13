"""仪表盘模块 API 集成测试."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project
from app.models.interface import Interface
from app.models.scenario import Scenario
from app.models.test_plan import TestPlan
from app.models.test_execution import TestExecution
from app.models.environment import Environment
from app.utils.password import hash_password
from datetime import datetime, timedelta


class TestDashboardStats:
    """测试核心指标 API."""

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, client: AsyncClient, db: AsyncSession):
        """测试空数据的统计指标."""
        user = User(
            email="dashboard@example.com",
            password_hash=hash_password("password123"),
            nickname="仪表盘用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/dashboard/stats",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # 验证返回的数据结构
        assert "total_projects" in data
        assert "total_scenarios" in data
        assert "total_executions" in data
        assert "success_rate" in data

    @pytest.mark.asyncio
    async def test_get_stats_with_data(self, client: AsyncClient, db: AsyncSession):
        """测试有数据的统计指标."""
        # 创建用户
        user = User(
            email="dashboard@example.com",
            password_hash=hash_password("password123"),
            nickname="仪表盘用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建项目
        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        # 创建场景
        scenario = Scenario(
            name="测试场景",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(scenario)
        await db.commit()

        # 创建环境
        env = Environment(
            name="测试环境",
            base_url="https://api.example.com",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(env)
        await db.commit()
        await db.refresh(env)

        # 创建测试计划
        plan = TestPlan(
            name="测试计划",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        # 创建执行记录
        execution = TestExecution(
            plan_id=plan.id,
            environment_id=env.id,
            executor_id=user.id,
            status="completed",
            total_scenarios=10,
            passed_scenarios=8,
            failed_scenarios=2,
            started_at=datetime.now() - timedelta(hours=1),
            finished_at=datetime.now(),
        )
        db.add(execution)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/dashboard/stats",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total_projects"] == 1
        assert data["total_scenarios"] == 1
        assert data["total_executions"] == 1
        assert data["success_rate"] == 80.0  # 8/10 = 80%


class TestDashboardTrends:
    """测试测试趋势 API."""

    @pytest.mark.asyncio
    async def test_get_trends_empty(self, client: AsyncClient, db: AsyncSession):
        """测试空数据的趋势."""
        user = User(
            email="dashboard@example.com",
            password_hash=hash_password("password123"),
            nickname="仪表盘用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/dashboard/trends?days=7",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # 验证返回的数据结构
        assert "dates" in data
        assert "passed" in data
        assert "failed" in data
        assert isinstance(data["dates"], list)
        assert isinstance(data["passed"], list)
        assert isinstance(data["failed"], list)

    @pytest.mark.asyncio
    async def test_get_trends_with_data(self, client: AsyncClient, db: AsyncSession):
        """测试有数据的趋势."""
        # 创建用户
        user = User(
            email="dashboard@example.com",
            password_hash=hash_password("password123"),
            nickname="仪表盘用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建项目、场景、环境、计划
        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        scenario = Scenario(
            name="测试场景",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(scenario)
        await db.commit()

        env = Environment(
            name="测试环境",
            base_url="https://api.example.com",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(env)
        await db.commit()
        await db.refresh(env)

        plan = TestPlan(
            name="测试计划",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        # 创建最近7天的执行记录
        for i in range(7):
            execution = TestExecution(
                plan_id=plan.id,
                environment_id=env.id,
                executor_id=user.id,
                status="completed",
                total_scenarios=10,
                passed_scenarios=9 - i % 2,
                failed_scenarios=i % 2,
                started_at=datetime.now() - timedelta(days=i),
                finished_at=datetime.now() - timedelta(days=i) + timedelta(minutes=10),
            )
            db.add(execution)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/dashboard/trends?days=7",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["dates"]) <= 7
        assert len(data["passed"]) <= 7
        assert len(data["failed"]) <= 7

    @pytest.mark.asyncio
    async def test_get_trends_custom_days(self, client: AsyncClient, db: AsyncSession):
        """测试自定义天数的趋势."""
        user = User(
            email="dashboard@example.com",
            password_hash=hash_password("password123"),
            nickname="仪表盘用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/dashboard/trends?days=30",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # 验证返回30天的数据
        assert len(data["dates"]) <= 30


class TestDashboardCoverage:
    """测试项目覆盖率 API."""

    @pytest.mark.asyncio
    async def test_get_coverage_empty(self, client: AsyncClient, db: AsyncSession):
        """测试空数据的覆盖率."""
        user = User(
            email="dashboard@example.com",
            password_hash=hash_password("password123"),
            nickname="仪表盘用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/dashboard/coverage",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # 验证返回的数据结构
        assert "projects" in data
        assert isinstance(data["projects"], list)

    @pytest.mark.asyncio
    async def test_get_coverage_with_data(self, client: AsyncClient, db: AsyncSession):
        """测试有数据的覆盖率."""
        # 创建用户
        user = User(
            email="dashboard@example.com",
            password_hash=hash_password("password123"),
            nickname="仪表盘用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建项目
        project1 = Project(name="项目A", creator_id=user.id)
        project2 = Project(name="项目B", creator_id=user.id)
        db.add_all([project1, project2])
        await db.commit()
        await db.refresh(project1)
        await db.refresh(project2)

        # 为项目A创建接口和场景
        interface1 = Interface(
            name="接口1",
            method="GET",
            path="/api/test1",
            project_id=project1.id,
        )
        interface2 = Interface(
            name="接口2",
            method="POST",
            path="/api/test2",
            project_id=project1.id,
        )
        db.add_all([interface1, interface2])

        scenario1 = Scenario(
            name="场景1",
            project_id=project1.id,
            creator_id=user.id,
        )
        scenario2 = Scenario(
            name="场景2",
            project_id=project1.id,
            creator_id=user.id,
        )
        db.add_all([scenario1, scenario2])

        # 为项目B创建接口
        interface3 = Interface(
            name="接口3",
            method="GET",
            path="/api/test3",
            project_id=project2.id,
        )
        db.add(interface3)

        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/dashboard/coverage",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # 验证返回的项目列表
        assert len(data["projects"]) == 2

        # 验证每个项目的数据结构
        for project in data["projects"]:
            assert "project_id" in project
            assert "project_name" in project
            assert "interface_count" in project
            assert "scenario_count" in project
            assert "coverage_rate" in project
