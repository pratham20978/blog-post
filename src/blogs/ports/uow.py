"""The unit of work — how "these writes share a fate" is expressed.

Services depend on ``UnitOfWorkFactory`` and never see a connection, a cursor
or a pool. That is what keeps the application layer free of psycopg, and what
makes the transactional outbox honest: staging an event and writing the row it
describes happen inside one ``begin()``, so there is no window in which one
exists without the other.

Two entry points, and choosing between them is a real decision:

``begin()``  a transaction. Every repository reached through it writes into the
             same one; leaving the block commits, raising rolls back.
``read()``   autocommit. No transaction is held, so a slow read cannot pin a
             transaction id and hold back vacuum.
"""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import Protocol

from blogs.ports.repositories.content import (
    BlogRepository,
    BlogSectionRepository,
    ReferencePinRepository,
    TaxonomyRepository,
)
from blogs.ports.repositories.engagement import AnalyticsRepository, EngagementLog
from blogs.ports.repositories.identity import (
    AdminLoginAttemptRepository,
    AnonymousActorRepository,
    OAuthIdentityRepository,
    OtpChallengeRepository,
    RefreshTokenRepository,
    UserRepository,
)
from blogs.ports.repositories.interaction import (
    CatalogRepository,
    CommentRepository,
    MarkerRepository,
    RecentViewRepository,
)
from blogs.ports.repositories.outbox import OutboxRepository


class UnitOfWork(Protocol):
    """Every repository, bound to one connection."""

    users: UserRepository
    oauth_identities: OAuthIdentityRepository
    otp: OtpChallengeRepository
    refresh_tokens: RefreshTokenRepository
    actors: AnonymousActorRepository
    admin_logins: AdminLoginAttemptRepository

    blogs: BlogRepository
    sections: BlogSectionRepository
    taxonomy: TaxonomyRepository
    pins: ReferencePinRepository

    comments: CommentRepository
    markers: MarkerRepository
    catalogs: CatalogRepository
    recent_views: RecentViewRepository

    engagement: EngagementLog
    analytics: AnalyticsRepository
    outbox: OutboxRepository


class UnitOfWorkFactory(Protocol):
    def begin(self) -> AbstractAsyncContextManager[UnitOfWork]:
        """A transaction. Commits on clean exit, rolls back on any exception."""
        ...

    def read(self) -> AbstractAsyncContextManager[UnitOfWork]:
        """Autocommit, for reads."""
        ...


__all__ = ["UnitOfWork", "UnitOfWorkFactory"]
