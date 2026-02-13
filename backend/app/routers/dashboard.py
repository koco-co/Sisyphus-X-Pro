"""Dashboard router."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.dashboard import (
    CoreStatsResponse,
    CoverageResponse,
    TrendResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
dashboard_service = DashboardService()


async def get_current_user_id() -> int:
    """
    Get current user ID from request.

    In production, this would decode JWT token.
    For development mode, returns a default user.
    """
    # TODO: Implement proper JWT token decoding
    # For now, return user_id=1 for development
    return 1


@router.get("/stats", response_model=CoreStatsResponse)
async def get_core_stats(
    session: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get core statistics for dashboard.

    Returns counts of projects, interfaces, scenarios, and test plans.
    """
    stats = await dashboard_service.get_core_stats(session, user_id)
    return stats


@router.get("/trend", response_model=TrendResponse)
async def get_execution_trend(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    session: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get test execution trend.

    Returns daily execution counts for the specified time period.
    """
    trend = await dashboard_service.get_execution_trend(session, user_id, days)
    return trend


@router.get("/coverage", response_model=CoverageResponse)
async def get_project_coverage(
    session: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get project coverage statistics.

    Returns tested/untested project counts and coverage percentage.
    """
    coverage = await dashboard_service.get_project_coverage(session, user_id)
    return coverage
