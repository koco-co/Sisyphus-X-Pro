"""File upload router."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.upload_service import UploadService

router = APIRouter(prefix="/upload", tags=["upload"])
security = HTTPBearer(auto_error=False)


def get_upload_service() -> UploadService:
    """Get upload service instance.

    Returns:
        UploadService instance
    """
    return UploadService()


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: Annotated[UploadFile, File(...)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)] = None,
    service: UploadService = Depends(get_upload_service),
):
    """Upload file to MinIO.

    Args:
        file: Uploaded file
        credentials: Optional authorization credentials
        service: Upload service

    Returns:
        File metadata including path and URL

    Raises:
        HTTPException: If upload fails
    """
    # TODO: Add authentication check if needed
    # For now, allow uploads without auth in development mode

    try:
        # Read file data
        file_data = await file.read()

        # Upload to MinIO
        result = await service.upload_file(
            file_data=file_data,
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
        )

        return {
            "success": True,
            "data": result,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {e}",
        ) from e


@router.delete("/{object_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    object_name: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)] = None,
    service: UploadService = Depends(get_upload_service),
):
    """Delete file from MinIO.

    Args:
        object_name: Object name in MinIO
        credentials: Authorization credentials
        service: Upload service

    Raises:
        HTTPException: If deletion fails
    """
    try:
        success = await service.delete_file(object_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {object_name} not found",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {e}",
        ) from e
