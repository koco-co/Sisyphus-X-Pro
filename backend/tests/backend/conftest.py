"""Backend test configuration and fixtures."""

import pytest
import pytest_asyncio
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base, get_db
from app.main import app
from app.models.test_execution import TestExecution
from app.models.test_report import TestReport
from app.models.user import User


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncClient:
    """Create async test client with database session override.

    Args:
        db_session: Database session fixture

    Yields:
        AsyncClient: Test client with overridden database dependency
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_execution(db_session: AsyncSession, test_user: User) -> TestExecution:
    """Create test execution."""
    execution = TestExecution(
        plan_id=1,
        environment_id=1,
        executor_id=test_user.id,
        status="completed",
        total_scenarios=10,
        passed_scenarios=8,
        failed_scenarios=1,
        skipped_scenarios=1,
        started_at=datetime.now(),
        finished_at=datetime.now(),
    )
    db_session.add(execution)
    await db_session.commit()
    await db_session.refresh(execution)
    return execution


@pytest_asyncio.fixture
async def test_report(db_session: AsyncSession, test_execution: TestExecution) -> TestReport:
    """Create test report."""
    report = TestReport(
        execution_id=test_execution.id,
        plan_id=test_execution.plan_id,
        status="completed",
        total_scenarios=test_execution.total_scenarios,
        passed=test_execution.passed_scenarios,
        failed=test_execution.failed_scenarios,
        skipped=test_execution.skipped_scenarios,
        duration_seconds=120.5,
        executor_id=test_execution.executor_id,
        environment_name="Test Environment",
        started_at=datetime.now(),
        finished_at=datetime.now(),
    )
    db_session.add(report)
    await db_session.commit()
    await db_session.refresh(report)
    return report


