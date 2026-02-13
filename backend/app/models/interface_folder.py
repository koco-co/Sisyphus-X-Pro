"""Interface folder model."""


from sqlalchemy import ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class InterfaceFolder(Base, TimestampMixin):
    """Interface folder model for organizing API interfaces hierarchically."""

    __tablename__ = "interface_folders"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("interface_folders.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(nullable=False)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)

    __table_args__ = (Index("ix_interface_folders_project_parent", "project_id", "parent_id"),)

    def __repr__(self) -> str:
        return f"<InterfaceFolder(id={self.id}, name={self.name}, parent_id={self.parent_id})>"
