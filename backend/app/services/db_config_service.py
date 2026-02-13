"""Database configuration service."""

import asyncio
from typing import List, Literal, Optional

import aiomysql
import asyncpg
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database_config import DatabaseConfig
from app.models.project import Project
from app.schemas.database_config import (
    DatabaseConfigCreate,
    DatabaseConfigUpdate,
)


class DatabaseConfigService:
    """Service for database configuration business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize database config service.

        Args:
            db: Database session
        """
        self.db = db

    async def list_db_configs(
        self,
        project_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[DatabaseConfig], int]:
        """List database configs for a project.

        Args:
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (configs list, total count)
        """
        # Get total count
        count_query = select(func.count()).select_from(
            select(DatabaseConfig).where(DatabaseConfig.project_id == project_id).subquery()
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = (
            select(DatabaseConfig)
            .where(DatabaseConfig.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .order_by(DatabaseConfig.created_at.desc())
        )

        result = await self.db.execute(query)
        configs = result.scalars().all()

        return list(configs), total

    async def get_db_config_by_id(
        self, config_id: int
    ) -> Optional[DatabaseConfig]:
        """Get database config by ID.

        Args:
            config_id: Config ID

        Returns:
            DatabaseConfig instance or None if not found
        """
        result = await self.db.execute(
            select(DatabaseConfig).where(DatabaseConfig.id == config_id)
        )
        return result.scalar_one_or_none()

    async def create_db_config(
        self, project_id: int, config_in: DatabaseConfigCreate
    ) -> DatabaseConfig:
        """Create new database config.

        Args:
            project_id: Project ID
            config_in: Config creation data

        Returns:
            Created database config instance

        Raises:
            ValueError: If variable_name already exists in project
        """
        # Check if variable_name already exists for this project
        existing = await self.db.execute(
            select(DatabaseConfig).where(
                DatabaseConfig.project_id == project_id,
                DatabaseConfig.variable_name == config_in.variable_name,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Variable name already exists in this project")

        # Check project exists
        project = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        if not project.scalar_one_or_none():
            raise ValueError("Project not found")

        # Create config
        config = DatabaseConfig(
            project_id=project_id,
            name=config_in.name,
            variable_name=config_in.variable_name,
            db_type=config_in.db_type,
            host=config_in.host,
            port=config_in.port,
            database=config_in.database,
            username=config_in.username,
            password=config_in.password,  # TODO: Encrypt password
        )
        self.db.add(config)
        await self.db.flush()
        await self.db.refresh(config)
        return config

    async def update_db_config(
        self, config_id: int, config_in: DatabaseConfigUpdate
    ) -> Optional[DatabaseConfig]:
        """Update database config.

        Args:
            config_id: Config ID
            config_in: Config update data

        Returns:
            Updated config instance or None if not found

        Raises:
            ValueError: If variable_name conflict
        """
        config = await self.get_db_config_by_id(config_id)
        if not config:
            return None

        # Check variable_name uniqueness if changed
        if config_in.variable_name and config_in.variable_name != config.variable_name:
            existing = await self.db.execute(
                select(DatabaseConfig).where(
                    DatabaseConfig.project_id == config.project_id,
                    DatabaseConfig.variable_name == config_in.variable_name,
                    DatabaseConfig.id != config_id,
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("Variable name already exists in this project")

        # Update fields
        update_data = config_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)

        await self.db.flush()
        await self.db.refresh(config)
        return config

    async def delete_db_config(self, config_id: int) -> bool:
        """Delete database config.

        Args:
            config_id: Config ID

        Returns:
            True if deleted, False if not found
        """
        config = await self.get_db_config_by_id(config_id)
        if not config:
            return False

        await self.db.delete(config)
        await self.db.flush()
        return True

    async def test_connection(
        self,
        db_type: Literal["mysql", "postgresql"],
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
    ) -> tuple[bool, str]:
        """Test database connection.

        Args:
            db_type: Database type (mysql or postgresql)
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if db_type == "mysql":
                # Test MySQL connection
                conn = await aiomysql.connect(
                    host=host,
                    port=port,
                    user=username,
                    password=password,
                    db=database,
                    connect_timeout=5,
                )
                await conn.ensure_closed()
                return True, "连接成功"

            elif db_type == "postgresql":
                # Test PostgreSQL connection
                conn = await asyncpg.connect(
                    host=host,
                    port=port,
                    user=username,
                    password=password,
                    database=database,
                    timeout=5,
                )
                await conn.close()
                return True, "连接成功"

        except asyncio.TimeoutError:
            return False, "连接超时,请检查网络和主机地址"
        except aiomysql.OperationalError as e:
            error_msg = str(e)
            if "Access denied" in error_msg:
                return False, "用户名或密码错误"
            elif "Unknown database" in error_msg:
                return False, "数据库不存在"
            elif "Can't connect to MySQL server" in error_msg:
                return False, "无法连接到 MySQL 服务器,请检查主机和端口"
            else:
                return False, f"MySQL 连接失败: {error_msg}"
        except asyncpg.PostgresError as e:
            error_msg = str(e)
            if "authentication failed" in error_msg.lower():
                return False, "用户名或密码错误"
            elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
                return False, "数据库不存在"
            elif "connection refused" in error_msg.lower():
                return False, "无法连接到 PostgreSQL 服务器,请检查主机和端口"
            else:
                return False, f"PostgreSQL 连接失败: {error_msg}"
        except Exception as e:
            return False, f"连接失败: {str(e)}"

        return False, "不支持的数据库类型"

    async def toggle_enabled(self, config_id: int, is_enabled: bool) -> Optional[DatabaseConfig]:
        """Toggle database config enabled status.

        Args:
            config_id: Config ID
            is_enabled: New enabled status

        Returns:
            Updated config or None if not found
        """
        config = await self.get_db_config_by_id(config_id)
        if not config:
            return None

        config.is_enabled = is_enabled
        await self.db.flush()
        await self.db.refresh(config)
        return config
