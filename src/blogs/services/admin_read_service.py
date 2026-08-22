"""Admin read models — the KPI half of doc 01.

Data and query contracts only; no UI, no charts. Every method is admin-gated
and every window is half-open ``[start, end)`` so adjacent periods tile without
double-counting the boundary event.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from blogs.contracts.admin import (
    AnalyticsWindow,
    BlogKpis,
    CategoryCoverageRow,
    EngagementOverTimeRow,
    TimeBucket,
    TopViewedRow,
    TrendingRow,
)
from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import Principal
from blogs.core.clock import Clock
from blogs.core.errors import raise_error
from blogs.ports.services import AuthorizationPolicy
from blogs.ports.uow import UnitOfWorkFactory
from blogs.services.policy import require

_DEFAULT_WINDOW = timedelta(days=30)
_MAX_LIMIT = 100


class AdminReadService:
    def __init__(
        self,
        *,
        uow: UnitOfWorkFactory,
        clock: Clock,
        policy: AuthorizationPolicy,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._policy = policy

    def _window(self, window: AnalyticsWindow | None) -> AnalyticsWindow:
        if window is not None:
            return window
        now = self._clock.now()
        return AnalyticsWindow(start=now - _DEFAULT_WINDOW, end=now)

    def _gate(self, principal: Principal, correlation_id: str | None) -> None:
        require(
            self._policy.can_read_analytics(principal),
            principal=principal,
            correlation_id=correlation_id,
        )

    async def top_viewed(
        self,
        *,
        principal: Principal,
        window: AnalyticsWindow | None = None,
        limit: int = 20,
        correlation_id: str | None = None,
    ) -> tuple[TopViewedRow, ...]:
        self._gate(principal, correlation_id)
        resolved = self._window(window)
        async with self._uow.read() as uow:
            return await uow.analytics.top_viewed(
                window_start=resolved.start,
                window_end=resolved.end,
                limit=min(limit, _MAX_LIMIT),
            )

    async def trending(
        self,
        *,
        principal: Principal,
        limit: int = 20,
        correlation_id: str | None = None,
    ) -> tuple[TrendingRow, ...]:
        """Time-decayed engagement over the trending window.

        Takes no window argument on purpose: the decay *is* the window. A
        caller-chosen span would produce a different ranking from the same data
        and quietly make two dashboards disagree.
        """
        self._gate(principal, correlation_id)
        async with self._uow.read() as uow:
            return await uow.analytics.trending(
                now=self._clock.now(), limit=min(limit, _MAX_LIMIT)
            )

    async def by_category(
        self,
        *,
        principal: Principal,
        window: AnalyticsWindow | None = None,
        correlation_id: str | None = None,
    ) -> tuple[CategoryCoverageRow, ...]:
        self._gate(principal, correlation_id)
        resolved = self._window(window)
        async with self._uow.read() as uow:
            return await uow.analytics.by_category(
                window_start=resolved.start, window_end=resolved.end
            )

    async def blog_kpis(
        self,
        *,
        principal: Principal,
        blog_id: str,
        window: AnalyticsWindow | None = None,
        correlation_id: str | None = None,
    ) -> BlogKpis:
        self._gate(principal, correlation_id)
        resolved = self._window(window)
        async with self._uow.read() as uow:
            kpis = await uow.analytics.blog_kpis(
                blog_id=blog_id, window_start=resolved.start, window_end=resolved.end
            )
        if kpis is None:
            raise_error(ErrorCategory.BLOG_NOT_FOUND, correlation_id=correlation_id)
        return kpis

    async def engagement_over_time(
        self,
        *,
        principal: Principal,
        window: AnalyticsWindow | None = None,
        bucket: TimeBucket = TimeBucket.DAY,
        blog_id: str | None = None,
        correlation_id: str | None = None,
    ) -> tuple[EngagementOverTimeRow, ...]:
        self._gate(principal, correlation_id)
        resolved = self._window(window)
        async with self._uow.read() as uow:
            return await uow.analytics.engagement_over_time(
                window_start=resolved.start,
                window_end=resolved.end,
                bucket=bucket,
                blog_id=blog_id,
            )


__all__ = ["AdminReadService", "datetime"]
