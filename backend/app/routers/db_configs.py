"""Database configuration router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.database_config import (
    DatabaseConfigCreate,
    DatabaseConfigListResponse,
    DatabaseConfigResponse,
    DatabaseConfigUpdate,
    TestConnectionRequest,
    TestConnectionResponse,
)
from app.services.db_config_service import DatabaseConfigService
from app.services.db_connection_scheduler import get_db_connection_scheduler

router = APIRouter(prefix="/projects/{project_id}/db-configs", tags=["Database Configs"])


async def get_db_config_service(
    db: AsyncSession = Depends(get_db),
) -> DatabaseConfigService:
    """Dependency to get database config service.

    Args:
        db: Database session

    Returns:
        DatabaseConfigService instance
    """
    return DatabaseConfigService(db)


def build_config_display(
    host: str, port: int, database: str
) -> str:
    """Build config display string.

    Args:
        host: Database host
        port: Database port
        database: Database name

    Returns:
        Display string in format "host:port/database"
    """
    return f"{host}:{port}/{database}"


@router.get("", response_model=DatabaseConfigListResponse)
async def list_db_configs(
    project_id: int,
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    pageSize: Annotated[int, Query(ge=1, le=100, description="每页条数")] = 10,  # noqa: N803
    current_user: User = Depends(get_current_user),
    service: DatabaseConfigService = Depends(get_db_config_service),
):
    """List database configs for a project.

    Args:
        project_id: Project ID (used for routing, accessed via service)
        page: Page number (1-indexed)
        pageSize: Number of items per page
        current_user: Current authenticated user (enforces authentication)
        service: Database config service

    Returns:
        Paginated list of database configs
    """
    # Mark parameters as intentionally used for routing and authentication
    _ = (project_id, current_user)
    skip = (page - 1) * pageSize
    configs, total = await service.list_db_configs(project_id, skip=skip, limit=pageSize)

    # Convert to response models
    items = [
        DatabaseConfigResponse(
            id=c.id,
            project_id=c.project_id,
            name=c.name,
            variable_name=c.variable_name,
            db_type=c.db_type,
            host=c.host,
            port=c.port,
            database=c.database,
            username=c.username,
            config_display=build_config_display(c.host, c.port, c.database),
            is_connected=c.is_connected,
            is_enabled=c.is_enabled,
            created_at=c.created_at,
            last_check_at=c.last_check_at,
            last_error=getattr(c, 'last_error', None),
        )
        for c in configs
    ]

    return DatabaseConfigListResponse(items=items, total=total, page=page, pageSize=pageSize)


@router.post("", response_model=DatabaseConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_db_config(
    project_id: int,
    config_in: DatabaseConfigCreate,
    current_user: User = Depends(get_current_user),
    service: DatabaseConfigService = Depends(get_db_config_service),
):
    """Create new database config.

    Args:
        project_id: Project ID (used for routing, accessed via service)
        config_in: Config creation data
        current_user: Current authenticated user (enforces authentication)
        service: Database config service

    Returns:
        Created database config

    Raises:
        HTTPException: If validation fails
    """
    # Mark parameters as intentionally used for routing and authentication
    _ = current_user
    try:
        config = await service.create_db_config(project_id, config_in)
        return DatabaseConfigResponse(
            id=config.id,
            project_id=config.project_id,
            name=config.name,
            variable_name=config.variable_name,
            db_type=config.db_type,
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            config_display=build_config_display(
                config.host, config.port, config.database
            ),
            is_connected=config.is_connected,
            is_enabled=config.is_enabled,
            created_at=config.created_at,
            last_check_at=config.last_check_at,
            last_error=getattr(config, 'last_error', None),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{config_id}", response_model=DatabaseConfigResponse)
async def get_db_config(
    project_id: int,
    config_id: int,
    current_user: User = Depends(get_current_user),
    service: DatabaseConfigService = Depends(get_db_config_service),
):
    """Get database config by ID.

    Args:
        project_id: Project ID
        config_id: Config ID
        current_user: Current authenticated user
        service: Database config service

    Returns:
        Database config details

    Raises:
        HTTPException: If config not found
    """
    config = await service.get_db_config_by_id(config_id)
    if not config or config.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database config not found",
        )

    return DatabaseConfigResponse(
        id=config.id,
        project_id=config.project_id,
        name=config.name,
        variable_name=config.variable_name,
        db_type=config.db_type,
        host=config.host,
        port=config.port,
        database=config.database,
        username=config.username,
        config_display=build_config_display(config.host, config.port, config.database),
        is_connected=config.is_connected,
        is_enabled=config.is_enabled,
        created_at=config.created_at,
        last_check_at=config.last_check_at,
        last_error=getattr(config, 'last_error', None),
    )


@router.put("/{config_id}", response_model=DatabaseConfigResponse)
async def update_db_config(
    project_id: int,
    config_id: int,
    config_in: DatabaseConfigUpdate,
    current_user: User = Depends(get_current_user),
    service: DatabaseConfigService = Depends(get_db_config_service),
):
    """Update database config.

    Args:
        project_id: Project ID
        config_id: Config ID
        config_in: Config update data
        current_user: Current authenticated user
        service: Database config service

    Returns:
        Updated database config

    Raises:
        HTTPException: If config not found or validation fails
    """
    try:
        config = await service.update_db_config(config_id, config_in)
        if not config or config.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database config not found",
            )

        return DatabaseConfigResponse(
            id=config.id,
            project_id=config.project_id,
            name=config.name,
            variable_name=config.variable_name,
            db_type=config.db_type,
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            config_display=build_config_display(
                config.host, config.port, config.database
            ),
            is_connected=config.is_connected,
            is_enabled=config.is_enabled,
            created_at=config.created_at,
            last_check_at=config.last_check_at,
            last_error=getattr(config, 'last_error', None),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_db_config(
    project_id: int,
    config_id: int,
    current_user: User = Depends(get_current_user),
    service: DatabaseConfigService = Depends(get_db_config_service),
):
    """Delete database config.

    Args:
        project_id: Project ID (used for routing and ownership validation)
        config_id: Config ID
        current_user: Current authenticated user (enforces authentication)
        service: Database config service

    Raises:
        HTTPException: If config not found
    """
    # Mark parameters as intentionally used for routing and authentication
    _ = current_user
    config = await service.get_db_config_by_id(config_id)
    if not config or config.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database config not found",
        )

    deleted = await service.delete_db_config(config_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database config not found",
        )


@router.post("/test-connection", response_model=TestConnectionResponse)
async def test_connection(
    project_id: int,
    test_request: TestConnectionRequest,
    current_user: User = Depends(get_current_user),
    service: DatabaseConfigService = Depends(get_db_config_service),
):
    """Test database connection.

    Args:
        project_id: Project ID (used for routing)
        test_request: Connection test parameters
        current_user: Current authenticated user (enforces authentication)
        service: Database config service

    Returns:
        Connection test result
    """
    # Mark parameters as intentionally used for routing and authentication
    _ = (project_id, current_user)
    connected, message = await service.test_connection(
        db_type=test_request.db_type,
        host=test_request.host,
        port=test_request.port,
        database=test_request.database,
        username=test_request.username,
        password=test_request.password,
    )

    return TestConnectionResponse(connected=connected, message=message)


@router.patch("/{config_id}/toggle", response_model=DatabaseConfigResponse)
async def toggle_db_config(
    project_id: int,
    config_id: int,
    request_data: dict,
    current_user: User = Depends(get_current_user),
    service: DatabaseConfigService = Depends(get_db_config_service),
):
    """Toggle database config enabled status.

    Args:
        project_id: Project ID
        config_id: Config ID
        request_data: Request body containing is_enabled
        current_user: Current authenticated user
        service: Database config service

    Returns:
        Updated database config

    Raises:
        HTTPException: If config not found
    """
    is_enabled = request_data.get("is_enabled", True)
    config = await service.toggle_enabled(config_id, is_enabled)
    if not config or config.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database config not found",
        )

    return DatabaseConfigResponse(
        id=config.id,
        project_id=config.project_id,
        name=config.name,
        variable_name=config.variable_name,
        db_type=config.db_type,
        host=config.host,
        port=config.port,
        database=config.database,
        username=config.username,
        config_display=build_config_display(config.host, config.port, config.database),
        is_connected=config.is_connected,
        is_enabled=config.is_enabled,
        created_at=config.created_at,
        last_check_at=config.last_check_at,
        last_error=getattr(config, 'last_error', None),
    )


@router.post("/check-all")
async def check_all_connections(
    project_id: int,
    current_user: User = Depends(get_current_user),
):
    """Manually trigger connection check for all database configs.

    Args:
        project_id: Project ID (used for routing)
        current_user: Current authenticated user (enforces authentication)

    Returns:
        Connection check results
    """
    # Mark parameters as intentionally used for routing and authentication
    _ = (project_id, current_user)
    scheduler = get_db_connection_scheduler()
    if not scheduler:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection scheduler not available",
        )

    result = await scheduler.check_now()
    return {
        "success_count": result["success_count"],
        "failure_count": result["failure_count"],
        "message": f"检查完成: {result['success_count']} 个成功, {result['failure_count']} 个失败",
    }


@router.get("/scheduler/status")
async def get_scheduler_status(
    project_id: int,
    current_user: User = Depends(get_current_user),
):
    """Get database connection scheduler status.

    Args:
        project_id: Project ID (used for routing)
        current_user: Current authenticated user (enforces authentication)

    Returns:
        Scheduler status information
    """
    # Mark parameters as intentionally used for routing and authentication
    _ = (project_id, current_user)
    scheduler = get_db_connection_scheduler()
    if not scheduler:
        return {
            "running": False,
            "check_interval_minutes": 0,
            "message": "调度器未启动",
        }

    return {
        "running": scheduler.scheduler.running,
        "check_interval_minutes": scheduler.check_interval_minutes,
        "message": f"调度器运行中,每 {scheduler.check_interval_minutes} 分钟检查一次",
    }
