"""Dashboard service unit tests."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import (
    CoreStatsResponse,
    TrendResponse,
    CoverageResponse,
)


@pytest.mark.asyncio
async def test_get_core_stats_empty_db(async_session: AsyncSession):
    """Test getting core stats with empty database."""
    service = DashboardService()
    stats = await service.get_core_stats(async_session, user_id=1)

    assert isinstance(stats, CoreStatsResponse)
    assert stats.total_projects == 0
    assert stats.total_interfaces == 0
    assert stats.total_scenarios == 0
    assert stats.total_plans == 0


@pytest.mark.asyncio
async def test_get_core_stats_with_data(
    async_session: AsyncSession,
    test_user,
    test_project,
    test_interface,
    test_scenario,
    test_plan,
):
    """Test getting core stats with sample data."""
    service = DashboardService()
    stats = await service.get_core_stats(async_session, user_id=test_user.id)

    assert isinstance(stats, CoreStatsResponse)
    assert stats.total_projects >= 1
    assert stats.total_interfaces >= 1
    assert stats.total_scenarios >= 1
    assert stats.total_plans >= 1


@pytest.mark.asyncio
async def test_get_execution_trend_empty(async_session: AsyncSession, test_user):
    """Test getting execution trend with no executions."""
    service = DashboardService()
    trend = await service.get_execution_trend(async_session, user_id=test_user.id, days=30)

    assert isinstance(trend, TrendResponse)
    assert len(trend.trend) == 0


@pytest.mark.asyncio
async def test_trend_date_range(async_session: AsyncSession, test_user):
    """Test that trend data respects the date range."""
    service = DashboardService()
    trend = await service.get_execution_trend(async_session, user_id=test_user.id, days=7)

    assert isinstance(trend, TrendResponse)
    # Verify all dates are within the last 7 days
    if len(trend.trend) > 0:
        for point in trend.trend:
            point_date = datetime.strptime(point.date, "%Y-%m-%d").date()
            assert point_date >= (datetime.now() - timedelta(days=7)).date()


@pytest.mark.asyncio
async def test_get_project_coverage_empty(async_session: AsyncSession):
    """Test getting project coverage with no projects."""
    service = DashboardService()
    coverage = await service.get_project_coverage(async_session, user_id=999)

    assert isinstance(coverage, CoverageResponse)
    assert coverage.tested_projects == 0
    assert coverage.untested_projects == 0
    assert coverage.coverage_percentage == 0.0


@pytest.mark.asyncio
async def test_get_project_coverage_with_project(
    async_session: AsyncSession, test_user, test_project
):
    """Test getting project coverage with a project but no executions."""
    service = DashboardService()
    coverage = await service.get_project_coverage(async_session, user_id=test_user.id)

    assert isinstance(coverage, CoverageResponse)
    # Project exists but no executions yet
    assert coverage.tested_projects == 0
    assert coverage.untested_projects >= 1
    assert coverage.coverage_percentage >= 0.0


@pytest.mark.asyncio
async def test_coverage_percentage_calculation(
    async_session: AsyncSession, test_user, test_project
):
    """Test that coverage percentage is calculated correctly."""
    service = DashboardService()
    coverage = await service.get_project_coverage(async_session, user_id=test_user.id)

    assert isinstance(coverage, CoverageResponse)
    total = coverage.tested_projects + coverage.untested_projects

    if total > 0:
        expected_percentage = (coverage.tested_projects / total) * 100
        assert abs(coverage.coverage_percentage - expected_percentage) < 0.01
