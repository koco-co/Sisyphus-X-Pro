"""Scenario schemas for request/response validation."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ScenarioStepBase(BaseModel):
    """Base schema for scenario step."""

    description: str = Field(..., min_length=1, max_length=500, description="步骤描述")
    keyword_id: int = Field(..., gt=0, description="关键字ID")
    params: dict[str, Any] = Field(default_factory=dict, description="关键字参数")


class ScenarioStepCreate(ScenarioStepBase):
    """Schema for creating a scenario step."""

    sort_order: int = Field(0, ge=0, description="排序顺序")


class ScenarioStepUpdate(BaseModel):
    """Schema for updating a scenario step."""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    keyword_id: Optional[int] = Field(None, gt=0)
    params: Optional[dict[str, Any]] = None
    sort_order: Optional[int] = Field(None, ge=0)


class ScenarioStepResponse(ScenarioStepBase):
    """Schema for scenario step response."""

    id: int
    scenario_id: int
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScenarioBase(BaseModel):
    """Base schema for scenario."""

    name: str = Field(..., min_length=1, max_length=200, description="场景名称")
    description: Optional[str] = Field(None, max_length=1000, description="场景描述")
    priority: str = Field("P2", pattern="^P[0-3]$", description="优先级 (P0/P1/P2/P3)")
    tags: dict[str, Any] = Field(default_factory=dict, description="标签")
    pre_sql: Optional[str] = Field(None, description="前置SQL")
    post_sql: Optional[str] = Field(None, description="后置SQL")
    variables: dict[str, Any] = Field(default_factory=dict, description="变量定义")
    environment_id: Optional[int] = Field(None, gt=0, description="环境ID")


class ScenarioCreate(ScenarioBase):
    """Schema for creating a scenario."""

    project_id: int = Field(..., gt=0, description="项目ID")
    steps: list[ScenarioStepCreate] = Field(default_factory=list, description="场景步骤")


class ScenarioUpdate(BaseModel):
    """Schema for updating a scenario."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^P[0-3]$")
    tags: Optional[dict[str, Any]] = None
    pre_sql: Optional[str] = None
    post_sql: Optional[str] = None
    variables: Optional[dict[str, Any]] = None
    environment_id: Optional[int] = Field(None, gt=0)


class ScenarioResponse(ScenarioBase):
    """Schema for scenario response."""

    id: int
    project_id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    steps: list[ScenarioStepResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ScenarioListResponse(BaseModel):
    """Schema for scenario list response."""

    id: int
    name: str
    description: Optional[str]
    priority: str
    tags: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    step_count: int = Field(0, description="步骤数量")

    class Config:
        from_attributes = True


class StepReorderRequest(BaseModel):
    """Schema for reordering steps."""

    step_ids: list[int] = Field(..., min_length=1, description="步骤ID列表(新顺序)")


class DatasetBase(BaseModel):
    """Base schema for dataset."""

    name: str = Field(..., min_length=1, max_length=200, description="数据集名称")
    headers: list[str] = Field(..., description="表头 (变量名数组)")
    rows: list[list[str]] = Field(..., description="数据行 (二维数组)")


class DatasetCreate(DatasetBase):
    """Schema for creating a dataset."""

    scenario_id: int = Field(..., gt=0, description="场景ID")


class DatasetResponse(DatasetBase):
    """Schema for dataset response."""

    id: int
    scenario_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CSVUploadResponse(BaseModel):
    """Schema for CSV upload response."""

    dataset: DatasetResponse
    rows_count: int = Field(..., description="导入的数据行数")
