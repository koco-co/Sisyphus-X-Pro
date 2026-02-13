"""Environment service for business logic."""


from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.env_variable import EnvVariable
from app.models.environment import Environment
from app.models.global_variable import GlobalVariable
from app.schemas.environment import (
    EnvironmentCreate,
    EnvironmentUpdate,
)


class EnvironmentService:
    """Service for environment-related business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize environment service.

        Args:
            db: Database session
        """
        self.db = db

    # ============== Environment CRUD ==============

    async def list_environments(
        self, project_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[Environment], int]:
        """List environments for a project.

        Args:
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (environments list, total count)
        """
        # Build base query
        query = select(Environment).where(Environment.project_id == project_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Environment.id)
        result = await self.db.execute(query)
        environments = result.scalars().all()

        return list(environments), total

    async def get_environment_by_id(self, environment_id: int) -> Environment | None:
        """Get environment by ID.

        Args:
            environment_id: Environment ID

        Returns:
            Environment instance or None if not found
        """
        result = await self.db.execute(
            select(Environment).where(Environment.id == environment_id)
        )
        return result.scalar_one_or_none()

    async def create_environment(
        self, env_in: EnvironmentCreate
    ) -> Environment:
        """Create new environment.

        Args:
            env_in: Environment creation data

        Returns:
            Created environment instance
        """
        environment = Environment(
            project_id=env_in.project_id,
            name=env_in.name,
            base_url=env_in.base_url,
        )
        self.db.add(environment)
        await self.db.flush()
        await self.db.refresh(environment)
        return environment

    async def update_environment(
        self, environment_id: int, env_in: EnvironmentUpdate
    ) -> Environment | None:
        """Update environment.

        Args:
            environment_id: Environment ID
            env_in: Environment update data

        Returns:
            Updated environment instance or None if not found
        """
        environment = await self.get_environment_by_id(environment_id)
        if not environment:
            return None

        update_data = env_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(environment, field, value)

        await self.db.flush()
        await self.db.refresh(environment)
        return environment

    async def delete_environment(self, environment_id: int) -> bool:
        """Delete environment.

        Args:
            environment_id: Environment ID

        Returns:
            True if deleted, False if not found
        """
        environment = await self.get_environment_by_id(environment_id)
        if not environment:
            return False

        await self.db.delete(environment)
        await self.db.flush()
        return True

    # ============== Environment Variable CRUD ==============

    async def list_env_variables(
        self, environment_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[EnvVariable], int]:
        """List environment variables.

        Args:
            environment_id: Environment ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (variables list, total count)
        """
        query = select(EnvVariable).where(EnvVariable.environment_id == environment_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(skip).limit(limit).order_by(EnvVariable.id)
        result = await self.db.execute(query)
        variables = result.scalars().all()

        return list(variables), total

    async def create_env_variable(
        self, environment_id: int, name: str, value: str, description: str | None = None
    ) -> EnvVariable:
        """Create new environment variable.

        Args:
            environment_id: Environment ID
            name: Variable name
            value: Variable value
            description: Variable description

        Returns:
            Created variable instance
        """
        variable = EnvVariable(
            environment_id=environment_id,
            name=name,
            value=value,
            description=description,
        )
        self.db.add(variable)
        await self.db.flush()
        await self.db.refresh(variable)
        return variable

    async def delete_env_variable(self, var_id: int) -> bool:
        """Delete environment variable.

        Args:
            var_id: Variable ID

        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            select(EnvVariable).where(EnvVariable.id == var_id)
        )
        variable = result.scalar_one_or_none()
        if not variable:
            return False

        await self.db.delete(variable)
        await self.db.flush()
        return True

    # ============== Global Variable CRUD ==============

    async def list_global_variables(
        self, project_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[GlobalVariable], int]:
        """List global variables for a project.

        Args:
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (variables list, total count)
        """
        query = select(GlobalVariable).where(GlobalVariable.project_id == project_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(skip).limit(limit).order_by(GlobalVariable.id)
        result = await self.db.execute(query)
        variables = result.scalars().all()

        return list(variables), total

    async def create_global_variable(
        self, project_id: int, name: str, value: str, description: str | None = None
    ) -> GlobalVariable:
        """Create new global variable.

        Args:
            project_id: Project ID
            name: Variable name
            value: Variable value
            description: Variable description

        Returns:
            Created variable instance
        """
        variable = GlobalVariable(
            project_id=project_id,
            name=name,
            value=value,
            description=description,
        )
        self.db.add(variable)
        await self.db.flush()
        await self.db.refresh(variable)
        return variable

    async def delete_global_variable(self, var_id: int) -> bool:
        """Delete global variable.

        Args:
            var_id: Variable ID

        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            select(GlobalVariable).where(GlobalVariable.id == var_id)
        )
        variable = result.scalar_one_or_none()
        if not variable:
            return False

        await self.db.delete(variable)
        await self.db.flush()
        return True
