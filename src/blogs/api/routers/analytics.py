"""Admin KPI read models.

Doc 01 asks for the data and the query contracts, not a dashboard. These return
rows; what draws them is somebody else's problem.

Mounted under the secret admin prefix, so every path below is really
``{admin_path_prefix}/admin/analytics/...``. Public taxonomy reads live in
``taxonomy.py`` precisely so they do not get hidden along with these.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Query

from blogs.api.deps import AdminUser, Assembled, CorrelationId
from blogs.api.envelope import success
from blogs.contracts.admin import (
    AnalyticsWindow,
    BlogKpis,
    CategoryCoverageRow,
    EngagementOverTimeRow,
    TimeBucket,
    TopViewedRow,
    TrendingRow,
)
from blogs.contracts.common import APIResponse

router = APIRouter(tags=["analytics"])


def _window(days: int, now: datetime) -> AnalyticsWindow:
    """A half-open ``[start, end)`` ending now.

    Half-open so consecutive windows tile exactly: an event on the boundary
    belongs to one period, never to both.
    """
    return AnalyticsWindow(start=now - timedelta(days=days), end=now)


@router.get("/admin/analytics/top-viewed")
async def top_viewed(
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> APIResponse[tuple[TopViewedRow, ...]]:
    rows = await assembled.admin_read_service.top_viewed(
        principal=admin,
        window=_window(days, assembled.clock.now()),
        limit=limit,
        correlation_id=correlation,
    )
    return success(rows)


@router.get("/admin/analytics/trending")
async def trending(
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> APIResponse[tuple[TrendingRow, ...]]:
    """Ranked by time-decayed engagement weight.

    No window parameter: the 24-hour half-life *is* the window, and the same
    decay shape F1 will use for freshness. A caller-chosen span would rank the
    same data differently and let two dashboards disagree.
    """
    rows = await assembled.admin_read_service.trending(
        principal=admin, limit=limit, correlation_id=correlation
    )
    return success(rows)


@router.get("/admin/analytics/by-category")
async def by_category(
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> APIResponse[tuple[CategoryCoverageRow, ...]]:
    rows = await assembled.admin_read_service.by_category(
        principal=admin,
        window=_window(days, assembled.clock.now()),
        correlation_id=correlation,
    )
    return success(rows)


@router.get("/admin/analytics/blogs/{blog_id}")
async def blog_kpis(
    blog_id: str,
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> APIResponse[BlogKpis]:
    kpis = await assembled.admin_read_service.blog_kpis(
        principal=admin,
        blog_id=blog_id,
        window=_window(days, assembled.clock.now()),
        correlation_id=correlation,
    )
    return success(kpis)


@router.get("/admin/analytics/over-time")
async def engagement_over_time(
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
    bucket: Annotated[TimeBucket, Query()] = TimeBucket.DAY,
    blog_id: Annotated[str | None, Query()] = None,
) -> APIResponse[tuple[EngagementOverTimeRow, ...]]:
    rows = await assembled.admin_read_service.engagement_over_time(
        principal=admin,
        window=_window(days, assembled.clock.now()),
        bucket=bucket,
        blog_id=blog_id,
        correlation_id=correlation,
    )
    return success(rows)
