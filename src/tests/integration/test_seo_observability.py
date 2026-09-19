from __future__ import annotations

from blogs.contracts.identity import UserPrincipal
from blogs.contracts.seo import (
    SeoAuditSubmission,
    SeoFindingInput,
    SeoPageInput,
    SeoSeverity,
)
from blogs.repository.uow import SqlUnitOfWorkFactory
from blogs.services.policy import DefaultAuthorizationPolicy
from blogs.services.seo_service import SeoService


async def test_records_audit_and_reports_latest_overview(
    uow: SqlUnitOfWorkFactory, clock, ids
) -> None:  # type: ignore[no-untyped-def]
    service = SeoService(
        uow=uow,
        ids=ids,
        policy=DefaultAuthorizationPolicy(),
    )
    admin = UserPrincipal(
        actor_id=ids.new_id(), user_id=ids.new_id(), is_admin=True
    )
    page_url = "https://canery.in/blogs/seo-example"
    submission = SeoAuditSubmission(
        site_url="https://canery.in",
        brand_name="Canery",
        started_at=clock.now(),
        completed_at=clock.now(),
        pages=(
            SeoPageInput(
                url=page_url,
                canonical_url=page_url,
                page_type="article",
                content_sha256="a" * 64,
            ),
        ),
        findings=(
            SeoFindingInput(
                page_url=page_url,
                rule_code="META_DESCRIPTION_MISSING",
                severity=SeoSeverity.WARNING,
                message="Meta description is missing",
            ),
        ),
        summary={"source": "plugin"},
    )

    recorded = await service.record_audit(principal=admin, submission=submission)
    overview = await service.overview(
        principal=admin, site_url="https://canery.in/"
    )

    assert recorded.pages_recorded == 1
    assert recorded.findings_recorded == 1
    assert recorded.warnings == 1
    assert overview.site_id == recorded.site_id
    assert overview.total_runs == 1
    assert overview.open_warnings == 1
    assert overview.tracked_pages == 1


async def test_reuses_site_and_page_across_audits(
    uow: SqlUnitOfWorkFactory, clock, ids
) -> None:  # type: ignore[no-untyped-def]
    service = SeoService(
        uow=uow,
        ids=ids,
        policy=DefaultAuthorizationPolicy(),
    )
    admin = UserPrincipal(
        actor_id=ids.new_id(), user_id=ids.new_id(), is_admin=True
    )
    submission = SeoAuditSubmission(
        site_url="https://canery.in",
        brand_name="Canery",
        started_at=clock.now(),
        completed_at=clock.now(),
        pages=(
            SeoPageInput(
                url="https://canery.in/blogs/one",
                canonical_url="https://canery.in/blogs/one",
                page_type="article",
            ),
        ),
    )

    first = await service.record_audit(principal=admin, submission=submission)
    second = await service.record_audit(principal=admin, submission=submission)
    overview = await service.overview(
        principal=admin, site_url="https://canery.in"
    )

    assert first.site_id == second.site_id
    assert overview.total_runs == 2
    assert overview.tracked_pages == 1
