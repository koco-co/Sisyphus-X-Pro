"""Interface model."""

from typing import Any, Optional

from sqlalchemy import JSON, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class Interface(Base, TimestampMixin):
    """Interface model for API endpoint definitions.

    Stores HTTP request details including method, path, headers, parameters, and body.
    """

    __tablename__ = "interfaces"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    folder_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("interface_folders.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)  # GET/POST/PUT/DELETE/PATCH
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    headers: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)
    params: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)  # Query parameters
    body: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, default=dict)
    body_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="json"
    )  # json/form-data/raw
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (Index("ix_interfaces_project_folder", "project_id", "folder_id"),)

    def __repr__(self) -> str:
        return (
            f"<Interface(id={self.id}, name={self.name}, method={self.method}, path={self.path})>"
        )
