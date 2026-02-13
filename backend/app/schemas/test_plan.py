"""Test plan-related schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TestPlanBase(BaseModel):
    """Base test plan schema."""

    name: str = Field(..., min_length=1, max_length=200, description="计划名称")
    description: str | None = Field(None, max_length=1000, description="计划描述")


class TestPlanCreate(TestPlanBase):
    """Test plan creation schema."""

    project_id: int = Field(..., description="所属项目 ID")


class TestPlanUpdate(BaseModel):
    """Test plan update schema."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)


class TestPlanResponse(TestPlanBase):
    """Test plan response schema."""

    id: int
    project_id: int
    project_name: str
    creator_name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestPlanListResponse(BaseModel):
    """Paginated test plan list response."""

    items: list[TestPlanResponse]
    total: int
    page: int
    pageSize: int  # noqa: N815


class ScenarioInPlan(BaseModel):
    """Scenario in plan response schema."""

    id: int
    scenario_id: int
    scenario_name: str
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


class TestPlanDetailResponse(TestPlanResponse):
    """Test plan detail response with scenarios."""

    scenarios: list[ScenarioInPlan] = []
