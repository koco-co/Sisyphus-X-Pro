"""Test report model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TestReport(Base):
    """Test report model for test execution results.

    Stores aggregated test results and Allure report metadata.
    Reports are automatically cleaned up after 30 days.
    """

    __tablename__ = "test_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("test_executions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # completed/terminated/paused/failed
    total_scenarios: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    allure_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    allure_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    executor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    environment_name: Mapped[str] = mapped_column(String(100), nullable=False)  # 快照: 运行环境名称
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )

    __table_args__ = ()

    def __repr__(self) -> str:
        return f"<TestReport(id={self.id}, status={self.status}, passed={self.passed}, failed={self.failed})>"
