"""The transactional-outbox SQL adapter."""

from __future__ import annotations

from datetime import datetime

from psycopg.types.json import Jsonb
from pydantic import JsonValue

from blogs.contracts.events import EVENT_TYPES, DomainEvent
from blogs.repository.base import SqlRepository, as_utc


class SqlOutboxRepository(SqlRepository):
    async def add(
        self, event: DomainEvent, *, aggregate_type: str, aggregate_id: str
    ) -> None:
        """Stage an event in the caller's transaction.

        The event name is checked against the catalogue here rather than trusted:
        a typo would otherwise be written happily and simply never match a
        subscriber, which is a silent failure discovered weeks later by someone
        wondering why no email arrived.
        """
        if event.event_name not in EVENT_TYPES:
            raise ValueError(f"unknown event name: {event.event_name!r}")

        payload = event.model_dump(mode="json")
        await self._execute(
            """
            INSERT INTO outbox_events
                (id, event_name, event_version, aggregate_type, aggregate_id,
                 payload, occurred_at)
            VALUES (%(id)s, %(name)s, %(version)s, %(agg_type)s, %(agg_id)s,
                    %(payload)s, %(at)s)
            """,
            {
                "id": event.id,
                "name": event.event_name,
                "version": event.event_version,
                "agg_type": aggregate_type,
                "agg_id": aggregate_id,
                "payload": Jsonb(payload),
                "at": as_utc(event.occurred_at),
            },
        )

    async def claim(
        self, *, limit: int, now: datetime
    ) -> tuple[tuple[str, str, int, dict[str, JsonValue]], ...]:
        """Take up to ``limit`` due events.

        ``FOR UPDATE SKIP LOCKED`` inside the sub-select is what lets several
        workers run without coordination: each takes rows the others have not
        locked instead of queueing behind them.

        Rows stay ``pending`` and are held by the row lock for the duration of
        this transaction rather than being flipped to a ``processing`` status.
        A status flag would strand rows in it forever if a worker died mid-batch;
        a lock is released by the crash itself.
        """
        rows = await self._fetch_all(
            """
            SELECT id, event_name, attempts, payload
            FROM outbox_events
            WHERE status = 'pending' AND next_attempt_at <= %(now)s
            ORDER BY next_attempt_at, id
            LIMIT %(limit)s
            FOR UPDATE SKIP LOCKED
            """,
            {"now": as_utc(now), "limit": limit},
        )
        return tuple(
            (str(r["id"]), r["event_name"], int(r["attempts"]), r["payload"]) for r in rows
        )

    async def mark_published(self, event_ids: tuple[str, ...], *, now: datetime) -> int:
        if not event_ids:
            return 0
        return await self._execute(
            """
            UPDATE outbox_events
            SET status = 'published', published_at = %(now)s, last_error = NULL
            WHERE id = ANY(%(ids)s::uuid[])
            """,
            {"now": as_utc(now), "ids": list(event_ids)},
        )

    async def mark_failed(
        self, *, event_id: str, error: str, next_attempt_at: datetime, dead: bool
    ) -> None:
        await self._execute(
            """
            UPDATE outbox_events
            SET attempts        = attempts + 1,
                last_error      = %(error)s,
                next_attempt_at = %(next)s,
                status          = CASE WHEN %(dead)s THEN 'dead' ELSE 'pending' END
            WHERE id = %(id)s
            """,
            {
                "id": event_id,
                # Truncated: a provider stack trace can be enormous and this
                # column is read by a human deciding whether to replay.
                "error": error[:2000],
                "next": as_utc(next_attempt_at),
                "dead": dead,
            },
        )

    async def pending_count(self) -> int:
        row = await self._fetch_one(
            "SELECT count(*) AS n FROM outbox_events WHERE status = 'pending'"
        )
        return int(row["n"]) if row else 0

    async def dead_count(self) -> int:
        row = await self._fetch_one(
            "SELECT count(*) AS n FROM outbox_events WHERE status = 'dead'"
        )
        return int(row["n"]) if row else 0
