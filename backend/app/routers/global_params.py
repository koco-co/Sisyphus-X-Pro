"""Global parameter router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.global_param import (
    FunctionParseRequest,
    FunctionParseResponse,
    GlobalParamCreate,
    GlobalParamGroupedResponse,
    GlobalParamListResponse,
    GlobalParamResponse,
    GlobalParamUpdate,
)
from app.services.global_param_service import GlobalParamService

router = APIRouter(prefix="/global-params", tags=["Global Parameters"])


async def get_global_param_service(
    db: AsyncSession = Depends(get_db),
) -> GlobalParamService:
    """Dependency to get global parameter service.

    Args:
        db: Database session

    Returns:
        GlobalParamService instance
    """
    return GlobalParamService(db)


@router.get("", response_model=GlobalParamListResponse)
async def list_global_params(
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    pageSize: Annotated[int, Query(ge=1, le=100, description="每页条数")] = 10,  # noqa: N803
    class_name: Annotated[str | None, Query(description="类名")] = None,
    is_builtin: Annotated[bool | None, Query(description="是否内置")] = None,
    current_user: User = Depends(get_current_user),
    service: GlobalParamService = Depends(get_global_param_service),
):
    """List global parameters with pagination and filtering.

    Args:
        page: Page number (1-indexed)
        pageSize: Number of items per page
        class_name: Filter by class name
        is_builtin: Filter by is_builtin flag
        current_user: Current authenticated user
        service: Global parameter service

    Returns:
        Paginated list of global parameters
    """
    skip = (page - 1) * pageSize
    params, total = await service.list_global_params(
        skip=skip,
        limit=pageSize,
        class_name=class_name,
        is_builtin=is_builtin,
    )

    # Convert to response models
    items = [
        GlobalParamResponse(
            id=p.id,
            class_name=p.class_name,
            method_name=p.method_name,
            description=p.description,
            code=p.code,
            params_in=p.params_in if isinstance(p.params_in, list) else [],
            params_out=p.params_out if isinstance(p.params_out, list) else [],
            is_builtin=p.is_builtin,
            created_at=p.created_at,
        )
        for p in params
    ]

    return GlobalParamListResponse(items=items, total=total, page=page, pageSize=pageSize)


@router.get("/grouped", response_model=GlobalParamGroupedResponse)
async def get_global_params_grouped(
    current_user: User = Depends(get_current_user),
    service: GlobalParamService = Depends(get_global_param_service),
):
    """Get all global parameters grouped by class name.

    Args:
        current_user: Current authenticated user
        service: Global parameter service

    Returns:
        Global parameters grouped by class name
    """
    grouped = await service.get_global_params_grouped()

    # Convert to response format
    params_by_class: dict[str, list[GlobalParamResponse]] = {}
    for class_name, params in grouped.items():
        params_by_class[class_name] = [
            GlobalParamResponse(
                id=p.id,
                class_name=p.class_name,
                method_name=p.method_name,
                description=p.description,
                code=p.code,
                params_in=p.params_in if isinstance(p.params_in, list) else [],
                params_out=p.params_out if isinstance(p.params_out, list) else [],
                is_builtin=p.is_builtin,
                created_at=p.created_at,
            )
            for p in params
        ]

    return GlobalParamGroupedResponse(params=params_by_class)


@router.post("", response_model=GlobalParamResponse, status_code=status.HTTP_201_CREATED)
async def create_global_param(
    param_in: GlobalParamCreate,
    current_user: User = Depends(get_current_user),
    service: GlobalParamService = Depends(get_global_param_service),
):
    """Create new global parameter.

    Args:
        param_in: Global parameter creation data
        current_user: Current authenticated user
        service: Global parameter service

    Returns:
        Created global parameter

    Raises:
        HTTPException: If validation fails
    """
    try:
        param = await service.create_global_param(param_in)
        return GlobalParamResponse(
            id=param.id,
            class_name=param.class_name,
            method_name=param.method_name,
            description=param.description,
            code=param.code,
            params_in=param.params_in if isinstance(param.params_in, list) else [],
            params_out=param.params_out if isinstance(param.params_out, list) else [],
            is_builtin=param.is_builtin,
            created_at=param.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{param_id}", response_model=GlobalParamResponse)
async def get_global_param(
    param_id: int,
    current_user: User = Depends(get_current_user),
    service: GlobalParamService = Depends(get_global_param_service),
):
    """Get global parameter by ID.

    Args:
        param_id: Global parameter ID
        current_user: Current authenticated user
        service: Global parameter service

    Returns:
        Global parameter details

    Raises:
        HTTPException: If global parameter not found
    """
    param = await service.get_global_param_by_id(param_id)
    if not param:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Global parameter not found",
        )

    return GlobalParamResponse(
        id=param.id,
        class_name=param.class_name,
        method_name=param.method_name,
        description=param.description,
        code=param.code,
        params_in=param.params_in or [],
        params_out=param.params_out or [],
        is_builtin=param.is_builtin,
        created_at=param.created_at,
    )


@router.put("/{param_id}", response_model=GlobalParamResponse)
async def update_global_param(
    param_id: int,
    param_in: GlobalParamUpdate,
    current_user: User = Depends(get_current_user),
    service: GlobalParamService = Depends(get_global_param_service),
):
    """Update global parameter.

    Args:
        param_id: Global parameter ID
        param_in: Global parameter update data
        current_user: Current authenticated user
        service: Global parameter service

    Returns:
        Updated global parameter

    Raises:
        HTTPException: If global parameter not found, builtin, or validation fails
    """
    try:
        param = await service.update_global_param(param_id, param_in)
        if not param:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Global parameter not found",
            )

        return GlobalParamResponse(
            id=param.id,
            class_name=param.class_name,
            method_name=param.method_name,
            description=param.description,
            code=param.code,
            params_in=param.params_in if isinstance(param.params_in, list) else [],
            params_out=param.params_out if isinstance(param.params_out, list) else [],
            is_builtin=param.is_builtin,
            created_at=param.created_at,
        )
    except ValueError as e:
        if "Built-in" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{param_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_global_param(
    param_id: int,
    current_user: User = Depends(get_current_user),
    service: GlobalParamService = Depends(get_global_param_service),
):
    """Delete global parameter.

    Args:
        param_id: Global parameter ID
        current_user: Current authenticated user
        service: Global parameter service

    Raises:
        HTTPException: If global parameter not found or builtin
    """
    try:
        deleted = await service.delete_global_param(param_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Global parameter not found",
            )
    except ValueError as e:
        if "Built-in" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/parse", response_model=FunctionParseResponse)
async def parse_function_calls(
    request: FunctionParseRequest,
    current_user: User = Depends(get_current_user),
    service: GlobalParamService = Depends(get_global_param_service),
):
    """Parse {{function()}} calls in text and replace with actual values.

    Supports nested function calls like {{timestamp_to_date(current_timestamp())}}.

    Args:
        request: Parse request containing text and context
        current_user: Current authenticated user
        service: Global parameter service

    Returns:
        Parsed text with function results
    """
    try:
        parsed_text, functions_called, success, error = await service.parse_function_calls(
            request.text, request.context
        )

        return FunctionParseResponse(
            original_text=request.text,
            parsed_text=parsed_text,
            functions_called=functions_called,
            success=success,
            error=error,
        )
    except Exception as e:
        return FunctionParseResponse(
            original_text=request.text,
            parsed_text=request.text,
            functions_called=[],
            success=False,
            error=str(e),
        )
