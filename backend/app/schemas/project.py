"""Project-related schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    """Base project schema."""

    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    description: str | None = Field(None, max_length=1000, description="项目描述")


class ProjectCreate(ProjectBase):
    """Project creation schema."""

    pass


class ProjectUpdate(BaseModel):
    """Project update schema."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)


class ProjectResponse(ProjectBase):
    """Project response schema."""

    id: int
    creator_name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Paginated project list response."""

    items: list[ProjectResponse]
    total: int
    page: int
    pageSize: int  # noqa: N815
