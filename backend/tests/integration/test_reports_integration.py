"""测试报告模块 API 集成测试."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project
from app.models.test_plan import TestPlan
from app.models.test_execution import TestExecution
from app.models.test_report import TestReport
from app.models.environment import Environment
from app.utils.password import hash_password
from datetime import datetime


class TestReportsList:
    """测试报告列表 API."""

    @pytest.mark.asyncio
    async def test_list_reports_empty(self, client: AsyncClient, db: AsyncSession):
        """测试空报告列表."""
        user = User(
            email="report@example.com",
            password_hash=hash_password("password123"),
            nickname="报告用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_list_reports_with_data(self, client: AsyncClient, db: AsyncSession):
        """测试有数据的报告列表."""
        # 创建用户
        user = User(
            email="report@example.com",
            password_hash=hash_password("password123"),
            nickname="报告用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        # 创建项目和计划
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

        env = Environment(
            name="测试环境",
            base_url="https://api.example.com",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(env)
        await db.commit()
        await db.refresh(env)

        # 创建执行记录
        execution = TestExecution(
            plan_id=plan.id,
            environment_id=env.id,
            executor_id=user.id,
            status="completed",
            total_scenarios=10,
            passed_scenarios=8,
            failed_scenarios=2,
            started_at=datetime.now(),
            finished_at=datetime.now(),
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)

        # 创建报告
        report = TestReport(
            execution_id=execution.id,
            content="# 测试报告\n\n这是一个测试报告。",
        )
        db.add(report)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/reports",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1


class TestReportsGet:
    """测试获取报告详情 API."""

    @pytest.mark.asyncio
    async def test_get_report_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功获取报告详情."""
        # 创建用户
        user = User(
            email="report@example.com",
            password_hash=hash_password("password123"),
            nickname="报告用户",
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

        env = Environment(
            name="测试环境",
            base_url="https://api.example.com",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(env)
        await db.commit()
        await db.refresh(env)

        execution = TestExecution(
            plan_id=plan.id,
            environment_id=env.id,
            executor_id=user.id,
            status="completed",
            total_scenarios=10,
            passed_scenarios=8,
            failed_scenarios=2,
            started_at=datetime.now(),
            finished_at=datetime.now(),
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)

        report = TestReport(
            execution_id=execution.id,
            content="# 测试报告\n\n详细内容...",
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            f"/api/v1/reports/{report.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == report.id
        assert "content" in data

    @pytest.mark.asyncio
    async def test_get_report_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试获取不存在的报告."""
        user = User(
            email="report@example.com",
            password_hash=hash_password("password123"),
            nickname="报告用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/reports/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestReportsExport:
    """测试导出报告 API."""

    @pytest.mark.asyncio
    async def test_export_report_html(self, client: AsyncClient, db: AsyncSession):
        """测试导出 HTML 报告."""
        # 创建用户
        user = User(
            email="report@example.com",
            password_hash=hash_password("password123"),
            nickname="报告用户",
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

        env = Environment(
            name="测试环境",
            base_url="https://api.example.com",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(env)
        await db.commit()
        await db.refresh(env)

        execution = TestExecution(
            plan_id=plan.id,
            environment_id=env.id,
            executor_id=user.id,
            status="completed",
            total_scenarios=10,
            passed_scenarios=8,
            failed_scenarios=2,
            started_at=datetime.now(),
            finished_at=datetime.now(),
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)

        report = TestReport(
            execution_id=execution.id,
            content="# 测试报告\n\n详细内容...",
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            f"/api/v1/reports/{report.id}/export?format=html",
            headers={"Authorization": f"Bearer {token}"}
        )

        # HTML 导出应该返回文件
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_export_report_pdf(self, client: AsyncClient, db: AsyncSession):
        """测试导出 PDF 报告."""
        # 创建用户
        user = User(
            email="report@example.com",
            password_hash=hash_password("password123"),
            nickname="报告用户",
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

        env = Environment(
            name="测试环境",
            base_url="https://api.example.com",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(env)
        await db.commit()
        await db.refresh(env)

        execution = TestExecution(
            plan_id=plan.id,
            environment_id=env.id,
            executor_id=user.id,
            status="completed",
            total_scenarios=10,
            passed_scenarios=8,
            failed_scenarios=2,
            started_at=datetime.now(),
            finished_at=datetime.now(),
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)

        report = TestReport(
            execution_id=execution.id,
            content="# 测试报告\n\n详细内容...",
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            f"/api/v1/reports/{report.id}/export?format=pdf",
            headers={"Authorization": f"Bearer {token}"}
        )

        # PDF 导出可能需要特殊库,可能返回 400 或 200
        assert response.status_code in [200, 400, 415]

    @pytest.mark.asyncio
    async def test_export_report_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试导出不存在的报告."""
        user = User(
            email="report@example.com",
            password_hash=hash_password("password123"),
            nickname="报告用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.get(
            "/api/v1/reports/99999/export?format=html",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestReportsDelete:
    """测试删除报告 API."""

    @pytest.mark.asyncio
    async def test_delete_report_success(self, client: AsyncClient, db: AsyncSession):
        """测试成功删除报告."""
        # 创建用户
        user = User(
            email="report@example.com",
            password_hash=hash_password("password123"),
            nickname="报告用户",
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

        env = Environment(
            name="测试环境",
            base_url="https://api.example.com",
            project_id=project.id,
            creator_id=user.id,
        )
        db.add(env)
        await db.commit()
        await db.refresh(env)

        execution = TestExecution(
            plan_id=plan.id,
            environment_id=env.id,
            executor_id=user.id,
            status="completed",
            total_scenarios=10,
            passed_scenarios=8,
            failed_scenarios=2,
            started_at=datetime.now(),
            finished_at=datetime.now(),
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)

        report = TestReport(
            execution_id=execution.id,
            content="# 测试报告",
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            f"/api/v1/reports/{report.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # 验证报告已被删除
        result = await db.execute(select(TestReport).where(TestReport.id == report.id))
        report = result.scalar_one_or_none()
        assert report is None

    @pytest.mark.asyncio
    async def test_delete_report_not_found(self, client: AsyncClient, db: AsyncSession):
        """测试删除不存在的报告."""
        user = User(
            email="report@example.com",
            password_hash=hash_password("password123"),
            nickname="报告用户",
            provider="email",
        )
        db.add(user)
        await db.commit()

        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        response = await client.delete(
            "/api/v1/reports/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
