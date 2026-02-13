"""Test plan model."""

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.database import Base
from app.models.base import TimestampMixin


class TestPlan(Base, TimestampMixin):
    """Test plan model for organizing test execution.

    A test plan contains multiple scenarios to be executed together.
    """

    __tablename__ = "test_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = ()

    def __repr__(self) -> str:
        return f"<TestPlan(id={self.id}, name={self.name})>"
