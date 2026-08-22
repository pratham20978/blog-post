"""Admin read models — data and query contracts only, no UI and no charts.

Every one of these is an aggregate over the engagement log joined to blog
metadata. They are read models in the strict sense: nothing here is written,
and nothing here is authoritative — the log is.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from blogs.contracts.common import BlogId, ContractModel, KeyStr, NonEmptyStr


class TimeBucket(StrEnum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class AnalyticsWindow(ContractModel):
    """A half-open interval ``[start, end)``.

    Half-open so adjacent windows tile without double-counting the boundary
    event — the classic off-by-one in every "this week vs last week" report.
    """

    start: datetime
    end: datetime


class TopViewedRow(ContractModel):
    blog_id: BlogId
    slug: KeyStr
    title: NonEmptyStr
    impressions: int = Field(ge=0)
    clicks: int = Field(ge=0)
    completions: int = Field(ge=0)
    unique_actors: int = Field(ge=0)


class TrendingRow(ContractModel):
    """Ranked by time-decayed engagement weight.

    ``score`` is the decayed sum; ``raw_events`` is the undecayed count beside
    it, because a score with no denominator is impossible to sanity-check.
    """

    blog_id: BlogId
    slug: KeyStr
    title: NonEmptyStr
    score: float
    raw_events: int = Field(ge=0)


class CategoryCoverageRow(ContractModel):
    category_key: KeyStr
    label: NonEmptyStr
    blog_count: int = Field(ge=0)
    impressions: int = Field(ge=0)
    clicks: int = Field(ge=0)


class BlogKpis(ContractModel):
    blog_id: BlogId
    slug: KeyStr
    title: NonEmptyStr
    impressions: int = Field(ge=0)
    clicks: int = Field(ge=0)
    completions: int = Field(ge=0)
    saves: int = Field(ge=0)
    shares: int = Field(ge=0)
    comment_count: int = Field(ge=0)
    unique_actors: int = Field(ge=0)
    unique_users: int = Field(ge=0)
    median_dwell_ms: int | None = None
    #: Clicks over impressions. ``None`` rather than 0.0 when there were no
    #: impressions: "nobody saw it" and "everybody ignored it" are different
    #: facts, and a zero here would quietly merge them.
    click_through_rate: float | None = Field(default=None, ge=0.0, le=1.0)


class EngagementOverTimeRow(ContractModel):
    bucket_start: datetime
    impressions: int = Field(ge=0)
    clicks: int = Field(ge=0)
    completions: int = Field(ge=0)
    saves: int = Field(ge=0)
    comments: int = Field(ge=0)
    unique_actors: int = Field(ge=0)
