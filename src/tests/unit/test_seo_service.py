from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime

import pytest

from blogs.contracts.identity import UserPrincipal
from blogs.contracts.seo import (
    SeoAuditSubmission,
    SeoFindingInput,
    SeoOverview,
    SeoPageInput,
    SeoSeverity,
)
from blogs.core.ids import SequentialIdGenerator
from blogs.services.policy import DefaultAuthorizationPolicy
from blogs.services.seo_service import SeoService


class FakeSeoRepository:
    def __init__(self) -> None:
        self.site_id = "00000000-0000-4000-8000-000000000010"
        self.runs = 0
        self.pages: set[str] = set()
        self.findings = 0

    async def upsert_site(self, **_: object) -> str:
        return self.site_id

    async def create_run(self, **_: object) -> None:
        self.runs += 1

    async def upsert_page(self, **values: object) -> str:
        url = str(values["url"])
        self.pages.add(url)
        return "00000000-0000-4000-8000-000000000011"

    async def add_finding(self, **_: object) -> bool:
        self.findings += 1
        return True

    async def complete_run(self, **_: object) -> None:
        return None

    async def overview(self, *, base_url: str) -> SeoOverview | None:
        return SeoOverview(
            site_id=self.site_id,
            site_url=base_url,
            total_runs=self.runs,
            open_errors=self.findings,
            open_warnings=0,
            tracked_pages=len(self.pages),
        )


class FakeUnit:
    def __init__(self, seo: FakeSeoRepository) -> None:
        self.seo = seo


class FakeUnitOfWorkFactory:
    def __init__(self) -> None:
        self.repository = FakeSeoRepository()

    @asynccontextmanager
    async def begin(self):  # type: ignore[no-untyped-def]
        yield FakeUnit(self.repository)

    @asynccontextmanager
    async def read(self):  # type: ignore[no-untyped-def]
        yield FakeUnit(self.repository)


@pytest.mark.anyio
async def test_service_records_admin_audit_and_reads_overview() -> None:
    now = datetime(2026, 9, 15, tzinfo=UTC)
    factory = FakeUnitOfWorkFactory()
    ids = SequentialIdGenerator(seed=100)
    service = SeoService(
        uow=factory,
        ids=ids,
        policy=DefaultAuthorizationPolicy(),
    )
    admin = UserPrincipal(
        actor_id=ids.new_id(), user_id=ids.new_id(), is_admin=True
    )
    url = "https://canery.in/blogs/example"
    submission = SeoAuditSubmission(
        site_url="https://canery.in",
        brand_name="Canery",
        started_at=now,
        completed_at=now,
        pages=(SeoPageInput(url=url, canonical_url=url, page_type="article"),),
        findings=(
            SeoFindingInput(
                page_url=url,
                rule_code="CANONICAL_MISMATCH",
                severity=SeoSeverity.ERROR,
                message="Canonical mismatch",
            ),
        ),
    )

    result = await service.record_audit(principal=admin, submission=submission)
    overview = await service.overview(principal=admin, site_url="https://canery.in/")

    assert result.pages_recorded == 1
    assert result.findings_recorded == 1
    assert result.errors == 1
    assert overview.total_runs == 1
    assert overview.open_errors == 1
