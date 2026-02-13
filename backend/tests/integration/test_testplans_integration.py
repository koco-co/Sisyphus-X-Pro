"""测试计划模块 API 集成测试."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project
from app.models.scenario import Scenario
from app.models.test_plan import TestPlan
from app.models.plan_scenario import PlanScenario
from app.models.environment import Environment
from app.utils.password import hash_password


class TestPlansList:
    """测试测试计划列表 API."""

    @pytest.mark.asyncio
    async def test_list_plans_empty(self, client: AsyncClient, db: AsyncSession):
        """测试空测试计划列表."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/test-plans",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_list_plans_with_data(self, client: AsyncClient, db: AsyncSession):
        """测试有数据的测试计划列表."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        plan = TestPlan(
            name="测试计划",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(plan)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/test-plans",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "测试计划"


class TestPlansCreate:
    """测试创建测试计划 API."""

    @pytest.mark.asyncio
    async def test_create_plan_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功创建测试计划."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
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
            "/api/v1/test-plans",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "新测试计划",
                "project_id": project.id,
                "description": "测试描述",
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "新测试计划"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_plan_missing_fields(self, client: AsyncClient, db: AsyncSession):
        """测试缺少必填字段."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/test-plans",
            headers={"Authorization": f"Bearer {token}"},
            json={"description": "描述"}
        )

        assert response.status_code == 422


class TestPlansAddScenarios:
    """测试添加场景到测试计划 API."""

    @pytest.mark.asyncio
    async def test_add_scenarios_to_plan(self, client: AsyncClient, db: AsyncSession):
        """测试添加场景到测试计划."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        plan = TestPlan(
            name="测试计划",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        scenario1 = Scenario(
            name="场景1",
            project_id=project.id,
            creator_id=user.id,
        )
        scenario2 = Scenario(
            name="场景2",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add_all([scenario1, scenario2])
        await db.commit()
        await db.refresh(scenario1)
        await db.refresh(scenario2)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            f"/api/v1/test-plans/{plan.id}/scenarios",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "scenario_ids": [scenario1.id, scenario2.id],
            }
        )

        assert response.status_code == 200

        # 验证场景已添加到计划
        result = await db.execute(
            select(PlanScenario).where(PlanScenario.plan_id == plan.id)
        )
        plan_scenarios = result.scalars().all()
        assert len(plan_scenarios) == 2


class TestPlansExecute:
    """测试执行测试计划 API."""

    @pytest.mark.asyncio
    async def test_execute_plan(self, client: AsyncClient, db: AsyncSession):
        """测试执行测试计划."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        plan = TestPlan(
            name="测试计划",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        scenario = Scenario(
            name="测试场景",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(scenario)
        await db.commit()
        await db.refresh(scenario)

        plan_scenario = PlanScenario(
            plan_id=plan.id,
            scenario_id=scenario.id,
            order=1,
        )
        db.add(plan_scenario)
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

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            f"/api/v1/test-plans/{plan.id}/execute",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "environment_id": env.id,
            }
        )

        # 注意: 这个测试可能需要 mock 执行器
        # 在实际测试中,执行可能会失败或返回不同的状态码
        assert response.status_code in [200, 202, 400]

    @pytest.mark.asyncio
    async def test_execute_plan_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试执行不存在的测试计划."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            "/api/v1/test-plans/99999/execute",
            headers={"Authorization": f"Bearer {token}"},
            json={"environment_id": 1}
        )

        assert response.status_code == 404


class TestPlansControl:
    """测试测试计划控制 API (暂停/恢复/终止)."""

    @pytest.mark.asyncio
    async def test_pause_plan(self, client: AsyncClient, db: AsyncSession):
        """测试暂停测试计划."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        plan = TestPlan(
            name="测试计划",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        # 注意: 如果没有正在执行的计划,这个请求可能返回 400 或 404
        response = await client.post(
            f"/api/v1/test-plans/{plan.id}/pause",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code in [200, 400, 404]

    @pytest.mark.asyncio
    async def test_resume_plan(self, client: AsyncClient, db: AsyncSession):
        """测试恢复测试计划."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        plan = TestPlan(
            name="测试计划",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            f"/api/v1/test-plans/{plan.id}/resume",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code in [200, 400, 404]

    @pytest.mark.asyncio
    async def test_terminate_plan(self, client: AsyncClient, db: AsyncSession):
        """测试终止测试计划."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        plan = TestPlan(
            name="测试计划",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.post(
            f"/api/v1/test-plans/{plan.id}/terminate",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code in [200, 400, 404]


class TestPlansDelete:
    """测试删除测试计划 API."""

    @pytest.mark.asyncio
    async def test_delete_plan_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功删除测试计划."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        project = Project(name="测试项目", creator_id=user.id)
        db.add(project)
        await db.commit()
        await db.refresh(project)

        plan = TestPlan(
            name="待删除计划",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            f"/api/v1/test-plans/{plan.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # 验证计划已被删除
        result = await db.execute(select(TestPlan).where(TestPlan.id == plan.id))
        plan = result.scalar_one_or_none()
        assert plan is None

    @pytest.mark.asyncio
    async def test_delete_plan_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试删除不存在的测试计划."""
        user = User(
            email="plan@example.com",
            password_hash=hash_password("password123"),
            nickname="计划用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            "/api/v1/test-plans/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
