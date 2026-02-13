"""Global parameter model."""

from typing import Any

from sqlalchemy import JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class GlobalParam(Base, TimestampMixin):
    """Global parameter model for built-in utility functions.

    Provides reusable Python utility functions that can be used in scenarios.
    Built-in parameters are provided by the system, custom ones can be created.
    """

    __tablename__ = "global_params"

    id: Mapped[int] = mapped_column(primary_key=True)
    class_name: Mapped[str] = mapped_column(String(200), nullable=False)  # 类名 (目录分组)
    method_name: Mapped[str] = mapped_column(String(200), nullable=False)  # 方法名
    description: Mapped[str] = mapped_column(Text, nullable=False)  # 功能描述
    code: Mapped[str] = mapped_column(Text, nullable=False)  # Python 代码
    params_in: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)  # [{name, type, description}]
    params_out: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)  # [{type, description}]
    is_builtin: Mapped[bool] = mapped_column(nullable=False, default=False)

    __table_args__ = (UniqueConstraint("class_name", "method_name", name="uq_class_method"),)

    def __repr__(self) -> str:
        return f"<GlobalParam(id={self.id}, class_name={self.class_name}, method_name={self.method_name})>"
