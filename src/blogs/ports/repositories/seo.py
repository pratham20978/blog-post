"""Persistence port for SEO audit observations."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from pydantic import JsonValue

from blogs.contracts.seo import SeoOverview


class SeoRepository(Protocol):
    async def upsert_site(
        self,
        *,
        site_id: str,
        base_url: str,
        brand_name: str,
        search_console_property: str | None,
        timezone: str,
    ) -> str: ...

    async def create_run(
        self,
        *,
        run_id: str,
        site_id: str,
        kind: str,
        trigger: str,
        started_at: datetime,
    ) -> None: ...

    async def upsert_page(
        self,
        *,
        page_id: str,
        site_id: str,
        url: str,
        canonical_url: str | None,
        blog_id: str | None,
        page_type: str,
        indexable: bool,
        content_sha256: str | None,
        audited_at: datetime,
    ) -> str: ...

    async def add_finding(
        self,
        *,
        finding_id: str,
        run_id: str,
        page_id: str | None,
        rule_code: str,
        severity: str,
        message: str,
        evidence: dict[str, JsonValue],
        fingerprint: str,
    ) -> bool: ...

    async def complete_run(
        self,
        *,
        run_id: str,
        completed_at: datetime,
        report: dict[str, JsonValue],
    ) -> None: ...

    async def overview(self, *, base_url: str) -> SeoOverview | None: ...


__all__ = ["SeoRepository"]
