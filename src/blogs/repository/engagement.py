"""SQL adapters for the engagement log and the admin read models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from psycopg.rows import DictRow
from psycopg.types.json import Jsonb

from blogs.contracts.admin import (
    BlogKpis,
    CategoryCoverageRow,
    EngagementOverTimeRow,
    TimeBucket,
    TopViewedRow,
    TrendingRow,
)
from blogs.contracts.engagement import (
    ENGAGEMENT_SIGNAL_WEIGHTS,
    TRENDING_HALF_LIFE_HOURS,
    TRENDING_WINDOW_DAYS,
    EngagedBlog,
    EngagementAggregateRow,
    EngagementEvent,
    EngagementKind,
)
from blogs.repository.base import SqlRepository, as_utc

#: PostgreSQL ``date_trunc`` accepts these directly. Mapped through a dict
#: rather than interpolated from the enum so nothing user-supplied can ever
#: reach the SQL string, even by accident.
_BUCKET_SQL: dict[TimeBucket, str] = {
    TimeBucket.HOUR: "hour",
    TimeBucket.DAY: "day",
    TimeBucket.WEEK: "week",
    TimeBucket.MONTH: "month",
}


def _signal_weights_sql() -> str:
    """Render the shared signal weights as a SQL CASE expression.

    Generated from ``ENGAGEMENT_SIGNAL_WEIGHTS`` rather than written out, so the
    query and F1's affinity maths cannot drift apart. The values are floats from
    a module constant, never from a request.
    """
    branches = " ".join(
        f"WHEN '{kind.value}' THEN {weight:.4f}"
        for kind, weight in ENGAGEMENT_SIGNAL_WEIGHTS.items()
    )
    return f"CASE e.kind {branches} ELSE 0.0 END"


class SqlEngagementLog(SqlRepository):
    async def append(self, event: EngagementEvent) -> bool:
        """Insert one event, suppressing the duplicate a retried beacon causes.

        Deduplication is claimed against ``engagement_dedupe`` first, whose
        primary key is the dedupe key alone. It cannot live on
        ``engagement_events`` itself: a unique index on a partitioned table must
        include the partition key, and pairing the key with the server-assigned
        ``occurred_at`` makes every retry unique again — which is precisely how
        this failed before migration 007.

        Claiming first is what makes it race-free. Two simultaneous retries
        contend on one primary key, exactly one wins, and only the winner goes
        on to write the event. Both statements are in the caller's transaction,
        so a rollback releases the claim rather than stranding it.
        """
        claimed = await self._execute(
            """
            INSERT INTO engagement_dedupe (dedupe_key, first_seen_at)
            VALUES (%(dedupe)s, %(at)s)
            ON CONFLICT (dedupe_key) DO NOTHING
            """,
            {"dedupe": event.dedupe_key, "at": as_utc(event.occurred_at)},
        )
        if claimed == 0:
            return False

        affected = await self._execute(
            """
            INSERT INTO engagement_events
                (id, occurred_at, actor_id, user_id, blog_id, kind, position,
                 query_id, dwell_ms, scroll_depth, source, dedupe_key, metadata)
            VALUES
                (%(id)s, %(at)s, %(actor)s, %(user)s, %(blog)s, %(kind)s, %(pos)s,
                 %(query)s, %(dwell)s, %(scroll)s, %(source)s, %(dedupe)s, %(meta)s)
            """,
            {
                "id": event.id,
                "at": as_utc(event.occurred_at),
                "actor": event.actor_id,
                "user": event.user_id,
                "blog": event.blog_id,
                "kind": event.kind.value,
                "pos": event.position,
                "query": event.query_id,
                "dwell": event.dwell_ms,
                "scroll": event.scroll_depth,
                "source": event.source.value if event.source else None,
                "dedupe": event.dedupe_key,
                "meta": Jsonb(event.metadata),
            },
        )
        return affected == 1

    async def aggregate(
        self,
        *,
        user_id: str,
        window_start: datetime,
        window_end: datetime,
        group_by: TimeBucket,
    ) -> tuple[EngagementAggregateRow, ...]:
        rows = await self._fetch_all(
            f"""
            SELECT date_trunc('{_BUCKET_SQL[group_by]}', e.occurred_at) AS bucket,
                   e.kind,
                   count(*)                    AS event_count,
                   count(DISTINCT e.actor_id)  AS actor_count
            FROM engagement_events e
            WHERE e.user_id = %(user)s
              AND e.occurred_at >= %(start)s AND e.occurred_at < %(end)s
            GROUP BY 1, 2
            ORDER BY 1, 2
            """,
            {"user": user_id, "start": as_utc(window_start), "end": as_utc(window_end)},
        )
        return tuple(
            EngagementAggregateRow(
                bucket=r["bucket"].isoformat(),
                kind=EngagementKind(r["kind"]),
                event_count=r["event_count"],
                actor_count=r["actor_count"],
            )
            for r in rows
        )

    async def blogs_engaged_by(
        self, *, user_id: str, since: datetime | None = None, limit: int = 1000
    ) -> tuple[EngagedBlog, ...]:
        rows = await self._fetch_all(
            """
            SELECT e.blog_id, e.kind, e.occurred_at
            FROM engagement_events e
            WHERE e.user_id = %(user)s
              AND e.blog_id IS NOT NULL
              AND (%(since)s::timestamptz IS NULL OR e.occurred_at >= %(since)s)
            ORDER BY e.occurred_at DESC
            LIMIT %(limit)s
            """,
            {
                "user": user_id,
                "since": as_utc(since) if since else None,
                "limit": limit,
            },
        )
        return tuple(
            EngagedBlog(
                blog_id=str(r["blog_id"]),
                kind=EngagementKind(r["kind"]),
                occurred_at=r["occurred_at"],
            )
            for r in rows
        )

    async def attribute_to_user(self, *, actor_id: str, user_id: str) -> int:
        """Claim an anonymous actor's history for the account that just signed in.

        Only rows still unattributed are touched, so replaying an actor token
        cannot move history between accounts.
        """
        return await self._execute(
            """
            UPDATE engagement_events SET user_id = %(user)s
            WHERE actor_id = %(actor)s AND user_id IS NULL
            """,
            {"user": user_id, "actor": actor_id},
        )

    async def count_for_actor(self, actor_id: str) -> int:
        row = await self._fetch_one(
            "SELECT count(*) AS n FROM engagement_events WHERE actor_id = %(a)s",
            {"a": actor_id},
        )
        return int(row["n"]) if row else 0


def _kind_counts(row: DictRow) -> dict[str, int]:
    return {k: int(row.get(k) or 0) for k in ("impressions", "clicks", "completions")}


class SqlAnalyticsRepository(SqlRepository):
    async def top_viewed(
        self, *, window_start: datetime, window_end: datetime, limit: int
    ) -> tuple[TopViewedRow, ...]:
        rows = await self._fetch_all(
            """
            SELECT b.id, b.slug, b.title,
                   count(*) FILTER (WHERE e.kind = 'impression') AS impressions,
                   count(*) FILTER (WHERE e.kind = 'click')      AS clicks,
                   count(*) FILTER (WHERE e.kind = 'complete')   AS completions,
                   count(DISTINCT e.actor_id)                    AS unique_actors
            FROM engagement_events e
            JOIN blogs b ON b.id = e.blog_id
            WHERE e.occurred_at >= %(start)s AND e.occurred_at < %(end)s
            GROUP BY b.id
            ORDER BY clicks DESC, impressions DESC
            LIMIT %(limit)s
            """,
            {"start": as_utc(window_start), "end": as_utc(window_end), "limit": limit},
        )
        return tuple(
            TopViewedRow(
                blog_id=str(r["id"]),
                slug=r["slug"],
                title=r["title"],
                impressions=r["impressions"],
                clicks=r["clicks"],
                completions=r["completions"],
                unique_actors=r["unique_actors"],
            )
            for r in rows
        )

    async def trending(self, *, now: datetime, limit: int) -> tuple[TrendingRow, ...]:
        """Time-decayed engagement weight.

        ``weight · 0.5 ^ (age_hours / half_life)`` — the same exponential shape
        F1 will use for freshness and affinity decay, with a deliberately short
        half-life. Doc 01 asks for a trending definition consistent with F1
        rather than a second, unrelated model, and sharing the shape *and* the
        signal weights is what makes that true rather than merely intended.
        """
        rows = await self._fetch_all(
            f"""
            SELECT b.id, b.slug, b.title,
                   sum(
                       ({_signal_weights_sql()})
                       * power(0.5, EXTRACT(EPOCH FROM (%(now)s - e.occurred_at))
                                    / 3600.0 / %(half_life)s)
                   )        AS score,
                   count(*) AS raw_events
            FROM engagement_events e
            JOIN blogs b ON b.id = e.blog_id
            WHERE e.occurred_at >= %(now)s - make_interval(days => %(window_days)s)
              AND e.occurred_at <= %(now)s
              AND b.status = 'published'
            GROUP BY b.id
            HAVING sum(
                       ({_signal_weights_sql()})
                       * power(0.5, EXTRACT(EPOCH FROM (%(now)s - e.occurred_at))
                                    / 3600.0 / %(half_life)s)
                   ) > 0
            ORDER BY score DESC
            LIMIT %(limit)s
            """,
            {
                "now": as_utc(now),
                "half_life": TRENDING_HALF_LIFE_HOURS,
                "window_days": TRENDING_WINDOW_DAYS,
                "limit": limit,
            },
        )
        return tuple(
            TrendingRow(
                blog_id=str(r["id"]),
                slug=r["slug"],
                title=r["title"],
                score=float(r["score"]),
                raw_events=r["raw_events"],
            )
            for r in rows
        )

    async def by_category(
        self, *, window_start: datetime, window_end: datetime
    ) -> tuple[CategoryCoverageRow, ...]:
        rows = await self._fetch_all(
            """
            SELECT c.key, c.label,
                   count(DISTINCT bc.blog_id) AS blog_count,
                   count(e.id) FILTER (WHERE e.kind = 'impression') AS impressions,
                   count(e.id) FILTER (WHERE e.kind = 'click')      AS clicks
            FROM categories c
            LEFT JOIN blog_categories bc ON bc.category_key = c.key
            LEFT JOIN engagement_events e
                   ON e.blog_id = bc.blog_id
                  AND e.occurred_at >= %(start)s AND e.occurred_at < %(end)s
            GROUP BY c.key, c.label
            ORDER BY clicks DESC, c.key
            """,
            {"start": as_utc(window_start), "end": as_utc(window_end)},
        )
        return tuple(
            CategoryCoverageRow(
                category_key=r["key"],
                label=r["label"],
                blog_count=r["blog_count"],
                impressions=r["impressions"],
                clicks=r["clicks"],
            )
            for r in rows
        )

    async def blog_kpis(
        self, *, blog_id: str, window_start: datetime, window_end: datetime
    ) -> BlogKpis | None:
        row = await self._fetch_one(
            """
            SELECT b.id, b.slug, b.title,
                   count(e.id) FILTER (WHERE e.kind = 'impression') AS impressions,
                   count(e.id) FILTER (WHERE e.kind = 'click')      AS clicks,
                   count(e.id) FILTER (WHERE e.kind = 'complete')   AS completions,
                   count(e.id) FILTER (WHERE e.kind = 'save')       AS saves,
                   count(e.id) FILTER (WHERE e.kind = 'share')      AS shares,
                   count(DISTINCT e.actor_id)                       AS unique_actors,
                   count(DISTINCT e.user_id)                        AS unique_users,
                   percentile_cont(0.5) WITHIN GROUP (ORDER BY e.dwell_ms)
                       FILTER (WHERE e.dwell_ms IS NOT NULL)        AS median_dwell,
                   (SELECT count(*) FROM comments cm
                     WHERE cm.blog_id = b.id AND cm.deleted_at IS NULL) AS comment_count
            FROM blogs b
            LEFT JOIN engagement_events e
                   ON e.blog_id = b.id
                  AND e.occurred_at >= %(start)s AND e.occurred_at < %(end)s
            WHERE b.id = %(id)s
            GROUP BY b.id
            """,
            {"id": blog_id, "start": as_utc(window_start), "end": as_utc(window_end)},
        )
        if row is None:
            return None

        impressions = int(row["impressions"])
        clicks = int(row["clicks"])
        return BlogKpis(
            blog_id=str(row["id"]),
            slug=row["slug"],
            title=row["title"],
            impressions=impressions,
            clicks=clicks,
            completions=row["completions"],
            saves=row["saves"],
            shares=row["shares"],
            comment_count=row["comment_count"],
            unique_actors=row["unique_actors"],
            unique_users=row["unique_users"],
            median_dwell_ms=int(row["median_dwell"]) if row["median_dwell"] else None,
            # None rather than 0.0 with no impressions: "nobody saw it" and
            # "everybody ignored it" are different facts.
            click_through_rate=(clicks / impressions) if impressions else None,
        )

    async def engagement_over_time(
        self,
        *,
        window_start: datetime,
        window_end: datetime,
        bucket: TimeBucket,
        blog_id: str | None = None,
    ) -> tuple[EngagementOverTimeRow, ...]:
        params: dict[str, Any] = {
            "start": as_utc(window_start),
            "end": as_utc(window_end),
            "blog": blog_id,
        }
        rows = await self._fetch_all(
            f"""
            SELECT date_trunc('{_BUCKET_SQL[bucket]}', e.occurred_at) AS bucket_start,
                   count(*) FILTER (WHERE e.kind = 'impression') AS impressions,
                   count(*) FILTER (WHERE e.kind = 'click')      AS clicks,
                   count(*) FILTER (WHERE e.kind = 'complete')   AS completions,
                   count(*) FILTER (WHERE e.kind = 'save')       AS saves,
                   count(*) FILTER (WHERE e.kind = 'comment')    AS comments,
                   count(DISTINCT e.actor_id)                    AS unique_actors
            FROM engagement_events e
            WHERE e.occurred_at >= %(start)s AND e.occurred_at < %(end)s
              AND (%(blog)s::uuid IS NULL OR e.blog_id = %(blog)s)
            GROUP BY 1
            ORDER BY 1
            """,
            params,
        )
        return tuple(
            EngagementOverTimeRow(
                bucket_start=r["bucket_start"],
                impressions=r["impressions"],
                clicks=r["clicks"],
                completions=r["completions"],
                saves=r["saves"],
                comments=r["comments"],
                unique_actors=r["unique_actors"],
            )
            for r in rows
        )

    async def kind_totals(
        self, *, window_start: datetime, window_end: datetime
    ) -> dict[EngagementKind, int]:
        rows = await self._fetch_all(
            """
            SELECT kind, count(*) AS n FROM engagement_events
            WHERE occurred_at >= %(start)s AND occurred_at < %(end)s
            GROUP BY kind
            """,
            {"start": as_utc(window_start), "end": as_utc(window_end)},
        )
        return {EngagementKind(r["kind"]): int(r["n"]) for r in rows}
