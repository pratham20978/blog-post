"""The domain event catalogue — the only cross-context contract.

Foundation §7 fixes these names and payloads. F3 emits; F1, F2 and F4 consume.
Anything added here must be added to the foundation document first.

Two rules the shapes encode:

* **Secrets never ride the bus.** ``OtpRequested`` and friends carry a
  ``token_ref``, an opaque handle. The code and the link exist only in the
  process that made them and in the message F2 eventually sends.
* **No tags.** ``BlogPublished`` has no ``tag_keys`` field. Foundation §7 lists
  one, but the vocabulary and its weighting are unresolved, and a field that is
  present but meaningless is worse than an absent one — F4 adds it, and adding
  a field is backward-compatible for every consumer.
"""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Literal

from blogs.contracts.common import (
    ActorId,
    BlogId,
    CatalogId,
    ContractModel,
    EmailStr,
    EventId,
    KeyStr,
    NonEmptyStr,
    SeriesId,
    UserId,
)


class DomainEvent(ContractModel):
    """Base for every published event.

    ``event_name`` is a class variable rather than a field: it identifies the
    type and is not something an instance gets to vary.
    """

    event_name: ClassVar[str]
    event_version: ClassVar[int] = 1

    id: EventId
    occurred_at: datetime


# ---------------------------------------------------------------------------
# Auth / user — consumed by F2
# ---------------------------------------------------------------------------


class UserRegistered(DomainEvent):
    event_name: ClassVar[str] = "UserRegistered"

    user_id: UserId
    email: EmailStr
    is_admin: bool
    registered_at: datetime


class OtpRequested(DomainEvent):
    event_name: ClassVar[str] = "OtpRequested"

    subject_user_id: UserId | None = None
    email: EmailStr
    purpose: Literal["login", "signup"]
    #: An opaque handle to the challenge. Never the code.
    token_ref: NonEmptyStr
    expires_at: datetime
    requested_at: datetime


class MagicLinkRequested(DomainEvent):
    event_name: ClassVar[str] = "MagicLinkRequested"

    email: EmailStr
    token_ref: NonEmptyStr
    expires_at: datetime
    requested_at: datetime


class PasswordResetRequested(DomainEvent):
    """Declared because foundation §7 declares it, and F2 will subscribe to it.

    F3 never emits this: authentication here is OTP and OAuth, so there is no
    password to reset. It exists so the catalogue matches the foundation and so
    a future credential type has a name already agreed.
    """

    event_name: ClassVar[str] = "PasswordResetRequested"

    user_id: UserId
    email: EmailStr
    token_ref: NonEmptyStr
    expires_at: datetime
    requested_at: datetime


# ---------------------------------------------------------------------------
# Content — consumed by F4 and F2
# ---------------------------------------------------------------------------


class BlogPublished(DomainEvent):
    event_name: ClassVar[str] = "BlogPublished"

    blog_id: BlogId
    slug: KeyStr
    title: NonEmptyStr
    category_keys: tuple[KeyStr, ...] = ()
    series_id: SeriesId | None = None
    author_id: UserId
    published_at: datetime


class BlogUpdated(DomainEvent):
    event_name: ClassVar[str] = "BlogUpdated"

    blog_id: BlogId
    changed_fields: tuple[NonEmptyStr, ...]
    updated_at: datetime


class BlogArchived(DomainEvent):
    """Deletion is an archive, and consumers must know: F2 should stop linking
    to it and F1 should drop it from candidate generation."""

    event_name: ClassVar[str] = "BlogArchived"

    blog_id: BlogId
    archived_at: datetime


# ---------------------------------------------------------------------------
# Engagement — the log is the primary record; these are for real-time consumers
# ---------------------------------------------------------------------------


class ArticleSaved(DomainEvent):
    event_name: ClassVar[str] = "ArticleSaved"

    user_id: UserId
    blog_id: BlogId
    catalog_id: CatalogId | None = None
    occurred_at: datetime


class ArticleCompleted(DomainEvent):
    event_name: ClassVar[str] = "ArticleCompleted"

    user_id: UserId
    blog_id: BlogId
    occurred_at: datetime


class AnonymousActorMerged(DomainEvent):
    """An anonymous actor's history now belongs to an account.

    F1 wants this: it is the moment a cold-start user stops being cold, and the
    signal to compute an affinity profile from history that already exists
    rather than waiting for the account to generate new engagement.
    """

    event_name: ClassVar[str] = "AnonymousActorMerged"

    actor_id: ActorId
    user_id: UserId
    events_merged: int
    merged_at: datetime


#: Every event this context can publish, by name. The outbox validates against
#: this, so a typo in an event name fails at publish rather than at whichever
#: consumer silently never matches it.
EVENT_TYPES: dict[str, type[DomainEvent]] = {
    cls.event_name: cls
    for cls in (
        UserRegistered,
        OtpRequested,
        MagicLinkRequested,
        PasswordResetRequested,
        BlogPublished,
        BlogUpdated,
        BlogArchived,
        ArticleSaved,
        ArticleCompleted,
        AnonymousActorMerged,
    )
}
