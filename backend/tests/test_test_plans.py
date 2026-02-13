"""测试计划模块的单元测试."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.test_plan import TestPlan
from app.models.plan_scenario import PlanScenario
from app.models.scenario import Scenario
from app.models.project import Project
from app.models.user import User


class TestTestPlan:
    """测试计划相关功能的测试."""

    @pytest.mark.asyncio
    async def test_create_test_plan_success(self, client: AsyncClient, async_session, test_user: User, test_project: Project):
        """测试成功创建测试计划."""
        # 绕过认证
        from app.main import app
        from app.middleware.auth import get_current_user
        from app.database import get_db

        async def override_get_user():
            return test_user

        async def override_get_db():
            yield async_session

        app.dependency_overrides[get_current_user] = override_get_user
        app.dependency_overrides[get_db] = override_get_db

        response = await client.post(
            "/api/v1/test-plans",
            json={
                "name": "Smoke Test Plan",
                "description": "Daily smoke testing",
                "project_id": test_project.id,
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Smoke Test Plan"
        assert data["description"] == "Daily smoke testing"
        assert data["project_id"] == test_project.id
        assert "id" in data

        # 验证数据库中的记录
        result = await async_session.execute(
            select(TestPlan).where(TestPlan.name == "Smoke Test Plan")
        )
        test_plan = result.scalar_one_or_none()
        assert test_plan is not None
        assert test_plan.name == "Smoke Test Plan"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_create_test_plan_duplicate_name(self, client: AsyncClient, async_session, test_user: User, test_project: Project):
        """测试创建重名测试计划应失败."""
        from app.main import app
        from app.middleware.auth import get_current_user
        from app.database import get_db

        async def override_get_user():
            return test_user

        async def override_get_db():
            yield async_session

        app.dependency_overrides[get_current_user] = override_get_user
        app.dependency_overrides[get_db] = override_get_db

        # 创建第一个测试计划
        await client.post(
            "/api/v1/test-plans",
            json={
                "name": "Duplicate Plan",
                "description": "First plan",
                "project_id": test_project.id,
            }
        )

        # 尝试创建重名计划
        response = await client.post(
            "/api/v1/test-plans",
            json={
                "name": "Duplicate Plan",
                "description": "Second plan",
                "project_id": test_project.id,
            }
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_list_test_plans(self, client: AsyncClient, async_session, test_user: User, test_project: Project):
        """测试获取测试计划列表."""
        from app.main import app
        from app.middleware.auth import get_current_user
        from app.database import get_db

        async def override_get_user():
            return test_user

        async def override_get_db():
            yield async_session

        app.dependency_overrides[get_current_user] = override_get_user
        app.dependency_overrides[get_db] = override_get_db

        # 创建多个测试计划
        for i in range(3):
            test_plan = TestPlan(
                name=f"Test Plan {i}",
                description=f"Description {i}",
                project_id=test_project.id,
                creator_id=test_user.id,
            )
            async_session.add(test_plan)
        await async_session.commit()

        response = await client.get("/api/v1/test-plans")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert len(data["items"]) >= 3
        assert "page" in data
        assert "pageSize" in data

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_list_test_plans_with_project_filter(self, client: AsyncClient, async_session, test_user: User, test_project: Project):
        """测试按项目筛选测试计划."""
        from app.main import app
        from app.middleware.auth import get_current_user
        from app.database import get_db

        async def override_get_user():
            return test_user

        async def override_get_db():
            yield async_session

        app.dependency_overrides[get_current_user] = override_get_user
        app.dependency_overrides[get_db] = override_get_db

        # 创建测试计划
        test_plan = TestPlan(
            name="Project Plan",
            description="For project",
            project_id=test_project.id,
            creator_id=test_user.id,
        )
        async_session.add(test_plan)
        await async_session.commit()

        response = await client.get(
            f"/api/v1/test-plans?project_id={test_project.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(p["name"] == "Project Plan" for p in data["items"])

        app.dependency_overrides.clear()


class TestPlanScenarios:
    """测试计划场景关联功能的测试."""

    @pytest.mark.asyncio
    async def test_add_scenario_to_plan(self, client: AsyncClient, async_session, test_user: User, test_project: Project, test_scenario: Scenario):
        """测试向测试计划添加场景."""
        from app.main import app
        from app.middleware.auth import get_current_user
        from app.database import get_db

        async def override_get_user():
            return test_user

        async def override_get_db():
            yield async_session

        app.dependency_overrides[get_current_user] = override_get_user
        app.dependency_overrides[get_db] = override_get_db

        # 创建测试计划
        test_plan = TestPlan(
            name="Plan with Scenario",
            description="Test plan",
            project_id=test_project.id,
            creator_id=test_user.id,
        )
        async_session.add(test_plan)
        await async_session.commit()
        await async_session.refresh(test_plan)

        response = await client.post(
            f"/api/v1/test-plans/{test_plan.id}/scenarios",
            params={
                "scenario_id": test_scenario.id,
                "sort_order": 1,
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["scenario_id"] == test_scenario.id
        assert data["sort_order"] == 1

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_remove_scenario_from_plan(self, client: AsyncClient, async_session, test_user: User, test_project: Project, test_scenario: Scenario):
        """测试从测试计划移除场景."""
        from app.main import app
        from app.middleware.auth import get_current_user
        from app.database import get_db

        async def override_get_user():
            return test_user

        async def override_get_db():
            yield async_session

        app.dependency_overrides[get_current_user] = override_get_user
        app.dependency_overrides[get_db] = override_get_db

        # 创建测试计划和关联
        test_plan = TestPlan(
            name="Plan",
            description="Test",
            project_id=test_project.id,
            creator_id=test_user.id,
        )
        async_session.add(test_plan)
        await async_session.commit()

        plan_scenario = PlanScenario(
            plan_id=test_plan.id,
            scenario_id=test_scenario.id,
            sort_order=1,
        )
        async_session.add(plan_scenario)
        await async_session.commit()

        response = await client.delete(
            f"/api/v1/test-plans/{test_plan.id}/scenarios/{test_scenario.id}"
        )

        assert response.status_code == 204

        # 验证已删除
        result = await async_session.execute(
            select(PlanScenario).where(
                PlanScenario.plan_id == test_plan.id,
                PlanScenario.scenario_id == test_scenario.id
            )
        )
        assert result.scalar_one_or_none() is None

        app.dependency_overrides.clear()
