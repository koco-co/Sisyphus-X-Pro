"""Plan-scenario association model."""

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class PlanScenario(Base, TimestampMixin):
    """Association model for test plans and scenarios.

    Defines which scenarios are included in a test plan and their execution order.
    """

    __tablename__ = "plan_scenarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_plans.id", ondelete="CASCADE"), nullable=False
    )
    scenario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("plan_id", "scenario_id", name="uq_plan_scenario"),)

    def __repr__(self) -> str:
        return (
            f"<PlanScenario(id={self.id}, plan_id={self.plan_id}, scenario_id={self.scenario_id})>"
        )
