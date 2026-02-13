"""Keyword model."""

from typing import Any

from sqlalchemy import JSON, Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class Keyword(Base, TimestampMixin):
    """Keyword model for reusable test actions.

    Keywords are predefined code blocks that can be used in scenario steps.
    Built-in keywords are provided by the system, custom keywords can be created by users.
    """

    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # 发送请求/断言类型/提取变量/数据库操作
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    method_name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    params: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, default=dict
    )  # [{name, description}]
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    __table_args__ = (
        UniqueConstraint("method_name", name="uq_method_name"),
    )

    def __repr__(self) -> str:
        return f"<Keyword(id={self.id}, type={self.type}, name={self.name}, method_name={self.method_name})>"
