"""Project router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


async def get_project_service(
    db: AsyncSession = Depends(get_db),
) -> ProjectService:
    """Dependency to get project service.

    Args:
        db: Database session

    Returns:
        ProjectService instance
    """
    return ProjectService(db)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    pageSize: Annotated[int, Query(ge=1, le=100, description="每页条数")] = 10,  # noqa: N803
    name: Annotated[str | None, Query(description="项目名称(模糊搜索)")] = None,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """List projects with pagination and search.

    Args:
        page: Page number (1-indexed)
        pageSize: Number of items per page
        name: Filter by project name (partial match)
        current_user: Current authenticated user
        project_service: Project service

    Returns:
        Paginated list of projects
    """
    skip = (page - 1) * pageSize
    projects, total = await project_service.list_projects(
        skip=skip, limit=pageSize, name=name
    )

    # Convert to response models
    items = [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            creator_name=p.creator.nickname,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in projects
    ]

    return ProjectListResponse(items=items, total=total, page=page, pageSize=pageSize)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Create new project.

    Args:
        project_in: Project creation data
        current_user: Current authenticated user
        project_service: Project service

    Returns:
        Created project

    Raises:
        HTTPException: If project name already exists
    """
    try:
        project = await project_service.create_project(project_in, current_user.id)
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            creator_name=project.creator.nickname,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Get project by ID.

    Args:
        project_id: Project ID
        current_user: Current authenticated user
        project_service: Project service

    Returns:
        Project details

    Raises:
        HTTPException: If project not found
    """
    project = await project_service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        creator_name=project.creator.nickname,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Update project.

    Args:
        project_id: Project ID
        project_in: Project update data
        current_user: Current authenticated user
        project_service: Project service

    Returns:
        Updated project

    Raises:
        HTTPException: If project not found or name conflict
    """
    try:
        project = await project_service.update_project(project_id, project_in)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            creator_name=project.creator.nickname,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    """Delete project.

    Args:
        project_id: Project ID
        current_user: Current authenticated user
        project_service: Project service

    Raises:
        HTTPException: If project not found
    """
    deleted = await project_service.delete_project(project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
