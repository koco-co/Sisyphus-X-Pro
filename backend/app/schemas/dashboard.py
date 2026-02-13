"""Dashboard schemas."""

from pydantic import BaseModel


class CoreStatsResponse(BaseModel):
    """Core statistics response."""

    total_projects: int
    total_interfaces: int
    total_scenarios: int
    total_plans: int


class TrendDataPoint(BaseModel):
    """Single data point in trend chart."""

    date: str  # YYYY-MM-DD format
    count: int


class TrendResponse(BaseModel):
    """Test execution trend response."""

    trend: list[TrendDataPoint]


class CoverageResponse(BaseModel):
    """Project coverage response."""

    tested_projects: int
    untested_projects: int
    coverage_percentage: float
