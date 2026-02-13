"""Tests for reports API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_reports(async_client: AsyncClient, test_report):
    """Test getting reports list."""
    response = await async_client.get("/api/v1/reports")

    assert response.status_code == 200
    data = response.json()
    assert "reports" in data
    assert "total" in data
    assert len(data["reports"]) >= 1


@pytest.mark.asyncio
async def test_get_reports_with_pagination(async_client: AsyncClient, test_report):
    """Test getting reports with pagination."""
    response = await async_client.get("/api/v1/reports?page=1&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 10


@pytest.mark.asyncio
async def test_get_reports_with_filters(async_client: AsyncClient, test_report):
    """Test getting reports with filters."""
    response = await async_client.get(
        f"/api/v1/reports?plan_id={test_report.plan_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert all(r["plan_id"] == test_report.plan_id for r in data["reports"])


@pytest.mark.asyncio
async def test_get_report_by_id(async_client: AsyncClient, test_report):
    """Test getting report by ID."""
    response = await async_client.get(f"/api/v1/reports/{test_report.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_report.id
    assert data["execution_id"] == test_report.execution_id


@pytest.mark.asyncio
async def test_get_report_not_found(async_client: AsyncClient):
    """Test getting non-existent report."""
    response = await async_client.get("/api/v1/reports/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_report_statistics(async_client: AsyncClient, test_report):
    """Test getting report statistics."""
    response = await async_client.get("/api/v1/reports/statistics")

    assert response.status_code == 200
    data = response.json()
    assert "total_reports" in data
    assert "pass_rate" in data
    assert data["total_reports"] >= 1


@pytest.mark.asyncio
async def test_delete_report(async_client: AsyncClient, test_report):
    """Test deleting a report."""
    response = await async_client.delete(f"/api/v1/reports/{test_report.id}")

    assert response.status_code == 204

    # Verify deletion
    response = await async_client.get(f"/api/v1/reports/{test_report.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_report_not_found(async_client: AsyncClient):
    """Test deleting non-existent report."""
    response = await async_client.delete("/api/v1/reports/99999")

    assert response.status_code == 404
