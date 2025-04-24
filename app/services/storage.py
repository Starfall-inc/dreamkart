# services/storage_manager.py
import io
import json
import os
import uuid
from typing import Optional, List, Tuple, BinaryIO, Union
from urllib.parse import urljoin

from minio import Minio
from minio.error import S3Error
from werkzeug.datastructures import FileStorage
from flask import current_app, g
import magic


class StorageManager:
    """Service class for handling file storage operations with MinIO."""

    @staticmethod
    def _get_client() -> Minio:
        """Get or create MinIO client instance."""
        if not hasattr(g, 'minio_client'):
            g.minio_client = Minio(
                endpoint=current_app.config['MINIO_ENDPOINT'],
                access_key=current_app.config['MINIO_ACCESS_KEY'],
                secret_key=current_app.config['MINIO_SECRET_KEY'],
                secure=current_app.config.get('MINIO_SECURE', True)
            )
        return g.minio_client

    @staticmethod
    def ensure_bucket_exists(bucket_name: str) -> bool:
        """
        Ensure the specified bucket exists, create if it doesn't.

        Args:
            bucket_name: Name of the bucket

        Returns:
            bool: True if bucket exists or was created successfully
        """
        client = StorageManager._get_client()
        try:
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)

                # Set bucket policy to allow public read if configured
                if current_app.config.get('MINIO_PUBLIC_BUCKETS', False):
                    policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"AWS": "*"},
                                "Action": ["s3:GetObject"],
                                "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                            }
                        ]
                    }
                    client.set_bucket_policy(bucket_name, policy)

            return True
        except S3Error as e:
            current_app.logger.error(f"Error ensuring bucket {bucket_name} exists: {str(e)}")
            return False

    @staticmethod
    def get_mime_type(file_data: Union[FileStorage, BinaryIO, bytes]) -> str:
        """
        Detect MIME type of a file.

        Args:
            file_data: File object or bytes

        Returns:
            str: MIME type of the file
        """
        if isinstance(file_data, FileStorage):
            # For Flask FileStorage objects
            file_data.seek(0)
            mime = magic.from_buffer(file_data.read(2048), mime=True)
            file_data.seek(0)
            return mime
        elif hasattr(file_data, 'read'):
            # For file-like objects
            pos = file_data.tell()
            mime = magic.from_buffer(file_data.read(2048), mime=True)
            file_data.seek(pos)
            return mime
        elif isinstance(file_data, bytes):
            # For bytes
            return magic.from_buffer(file_data[:2048], mime=True)
        else:
            return 'application/octet-stream'

    @staticmethod
    def upload(
            bucket_name: str,
            file_data: Union[FileStorage, BinaryIO, bytes],
            file_path: Optional[str] = None,
            content_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload a file to MinIO bucket.

        Args:
            bucket_name: Target bucket name
            file_data: File object to upload
            file_path: Path/name for the file in the bucket (generated if None)
            content_type: MIME type (auto-detected if None)

        Returns:
            str: File path/ID in the bucket if successful, None otherwise
        """
        client = StorageManager._get_client()

        try:
            # Ensure bucket exists
            StorageManager.ensure_bucket_exists(bucket_name)

            # Generate file path if not provided
            if not file_path:
                if isinstance(file_data, FileStorage) and file_data.filename:
                    extension = os.path.splitext(file_data.filename)[1]
                else:
                    extension = ''
                file_path = f"{uuid.uuid4()}{extension}"

            # Auto-detect content type if not provided
            if not content_type:
                content_type = StorageManager.get_mime_type(file_data)

            # Handle different file data types
            if isinstance(file_data, FileStorage):
                file_data.seek(0)
                size = os.fstat(file_data.fileno()).st_size
                client.put_object(
                    bucket_name,
                    file_path,
                    file_data,
                    size,
                    content_type=content_type
                )
            elif hasattr(file_data, 'read'):
                # For file-like objects, we need to get size
                pos = file_data.tell()
                file_data.seek(0, os.SEEK_END)
                size = file_data.tell()
                file_data.seek(pos)

                client.put_object(
                    bucket_name,
                    file_path,
                    file_data,
                    size,
                    content_type=content_type
                )
            elif isinstance(file_data, bytes):
                # For bytes data
                client.put_object(
                    bucket_name,
                    file_path,
                    data=io.BytesIO(file_data),
                    length=len(file_data),
                    content_type=content_type
                )

            return file_path

        except S3Error as err:
            current_app.logger.error(f"Error uploading file to MinIO: {str(err)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Unexpected error uploading file: {str(e)}")
            return None

    @staticmethod
    def delete(bucket_name: str, file_path: str) -> bool:
        """
        Delete a file from MinIO bucket.

        Args:
            bucket_name: Bucket name containing the file
            file_path: Path/ID of the file to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        client = StorageManager._get_client()

        try:
            client.remove_object(bucket_name, file_path)
            return True
        except S3Error as err:
            current_app.logger.error(f"Error deleting file from MinIO: {str(err)}")
            return False

    @staticmethod
    def get_file_url(bucket_name: str, file_path: str) -> str:
        """
        Get the URL for accessing a file.

        Args:
            bucket_name: Bucket name containing the file
            file_path: Path/ID of the file

        Returns:
            str: URL to access the file
        """
        base_url = current_app.config.get('MINIO_PUBLIC_URL')
        if not base_url:
            base_url = f"http{'s' if current_app.config.get('MINIO_SECURE', True) else ''}://{current_app.config['MINIO_ENDPOINT']}"

        return urljoin(f"{base_url}/{bucket_name}/", file_path)

    @staticmethod
    def generate_presigned_url(
            bucket_name: str,
            file_path: str,
            expires: int = 3600,
            response_headers: dict = None
    ) -> Optional[str]:
        """
        Generate a presigned URL for temporary file access.

        Args:
            bucket_name: Bucket name containing the file
            file_path: Path/ID of the file
            expires: Expiration time in seconds (default: 1 hour)
            response_headers: Custom response headers for the URL

        Returns:
            str: Presigned URL or None if failed
        """
        client = StorageManager._get_client()

        try:
            url = client.presigned_get_object(
                bucket_name,
                file_path,
                expires=expires,
                response_headers=response_headers
            )
            return url
        except S3Error as err:
            current_app.logger.error(f"Error generating presigned URL: {str(err)}")
            return None

    @staticmethod
    def list_files(bucket_name: str, prefix: str = '', recursive: bool = True) -> List[str]:
        """
        List files in a bucket with optional prefix filtering.

        Args:
            bucket_name: Bucket name to list files from
            prefix: Optional prefix to filter results
            recursive: Whether to list files recursively

        Returns:
            List[str]: List of file paths/IDs
        """
        client = StorageManager._get_client()

        try:
            objects = client.list_objects(bucket_name, prefix=prefix, recursive=recursive)
            return [obj.object_name for obj in objects]
        except S3Error as err:
            current_app.logger.error(f"Error listing files from MinIO: {str(err)}")
            return []

    @staticmethod
    def get_file(bucket_name: str, file_path: str) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Get file content and its content type.

        Args:
            bucket_name: Bucket name containing the file
            file_path: Path/ID of the file

        Returns:
            Tuple[Optional[bytes], Optional[str]]: File content and content type, or (None, None) if failed
        """
        client = StorageManager._get_client()

        try:
            response = client.get_object(bucket_name, file_path)
            content = response.read()
            content_type = response.headers.get('Content-Type')
            response.close()
            return content, content_type
        except S3Error as err:
            current_app.logger.error(f"Error getting file from MinIO: {str(err)}")
            return None, None
        except Exception as e:
            current_app.logger.error(f"Unexpected error getting file: {str(e)}")
            return None, None

    @staticmethod
    def file_exists(bucket_name: str, file_path: str) -> bool:
        """
        Check if a file exists in the bucket.

        Args:
            bucket_name: Bucket name to check
            file_path: Path/ID of the file

        Returns:
            bool: True if file exists, False otherwise
        """
        client = StorageManager._get_client()

        try:
            client.stat_object(bucket_name, file_path)
            return True
        except S3Error:
            return False

    @staticmethod
    def create_bucket(bucket_name: str, public_access: bool = False) -> bool:
        """
        Create a new bucket in MinIO.

        Args:
            bucket_name: Name of the bucket to create
            public_access: Whether to make the bucket publicly readable

        Returns:
            bool: True if bucket was created successfully, False otherwise
        """
        client = StorageManager._get_client()

        try:
            # Check if bucket already exists
            if client.bucket_exists(bucket_name):
                current_app.logger.info(f"Bucket {bucket_name} already exists")
                return True

            # Create the bucket
            client.make_bucket(bucket_name)
            current_app.logger.info(f"Created bucket {bucket_name} successfully")

            # Set bucket policy for public access if requested
            if public_access:
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                        }
                    ]
                }
                client.set_bucket_policy(bucket_name, json.dumps(policy))
                current_app.logger.info(f"Set public read policy for bucket {bucket_name}")

            return True

        except S3Error as err:
            current_app.logger.error(f"Error creating bucket {bucket_name}: {str(err)}")
            return False
        except Exception as e:
            current_app.logger.error(f"Unexpected error creating bucket {bucket_name}: {str(e)}")
            return False
