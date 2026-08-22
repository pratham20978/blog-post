"""The connection pool and the two ways to use it.

One ``Database`` owns one ``AsyncConnectionPool`` for the process lifetime.
Nothing else opens a connection, and no module holds a global one — the pool
lives on the container, which lives on ``app.state``, so two apps can exist in
one process and a test can build its own without the import having already
opened a socket.

Callers pick between two shapes, and the choice is the whole point:

``connection()``  autocommit, for reads. No transaction is held open, so a slow
                  serialisation of a large result set cannot pin a transaction
                  id and block vacuum.
``transaction()`` an explicit transaction, for writes. Everything inside commits
                  together or not at all — which is what makes the outbox
                  trustworthy: the event row and the business row share a fate.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import psycopg
from psycopg import AsyncConnection
from psycopg.rows import DictRow, dict_row
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)

#: Every feature planned here works on 15; the deployed server is 15.18.
MINIMUM_SERVER_VERSION = 150000


class DatabaseUnavailableError(RuntimeError):
    """The pool could not be opened or the server failed its checks."""


class Database:
    """Owns the pool lifecycle. Open once at startup, close once at shutdown."""

    def __init__(
        self,
        dsn: str,
        *,
        min_size: int = 2,
        max_size: int = 10,
        connect_timeout_s: float = 10.0,
        pool_timeout_s: float = 10.0,
        statement_timeout_ms: int = 15_000,
        idle_in_transaction_timeout_ms: int = 30_000,
        max_lifetime_s: float = 3600.0,
        max_idle_s: float = 600.0,
        application_name: str = "blogs",
    ) -> None:
        self._dsn = dsn
        self._statement_timeout_ms = statement_timeout_ms
        self._idle_in_transaction_timeout_ms = idle_in_transaction_timeout_ms
        self._server_version: int | None = None

        self._pool: AsyncConnectionPool[AsyncConnection[DictRow]] = AsyncConnectionPool(
            conninfo=dsn,
            min_size=min_size,
            max_size=max_size,
            timeout=pool_timeout_s,
            max_lifetime=max_lifetime_s,
            max_idle=max_idle_s,
            # Opening in the constructor is deprecated in psycopg_pool 3.2+ and
            # would also mean importing this module has a side effect on the
            # network. `open()` is awaited explicitly by bootstrap instead.
            open=False,
            configure=self._configure_connection,
            # Hands out a connection only after confirming it is alive, so a
            # server restart surfaces as one retry rather than as a failed
            # request for every connection that was open at the time.
            check=AsyncConnectionPool.check_connection,
            kwargs={
                "row_factory": dict_row,
                "autocommit": True,
                "connect_timeout": int(connect_timeout_s),
                "application_name": application_name,
            },
        )

    async def _configure_connection(self, conn: AsyncConnection[DictRow]) -> None:
        """Per-connection settings, applied once when the pool creates it.

        ``statement_timeout`` bounds a runaway query.
        ``idle_in_transaction_session_timeout`` bounds a transaction left open by
        a bug — the failure mode that blocks vacuum and eventually wedges the
        whole database, and the one worth spending a setting on.
        ``TimeZone`` is pinned because foundation §9 puts everything in UTC and a
        server default is not something to inherit silently.
        """
        await conn.execute(
            f"SET statement_timeout = {int(self._statement_timeout_ms)}; "
            f"SET idle_in_transaction_session_timeout = "
            f"{int(self._idle_in_transaction_timeout_ms)}; "
            "SET TimeZone = 'UTC';"
        )

    async def open(self) -> None:
        """Open the pool and refuse to proceed on an unusable server."""
        try:
            await self._pool.open(wait=True, timeout=30.0)
        except Exception as exc:  # re-raised as a domain failure
            raise DatabaseUnavailableError(f"could not open the connection pool: {exc}") from exc

        async with self.connection() as conn:
            cursor = await conn.execute(
                "SELECT current_database() AS db, current_user AS usr, version() AS version"
            )
            row = await cursor.fetchone()
            self._server_version = conn.info.server_version

        if self._server_version < MINIMUM_SERVER_VERSION:
            await self.close()
            raise DatabaseUnavailableError(
                f"PostgreSQL {MINIMUM_SERVER_VERSION} or newer is required, "
                f"server reports {self._server_version}"
            )

        logger.info(
            "database pool open",
            extra={
                "database": row["db"] if row else None,
                "db_user": row["usr"] if row else None,
                "server_version": self._server_version,
            },
        )

    async def close(self) -> None:
        await self._pool.close()
        logger.info("database pool closed")

    @property
    def server_version(self) -> int | None:
        return self._server_version

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[AsyncConnection[DictRow]]:
        """A pooled connection in autocommit. For reads."""
        async with self._pool.connection() as conn:
            yield conn

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncConnection[DictRow]]:
        """A pooled connection inside one transaction. For writes.

        Commits on a clean exit, rolls back on any exception. Connections are
        autocommit by default, so ``conn.transaction()`` is what opens the
        explicit block rather than merely nesting a savepoint.
        """
        async with self._pool.connection() as conn, conn.transaction():
            yield conn

    async def healthcheck(self) -> bool:
        """Cheap liveness probe for ``/readyz``."""
        try:
            async with self.connection() as conn:
                await conn.execute("SELECT 1")
        except (psycopg.Error, OSError):
            logger.warning("database healthcheck failed", exc_info=True)
            return False
        return True

    def stats(self) -> dict[str, int]:
        """Pool counters, for the readiness payload and for diagnosing
        exhaustion — a request queue that never drains is visible here long
        before it shows up as a timeout."""
        return dict(self._pool.get_stats())


def build_database(
    dsn: str,
    *,
    min_size: int,
    max_size: int,
    connect_timeout_s: float,
    pool_timeout_s: float,
    statement_timeout_ms: int,
    idle_in_transaction_timeout_ms: int,
    max_lifetime_s: float,
    max_idle_s: float,
) -> Database:
    return Database(
        dsn,
        min_size=min_size,
        max_size=max_size,
        connect_timeout_s=connect_timeout_s,
        pool_timeout_s=pool_timeout_s,
        statement_timeout_ms=statement_timeout_ms,
        idle_in_transaction_timeout_ms=idle_in_transaction_timeout_ms,
        max_lifetime_s=max_lifetime_s,
        max_idle_s=max_idle_s,
    )


__all__ = ["Database", "DatabaseUnavailableError", "build_database"]
