"""Scenario step model."""

from typing import Any, Optional

from sqlalchemy import JSON, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class ScenarioStep(Base, TimestampMixin):
    """Scenario step model for individual test steps in a scenario.

    Each step uses a keyword and can have dynamic parameters.
    """

    __tablename__ = "scenario_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    keyword_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("keywords.id", ondelete="RESTRICT"), nullable=False
    )
    params: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)  # 动态关键字参数

    # Relationships
    scenario = relationship("Scenario", back_populates="steps")

    __table_args__ = (Index("ix_scenario_steps_scenario_order", "scenario_id", "sort_order"),)

    def __repr__(self) -> str:
        return f"<ScenarioStep(id={self.id}, scenario_id={self.scenario_id}, sort_order={self.sort_order})>"
