"""Interface management router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.interface import (
    CurlImportRequest,
    InterfaceCreate,
    InterfaceFolderCreate,
    InterfaceFolderResponse,
    InterfaceFolderUpdate,
    InterfaceReorderRequest,
    InterfaceResponse,
    InterfaceTreeNode,
    InterfaceUpdate,
)
from app.services.interface_service import InterfaceService

router = APIRouter(prefix="/interfaces", tags=["interfaces"])


# ============== Dependency Injection ==============

def get_interface_service(db: Annotated[AsyncSession, Depends(get_db)]) -> InterfaceService:
    """Get interface service instance.

    Args:
        db: Database session

    Returns:
        InterfaceService instance
    """
    return InterfaceService(db)


# ============== Tree Structure ==============

@router.get("/tree", response_model=list[InterfaceTreeNode])
async def get_interface_tree(
    project_id: int = Query(..., description="Project ID"),
    service: InterfaceService = Depends(get_interface_service),
):
    """Get full interface tree for a project.

    Args:
        project_id: Project ID
        service: Interface service

    Returns:
        List of tree nodes (folders and interfaces)
    """
    tree = await service.get_interface_tree(project_id)
    return tree


# ============== Folder Endpoints ==============

@router.post(
    "/folders",
    response_model=InterfaceFolderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_folder(
    folder_in: InterfaceFolderCreate,
    service: InterfaceService = Depends(get_interface_service),
):
    """Create a new interface folder.

    Args:
        folder_in: Folder creation data
        service: Interface service

    Returns:
        Created folder
    """
    folder = await service.create_folder(folder_in)
    return folder


@router.put("/folders/{folder_id}", response_model=InterfaceFolderResponse)
async def update_folder(
    folder_id: int,
    folder_in: InterfaceFolderUpdate,
    service: InterfaceService = Depends(get_interface_service),
):
    """Update an interface folder.

    Args:
        folder_id: Folder ID
        folder_in: Folder update data
        service: Interface service

    Returns:
        Updated folder

    Raises:
        HTTPException: If folder not found
    """
    folder = await service.update_folder(folder_id, folder_in)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Folder {folder_id} not found",
        )
    return folder


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: int,
    service: InterfaceService = Depends(get_interface_service),
):
    """Delete an interface folder and all its children.

    Args:
        folder_id: Folder ID
        service: Interface service

    Raises:
        HTTPException: If folder not found
    """
    success = await service.delete_folder(folder_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Folder {folder_id} not found",
        )


# ============== Interface Endpoints ==============

@router.get("", response_model=list[InterfaceResponse])
async def list_interfaces(
    project_id: int = Query(..., description="Project ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    service: InterfaceService = Depends(get_interface_service),
):
    """List all interfaces for a project.

    Args:
        project_id: Project ID
        skip: Number of records to skip
        limit: Maximum number of records
        service: Interface service

    Returns:
        List of interfaces
    """
    interfaces, _ = await service.list_interfaces(project_id, skip, limit)
    return interfaces


@router.post("", response_model=InterfaceResponse, status_code=status.HTTP_201_CREATED)
async def create_interface(
    interface_in: InterfaceCreate,
    service: InterfaceService = Depends(get_interface_service),
):
    """Create a new interface.

    Args:
        interface_in: Interface creation data
        service: Interface service

    Returns:
        Created interface
    """
    interface = await service.create_interface(interface_in)
    return interface


@router.get("/{interface_id}", response_model=InterfaceResponse)
async def get_interface(
    interface_id: int,
    service: InterfaceService = Depends(get_interface_service),
):
    """Get an interface by ID.

    Args:
        interface_id: Interface ID
        service: Interface service

    Returns:
        Interface

    Raises:
        HTTPException: If interface not found
    """
    interface = await service.get_interface_by_id(interface_id)
    if not interface:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interface {interface_id} not found",
        )
    return interface


@router.put("/{interface_id}", response_model=InterfaceResponse)
async def update_interface(
    interface_id: int,
    interface_in: InterfaceUpdate,
    service: InterfaceService = Depends(get_interface_service),
):
    """Update an interface.

    Args:
        interface_id: Interface ID
        interface_in: Interface update data
        service: Interface service

    Returns:
        Updated interface

    Raises:
        HTTPException: If interface not found
    """
    interface = await service.update_interface(interface_id, interface_in)
    if not interface:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interface {interface_id} not found",
        )
    return interface


@router.delete("/{interface_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interface(
    interface_id: int,
    service: InterfaceService = Depends(get_interface_service),
):
    """Delete an interface.

    Args:
        interface_id: Interface ID
        service: Interface service

    Raises:
        HTTPException: If interface not found
    """
    success = await service.delete_interface(interface_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interface {interface_id} not found",
        )


# ============== Batch Operations ==============

@router.post("/batch/reorder")
async def batch_reorder(
    reorder_in: InterfaceReorderRequest,
    service: InterfaceService = Depends(get_interface_service),
):
    """Batch reorder interfaces and folders.

    Args:
        reorder_in: Reorder request with list of {id, sort_order}
        service: Interface service

    Returns:
        Summary of reorder operation
    """
    result = await service.batch_reorder(reorder_in)
    return result


# ============== cURL Import ==============

@router.post("/import/curl", response_model=InterfaceResponse, status_code=status.HTTP_201_CREATED)
async def import_from_curl(
    curl_in: CurlImportRequest,
    service: InterfaceService = Depends(get_interface_service),
):
    """Import interface from cURL command.

    Args:
        curl_in: cURL import request
        service: Interface service

    Returns:
        Created interface

    Raises:
        HTTPException: If cURL command is invalid
    """
    try:
        interface = await service.import_from_curl(curl_in)
        return interface
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
