"""Database connection status scheduler for automated health checks."""

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.db_config_service import DatabaseConfigService


class DBConnectionScheduler:
    """Scheduler for automated database connection status checks."""

    def __init__(self, session_factory) -> None:
        """Initialize database connection scheduler.

        Args:
            session_factory: Database session factory
        """
        self.scheduler = AsyncIOScheduler()
        self.session_factory = session_factory
        self.check_interval_minutes = 10  # Default check interval

    def start(self) -> None:
        """Start the scheduler."""
        # Schedule connection check task to run every 10 minutes
        self.scheduler.add_job(
            self._check_all_connections,
            "interval",
            minutes=self.check_interval_minutes,
            id="check_db_connections",
            replace_existing=True,
        )
        self.scheduler.start()
        print(f"✓ DB connection scheduler started (checks every {self.check_interval_minutes} minutes)")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown(wait=True)
        print("✓ DB connection scheduler stopped")

    async def _check_all_connections(self) -> None:
        """Check all database connections task.

        This runs automatically every 10 minutes.
        """
        print(f"[{datetime.now()}] Starting database connection health check...")

        async with self.session_factory() as session:
            service = DatabaseConfigService(session)
            configs = await service.get_all_configs()

            success_count = 0
            failure_count = 0

            for config in configs:
                if config.is_enabled:
                    success, message = await service.test_connection(
                        db_type=config.db_type,
                        host=config.host,
                        port=config.port,
                        database=config.database,
                        username=config.username,
                        password=config.password,
                    )

                    # Update connection status
                    await service.update_connection_status(
                        config_id=config.id,
                        is_connected=success,
                        last_error=message if not success else None,
                    )

                    if success:
                        success_count += 1
                    else:
                        failure_count += 1

        print(f"[{datetime.now()}] Health check completed: {success_count} OK, {failure_count} failed")

    def set_check_interval(self, minutes: int) -> None:
        """Set connection check interval.

        Args:
            minutes: Check interval in minutes
        """
        if minutes < 1:
            raise ValueError("Check interval must be at least 1 minute")
        self.check_interval_minutes = minutes

        # Reschedule job with new interval
        self.scheduler.reschedule_job(
            "check_db_connections",
            trigger="interval",
            minutes=minutes,
        )
        print(f"✓ DB connection check interval set to {minutes} minutes")

    async def check_now(self) -> dict[str, int]:
        """Run connection check task immediately (for testing or manual trigger).

        Returns:
            Dictionary with success_count and failure_count
        """
        async with self.session_factory() as session:
            service = DatabaseConfigService(session)
            configs = await service.get_all_configs()

            success_count = 0
            failure_count = 0

            for config in configs:
                if config.is_enabled:
                    success, message = await service.test_connection(
                        db_type=config.db_type,
                        host=config.host,
                        port=config.port,
                        database=config.database,
                        username=config.username,
                        password=config.password,
                    )

                    # Update connection status
                    await service.update_connection_status(
                        config_id=config.id,
                        is_connected=success,
                        last_error=message if not success else None,
                    )

                    if success:
                        success_count += 1
                    else:
                        failure_count += 1

        return {"success_count": success_count, "failure_count": failure_count}


# Global scheduler instance
_db_connection_scheduler: DBConnectionScheduler | None = None


def init_db_connection_scheduler(session_factory) -> DBConnectionScheduler:
    """Initialize the global database connection scheduler.

    Args:
        session_factory: Database session factory

    Returns:
        DBConnectionScheduler instance
    """
    global _db_connection_scheduler
    if _db_connection_scheduler is None:
        _db_connection_scheduler = DBConnectionScheduler(session_factory)
        _db_connection_scheduler.start()
    return _db_connection_scheduler


def get_db_connection_scheduler() -> DBConnectionScheduler | None:
    """Get the global database connection scheduler instance.

    Returns:
        DBConnectionScheduler instance or None
    """
    return _db_connection_scheduler


def shutdown_db_connection_scheduler() -> None:
    """Shutdown the global database connection scheduler."""
    global _db_connection_scheduler
    if _db_connection_scheduler is not None:
        _db_connection_scheduler.shutdown()
        _db_connection_scheduler = None
