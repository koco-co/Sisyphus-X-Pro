"""Project service for business logic."""

from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for project-related business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize project service.

        Args:
            db: Database session
        """
        self.db = db

    async def list_projects(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        creator_id: Optional[int] = None,
    ) -> tuple[List[Project], int]:
        """List projects with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            name: Filter by project name (partial match)
            creator_id: Filter by creator ID

        Returns:
            Tuple of (projects list, total count)
        """
        # Build base query
        query = select(Project).join(User)

        # Apply filters
        if name:
            query = query.where(Project.name.ilike(f"%{name}%"))
        if creator_id:
            query = query.where(Project.creator_id == creator_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results with eager loading
        query = query.options(selectinload(Project.creator)).offset(skip).limit(limit)
        query = query.order_by(Project.created_at.desc())

        result = await self.db.execute(query)
        projects = result.scalars().all()

        return list(projects), total

    async def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID.

        Args:
            project_id: Project ID

        Returns:
            Project instance or None if not found
        """
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.creator))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def create_project(
        self, project_in: ProjectCreate, creator_id: int
    ) -> Project:
        """Create new project.

        Args:
            project_in: Project creation data
            creator_id: ID of user creating the project

        Returns:
            Created project instance

        Raises:
            ValueError: If project name already exists for this creator
        """
        # Check if project name already exists for this creator
        existing = await self.db.execute(
            select(Project).where(
                Project.creator_id == creator_id, Project.name == project_in.name
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Project with this name already exists")

        # Create project
        project = Project(
            name=project_in.name,
            description=project_in.description,
            creator_id=creator_id,
        )
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)

        # Load creator relationship
        await self.db.refresh(project, ["creator"])
        return project

    async def update_project(
        self, project_id: int, project_in: ProjectUpdate
    ) -> Optional[Project]:
        """Update project.

        Args:
            project_id: Project ID
            project_in: Project update data

        Returns:
            Updated project instance or None if not found

        Raises:
            ValueError: If project name already exists for this creator
        """
        project = await self.get_project_by_id(project_id)
        if not project:
            return None

        # Check if new name conflicts with existing project
        if project_in.name and project_in.name != project.name:
            existing = await self.db.execute(
                select(Project).where(
                    Project.creator_id == project.creator_id,
                    Project.name == project_in.name,
                    Project.id != project_id,
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("Project with this name already exists")

        # Update fields
        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: int) -> bool:
        """Delete project.

        Args:
            project_id: Project ID

        Returns:
            True if deleted, False if not found
        """
        project = await self.get_project_by_id(project_id)
        if not project:
            return False

        await self.db.delete(project)
        await self.db.flush()
        return True
