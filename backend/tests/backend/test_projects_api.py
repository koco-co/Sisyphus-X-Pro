"""Unit tests for Project API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_projects_empty(client: AsyncClient, test_token: str):
    """Test listing projects when database is empty."""
    response = await client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, test_token: str):
    """Test creating a new project."""
    response = await client.post(
        "/api/projects",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"name": "Test Project", "description": "Test Description"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_project_missing_name(client: AsyncClient, test_token: str):
    """Test creating project without name fails."""
    response = await client.post(
        "/api/projects",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"description": "Test Description"},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, test_token: str, test_project):
    """Test getting a project by ID."""
    response = await client.get(
        f"/api/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_project.id
    assert data["name"] == test_project.name


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient, test_token: str):
    """Test getting non-existent project returns 404."""
    response = await client.get(
        "/api/projects/99999",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, test_token: str, test_project):
    """Test updating a project."""
    response = await client.put(
        f"/api/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"name": "Updated Project", "description": "Updated Description"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"
    assert data["description"] == "Updated Description"


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, test_token: str, test_project):
    """Test deleting a project."""
    response = await client.delete(
        f"/api/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 204

    # Verify project is deleted
    get_response = await client.get(
        f"/api/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_search_projects(client: AsyncClient, test_token: str):
    """Test searching projects by name."""
    # Create projects
    await client.post(
        "/api/projects",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"name": "Alpha Project"},
    )
    await client.post(
        "/api/projects",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"name": "Beta Project"},
    )

    # Search for "Alpha"
    response = await client.get(
        "/api/projects?name=Alpha",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(p["name"] == "Alpha Project" for p in data["items"])
