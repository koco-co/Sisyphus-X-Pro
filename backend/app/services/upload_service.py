"""File upload service for MinIO object storage."""

import uuid
from io import BytesIO
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.config import settings


class UploadService:
    """Service for handling file uploads to MinIO."""

    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            print(f"MinIO bucket check failed: {e}")

    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
    ) -> dict[str, any]:
        """Upload file to MinIO.

        Args:
            file_data: File bytes data
            filename: Original filename
            content_type: MIME type of the file

        Returns:
            Dict with file metadata (path, url, size)
        """
        # Generate unique filename
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        unique_filename = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
        object_name = f"uploads/{unique_filename}"

        try:
            # Upload file
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )

            # Generate presigned URL (valid for 7 days)
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=60 * 60 * 24 * 7,  # 7 days
            )

            return {
                "path": object_name,
                "url": url,
                "size": len(file_data),
                "filename": filename,
                "content_type": content_type,
            }
        except S3Error as e:
            raise ValueError(f"Upload failed: {e}") from e

    async def delete_file(self, object_name: str) -> bool:
        """Delete file from MinIO.

        Args:
            object_name: Object name in MinIO

        Returns:
            True if deleted successfully
        """
        try:
            self.client.remove_object(bucket_name=self.bucket, object_name=object_name)
            return True
        except S3Error as e:
            print(f"Delete failed: {e}")
            return False

    def get_file_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """Get presigned URL for file.

        Args:
            object_name: Object name in MinIO
            expires: URL expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL or None if failed
        """
        try:
            return self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires,
            )
        except S3Error as e:
            print(f"Get URL failed: {e}")
            return None
