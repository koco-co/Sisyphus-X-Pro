"""Scenario model."""

from typing import Any, Optional

from sqlalchemy import JSON, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class Scenario(Base, TimestampMixin):
    """Scenario model for test scenarios.

    A scenario is a sequence of test steps that verify a specific behavior.
    """

    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(
        String(5), nullable=False, default="P2", index=True
    )  # P0/P1/P2/P3
    tags: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)  # 标签数组
    pre_sql: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 前置 SQL
    post_sql: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 后置 SQL
    variables: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)  # 变量定义列表
    environment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("environments.id", ondelete="SET NULL"), nullable=True
    )
    creator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    steps = relationship("ScenarioStep", back_populates="scenario", cascade="all, delete-orphan")

    __table_args__ = ()

    def __repr__(self) -> str:
        return f"<Scenario(id={self.id}, name={self.name}, priority={self.priority})>"
