"""Tests for database connection scheduler."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database_config import DatabaseConfig
from app.services.db_connection_scheduler import DBConnectionScheduler


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def mock_session_factory(mock_session):
    """Create a mock session factory."""
    def _factory():
        return mock_session
    return _factory


@pytest.fixture
def db_connection_scheduler(mock_session_factory):
    """Create a database connection scheduler fixture."""
    return DBConnectionScheduler(mock_session_factory)


@pytest.fixture
def mock_configs():
    """Create mock database configs."""
    configs = [
        MagicMock(
            spec=DatabaseConfig,
            id=1,
            project_id=1,
            name="Test MySQL",
            variable_name="test_mysql",
            db_type="mysql",
            host="localhost",
            port=3306,
            database="testdb",
            username="root",
            password="password",
            is_enabled=True,
            is_connected=False,
            last_check_at=None,
            last_error=None,
        ),
        MagicMock(
            spec=DatabaseConfig,
            id=2,
            project_id=1,
            name="Test PostgreSQL",
            variable_name="test_postgres",
            db_type="postgresql",
            host="localhost",
            port=5432,
            database="testdb",
            username="postgres",
            password="password",
            is_enabled=True,
            is_connected=False,
            last_check_at=None,
            last_error=None,
        ),
    ]
    return configs


@pytest.mark.asyncio
async def test_init_scheduler(db_connection_scheduler):
    """Test scheduler initialization."""
    assert db_connection_scheduler.check_interval_minutes == 10
    assert db_connection_scheduler.scheduler is not None


@pytest.mark.asyncio
async def test_start_scheduler(db_connection_scheduler):
    """Test starting the scheduler."""
    db_connection_scheduler.start()

    assert db_connection_scheduler.scheduler.running is True

    # Check job was added
    jobs = db_connection_scheduler.scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == "check_db_connections"

    # Cleanup
    db_connection_scheduler.shutdown()


@pytest.mark.asyncio
async def test_shutdown_scheduler(db_connection_scheduler):
    """Test shutting down the scheduler."""
    db_connection_scheduler.start()
    await db_connection_scheduler.scheduler.shutdown(wait=True)

    assert db_connection_scheduler.scheduler.running is False


@pytest.mark.asyncio
async def test_check_all_connections_success(
    db_connection_scheduler, mock_configs, mock_session_factory
):
    """Test checking all connections successfully."""
    # Mock the service and its methods
    mock_service = MagicMock()
    mock_service.get_all_configs = AsyncMock(return_value=mock_configs)
    mock_service.test_connection = AsyncMock(return_value=(True, "连接成功"))
    mock_service.update_connection_status = AsyncMock()

    with patch(
        "app.services.db_connection_scheduler.DatabaseConfigService",
        return_value=mock_service,
    ):
        await db_connection_scheduler._check_all_connections()

        # Verify all configs were checked
        assert mock_service.test_connection.call_count == 2
        assert mock_service.update_connection_status.call_count == 2


@pytest.mark.asyncio
async def test_check_all_connections_with_failure(
    db_connection_scheduler, mock_configs, mock_session_factory
):
    """Test checking all connections with some failures."""
    # Mock the service
    mock_service = MagicMock()
    mock_service.get_all_configs = AsyncMock(return_value=mock_configs)

    # First connection succeeds, second fails
    async def mock_test_connection(*args, **kwargs):
        if mock_service.test_connection.call_count == 1:
            return True, "连接成功"
        else:
            return False, "连接超时"

    mock_service.test_connection = AsyncMock(side_effect=mock_test_connection)
    mock_service.update_connection_status = AsyncMock()

    with patch(
        "app.services.db_connection_scheduler.DatabaseConfigService",
        return_value=mock_service,
    ):
        await db_connection_scheduler._check_all_connections()

        # Verify both configs were checked and updated
        assert mock_service.test_connection.call_count == 2
        assert mock_service.update_connection_status.call_count == 2

        # Verify update calls with correct parameters
        first_call = mock_service.update_connection_status.call_args_list[0]
        assert first_call[1]["is_connected"] is True
        assert first_call[1]["last_error"] is None

        second_call = mock_service.update_connection_status.call_args_list[1]
        assert second_call[1]["is_connected"] is False
        assert second_call[1]["last_error"] == "连接超时"


@pytest.mark.asyncio
async def test_check_now(db_connection_scheduler, mock_configs, mock_session_factory):
    """Test manually triggering connection check."""
    mock_service = MagicMock()
    mock_service.get_all_configs = AsyncMock(return_value=mock_configs)
    mock_service.test_connection = AsyncMock(return_value=(True, "连接成功"))
    mock_service.update_connection_status = AsyncMock()

    with patch(
        "app.services.db_connection_scheduler.DatabaseConfigService",
        return_value=mock_service,
    ):
        result = await db_connection_scheduler.check_now()

        assert result["success_count"] == 2
        assert result["failure_count"] == 0


@pytest.mark.asyncio
async def test_set_check_interval(db_connection_scheduler):
    """Test setting check interval."""
    db_connection_scheduler.set_check_interval(5)

    assert db_connection_scheduler.check_interval_minutes == 5


def test_set_check_interval_invalid(db_connection_scheduler):
    """Test setting invalid check interval."""
    with pytest.raises(ValueError, match="Check interval must be at least 1 minute"):
        db_connection_scheduler.set_check_interval(0)


@pytest.mark.asyncio
async def test_set_check_interval_reschedules_job(db_connection_scheduler):
    """Test that setting interval reschedules the job."""
    db_connection_scheduler.start()

    # Change interval
    db_connection_scheduler.set_check_interval(15)

    # Verify job was rescheduled
    jobs = db_connection_scheduler.scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].trigger.interval.total_seconds() == 15 * 60

    # Cleanup
    db_connection_scheduler.shutdown()


@pytest.mark.asyncio
async def test_check_now_with_mixed_results(
    db_connection_scheduler, mock_configs, mock_session_factory
):
    """Test manually triggering connection check with mixed results."""
    mock_service = MagicMock()
    mock_service.get_all_configs = AsyncMock(return_value=mock_configs)

    # First succeeds, second fails
    async def mock_test_connection(*args, **kwargs):
        if mock_service.test_connection.call_count == 1:
            return True, "连接成功"
        else:
            return False, "认证失败"

    mock_service.test_connection = AsyncMock(side_effect=mock_test_connection)
    mock_service.update_connection_status = AsyncMock()

    with patch(
        "app.services.db_connection_scheduler.DatabaseConfigService",
        return_value=mock_service,
    ):
        result = await db_connection_scheduler.check_now()

        assert result["success_count"] == 1
        assert result["failure_count"] == 1


@pytest.mark.asyncio
async def test_scheduler_multiple_starts(db_connection_scheduler):
    """Test starting scheduler multiple times doesn't create duplicate jobs."""
    db_connection_scheduler.start()
    db_connection_scheduler.start()  # Should not create duplicate jobs

    jobs = db_connection_scheduler.scheduler.get_jobs()
    assert len(jobs) == 1

    # Cleanup
    db_connection_scheduler.shutdown()
