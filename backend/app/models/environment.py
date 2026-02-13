"""Environment model."""

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class Environment(Base, TimestampMixin):
    """Environment model for different deployment environments.

    Each project can have multiple environments (dev, staging, prod)
    with different base URLs and environment variables.
    """

    __tablename__ = "environments"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)

    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_project_environment"),)

    def __repr__(self) -> str:
        return f"<Environment(id={self.id}, name={self.name}, base_url={self.base_url})>"
