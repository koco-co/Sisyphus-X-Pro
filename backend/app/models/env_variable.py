"""Environment variable model."""

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.database import Base
from app.models.base import TimestampMixin


class EnvVariable(Base, TimestampMixin):
    """Environment variable model for environment-specific variables.

    Variables can be manually defined or extracted from API responses.
    """

    __tablename__ = "env_variables"

    id: Mapped[int] = mapped_column(primary_key=True)
    environment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(
        String(20), nullable=False, default="manual"
    )  # manual / extracted

    __table_args__ = (UniqueConstraint("environment_id", "name", name="uq_environment_variable"),)

    def __repr__(self) -> str:
        return f"<EnvVariable(id={self.id}, name={self.name}, source={self.source})>"
