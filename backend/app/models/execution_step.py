"""Execution step model."""

from typing import Any, Optional

from sqlalchemy import JSON, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class ExecutionStep(Base, TimestampMixin):
    """Execution step model for tracking step execution details.

    Records detailed execution information for each step including
    request/response data, execution time, and error messages.
    """

    __tablename__ = "execution_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    execution_scenario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("execution_scenarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scenario_steps.id", ondelete="RESTRICT"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending/passed/failed/skipped
    request_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    response_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    elapsed_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 耗时 (毫秒)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = ()

    def __repr__(self) -> str:
        return f"<ExecutionStep(id={self.id}, status={self.status}, elapsed_ms={self.elapsed_ms})>"
