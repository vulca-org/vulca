"""Storage abstraction for generated images.

Provides a unified interface for saving/serving images, with backends:
- LocalStorage: filesystem (development, Render free tier)
- GCSStorage: Google Cloud Storage (Cloud Run production)

The active backend is selected by STORAGE_BACKEND env var:
- "local" (default): saves to app/prototype/checkpoints/draft/
- "gcs": saves to GCS bucket specified by GCS_BUCKET env var
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Protocol

logger = logging.getLogger(__name__)


class StorageBackend(Protocol):
    """Protocol for image storage backends."""

    def save(self, data: bytes, relative_path: str) -> str:
        """Save image bytes and return a URL or path for serving."""
        ...

    def exists(self, relative_path: str) -> bool:
        """Check if a file exists at the given path."""
        ...

    def delete(self, relative_path: str) -> None:
        """Delete a file at the given path."""
        ...


class LocalStorage:
    """Local filesystem storage backend."""

    def __init__(self, base_dir: str | None = None) -> None:
        if base_dir is None:
            base_dir = str(
                Path(__file__).resolve().parent.parent / "checkpoints" / "draft"
            )
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, relative_path: str) -> str:
        full_path = self._base_dir / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(data)
        return f"/static/prototype/draft/{relative_path}"

    def exists(self, relative_path: str) -> bool:
        return (self._base_dir / relative_path).exists()

    def delete(self, relative_path: str) -> None:
        path = self._base_dir / relative_path
        if path.exists():
            path.unlink()


class GCSStorage:
    """Google Cloud Storage backend for production."""

    def __init__(
        self,
        bucket_name: str | None = None,
        prefix: str = "prototype/draft",
    ) -> None:
        self._bucket_name = bucket_name or os.getenv("GCS_BUCKET", "")
        self._prefix = prefix
        self._client = None

    def _get_bucket(self):
        if self._client is None:
            from google.cloud import storage

            self._client = storage.Client()
        return self._client.bucket(self._bucket_name)

    def save(self, data: bytes, relative_path: str) -> str:
        blob_name = f"{self._prefix}/{relative_path}"
        bucket = self._get_bucket()
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data, content_type="image/png")
        return blob.public_url

    def exists(self, relative_path: str) -> bool:
        blob_name = f"{self._prefix}/{relative_path}"
        bucket = self._get_bucket()
        return bucket.blob(blob_name).exists()

    def delete(self, relative_path: str) -> None:
        blob_name = f"{self._prefix}/{relative_path}"
        bucket = self._get_bucket()
        blob = bucket.blob(blob_name)
        if blob.exists():
            blob.delete()


# Singleton storage instance
_storage: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Get the configured storage backend (singleton)."""
    global _storage
    if _storage is None:
        backend = os.getenv("STORAGE_BACKEND", "local")
        if backend == "gcs":
            bucket = os.getenv("GCS_BUCKET", "")
            if not bucket:
                logger.warning("GCS_BUCKET not set, falling back to local storage")
                _storage = LocalStorage()
            else:
                logger.info("Using GCS storage: bucket=%s", bucket)
                _storage = GCSStorage(bucket_name=bucket)
        else:
            logger.info("Using local file storage")
            _storage = LocalStorage()
    return _storage
