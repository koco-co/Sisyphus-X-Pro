"""Report scheduler for automated cleanup tasks."""

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.report_service import ReportService


class ReportScheduler:
    """Scheduler for automated report cleanup."""

    def __init__(self, session_factory) -> None:
        """Initialize report scheduler.

        Args:
            session_factory: Database session factory
        """
        self.scheduler = AsyncIOScheduler()
        self.session_factory = session_factory
        self.retention_days = 30  # Default retention period

    def start(self) -> None:
        """Start the scheduler."""
        # Schedule cleanup task to run daily at 2 AM
        self.scheduler.add_job(
            self._cleanup_old_reports,
            "cron",
            hour=2,
            minute=0,
            id="cleanup_old_reports",
            replace_existing=True,
        )
        self.scheduler.start()
        print("✓ Report scheduler started (cleanup runs daily at 2 AM)")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown(wait=True)
        print("✓ Report scheduler stopped")

    async def _cleanup_old_reports(self) -> None:
        """Cleanup old reports task.

        This runs automatically every day at 2 AM.
        """
        print(f"[{datetime.now()}] Starting report cleanup...")

        async with self.session_factory() as session:
            service = ReportService(session)
            deleted_count = await service.cleanup_old_reports(days=self.retention_days)

        print(f"[{datetime.now()}] Cleanup completed: {deleted_count} old reports deleted")

    def set_retention_days(self, days: int) -> None:
        """Set report retention period.

        Args:
            days: Number of days to retain reports
        """
        if days < 1:
            raise ValueError("Retention days must be at least 1")
        self.retention_days = days
        print(f"✓ Report retention set to {days} days")

    async def cleanup_now(self) -> int:
        """Run cleanup task immediately (for testing or manual trigger).

        Returns:
            Number of deleted reports
        """
        async with self.session_factory() as session:
            service = ReportService(session)
            deleted_count = await service.cleanup_old_reports(days=self.retention_days)
        return deleted_count


# Global scheduler instance
_report_scheduler: ReportScheduler | None = None


def init_report_scheduler(session_factory) -> ReportScheduler:
    """Initialize the global report scheduler.

    Args:
        session_factory: Database session factory

    Returns:
        ReportScheduler instance
    """
    global _report_scheduler
    if _report_scheduler is None:
        _report_scheduler = ReportScheduler(session_factory)
        _report_scheduler.start()
    return _report_scheduler


def get_report_scheduler() -> ReportScheduler | None:
    """Get the global report scheduler instance.

    Returns:
        ReportScheduler instance or None
    """
    return _report_scheduler


def shutdown_report_scheduler() -> None:
    """Shutdown the global report scheduler."""
    global _report_scheduler
    if _report_scheduler is not None:
        _report_scheduler.shutdown()
        _report_scheduler = None
