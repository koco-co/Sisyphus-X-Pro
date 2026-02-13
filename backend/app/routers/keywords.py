"""Keyword router."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.keyword import (
    DocstringParseRequest,
    DocstringParseResponse,
    KeywordCreate,
    KeywordEnabledResponse,
    KeywordListResponse,
    KeywordResponse,
    KeywordUpdate,
)
from app.utils.docstring_parser import parse_docstring
from app.services.keyword_service import KeywordService

router = APIRouter(prefix="/keywords", tags=["Keywords"])


async def get_keyword_service(
    db: AsyncSession = Depends(get_db),
) -> KeywordService:
    """Dependency to get keyword service.

    Args:
        db: Database session

    Returns:
        KeywordService instance
    """
    return KeywordService(db)


@router.get("", response_model=KeywordListResponse)
async def list_keywords(
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    pageSize: Annotated[int, Query(ge=1, le=100, description="每页条数")] = 10,  # noqa: N803
    type: Annotated[Optional[str], Query(description="关键字类型")] = None,
    is_builtin: Annotated[Optional[bool], Query(description="是否内置")] = None,
    is_enabled: Annotated[Optional[bool], Query(description="是否启用")] = None,
    current_user: User = Depends(get_current_user),
    service: KeywordService = Depends(get_keyword_service),
):
    """List keywords with pagination and filtering.

    Args:
        page: Page number (1-indexed)
        pageSize: Number of items per page
        type: Filter by keyword type
        is_builtin: Filter by is_builtin flag
        is_enabled: Filter by is_enabled flag
        current_user: Current authenticated user
        service: Keyword service

    Returns:
        Paginated list of keywords
    """
    skip = (page - 1) * pageSize
    keywords, total = await service.list_keywords(
        skip=skip,
        limit=pageSize,
        keyword_type=type,
        is_builtin=is_builtin,
        is_enabled=is_enabled,
    )

    # Convert to response models
    items = [
        KeywordResponse(
            id=k.id,
            type=k.type,
            name=k.name,
            method_name=k.method_name,
            code=k.code,
            params=k.params or [],
            is_builtin=k.is_builtin,
            is_enabled=k.is_enabled,
            created_at=k.created_at,
        )
        for k in keywords
    ]

    return KeywordListResponse(items=items, total=total, page=page, pageSize=pageSize)


@router.get("/enabled", response_model=KeywordEnabledResponse)
async def get_enabled_keywords(
    current_user: User = Depends(get_current_user),
    service: KeywordService = Depends(get_keyword_service),
):
    """Get all enabled keywords grouped by type.

    Args:
        current_user: Current authenticated user
        service: Keyword service

    Returns:
        Keywords grouped by type
    """
    grouped = await service.get_enabled_keywords_grouped()

    # Convert to response format
    keywords_by_type: dict[str, list[KeywordResponse]] = {}
    for keyword_type, keywords in grouped.items():
        keywords_by_type[keyword_type] = [
            KeywordResponse(
                id=k.id,
                type=k.type,
                name=k.name,
                method_name=k.method_name,
                code=k.code,
                params=k.params or [],
                is_builtin=k.is_builtin,
                is_enabled=k.is_enabled,
                created_at=k.created_at,
            )
            for k in keywords
        ]

    return KeywordEnabledResponse(keywords=keywords_by_type)


@router.post("/parse", response_model=DocstringParseResponse)
async def parse_code_docstring(
    request: DocstringParseRequest,
    current_user: User = Depends(get_current_user),
):
    """Parse Python code docstring to extract function info.

    Args:
        request: Code to parse
        current_user: Current authenticated user

    Returns:
        Parsed function info including parameters

    Raises:
        HTTPException: If parsing fails
    """
    result = parse_docstring(request.code)

    if result.get("error") and not result.get("function_name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"],
        )

    # Convert params to response format
    params = []
    for param in result.get("params", []):
        params.append(
            {
                "name": param["name"],
                "type": param.get("type"),
                "description": param.get("description", ""),
                "default": param.get("default"),
            }
        )

    return DocstringParseResponse(
        function_name=result.get("function_name"),
        description=result.get("description", ""),
        params=params,
        error=result.get("error"),
    )


@router.post("", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    keyword_in: KeywordCreate,
    current_user: User = Depends(get_current_user),
    service: KeywordService = Depends(get_keyword_service),
):
    """Create new keyword.

    Args:
        keyword_in: Keyword creation data
        current_user: Current authenticated user
        service: Keyword service

    Returns:
        Created keyword

    Raises:
        HTTPException: If validation fails
    """
    try:
        keyword = await service.create_keyword(keyword_in)
        return KeywordResponse(
            id=keyword.id,
            type=keyword.type,
            name=keyword.name,
            method_name=keyword.method_name,
            code=keyword.code,
            params=keyword.params or [],
            is_builtin=keyword.is_builtin,
            is_enabled=keyword.is_enabled,
            created_at=keyword.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    keyword_id: int,
    current_user: User = Depends(get_current_user),
    service: KeywordService = Depends(get_keyword_service),
):
    """Get keyword by ID.

    Args:
        keyword_id: Keyword ID
        current_user: Current authenticated user
        service: Keyword service

    Returns:
        Keyword details

    Raises:
        HTTPException: If keyword not found
    """
    keyword = await service.get_keyword_by_id(keyword_id)
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found",
        )

    return KeywordResponse(
        id=keyword.id,
        type=keyword.type,
        name=keyword.name,
        method_name=keyword.method_name,
        code=keyword.code,
        params=keyword.params or [],
        is_builtin=keyword.is_builtin,
        is_enabled=keyword.is_enabled,
        created_at=keyword.created_at,
    )


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    keyword_in: KeywordUpdate,
    current_user: User = Depends(get_current_user),
    service: KeywordService = Depends(get_keyword_service),
):
    """Update keyword.

    Args:
        keyword_id: Keyword ID
        keyword_in: Keyword update data
        current_user: Current authenticated user
        service: Keyword service

    Returns:
        Updated keyword

    Raises:
        HTTPException: If keyword not found, builtin, or validation fails
    """
    try:
        keyword = await service.update_keyword(keyword_id, keyword_in)
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Keyword not found",
            )

        return KeywordResponse(
            id=keyword.id,
            type=keyword.type,
            name=keyword.name,
            method_name=keyword.method_name,
            code=keyword.code,
            params=keyword.params or [],
            is_builtin=keyword.is_builtin,
            is_enabled=keyword.is_enabled,
            created_at=keyword.created_at,
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


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
    keyword_id: int,
    current_user: User = Depends(get_current_user),
    service: KeywordService = Depends(get_keyword_service),
):
    """Delete keyword.

    Args:
        keyword_id: Keyword ID
        current_user: Current authenticated user
        service: Keyword service

    Raises:
        HTTPException: If keyword not found or builtin
    """
    try:
        deleted = await service.delete_keyword(keyword_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Keyword not found",
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


@router.patch("/{keyword_id}/toggle", response_model=KeywordResponse)
async def toggle_keyword(
    keyword_id: int,
    is_enabled: bool,
    current_user: User = Depends(get_current_user),
    service: KeywordService = Depends(get_keyword_service),
):
    """Toggle keyword enabled status.

    Args:
        keyword_id: Keyword ID
        is_enabled: New enabled status
        current_user: Current authenticated user
        service: Keyword service

    Returns:
        Updated keyword

    Raises:
        HTTPException: If keyword not found
    """
    keyword = await service.toggle_enabled(keyword_id, is_enabled)
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found",
        )

    return KeywordResponse(
        id=keyword.id,
        type=keyword.type,
        name=keyword.name,
        method_name=keyword.method_name,
        code=keyword.code,
        params=keyword.params or [],
        is_builtin=keyword.is_builtin,
        is_enabled=keyword.is_enabled,
        created_at=keyword.created_at,
    )
