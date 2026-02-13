"""Dashboard service."""

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interface import Interface
from app.models.project import Project
from app.models.scenario import Scenario
from app.models.test_execution import TestExecution
from app.models.test_plan import TestPlan
from app.schemas.dashboard import (
    CoreStatsResponse,
    CoverageResponse,
    TrendDataPoint,
    TrendResponse,
)


class DashboardService:
    """Dashboard service for statistics and analytics."""

    async def get_core_stats(self, session: AsyncSession, user_id: int) -> CoreStatsResponse:
        """
        Get core statistics for dashboard.

        Args:
            session: Database session
            user_id: Current user ID

        Returns:
            CoreStatsResponse with counts
        """
        # Count projects
        projects_result = await session.execute(
            select(func.count(Project.id)).where(Project.creator_id == user_id)
        )
        total_projects = projects_result.scalar() or 0

        # Count interfaces (through projects)
        interfaces_result = await session.execute(
            select(func.count(Interface.id))
            .select_from(Project)
            .join(Interface, Project.id == Interface.project_id)
            .where(Project.creator_id == user_id)
        )
        total_interfaces = interfaces_result.scalar() or 0

        # Count scenarios (through projects)
        scenarios_result = await session.execute(
            select(func.count(Scenario.id))
            .select_from(Project)
            .join(Scenario, Project.id == Scenario.project_id)
            .where(Project.creator_id == user_id)
        )
        total_scenarios = scenarios_result.scalar() or 0

        # Count test plans (through projects)
        plans_result = await session.execute(
            select(func.count(TestPlan.id))
            .select_from(Project)
            .join(TestPlan, Project.id == TestPlan.project_id)
            .where(Project.creator_id == user_id)
        )
        total_plans = plans_result.scalar() or 0

        return CoreStatsResponse(
            total_projects=total_projects,
            total_interfaces=total_interfaces,
            total_scenarios=total_scenarios,
            total_plans=total_plans,
        )

    async def get_execution_trend(
        self, session: AsyncSession, user_id: int, days: int = 30
    ) -> TrendResponse:
        """
        Get test execution trend for the last N days.

        Args:
            session: Database session
            user_id: Current user ID
            days: Number of days to look back (default 30)

        Returns:
            TrendResponse with daily execution counts
        """
        start_date = datetime.now() - timedelta(days=days)

        # Query executions by date for user's projects
        result = await session.execute(
            select(
                func.date(TestExecution.created_at).label("date"),
                func.count(TestExecution.id).label("execution_count"),
            )
            .select_from(TestExecution)
            .join(TestPlan, TestExecution.plan_id == TestPlan.id)
            .join(Project, TestPlan.project_id == Project.id)
            .where(Project.creator_id == user_id)
            .where(TestExecution.created_at >= start_date)
            .group_by(func.date(TestExecution.created_at))
            .order_by(func.date(TestExecution.created_at))
        )

        trend = [
            TrendDataPoint(date=str(row.date), count=row.execution_count) for row in result.all()
        ]

        return TrendResponse(trend=trend)

    async def get_project_coverage(
        self, session: AsyncSession, user_id: int
    ) -> CoverageResponse:
        """
        Get project coverage statistics.

        Args:
            session: Database session
            user_id: Current user ID

        Returns:
            CoverageResponse with tested/untested project counts
        """
        # Count total projects
        total_result = await session.execute(
            select(func.count(Project.id)).where(Project.creator_id == user_id)
        )
        total_projects = total_result.scalar() or 0

        if total_projects == 0:
            return CoverageResponse(
                tested_projects=0,
                untested_projects=0,
                coverage_percentage=0.0,
            )

        # Count projects with at least one execution
        tested_result = await session.execute(
            select(func.count(Project.id.distinct()))
            .select_from(Project)
            .join(TestPlan, Project.id == TestPlan.project_id)
            .join(TestExecution, TestPlan.id == TestExecution.plan_id)
            .where(Project.creator_id == user_id)
        )
        tested_projects = tested_result.scalar() or 0

        untested_projects = total_projects - tested_projects
        coverage_percentage = (tested_projects / total_projects * 100) if total_projects > 0 else 0.0

        return CoverageResponse(
            tested_projects=tested_projects,
            untested_projects=untested_projects,
            coverage_percentage=round(coverage_percentage, 2),
        )
