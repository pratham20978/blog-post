"""Recording what readers do, and reading it back.

This is the write path for the log every other feature consumes, so two things
are non-negotiable:

**The server decides the subject.** ``RecordEngagementCommand`` carries no
``actor_id``, ``user_id`` or ``occurred_at``. A client able to set those could
write engagement attributed to anyone, and the log is exactly what F1's affinity
and F2's segmentation are computed from — corrupting it corrupts both.

**The append and the projection commit together.** ``recent_views`` is a summary
of the log, so it is written in the same transaction. Two transactions could
leave a view count that no event supports.
"""

from __future__ import annotations

import logging
from datetime import datetime

from blogs.contracts.common import ErrorCategory
from blogs.contracts.engagement import (
    EngagementEvent,
    EngagementKind,
    RecordEngagementCommand,
)
from blogs.contracts.events import ArticleCompleted, ArticleSaved
from blogs.contracts.identity import Principal, UserPrincipal
from blogs.contracts.interaction import RecentView
from blogs.core.clock import Clock
from blogs.core.errors import raise_error
from blogs.core.ids import IdGenerator
from blogs.ports.services import AuthorizationPolicy
from blogs.ports.uow import UnitOfWorkFactory
from blogs.services.policy import require

logger = logging.getLogger(__name__)

#: Kinds that mean "this person actually looked at this article", and so should
#: move the recent-views projection. An impression is a listing appearing on
#: screen, which is not the same as having read anything.
_VIEW_KINDS = frozenset(
    {EngagementKind.CLICK, EngagementKind.DWELL, EngagementKind.COMPLETE}
)


class EngagementService:
    def __init__(
        self,
        *,
        uow: UnitOfWorkFactory,
        clock: Clock,
        ids: IdGenerator,
        policy: AuthorizationPolicy,
        recent_view_limit: int = 50,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._ids = ids
        self._policy = policy
        self._recent_view_limit = recent_view_limit

    async def record(
        self,
        *,
        principal: Principal,
        command: RecordEngagementCommand,
        client_ip: str | None = None,
        correlation_id: str | None = None,
    ) -> bool:
        """Append one event. Returns False when it was a duplicate.

        Allowed for anonymous callers — that is the entire point of the actor
        id, and without it every account would start genuinely cold.
        """
        require(
            self._policy.can_record_engagement(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        now = self._clock.now()
        event_id = self._ids.new_id()
        user_id = principal.user_id if isinstance(principal, UserPrincipal) else None

        event = EngagementEvent(
            id=event_id,
            occurred_at=now,
            actor_id=principal.actor_id,
            user_id=user_id,
            blog_id=command.blog_id,
            kind=command.kind,
            position=command.position,
            query_id=command.query_id,
            dwell_ms=command.dwell_ms,
            scroll_depth=command.scroll_depth,
            source=command.source,
            # Scoped to the actor so one client's key cannot collide with — or
            # be used to suppress — another's.
            dedupe_key=(
                f"{principal.actor_id}:{command.dedupe_key}"
                if command.dedupe_key
                else event_id
            ),
            metadata={},
        )

        async with self._uow.begin() as uow:
            appended = await uow.engagement.append(event)
            if not appended:
                # A retried beacon. Expected, not exceptional — and it must not
                # increment the view count a second time.
                return False

            if command.blog_id and command.kind in _VIEW_KINDS:
                await uow.recent_views.record(
                    actor_id=principal.actor_id,
                    user_id=user_id,
                    blog_id=command.blog_id,
                    now=now,
                )

            # Foundation §7 publishes these two for real-time consumers; the
            # rest live in the log alone until something needs them.
            if user_id and command.blog_id:
                if command.kind is EngagementKind.COMPLETE:
                    await uow.outbox.add(
                        ArticleCompleted(
                            id=self._ids.new_id(),
                            occurred_at=now,
                            user_id=user_id,
                            blog_id=command.blog_id,
                        ),
                        aggregate_type="blog",
                        aggregate_id=command.blog_id,
                    )
                elif command.kind is EngagementKind.SAVE:
                    await uow.outbox.add(
                        ArticleSaved(
                            id=self._ids.new_id(),
                            occurred_at=now,
                            user_id=user_id,
                            blog_id=command.blog_id,
                        ),
                        aggregate_type="blog",
                        aggregate_id=command.blog_id,
                    )
        return True

    async def recent_views(
        self, *, principal: Principal, limit: int | None = None
    ) -> tuple[RecentView, ...]:
        """What this caller looked at lately.

        Reads by user when signed in and by actor otherwise. After a merge the
        two agree, because the merge rewrote ``user_id`` on the rows the actor
        had already accumulated.
        """
        resolved = min(limit or self._recent_view_limit, self._recent_view_limit)
        async with self._uow.read() as uow:
            if isinstance(principal, UserPrincipal):
                return await uow.recent_views.list_for_user(
                    user_id=principal.user_id, limit=resolved
                )
            return await uow.recent_views.list_for_actor(
                actor_id=principal.actor_id, limit=resolved
            )

    async def engaged_blogs(
        self,
        *,
        principal: Principal,
        since: datetime | None = None,
        correlation_id: str | None = None,
    ) -> tuple[object, ...]:
        """A user's engaged set — the shape F1 will consume for affinity."""
        if not isinstance(principal, UserPrincipal):
            raise_error(ErrorCategory.AUTH_REQUIRED, correlation_id=correlation_id)
        async with self._uow.read() as uow:
            return await uow.engagement.blogs_engaged_by(
                user_id=principal.user_id, since=since
            )
