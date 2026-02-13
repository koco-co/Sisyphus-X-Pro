"""Global variable model."""


from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class GlobalVariable(Base, TimestampMixin):
    """Global variable model for project-wide variables.

    Global variables are shared across all scenarios in a project.
    """

    __tablename__ = "global_variables"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(
        String(20), nullable=False, default="manual"
    )  # manual / extracted

    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_project_global_variable"),)

    def __repr__(self) -> str:
        return f"<GlobalVariable(id={self.id}, name={self.name})>"
