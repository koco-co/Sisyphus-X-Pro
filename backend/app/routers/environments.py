"""Environment management router."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.environment import (
    EnvironmentCreate,
    EnvironmentResponse,
    EnvironmentUpdate,
    EnvVariableCreate,
    EnvVariableResponse,
    GlobalVariableCreate,
    GlobalVariableResponse,
)
from app.services.environment_service import EnvironmentService

router = APIRouter(prefix="/environments", tags=["environments"])


# ============== Dependency Injection ==============

def get_environment_service(db: Annotated[AsyncSession, Depends(get_db)]) -> EnvironmentService:
    """Get environment service instance.

    Args:
        db: Database session

    Returns:
        EnvironmentService instance
    """
    return EnvironmentService(db)


# ============== Environment Endpoints ==============

@router.get("", response_model=List[EnvironmentResponse])
async def list_environments(
    project_id: int = Query(..., description="Project ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    service: EnvironmentService = Depends(get_environment_service),
):
    """List all environments for a project.

    Args:
        project_id: Project ID
        skip: Number of records to skip
        limit: Maximum number of records
        service: Environment service

    Returns:
        List of environments
    """
    environments, _ = await service.list_environments(project_id, skip, limit)
    return environments


@router.post("", response_model=EnvironmentResponse, status_code=status.HTTP_201_CREATED)
async def create_environment(
    env_in: EnvironmentCreate,
    service: EnvironmentService = Depends(get_environment_service),
):
    """Create a new environment.

    Args:
        env_in: Environment creation data
        service: Environment service

    Returns:
        Created environment
    """
    environment = await service.create_environment(env_in)
    return environment


@router.put("/{environment_id}", response_model=EnvironmentResponse)
async def update_environment(
    environment_id: int,
    env_in: EnvironmentUpdate,
    service: EnvironmentService = Depends(get_environment_service),
):
    """Update an environment.

    Args:
        environment_id: Environment ID
        env_in: Environment update data
        service: Environment service

    Returns:
        Updated environment

    Raises:
        HTTPException: If environment not found
    """
    environment = await service.update_environment(environment_id, env_in)
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Environment {environment_id} not found",
        )
    return environment


@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_environment(
    environment_id: int,
    service: EnvironmentService = Depends(get_environment_service),
):
    """Delete an environment.

    Args:
        environment_id: Environment ID
        service: Environment service

    Raises:
        HTTPException: If environment not found
    """
    success = await service.delete_environment(environment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Environment {environment_id} not found",
        )


# ============== Environment Variable Endpoints ==============

@router.get("/{environment_id}/variables", response_model=List[EnvVariableResponse])
async def list_env_variables(
    environment_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: EnvironmentService = Depends(get_environment_service),
):
    """List all variables for an environment.

    Args:
        environment_id: Environment ID
        skip: Number of records to skip
        limit: Maximum number of records
        service: Environment service

    Returns:
        List of environment variables
    """
    variables, _ = await service.list_env_variables(environment_id, skip, limit)
    return variables


@router.post(
    "/{environment_id}/variables",
    response_model=EnvVariableResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_env_variable(
    environment_id: int,
    var_in: EnvVariableCreate,
    service: EnvironmentService = Depends(get_environment_service),
):
    """Create a new environment variable.

    Args:
        environment_id: Environment ID
        var_in: Variable creation data
        service: Environment service

    Returns:
        Created variable
    """
    variable = await service.create_env_variable(
        environment_id=environment_id,
        name=var_in.name,
        value=var_in.value,
        description=var_in.description,
    )
    return variable


@router.delete("/variables/{variable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_env_variable(
    variable_id: int,
    service: EnvironmentService = Depends(get_environment_service),
):
    """Delete an environment variable.

    Args:
        variable_id: Variable ID
        service: Environment service

    Raises:
        HTTPException: If variable not found
    """
    success = await service.delete_env_variable(variable_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Environment variable {variable_id} not found",
        )


# ============== Global Variable Endpoints ==============

@router.get("/global/variables", response_model=List[GlobalVariableResponse])
async def list_global_variables(
    project_id: int = Query(..., description="Project ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: EnvironmentService = Depends(get_environment_service),
):
    """List all global variables for a project.

    Args:
        project_id: Project ID
        skip: Number of records to skip
        limit: Maximum number of records
        service: Environment service

    Returns:
        List of global variables
    """
    variables, _ = await service.list_global_variables(project_id, skip, limit)
    return variables


@router.post(
    "/global/variables",
    response_model=GlobalVariableResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_global_variable(
    var_in: GlobalVariableCreate,
    service: EnvironmentService = Depends(get_environment_service),
):
    """Create a new global variable.

    Args:
        var_in: Variable creation data
        service: Environment service

    Returns:
        Created variable
    """
    variable = await service.create_global_variable(
        project_id=var_in.project_id,
        name=var_in.name,
        value=var_in.value,
        description=var_in.description,
    )
    return variable


@router.delete("/global/variables/{variable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_global_variable(
    variable_id: int,
    service: EnvironmentService = Depends(get_environment_service),
):
    """Delete a global variable.

    Args:
        variable_id: Variable ID
        service: Environment service

    Raises:
        HTTPException: If variable not found
    """
    success = await service.delete_global_variable(variable_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Global variable {variable_id} not found",
        )
