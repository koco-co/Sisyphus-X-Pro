"""Tests for report service."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_report import TestReport
from app.models.test_execution import TestExecution
from app.services.report_service import ReportService


@pytest.mark.asyncio
async def test_create_report(db_session: AsyncSession, test_execution: TestExecution):
    """Test creating a report from execution."""
    service = ReportService(db_session)

    report = await service.create_report(
        execution_id=test_execution.id,
        plan_id=test_execution.plan_id,
        executor_id=test_execution.executor_id,
        environment_name="Test Environment",
        started_at=datetime.now(),
    )

    assert report.id is not None
    assert report.execution_id == test_execution.id
    assert report.plan_id == test_execution.plan_id
    assert report.total_scenarios == test_execution.total_scenarios
    assert report.passed == test_execution.passed_scenarios
    assert report.failed == test_execution.failed_scenarios


@pytest.mark.asyncio
async def test_get_report_by_id(db_session: AsyncSession, test_report: TestReport):
    """Test getting report by ID."""
    service = ReportService(db_session)

    report = await service.get_report_by_id(test_report.id)

    assert report is not None
    assert report.id == test_report.id
    assert report.execution_id == test_report.execution_id


@pytest.mark.asyncio
async def test_get_report_by_id_not_found(db_session: AsyncSession):
    """Test getting non-existent report."""
    service = ReportService(db_session)

    report = await service.get_report_by_id(99999)

    assert report is None


@pytest.mark.asyncio
async def test_get_reports(db_session: AsyncSession, test_report: TestReport):
    """Test getting paginated reports."""
    service = ReportService(db_session)

    reports, total = await service.get_reports(page=1, limit=10)

    assert len(reports) >= 1
    assert total >= 1
    assert any(r.id == test_report.id for r in reports)


@pytest.mark.asyncio
async def test_get_reports_with_filters(db_session: AsyncSession, test_report: TestReport):
    """Test getting reports with filters."""
    service = ReportService(db_session)

    # Filter by plan_id
    reports, total = await service.get_reports(plan_id=test_report.plan_id, page=1, limit=10)

    assert all(r.plan_id == test_report.plan_id for r in reports)

    # Filter by status
    reports, total = await service.get_reports(status=test_report.status, page=1, limit=10)

    assert all(r.status == test_report.status for r in reports)


@pytest.mark.asyncio
async def test_delete_report(db_session: AsyncSession, test_report: TestReport):
    """Test deleting a report."""
    service = ReportService(db_session)

    deleted = await service.delete_report(test_report.id)

    assert deleted is True

    # Verify deletion
    report = await service.get_report_by_id(test_report.id)
    assert report is None


@pytest.mark.asyncio
async def test_delete_report_not_found(db_session: AsyncSession):
    """Test deleting non-existent report."""
    service = ReportService(db_session)

    deleted = await service.delete_report(99999)

    assert deleted is False


@pytest.mark.asyncio
async def test_cleanup_old_reports(db_session: AsyncSession):
    """Test cleaning up old reports."""
    service = ReportService(db_session)

    # Create an old report
    old_report = TestReport(
        execution_id="old-execution-id",
        plan_id=1,
        status="completed",
        total_scenarios=10,
        passed=10,
        failed=0,
        skipped=0,
        executor_id=1,
        environment_name="Old Environment",
        started_at=datetime.now() - timedelta(days=35),
        created_at=datetime.now() - timedelta(days=35),
    )
    db_session.add(old_report)
    await db_session.commit()

    # Create a recent report
    recent_report = TestReport(
        execution_id="recent-execution-id",
        plan_id=1,
        status="completed",
        total_scenarios=10,
        passed=10,
        failed=0,
        skipped=0,
        executor_id=1,
        environment_name="Recent Environment",
        started_at=datetime.now() - timedelta(days=10),
        created_at=datetime.now() - timedelta(days=10),
    )
    db_session.add(recent_report)
    await db_session.commit()

    # Run cleanup
    deleted_count = await service.cleanup_old_reports(days=30)

    assert deleted_count >= 1

    # Verify old report is deleted
    deleted_report = await service.get_report_by_id(old_report.id)
    assert deleted_report is None

    # Verify recent report still exists
    existing_report = await service.get_report_by_id(recent_report.id)
    assert existing_report is not None


@pytest.mark.asyncio
async def test_get_report_statistics(db_session: AsyncSession, test_report: TestReport):
    """Test getting report statistics."""
    service = ReportService(db_session)

    stats = await service.get_report_statistics()

    assert "total_reports" in stats
    assert "total_scenarios" in stats
    assert "total_passed" in stats
    assert "total_failed" in stats
    assert "total_skipped" in stats
    assert "pass_rate" in stats
    assert stats["total_reports"] >= 1
