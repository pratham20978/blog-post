"""Liveness and readiness.

The distinction is operational, not cosmetic. ``/healthz`` answers "is this
process running" and must never touch a dependency — a liveness probe that
fails when the database blips gets the container killed and restarted, which
does not fix the database and does remove the capacity that was still serving
cached reads. ``/readyz`` answers "should traffic come here", and that one does
check dependencies.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Response

from blogs.api.deps import Assembled
from blogs.api.envelope import success
from blogs.contracts.common import APIResponse

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def liveness() -> APIResponse[dict[str, str]]:
    """Unauthenticated, dependency-free, always cheap."""
    return success({"status": "alive"})


@router.get("/readyz")
async def readiness(assembled: Assembled, response: Response) -> APIResponse[dict[str, Any]]:
    """Check what a request would actually need.

    Reports 503 when a dependency is down so a load balancer stops sending
    traffic here, and includes pool counters — a request queue that never drains
    shows up in these numbers long before it shows up as a timeout.
    """
    database_ok = await assembled.database.healthcheck()
    storage_ok = await assembled.object_store.healthcheck()

    outbox: dict[str, int] = {}
    if database_ok:
        async with assembled.uow.read() as uow:
            outbox = {
                "pending": await uow.outbox.pending_count(),
                "dead": await uow.outbox.dead_count(),
            }

    ready = database_ok and storage_ok
    if not ready:
        response.status_code = 503

    return success(
        {
            "ready": ready,
            "database": "up" if database_ok else "down",
            "object_store": "up" if storage_ok else "down",
            "pool": assembled.database.stats(),
            "outbox": outbox,
        }
    )
