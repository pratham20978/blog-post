"""The Postgres unit of work.

This is the only place that knows a repository needs a connection. Services ask
the factory for a scope, use the repositories hanging off it, and never learn
that psycopg exists.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from psycopg import AsyncConnection
from psycopg.rows import DictRow

from blogs.database.session import Database
from blogs.repository.content import (
    SqlBlogRepository,
    SqlBlogSectionRepository,
    SqlReferencePinRepository,
    SqlTaxonomyRepository,
)
from blogs.repository.engagement import SqlAnalyticsRepository, SqlEngagementLog
from blogs.repository.identity import (
    SqlAdminLoginAttemptRepository,
    SqlAnonymousActorRepository,
    SqlOAuthIdentityRepository,
    SqlOtpChallengeRepository,
    SqlRefreshTokenRepository,
    SqlUserRepository,
)
from blogs.repository.interaction import (
    SqlCatalogRepository,
    SqlCommentRepository,
    SqlMarkerRepository,
    SqlRecentViewRepository,
)
from blogs.repository.outbox import SqlOutboxRepository


class SqlUnitOfWork:
    """Every repository, all sharing one connection.

    Constructing the whole set costs a dozen small objects holding a single
    reference each — cheap enough that binding them eagerly is simpler than
    lazily, and it means a service can reach any of them without the factory
    having to know in advance which it will use.
    """

    __slots__ = (
        "actors",
        "admin_logins",
        "analytics",
        "blogs",
        "catalogs",
        "comments",
        "connection",
        "engagement",
        "markers",
        "oauth_identities",
        "otp",
        "outbox",
        "pins",
        "recent_views",
        "refresh_tokens",
        "sections",
        "taxonomy",
        "users",
    )

    def __init__(self, conn: AsyncConnection[DictRow]) -> None:
        self.connection = conn

        self.users = SqlUserRepository(conn)
        self.oauth_identities = SqlOAuthIdentityRepository(conn)
        self.otp = SqlOtpChallengeRepository(conn)
        self.refresh_tokens = SqlRefreshTokenRepository(conn)
        self.actors = SqlAnonymousActorRepository(conn)
        self.admin_logins = SqlAdminLoginAttemptRepository(conn)

        self.blogs = SqlBlogRepository(conn)
        self.sections = SqlBlogSectionRepository(conn)
        self.taxonomy = SqlTaxonomyRepository(conn)
        self.pins = SqlReferencePinRepository(conn)

        self.comments = SqlCommentRepository(conn)
        self.markers = SqlMarkerRepository(conn)
        self.catalogs = SqlCatalogRepository(conn)
        self.recent_views = SqlRecentViewRepository(conn)

        self.engagement = SqlEngagementLog(conn)
        self.analytics = SqlAnalyticsRepository(conn)
        self.outbox = SqlOutboxRepository(conn)


class SqlUnitOfWorkFactory:
    """Hands out scopes over one pool."""

    __slots__ = ("_database",)

    def __init__(self, database: Database) -> None:
        self._database = database

    @asynccontextmanager
    async def begin(self) -> AsyncIterator[SqlUnitOfWork]:
        """A transaction.

        Everything written through the yielded unit of work commits together.
        This is what makes the outbox meaningful: an event staged here cannot
        outlive a rollback of the change it describes.
        """
        async with self._database.transaction() as conn:
            yield SqlUnitOfWork(conn)

    @asynccontextmanager
    async def read(self) -> AsyncIterator[SqlUnitOfWork]:
        """Autocommit, for reads.

        No transaction is held open, so serialising a large result set cannot
        pin a transaction id and hold back vacuum on the engagement log.
        """
        async with self._database.connection() as conn:
            yield SqlUnitOfWork(conn)
