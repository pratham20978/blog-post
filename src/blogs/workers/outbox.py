"""The outbox relay.

Runs as its **own process**, deliberately. Inside the API it would start once
per uvicorn worker, and N pollers competing over the same table is wasted work
even though ``SKIP LOCKED`` keeps it correct. A ``pg_try_advisory_lock`` guards
the case anyway, so starting two by accident costs nothing.

Latency comes from ``LISTEN``, not from the poll interval: an insert notifies,
the worker wakes immediately, and the timeout is only the fallback. That
fallback is not optional — ``NOTIFY`` is not durable, so a worker that was
reconnecting when an event landed must still find it on the next tick.

Delivery is at-least-once. Exactly-once across a process boundary is not
achievable, which is why ``consumed_events`` exists and why every consumer must
be idempotent.

Usage::

    python -m blogs.workers.outbox
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import secrets
import signal
from datetime import UTC, datetime, timedelta

from psycopg import errors

from blogs.core.logging import configure_logging
from blogs.core.settings import Settings
from blogs.database.session import Database
from blogs.repository.uow import SqlUnitOfWorkFactory

logger = logging.getLogger(__name__)

_CHANNEL = "outbox_events"
_ADVISORY_LOCK_KEY = 0x1B10_0B0C

#: Full jitter, per the AWS "Exponential Backoff And Jitter" guidance: sleep is
#: uniform over [0, min(cap, base * 2^attempt)]. Without the randomness a burst
#: of simultaneous failures retries in lockstep forever.
_BACKOFF_BASE_S = 2.0
_BACKOFF_CAP_S = 600.0


def _next_attempt_at(attempts: int, now: datetime) -> datetime:
    ceiling = min(_BACKOFF_CAP_S, _BACKOFF_BASE_S * (2**attempts))
    return now + timedelta(seconds=secrets.SystemRandom().uniform(0, ceiling))


class OutboxWorker:
    def __init__(
        self,
        *,
        database: Database,
        uow: SqlUnitOfWorkFactory,
        batch_size: int,
        poll_interval_s: float,
        max_attempts: int,
    ) -> None:
        self._database = database
        self._uow = uow
        self._batch_size = batch_size
        self._poll_interval = poll_interval_s
        self._max_attempts = max_attempts
        self._stopping = asyncio.Event()
        self._woken = asyncio.Event()

    def stop(self) -> None:
        self._stopping.set()

    async def run(self) -> None:
        logger.info("outbox worker started", extra={"batch_size": self._batch_size})
        listener = asyncio.create_task(self._listen())
        try:
            while not self._stopping.is_set():
                published = await self._drain()
                if published == 0:
                    # Nothing to do — wait for a notification or the fallback
                    # tick, whichever comes first.
                    with contextlib.suppress(TimeoutError):
                        await asyncio.wait_for(
                            self._woken.wait(), timeout=self._poll_interval
                        )
                    self._woken.clear()
        finally:
            listener.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await listener
            logger.info("outbox worker stopped")

    async def _listen(self) -> None:
        """Hold a dedicated connection on LISTEN.

        Its own connection because a listening one cannot be shared: it blocks
        on notifications and must not be handed to a query mid-wait.
        """
        while not self._stopping.is_set():
            try:
                async with self._database.connection() as conn:
                    await conn.execute(f"LISTEN {_CHANNEL}")
                    logger.debug("listening for outbox notifications")
                    async for _ in conn.notifies():
                        self._woken.set()
                        if self._stopping.is_set():
                            return
            except (errors.Error, OSError):
                # A dropped connection is expected over a long life. Reconnect
                # after a pause; the poll fallback covers the gap.
                logger.warning("outbox listener reconnecting", exc_info=True)
                await asyncio.sleep(self._poll_interval)

    async def _drain(self) -> int:
        """Claim and publish one batch. Returns how many were published."""
        now = datetime.now(UTC)
        published = 0

        async with self._uow.begin() as uow:
            claimed = await uow.outbox.claim(limit=self._batch_size, now=now)
            if not claimed:
                return 0

            succeeded: list[str] = []
            for event_id, event_name, attempts, payload in claimed:
                try:
                    await self._publish(
                        event_id=event_id, event_name=event_name, payload=payload
                    )
                    succeeded.append(event_id)
                except Exception as exc:  # one bad event must not stall the batch
                    dead = attempts + 1 >= self._max_attempts
                    await uow.outbox.mark_failed(
                        event_id=event_id,
                        error=f"{type(exc).__name__}: {exc}",
                        next_attempt_at=_next_attempt_at(attempts, now),
                        dead=dead,
                    )
                    logger.warning(
                        "outbox delivery failed",
                        extra={
                            "event": event_name,
                            "attempts": attempts + 1,
                            "dead_lettered": dead,
                        },
                    )

            if succeeded:
                published = await uow.outbox.mark_published(tuple(succeeded), now=now)

        if published:
            logger.info("outbox batch published", extra={"published": published})
        return published

    async def _publish(self, *, event_id: str, event_name: str, payload: dict) -> None:  # type: ignore[type-arg]
        """Hand the event to its subscribers.

        F3 emits and does not consume, and F1/F2/F4 do not exist yet, so today
        this only records that the event was relayed. When a consumer arrives it
        subscribes here — and because delivery is at-least-once it must dedupe
        on ``event_id`` through ``consumed_events``.
        """
        logger.info(
            "event published",
            extra={"event": event_name, "event_id": event_id, "keys": sorted(payload)},
        )


async def _main() -> int:
    settings = Settings()
    configure_logging()

    database = Database(
        settings.database_url,
        min_size=1,
        # Two: one held on LISTEN, one for the claim/publish transactions.
        max_size=4,
        statement_timeout_ms=settings.db_statement_timeout_ms,
    )
    await database.open()

    # Second guard against a duplicate worker. SKIP LOCKED already makes two
    # correct, but two is still wasted effort and a confusing thing to find.
    async with database.connection() as conn:
        cursor = await conn.execute(
            "SELECT pg_try_advisory_lock(%s) AS acquired", (_ADVISORY_LOCK_KEY,)
        )
        row = await cursor.fetchone()
        if not (row and row["acquired"]):
            logger.error("another outbox worker holds the lock; exiting")
            await database.close()
            return 1

        worker = OutboxWorker(
            database=database,
            uow=SqlUnitOfWorkFactory(database),
            batch_size=settings.outbox_batch_size,
            poll_interval_s=settings.outbox_poll_interval_s,
            max_attempts=settings.outbox_max_attempts,
        )

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, worker.stop)

        try:
            await worker.run()
        finally:
            await database.close()
    return 0


def main() -> int:
    return asyncio.run(_main())


if __name__ == "__main__":
    raise SystemExit(main())
