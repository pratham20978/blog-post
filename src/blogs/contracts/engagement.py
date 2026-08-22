"""The engagement log — the one thing F1, F2 and F4 all read.

Append-only, partitioned by month. Foundation §8 fixes the port's shape and §9
fixes the conventions; this module fixes the row.

Every event carries an ``actor_id`` and an optional ``user_id``. Anonymous
traffic writes with ``user_id`` null and gets it backfilled when that actor
signs in, which is what gives a brand-new account a history to personalise from
on its very first page.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import Field, JsonValue

from blogs.contracts.common import (
    ActorId,
    BlogId,
    ContractModel,
    EventId,
    NonEmptyStr,
    UserId,
)


class EngagementKind(StrEnum):
    """The closed set of things we record. Foundation §5."""

    IMPRESSION = "impression"
    CLICK = "click"
    DWELL = "dwell"
    COMPLETE = "complete"
    SAVE = "save"
    SHARE = "share"
    COMMENT = "comment"
    #: Written by F1 when it shows a result list. Defined here because the log
    #: is shared and its closed set must be agreed in one place.
    SEARCH_IMPRESSION = "search_impression"


class EngagementSource(StrEnum):
    FEED = "feed"
    SEARCH = "search"
    SERIES = "series"
    CATALOG = "catalog"
    DIRECT = "direct"


class EngagementEvent(ContractModel):
    """One row of the log.

    ``dedupe_key`` exists because ingestion from a browser is at-least-once: a
    retried beacon must not become a second row. It defaults to the event id,
    so a caller that has no natural key still gets a unique one.
    """

    id: EventId
    occurred_at: datetime
    actor_id: ActorId
    user_id: UserId | None = None
    blog_id: BlogId | None = None
    kind: EngagementKind
    position: int | None = Field(default=None, ge=0)
    query_id: str | None = None
    dwell_ms: int | None = Field(default=None, ge=0)
    scroll_depth: float | None = Field(default=None, ge=0.0, le=1.0)
    source: EngagementSource | None = None
    dedupe_key: NonEmptyStr
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class RecordEngagementCommand(ContractModel):
    """What a client may assert. Note what is absent: ``actor_id``, ``user_id``
    and ``occurred_at``. Those are the server's to decide — a client that could
    set them could write engagement for somebody else, poisoning the log that
    F1's affinity and F2's segmentation are computed from.
    """

    blog_id: BlogId | None = None
    kind: EngagementKind
    position: int | None = Field(default=None, ge=0)
    query_id: str | None = None
    dwell_ms: int | None = Field(default=None, ge=0, le=86_400_000)
    scroll_depth: float | None = Field(default=None, ge=0.0, le=1.0)
    source: EngagementSource | None = None
    dedupe_key: str | None = None


class EngagementAggregateRow(ContractModel):
    bucket: NonEmptyStr
    kind: EngagementKind | None = None
    event_count: int = Field(ge=0)
    actor_count: int = Field(ge=0)


class EngagedBlog(ContractModel):
    """What ``EngagementLog.blogs_engaged_by`` returns — F1's input for
    recomputing affinity over a user's engaged set."""

    blog_id: BlogId
    kind: EngagementKind
    occurred_at: datetime


# ---------------------------------------------------------------------------
# Signal weights
#
# One definition site, imported by both the trending query here and F1's
# affinity math later. Two copies of these numbers would drift, and the moment
# they did, "trending" and "what we think you like" would silently disagree.
#
# Values are the starting points from doc 03 §"Signals"; negatives are kept
# small so exploration is not punished.
# ---------------------------------------------------------------------------

ENGAGEMENT_SIGNAL_WEIGHTS: dict[EngagementKind, float] = {
    EngagementKind.IMPRESSION: -0.1,
    EngagementKind.CLICK: 1.0,
    EngagementKind.DWELL: 2.0,
    EngagementKind.COMPLETE: 3.0,
    EngagementKind.SAVE: 5.0,
    EngagementKind.SHARE: 5.0,
    EngagementKind.COMMENT: 4.0,
    EngagementKind.SEARCH_IMPRESSION: 0.0,
}

#: Silent reading rate for English non-fiction, from Brysbaert (2019), a
#: meta-analysis over 190 studies. Used for reading-time display now and for
#: length-normalised dwell in F1 later — the same constant, one place.
WORDS_PER_MINUTE: Annotated[int, "Brysbaert 2019, J. Memory and Language 109"] = 238

#: Trending decays with a 24-hour half-life over a 7-day window: the same
#: exponential shape F1 uses for freshness and affinity, just impatient. Doc 01
#: open question 4 asks for consistency with F1 rather than a second decay model.
TRENDING_HALF_LIFE_HOURS = 24.0
TRENDING_WINDOW_DAYS = 7
