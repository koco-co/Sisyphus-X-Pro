"""Unit tests for Project service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService


@pytest.mark.asyncio
async def test_list_projects_empty(db_session: AsyncSession, test_user: User):
    """Test listing projects when database is empty."""
    service = ProjectService(db_session)
    projects, total = await service.list_projects()

    assert total == 0
    assert len(projects) == 0


@pytest.mark.asyncio
async def test_create_project(db_session: AsyncSession, test_user: User):
    """Test creating a new project."""
    service = ProjectService(db_session)
    project_in = ProjectCreate(name="Test Project", description="Test Description")

    project = await service.create_project(project_in, test_user.id)

    assert project.id is not None
    assert project.name == "Test Project"
    assert project.description == "Test Description"
    assert project.creator_id == test_user.id


@pytest.mark.asyncio
async def test_create_project_duplicate_name(db_session: AsyncSession, test_user: User):
    """Test creating a project with duplicate name raises error."""
    service = ProjectService(db_session)
    project_in = ProjectCreate(name="Test Project", description="Test Description")

    # Create first project
    await service.create_project(project_in, test_user.id)

    # Try to create duplicate
    with pytest.raises(ValueError, match="Project with this name already exists"):
        await service.create_project(project_in, test_user.id)


@pytest.mark.asyncio
async def test_get_project_by_id(db_session: AsyncSession, test_user: User):
    """Test getting project by ID."""
    service = ProjectService(db_session)
    project_in = ProjectCreate(name="Test Project", description="Test Description")

    created = await service.create_project(project_in, test_user.id)
    fetched = await service.get_project_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Test Project"
    assert fetched.description == "Test Description"


@pytest.mark.asyncio
async def test_get_project_by_id_not_found(db_session: AsyncSession):
    """Test getting non-existent project returns None."""
    service = ProjectService(db_session)
    project = await service.get_project_by_id(99999)

    assert project is None


@pytest.mark.asyncio
async def test_update_project(db_session: AsyncSession, test_user: User):
    """Test updating a project."""
    service = ProjectService(db_session)
    project_in = ProjectCreate(name="Test Project", description="Test Description")

    created = await service.create_project(project_in, test_user.id)
    update_data = ProjectUpdate(name="Updated Project", description="Updated Description")

    updated = await service.update_project(created.id, update_data)

    assert updated.id == created.id
    assert updated.name == "Updated Project"
    assert updated.description == "Updated Description"


@pytest.mark.asyncio
async def test_delete_project(db_session: AsyncSession, test_user: User):
    """Test deleting a project."""
    service = ProjectService(db_session)
    project_in = ProjectCreate(name="Test Project", description="Test Description")

    created = await service.create_project(project_in, test_user.id)
    deleted = await service.delete_project(created.id)

    assert deleted is True

    # Verify project is deleted
    project = await service.get_project_by_id(created.id)
    assert project is None


@pytest.mark.asyncio
async def test_list_projects_with_search(db_session: AsyncSession, test_user: User):
    """Test listing projects with name search."""
    service = ProjectService(db_session)

    # Create multiple projects
    await service.create_project(ProjectCreate(name="Alpha Project"), test_user.id)
    await service.create_project(ProjectCreate(name="Beta Project"), test_user.id)
    await service.create_project(ProjectCreate(name="Gamma Project"), test_user.id)

    # Search for "Alpha"
    projects, total = await service.list_projects(name="Alpha")

    assert total == 1
    assert len(projects) == 1
    assert projects[0].name == "Alpha Project"


@pytest.mark.asyncio
async def test_list_projects_pagination(db_session: AsyncSession, test_user: User):
    """Test listing projects with pagination."""
    service = ProjectService(db_session)

    # Create 15 projects
    for i in range(15):
        await service.create_project(ProjectCreate(name=f"Project {i}"), test_user.id)

    # Get first page
    projects1, total = await service.list_projects(skip=0, limit=10)
    assert total == 15
    assert len(projects1) == 10

    # Get second page
    projects2, _ = await service.list_projects(skip=10, limit=10)
    assert len(projects2) == 5
