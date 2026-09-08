"""Persistence port for blog-announcement campaigns and delivery leases."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from blogs.contracts.announcement import AnnouncementCampaignSummary, AnnouncementDelivery
from blogs.contracts.events import BlogPublished


class AnnouncementRepository(Protocol):
    async def create_for_published(
        self,
        *,
        campaign_id: str,
        event: BlogPublished,
        article_url: str,
        now: datetime,
    ) -> bool:
        """Create one campaign and its eligible delivery rows, idempotently."""
        ...

    async def claim_due(
        self, *, now: datetime, lease_before: datetime, limit: int
    ) -> tuple[AnnouncementDelivery, ...]: ...

    async def preference_enabled(self, user_id: str) -> bool: ...

    async def mark_sent(
        self, *, delivery_id: str, provider_message_id: str | None, now: datetime
    ) -> None: ...

    async def mark_cancelled(self, *, delivery_id: str, now: datetime) -> None: ...

    async def mark_failed(
        self,
        *,
        delivery_id: str,
        error: str,
        next_attempt_at: datetime,
        dead: bool,
    ) -> None: ...

    async def cancel_pending_for_user(self, *, user_id: str, now: datetime) -> int: ...

    async def settle_campaigns(self, *, now: datetime) -> int: ...

    async def get_by_blog(self, blog_id: str) -> AnnouncementCampaignSummary | None: ...

    async def retry_dead(self, *, blog_id: str, now: datetime) -> int: ...


__all__ = ["AnnouncementRepository"]
