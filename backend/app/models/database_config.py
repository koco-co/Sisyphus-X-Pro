"""Database configuration model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class DatabaseConfig(Base, TimestampMixin):
    """Database configuration model for testing database connections.

    Stores encrypted database credentials for MySQL and PostgreSQL connections.
    """

    __tablename__ = "database_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    variable_name: Mapped[str] = mapped_column(String(100), nullable=False)
    db_type: Mapped[str] = mapped_column(String(20), nullable=False)  # mysql / postgresql
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    database: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(500), nullable=False)  # Encrypted
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_connected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("project_id", "variable_name", name="uq_project_variable"),)

    def __repr__(self) -> str:
        return (
            f"<DatabaseConfig(id={self.id}, name={self.name}, variable_name={self.variable_name})>"
        )
