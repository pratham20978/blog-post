"""An in-memory object store, for tests.

Not a mock: it implements the same port with the same failure modes, so a test
exercises the real code path rather than an assertion about a call that was
recorded. Publishing an article in a unit test needs no MinIO, no network and no
container.
"""

from __future__ import annotations

import asyncio

from blogs.contracts.common import ErrorCategory
from blogs.core.errors import BlogPlatformError

_SCHEME = "s3"


class InMemoryObjectStore:
    def __init__(self, bucket: str = "blogs") -> None:
        self._bucket = bucket
        self._objects: dict[str, tuple[bytes, str]] = {}
        self._lock = asyncio.Lock()
        #: Flipped by a test to assert the caller degrades rather than crashes.
        self.fail_next = False

    def _key_of(self, uri: str) -> str:
        prefix = f"{_SCHEME}://{self._bucket}/"
        if not uri.startswith(prefix):
            raise BlogPlatformError(
                ErrorCategory.STORAGE_OBJECT_NOT_FOUND,
                safe_details={"reason": "URI_NOT_IN_BUCKET"},
            )
        return uri[len(prefix) :]

    def _guard(self) -> None:
        if self.fail_next:
            self.fail_next = False
            raise BlogPlatformError(ErrorCategory.STORAGE_UNAVAILABLE)

    async def put(self, *, key: str, data: bytes, content_type: str) -> str:
        self._guard()
        async with self._lock:
            self._objects[key] = (data, content_type)
        return f"{_SCHEME}://{self._bucket}/{key}"

    async def get(self, uri: str) -> bytes:
        self._guard()
        key = self._key_of(uri)
        async with self._lock:
            stored = self._objects.get(key)
        if stored is None:
            raise BlogPlatformError(ErrorCategory.STORAGE_OBJECT_NOT_FOUND)
        return stored[0]

    async def exists(self, uri: str) -> bool:
        async with self._lock:
            return self._key_of(uri) in self._objects

    async def delete(self, uri: str) -> None:
        key = self._key_of(uri)
        async with self._lock:
            self._objects.pop(key, None)

    async def presign_get(self, uri: str, ttl_seconds: int) -> str:
        return f"{uri}?expires={ttl_seconds}"

    async def ensure_bucket(self) -> None:
        return None

    async def healthcheck(self) -> bool:
        return True

    def object_count(self) -> int:
        return len(self._objects)
