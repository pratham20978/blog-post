"""MinIO object store, behind ``ObjectStore``.

The MinIO SDK is synchronous, so every call is pushed to a worker thread. That
is acceptable precisely because of how rarely it happens: an article is written
once and its bytes are content-addressed, so the read path is served from an
immutable key that an in-process cache can hold indefinitely.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from io import BytesIO
from urllib.parse import urlparse

from minio import Minio
from minio.error import S3Error

from blogs.contracts.common import ErrorCategory
from blogs.core.errors import BlogPlatformError

logger = logging.getLogger(__name__)

_SCHEME = "s3"


class MinioObjectStore:
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False,
        region: str | None = None,
    ) -> None:
        self._bucket = bucket
        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            region=region,
        )

    def _key_of(self, uri: str) -> str:
        """Extract the object key from an ``s3://bucket/key`` URI.

        Refuses a URI naming a different bucket rather than quietly reading from
        it — a stored URI is data, and data that can redirect a read is a way in.
        """
        parsed = urlparse(uri)
        if parsed.scheme != _SCHEME or parsed.netloc != self._bucket:
            raise BlogPlatformError(
                ErrorCategory.STORAGE_OBJECT_NOT_FOUND,
                safe_details={"reason": "URI_NOT_IN_BUCKET"},
            )
        return parsed.path.lstrip("/")

    def _uri_of(self, key: str) -> str:
        return f"{_SCHEME}://{self._bucket}/{key}"

    async def put(self, *, key: str, data: bytes, content_type: str) -> str:
        def _put() -> None:
            self._client.put_object(
                self._bucket, key, BytesIO(data), length=len(data), content_type=content_type
            )

        try:
            await asyncio.to_thread(_put)
        except S3Error as exc:
            logger.warning("object store put failed", extra={"object_key": key}, exc_info=True)
            raise BlogPlatformError(ErrorCategory.STORAGE_UNAVAILABLE) from exc
        return self._uri_of(key)

    async def get(self, uri: str) -> bytes:
        key = self._key_of(uri)

        def _get() -> bytes:
            response = self._client.get_object(self._bucket, key)
            try:
                return bytes(response.read())
            finally:
                # Both are required: close returns the socket, release_conn
                # returns it to the pool. Skipping either leaks a connection per
                # read, which only shows up under load.
                response.close()
                response.release_conn()

        try:
            return await asyncio.to_thread(_get)
        except S3Error as exc:
            if exc.code in ("NoSuchKey", "NoSuchObject"):
                raise BlogPlatformError(ErrorCategory.STORAGE_OBJECT_NOT_FOUND) from exc
            raise BlogPlatformError(ErrorCategory.STORAGE_UNAVAILABLE) from exc

    async def exists(self, uri: str) -> bool:
        key = self._key_of(uri)

        def _stat() -> bool:
            try:
                self._client.stat_object(self._bucket, key)
            except S3Error as exc:
                if exc.code in ("NoSuchKey", "NoSuchObject", "NoSuchBucket"):
                    return False
                raise
            return True

        try:
            return await asyncio.to_thread(_stat)
        except S3Error as exc:
            raise BlogPlatformError(ErrorCategory.STORAGE_UNAVAILABLE) from exc

    async def delete(self, uri: str) -> None:
        key = self._key_of(uri)
        try:
            await asyncio.to_thread(self._client.remove_object, self._bucket, key)
        except S3Error as exc:
            raise BlogPlatformError(ErrorCategory.STORAGE_UNAVAILABLE) from exc

    async def presign_get(self, uri: str, ttl_seconds: int) -> str:
        key = self._key_of(uri)
        try:
            return await asyncio.to_thread(
                self._client.presigned_get_object,
                self._bucket,
                key,
                timedelta(seconds=ttl_seconds),
            )
        except S3Error as exc:
            raise BlogPlatformError(ErrorCategory.STORAGE_UNAVAILABLE) from exc

    async def ensure_bucket(self) -> None:
        def _ensure() -> None:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)

        try:
            await asyncio.to_thread(_ensure)
        except S3Error as exc:
            raise BlogPlatformError(ErrorCategory.STORAGE_UNAVAILABLE) from exc

    async def healthcheck(self) -> bool:
        try:
            return bool(await asyncio.to_thread(self._client.bucket_exists, self._bucket))
        except (S3Error, OSError):
            logger.warning("object store healthcheck failed", exc_info=True)
            return False
