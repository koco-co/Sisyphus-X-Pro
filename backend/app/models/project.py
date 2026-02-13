"""Project model."""

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.database import Base
from app.models.base import TimestampMixin


class Project(Base, TimestampMixin):
    """Project model for organizing testing resources."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    creator = relationship("User", lazy="joined")

    __table_args__ = ()

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name})>"
