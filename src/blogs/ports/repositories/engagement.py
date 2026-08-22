"""The engagement log port — foundation §8, verbatim.

F1 binds to this to compute affinity and F2 to segment. The three methods the
foundation names are kept with those names and shapes so neither has to adapt.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from blogs.contracts.admin import (
    BlogKpis,
    CategoryCoverageRow,
    EngagementOverTimeRow,
    TimeBucket,
    TopViewedRow,
    TrendingRow,
)
from blogs.contracts.engagement import (
    EngagedBlog,
    EngagementAggregateRow,
    EngagementEvent,
    EngagementKind,
)


class EngagementLog(Protocol):
    """Append-only. There is no update and no delete, by design."""

    async def append(self, event: EngagementEvent) -> bool:
        """Write one event. False when ``dedupe_key`` already existed.

        Not an error: at-least-once delivery from a browser beacon means a
        duplicate is the expected case, not an exceptional one.
        """
        ...

    async def aggregate(
        self,
        *,
        user_id: str,
        window_start: datetime,
        window_end: datetime,
        group_by: TimeBucket,
    ) -> tuple[EngagementAggregateRow, ...]: ...

    async def blogs_engaged_by(
        self, *, user_id: str, since: datetime | None = None, limit: int = 1000
    ) -> tuple[EngagedBlog, ...]:
        """A user's engaged set — F1's input for recomputing affinity."""
        ...

    async def attribute_to_user(self, *, actor_id: str, user_id: str) -> int:
        """Backfill ``user_id`` on an anonymous actor's history at sign-in.

        This is what turns a cold start warm: the account inherits everything
        the visitor did before it existed.
        """
        ...

    async def count_for_actor(self, actor_id: str) -> int: ...


class AnalyticsRepository(Protocol):
    """Admin read models. Nothing here is authoritative — the log is."""

    async def top_viewed(
        self, *, window_start: datetime, window_end: datetime, limit: int
    ) -> tuple[TopViewedRow, ...]: ...

    async def trending(self, *, now: datetime, limit: int) -> tuple[TrendingRow, ...]:
        """Time-decayed engagement weight over the trending window.

        Uses the half-life shape F1 uses for freshness and affinity, with the
        signal weights from ``contracts.engagement`` — one definition site, so
        "trending" and "what we think you like" cannot drift apart.
        """
        ...

    async def by_category(
        self, *, window_start: datetime, window_end: datetime
    ) -> tuple[CategoryCoverageRow, ...]: ...

    async def blog_kpis(
        self, *, blog_id: str, window_start: datetime, window_end: datetime
    ) -> BlogKpis | None: ...

    async def engagement_over_time(
        self,
        *,
        window_start: datetime,
        window_end: datetime,
        bucket: TimeBucket,
        blog_id: str | None = None,
    ) -> tuple[EngagementOverTimeRow, ...]: ...

    async def kind_totals(
        self, *, window_start: datetime, window_end: datetime
    ) -> dict[EngagementKind, int]: ...
