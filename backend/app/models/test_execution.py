"""Test execution model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TestExecution(Base):
    """Test execution model for tracking test runs.

    Records the execution of a test plan with status and statistics.
    Uses UUID as primary key for security and uniqueness.
    """

    __tablename__ = "test_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    environment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("environments.id", ondelete="RESTRICT"), nullable=False
    )
    executor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )  # pending/running/completed/terminated/paused/failed
    total_scenarios: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed_scenarios: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_scenarios: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_scenarios: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )

    __table_args__ = ()

    # Relationships
    executor = relationship("User", back_populates="test_executions")

    def __repr__(self) -> str:
        return f"<TestExecution(id={self.id}, status={self.status})>"
