"""Reader email preferences and durable new-article delivery state."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from blogs.contracts.common import BlogId, ContractModel, EmailStr, UserId


class BlogEmailPreference(ContractModel):
    user_id: UserId
    blog_announcements_enabled: bool
    updated_at: datetime


class AnnouncementCampaignStatus(StrEnum):
    QUEUED = "queued"
    SENDING = "sending"
    COMPLETED = "completed"
    PARTIAL = "partial"


class AnnouncementDeliveryStatus(StrEnum):
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    CANCELLED = "cancelled"
    DEAD = "dead"


class AnnouncementCampaignSummary(ContractModel):
    id: str
    blog_id: BlogId
    slug: str
    title: str
    status: AnnouncementCampaignStatus
    pending: int = Field(ge=0)
    sending: int = Field(ge=0)
    sent: int = Field(ge=0)
    cancelled: int = Field(ge=0)
    dead: int = Field(ge=0)
    created_at: datetime
    completed_at: datetime | None = None


class AnnouncementDelivery(ContractModel):
    id: str
    campaign_id: str
    user_id: UserId
    recipient_email: EmailStr
    attempts: int = Field(ge=0)
    title: str
    summary: str | None = None
    cover_image_url: str | None = None
    cover_image_alt: str | None = None
    tag_keys: tuple[str, ...] = ()
    tier: str | None = None
    difficulty: str | None = None
    article_url: str


__all__ = [
    "AnnouncementCampaignStatus",
    "AnnouncementCampaignSummary",
    "AnnouncementDelivery",
    "AnnouncementDeliveryStatus",
    "BlogEmailPreference",
]
