"""The outbox port.

``add`` is called inside a business transaction and nowhere else — that
co-location is the entire guarantee. The claim/settle methods belong to the
worker and run in their own transactions.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from pydantic import JsonValue

from blogs.contracts.events import DomainEvent


class OutboxRepository(Protocol):
    async def add(self, event: DomainEvent, *, aggregate_type: str, aggregate_id: str) -> None:
        """Stage an event in the caller's transaction.

        If the surrounding transaction rolls back so does this row, which is
        why an event can never describe a change that did not happen.
        """
        ...

    async def claim(
        self, *, limit: int, now: datetime
    ) -> tuple[tuple[str, str, int, dict[str, JsonValue]], ...]:
        """Take up to ``limit`` due events for this worker.

        ``SELECT ... FOR UPDATE SKIP LOCKED`` inside an UPDATE, so concurrent
        workers take disjoint sets without blocking one another. Returns
        ``(id, event_name, attempts, payload)``.
        """
        ...

    async def mark_published(self, event_ids: tuple[str, ...], *, now: datetime) -> int: ...

    async def mark_failed(
        self, *, event_id: str, error: str, next_attempt_at: datetime, dead: bool
    ) -> None:
        """Record a failure and schedule the retry, or dead-letter it."""
        ...

    async def pending_count(self) -> int: ...

    async def dead_count(self) -> int: ...
