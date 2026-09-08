"""Postgres adapter for durable new-blog email campaigns."""

from __future__ import annotations

from datetime import datetime

from blogs.contracts.announcement import (
    AnnouncementCampaignStatus,
    AnnouncementCampaignSummary,
    AnnouncementDelivery,
)
from blogs.contracts.events import BlogPublished
from blogs.repository.base import SqlRepository, as_utc


class SqlAnnouncementRepository(SqlRepository):
    async def create_for_published(
        self,
        *,
        campaign_id: str,
        event: BlogPublished,
        article_url: str,
        now: datetime,
    ) -> bool:
        row = await self._fetch_one(
            """
            INSERT INTO blog_announcement_campaigns
                (id, event_id, blog_id, slug, title, summary,
                 cover_image_url, cover_image_alt, tag_keys, tier, difficulty,
                 article_url, created_at)
            VALUES
                (%(id)s, %(event)s, %(blog)s, %(slug)s, %(title)s, %(summary)s,
                 %(cover_url)s, %(cover_alt)s, %(tags)s, %(tier)s, %(difficulty)s,
                 %(url)s, %(now)s)
            ON CONFLICT DO NOTHING
            RETURNING id
            """,
            {
                "id": campaign_id,
                "event": event.id,
                "blog": event.blog_id,
                "slug": event.slug,
                "title": event.title,
                "summary": event.summary,
                "cover_url": event.cover_image_url,
                "cover_alt": event.cover_image_alt,
                "tags": list(event.tag_keys),
                "tier": event.tier.value if event.tier else None,
                "difficulty": event.difficulty.value if event.difficulty else None,
                "url": article_url,
                "now": as_utc(now),
            },
        )
        if row is None:
            return False

        # gen_random_uuid() is built into supported PostgreSQL versions; it is
        # used only for opaque delivery row identity. Domain aggregate ids stay
        # application-generated UUIDv7 values.
        await self._execute(
            """
            INSERT INTO blog_announcement_deliveries
                (id, campaign_id, user_id, recipient_email, next_attempt_at, created_at)
            SELECT gen_random_uuid(), %(campaign)s, u.id, u.email, %(now)s, %(now)s
            FROM users u
            WHERE u.status = 'active'
              AND NOT u.is_admin
              AND u.email_verified_at IS NOT NULL
              AND u.blog_announcements_enabled
            ON CONFLICT (campaign_id, user_id) DO NOTHING
            """,
            {"campaign": campaign_id, "now": as_utc(now)},
        )
        await self.settle_campaigns(now=now)
        return True

    async def claim_due(
        self, *, now: datetime, lease_before: datetime, limit: int
    ) -> tuple[AnnouncementDelivery, ...]:
        rows = await self._fetch_all(
            """
            WITH selected AS (
                SELECT d.id
                FROM blog_announcement_deliveries d
                WHERE (
                    d.status = 'pending' AND d.next_attempt_at <= %(now)s
                ) OR (
                    d.status = 'sending' AND d.locked_at <= %(lease_before)s
                )
                ORDER BY d.next_attempt_at, d.id
                LIMIT %(limit)s
                FOR UPDATE SKIP LOCKED
            ), claimed AS (
                UPDATE blog_announcement_deliveries d
                SET status = 'sending', locked_at = %(now)s, attempts = attempts + 1
                FROM selected
                WHERE d.id = selected.id
                RETURNING d.*
            )
            SELECT c.id AS campaign_id, c.title, c.summary, c.cover_image_url,
                   c.cover_image_alt, c.tag_keys, c.tier, c.difficulty, c.article_url,
                   d.id, d.user_id, d.recipient_email, d.attempts
            FROM claimed d
            JOIN blog_announcement_campaigns c ON c.id = d.campaign_id
            ORDER BY d.id
            """,
            {
                "now": as_utc(now),
                "lease_before": as_utc(lease_before),
                "limit": limit,
            },
        )
        return tuple(
            AnnouncementDelivery(
                id=str(row["id"]),
                campaign_id=str(row["campaign_id"]),
                user_id=str(row["user_id"]),
                recipient_email=row["recipient_email"],
                attempts=int(row["attempts"]),
                title=row["title"],
                summary=row["summary"],
                cover_image_url=row["cover_image_url"],
                cover_image_alt=row["cover_image_alt"],
                tag_keys=tuple(row["tag_keys"] or ()),
                tier=row["tier"],
                difficulty=row["difficulty"],
                article_url=row["article_url"],
            )
            for row in rows
        )

    async def preference_enabled(self, user_id: str) -> bool:
        row = await self._fetch_one(
            """
            SELECT 1 AS enabled FROM users
            WHERE id = %(user)s AND status = 'active' AND NOT is_admin
              AND email_verified_at IS NOT NULL AND blog_announcements_enabled
            """,
            {"user": user_id},
        )
        return row is not None

    async def mark_sent(
        self, *, delivery_id: str, provider_message_id: str | None, now: datetime
    ) -> None:
        await self._execute(
            """
            UPDATE blog_announcement_deliveries
            SET status = 'sent', sent_at = %(now)s, locked_at = NULL,
                provider_message_id = %(provider)s, last_error = NULL
            WHERE id = %(id)s AND status = 'sending'
            """,
            {"id": delivery_id, "provider": provider_message_id, "now": as_utc(now)},
        )

    async def mark_cancelled(self, *, delivery_id: str, now: datetime) -> None:
        await self._execute(
            """
            UPDATE blog_announcement_deliveries
            SET status = 'cancelled', locked_at = NULL, last_error = NULL
            WHERE id = %(id)s AND status IN ('pending', 'sending')
            """,
            {"id": delivery_id, "now": as_utc(now)},
        )

    async def mark_failed(
        self,
        *,
        delivery_id: str,
        error: str,
        next_attempt_at: datetime,
        dead: bool,
    ) -> None:
        await self._execute(
            """
            UPDATE blog_announcement_deliveries
            SET status = CASE WHEN %(dead)s THEN 'dead' ELSE 'pending' END,
                next_attempt_at = %(next)s, locked_at = NULL,
                last_error = %(error)s
            WHERE id = %(id)s AND status = 'sending'
            """,
            {
                "id": delivery_id,
                "dead": dead,
                "next": as_utc(next_attempt_at),
                "error": error[:2000],
            },
        )

    async def cancel_pending_for_user(self, *, user_id: str, now: datetime) -> int:
        return await self._execute(
            """
            UPDATE blog_announcement_deliveries
            SET status = 'cancelled', locked_at = NULL, last_error = NULL
            WHERE user_id = %(user)s AND status IN ('pending', 'sending')
            """,
            {"user": user_id, "now": as_utc(now)},
        )

    async def settle_campaigns(self, *, now: datetime) -> int:
        return await self._execute(
            """
            WITH counts AS (
                SELECT c.id,
                       count(d.id) FILTER (WHERE d.status IN ('pending', 'sending')) AS open,
                       count(d.id) FILTER (WHERE d.status = 'dead') AS dead
                FROM blog_announcement_campaigns c
                LEFT JOIN blog_announcement_deliveries d ON d.campaign_id = c.id
                GROUP BY c.id
            )
            UPDATE blog_announcement_campaigns c
            SET status = CASE
                    WHEN x.open > 0 THEN 'sending'
                    WHEN x.dead > 0 THEN 'partial'
                    ELSE 'completed'
                END,
                completed_at = CASE WHEN x.open > 0 THEN NULL ELSE %(now)s END
            FROM counts x
            WHERE c.id = x.id
              AND (
                  (x.open > 0 AND c.status <> 'sending')
                  OR (x.open = 0 AND x.dead > 0 AND c.status <> 'partial')
                  OR (x.open = 0 AND x.dead = 0 AND c.status <> 'completed')
              )
            """,
            {"now": as_utc(now)},
        )

    async def get_by_blog(self, blog_id: str) -> AnnouncementCampaignSummary | None:
        row = await self._fetch_one(
            """
            SELECT c.id, c.blog_id, c.slug, c.title, c.status, c.created_at,
                   c.completed_at,
                   count(d.id) FILTER (WHERE d.status = 'pending') AS pending,
                   count(d.id) FILTER (WHERE d.status = 'sending') AS sending,
                   count(d.id) FILTER (WHERE d.status = 'sent') AS sent,
                   count(d.id) FILTER (WHERE d.status = 'cancelled') AS cancelled,
                   count(d.id) FILTER (WHERE d.status = 'dead') AS dead
            FROM blog_announcement_campaigns c
            LEFT JOIN blog_announcement_deliveries d ON d.campaign_id = c.id
            WHERE c.blog_id = %(blog)s
            GROUP BY c.id
            """,
            {"blog": blog_id},
        )
        if row is None:
            return None
        return AnnouncementCampaignSummary(
            id=str(row["id"]),
            blog_id=str(row["blog_id"]),
            slug=row["slug"],
            title=row["title"],
            status=AnnouncementCampaignStatus(row["status"]),
            pending=int(row["pending"]),
            sending=int(row["sending"]),
            sent=int(row["sent"]),
            cancelled=int(row["cancelled"]),
            dead=int(row["dead"]),
            created_at=row["created_at"],
            completed_at=row["completed_at"],
        )

    async def retry_dead(self, *, blog_id: str, now: datetime) -> int:
        affected = await self._execute(
            """
            UPDATE blog_announcement_deliveries d
            SET status = 'pending', attempts = 0, next_attempt_at = %(now)s,
                locked_at = NULL, last_error = NULL
            FROM blog_announcement_campaigns c
            WHERE d.campaign_id = c.id AND c.blog_id = %(blog)s AND d.status = 'dead'
            """,
            {"blog": blog_id, "now": as_utc(now)},
        )
        if affected:
            await self._execute(
                """
                UPDATE blog_announcement_campaigns
                SET status = 'queued', completed_at = NULL
                WHERE blog_id = %(blog)s
                """,
                {"blog": blog_id},
            )
        return affected


__all__ = ["SqlAnnouncementRepository"]
