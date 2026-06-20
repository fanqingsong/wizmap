from minio import Minio as MinioClient
from minio.error import S3Error
from io import BytesIO
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MinioService:
    def __init__(self):
        self.client = None
        self.bucket = settings.MINIO_BUCKET
        self._initialize_client()

    def _initialize_client(self):
        """Initialize MinIO client"""
        try:
            self.client = MinioClient(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            # Ensure bucket exists
            self._ensure_bucket()
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")

    def _ensure_bucket(self):
        """Ensure the bucket exists"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Created bucket: {self.bucket}")
        except S3Error as e:
            logger.error(f"MinIO bucket operation failed: {e}")

    async def upload_file(self, file, file_path: str):
        """Upload a file to MinIO"""
        try:
            # Read file content asynchronously
            content = await file.read()

            # Upload to MinIO
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=file_path,
                data=BytesIO(content),
                length=len(content)
            )
            logger.info(f"Uploaded file to {file_path}")
            return True
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise

    async def get_file(self, file_path: str):
        """Get a file from MinIO"""
        return self.get_file_sync(file_path)

    def get_file_sync(self, file_path: str) -> bytes:
        """Synchronous version of get_file for use in non-async contexts
        (e.g. the Celery worker). The underlying minio client is blocking."""
        try:
            response = self.client.get_object(self.bucket, file_path)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Failed to get file {file_path}: {e}")
            raise

    async def delete_file(self, file_path: str):
        """Delete a file from MinIO"""
        try:
            self.client.remove_object(self.bucket, file_path)
            logger.info(f"Deleted file: {file_path}")
            return True
        except S3Error as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise

    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in MinIO"""
        try:
            self.client.stat_object(self.bucket, file_path)
            return True
        except S3Error:
            return False
