"""Dataset model."""

from typing import Any

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class Dataset(Base, TimestampMixin):
    """Dataset model for data-driven testing.

    Datasets provide test data for scenarios with multiple test cases.
    """

    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    headers: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)  # 表头 (变量名数组)
    rows: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)  # 二维数据数组

    __table_args__ = ()

    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, name={self.name}, scenario_id={self.scenario_id})>"
