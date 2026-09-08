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

from blogs.bootstrap import build_email_sender
from blogs.contracts.events import BlogPublished
from blogs.core.clock import SystemClock
from blogs.core.errors import BlogPlatformError
from blogs.core.ids import Uuid7Generator
from blogs.core.logging import configure_logging
from blogs.core.settings import Settings
from blogs.database.session import Database
from blogs.ports.services import EmailSender
from blogs.repository.uow import SqlUnitOfWorkFactory
from blogs.services.announcement_service import AnnouncementService
from blogs.services.policy import DefaultAuthorizationPolicy

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
        announcements: AnnouncementService,
        email: EmailSender,
        announcement_batch_size: int,
        announcement_max_attempts: int,
        announcement_lease_s: int,
        announcement_send_rate_per_s: float,
    ) -> None:
        self._database = database
        self._uow = uow
        self._batch_size = batch_size
        self._poll_interval = poll_interval_s
        self._max_attempts = max_attempts
        self._announcements = announcements
        self._email = email
        self._announcement_batch_size = announcement_batch_size
        self._announcement_max_attempts = announcement_max_attempts
        self._announcement_lease_s = announcement_lease_s
        self._announcement_send_interval = 1.0 / announcement_send_rate_per_s
        self._next_announcement_send_at = 0.0
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
                delivered = await self._drain_deliveries()
                if published == 0 and delivered == 0:
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

        New-blog delivery is the first local consumer. Campaign uniqueness makes
        its at-least-once handling idempotent; unrelated events remain available
        for future recommendation and notification consumers.
        """
        if event_name == BlogPublished.event_name:
            event = BlogPublished.model_validate(payload)
            created = await self._announcements.stage_published(event)
            logger.info(
                "blog announcement staged",
                extra={"event_id": event_id, "blog_id": event.blog_id, "created": created},
            )
            return

        logger.info(
            "event published",
            extra={"event": event_name, "event_id": event_id, "keys": sorted(payload)},
        )

    async def _drain_deliveries(self) -> int:
        now = datetime.now(UTC)
        async with self._uow.begin() as uow:
            deliveries = await uow.announcements.claim_due(
                now=now,
                lease_before=now - timedelta(seconds=self._announcement_lease_s),
                limit=self._announcement_batch_size,
            )
            if deliveries:
                await uow.announcements.settle_campaigns(now=now)
        if not deliveries:
            return 0

        for delivery in deliveries:
            await self._pace_announcement_send()
            async with self._uow.read() as uow:
                enabled = await uow.announcements.preference_enabled(delivery.user_id)
            if not enabled:
                async with self._uow.begin() as uow:
                    await uow.announcements.mark_cancelled(
                        delivery_id=delivery.id, now=datetime.now(UTC)
                    )
                continue

            result = None
            error = "UNREACHABLE"
            try:
                result = await self._email.send(
                    self._announcements.message_for(delivery)
                )
                error = result.detail or "PROVIDER_REFUSED"
            except BlogPlatformError as exc:
                error = exc.category.value
            except Exception as exc:  # one delivery cannot abandon the batch
                error = type(exc).__name__

            settled_at = datetime.now(UTC)
            async with self._uow.begin() as uow:
                if result is not None and result.sent:
                    await uow.announcements.mark_sent(
                        delivery_id=delivery.id,
                        provider_message_id=result.detail,
                        now=settled_at,
                    )
                else:
                    dead = delivery.attempts >= self._announcement_max_attempts
                    retry_after = result.retry_after_seconds if result is not None else None
                    next_at = (
                        settled_at + timedelta(seconds=retry_after)
                        if retry_after is not None
                        else _next_attempt_at(delivery.attempts, settled_at)
                    )
                    await uow.announcements.mark_failed(
                        delivery_id=delivery.id,
                        error=error,
                        next_attempt_at=next_at,
                        dead=dead,
                    )
                await uow.announcements.settle_campaigns(now=settled_at)

        return len(deliveries)

    async def _pace_announcement_send(self) -> None:
        """Apply one global send rate across batches, retries, and wakeups."""
        loop = asyncio.get_running_loop()
        now = loop.time()
        if self._next_announcement_send_at > now:
            await asyncio.sleep(self._next_announcement_send_at - now)
            now = loop.time()
        self._next_announcement_send_at = now + self._announcement_send_interval

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
    email = build_email_sender(settings)
    uow = SqlUnitOfWorkFactory(database)
    clock = SystemClock()
    announcements = AnnouncementService(
        uow=uow,
        clock=clock,
        ids=Uuid7Generator(),
        policy=DefaultAuthorizationPolicy(),
        public_site_url=settings.public_site_url,
        token_secret=settings.jwt_secret.get_secret_value(),
    )

    # Second guard against a duplicate worker. SKIP LOCKED already makes two
    # correct, but two is still wasted effort and a confusing thing to find.
    async with database.connection() as conn:
        cursor = await conn.execute(
            "SELECT pg_try_advisory_lock(%s) AS acquired", (_ADVISORY_LOCK_KEY,)
        )
        row = await cursor.fetchone()
        if not (row and row["acquired"]):
            logger.error("another outbox worker holds the lock; exiting")
            closer = getattr(email, "aclose", None)
            if closer is not None:
                await closer()
            await database.close()
            return 1

        worker = OutboxWorker(
            database=database,
            uow=uow,
            batch_size=settings.outbox_batch_size,
            poll_interval_s=settings.outbox_poll_interval_s,
            max_attempts=settings.outbox_max_attempts,
            announcements=announcements,
            email=email,
            announcement_batch_size=settings.announcement_batch_size,
            announcement_max_attempts=settings.announcement_max_attempts,
            announcement_lease_s=settings.announcement_lease_s,
            announcement_send_rate_per_s=settings.announcement_send_rate_per_s,
        )

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, worker.stop)

        try:
            await worker.run()
        finally:
            closer = getattr(email, "aclose", None)
            if closer is not None:
                await closer()
            await database.close()
    return 0


def main() -> int:
    return asyncio.run(_main())


if __name__ == "__main__":
    raise SystemExit(main())
