"""Report schemas for request and response models."""

from datetime import datetime

from pydantic import BaseModel, Field


class ReportBase(BaseModel):
    """Base report schema."""

    total_scenarios: int = Field(..., ge=0, description="Total number of scenarios")
    passed: int = Field(..., ge=0, description="Number of passed scenarios")
    failed: int = Field(..., ge=0, description="Number of failed scenarios")
    skipped: int = Field(..., ge=0, description="Number of skipped scenarios")
    duration_seconds: float | None = Field(None, ge=0, description="Duration in seconds")


class ReportCreate(ReportBase):
    """Schema for creating a report."""

    execution_id: str = Field(..., description="Execution ID")
    plan_id: int = Field(..., description="Test plan ID")
    status: str = Field(..., description="Execution status")
    executor_id: int = Field(..., description="Executor user ID")
    environment_name: str = Field(..., description="Environment name")
    started_at: datetime = Field(..., description="Execution start time")
    finished_at: datetime | None = Field(None, description="Execution finish time")
    allure_path: str | None = Field(None, description="Allure report path")


class ReportUpdate(BaseModel):
    """Schema for updating a report."""

    status: str | None = None
    total_scenarios: int | None = None
    passed: int | None = None
    failed: int | None = None
    skipped: int | None = None
    duration_seconds: float | None = None
    finished_at: datetime | None = None


class ReportResponse(ReportBase):
    """Schema for report response."""

    id: int
    execution_id: str
    plan_id: int
    status: str
    executor_id: int
    environment_name: str
    started_at: datetime
    finished_at: datetime | None
    allure_path: str | None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ReportListResponse(BaseModel):
    """Schema for report list response."""

    reports: list[ReportResponse]
    total: int
    page: int
    limit: int


class ReportExportRequest(BaseModel):
    """Schema for report export request."""

    format: str = Field(..., description="Export format: pdf, excel, or html")
    include_details: bool = Field(True, description="Include execution details")


class ReportStatistics(BaseModel):
    """Schema for report statistics."""

    total_reports: int
    total_scenarios: int
    total_passed: int
    total_failed: int
    total_skipped: int
    pass_rate: float = Field(..., description="Pass rate as percentage")
    average_duration: float | None = Field(None, description="Average duration in seconds")


class AllureReportResponse(BaseModel):
    """Schema for Allure report URL response."""

    url: str
    expires_at: datetime | None = Field(None, description="URL expiration time")
