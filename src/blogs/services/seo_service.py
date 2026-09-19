"""Admin-gated ingestion and read models for SEO audit observations."""

from __future__ import annotations

from collections import Counter

from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import Principal
from blogs.contracts.seo import SeoAuditResult, SeoAuditSubmission, SeoOverview
from blogs.core.errors import raise_error
from blogs.core.ids import IdGenerator
from blogs.ports.services import AuthorizationPolicy
from blogs.ports.uow import UnitOfWorkFactory
from blogs.services.policy import require


class SeoService:
    def __init__(
        self,
        *,
        uow: UnitOfWorkFactory,
        ids: IdGenerator,
        policy: AuthorizationPolicy,
    ) -> None:
        self._uow = uow
        self._ids = ids
        self._policy = policy

    def _gate(self, principal: Principal, correlation_id: str | None) -> None:
        require(
            self._policy.can_read_analytics(principal),
            principal=principal,
            correlation_id=correlation_id,
        )

    async def record_audit(
        self,
        *,
        principal: Principal,
        submission: SeoAuditSubmission,
        correlation_id: str | None = None,
    ) -> SeoAuditResult:
        self._gate(principal, correlation_id)
        run_id = self._ids.new_id()
        page_ids: dict[str, str] = {}
        findings_recorded = 0

        async with self._uow.begin() as uow:
            site_id = await uow.seo.upsert_site(
                site_id=self._ids.new_id(),
                base_url=submission.site_url,
                brand_name=submission.brand_name,
                search_console_property=submission.search_console_property,
                timezone=submission.timezone,
            )
            await uow.seo.create_run(
                run_id=run_id,
                site_id=site_id,
                kind=submission.kind.value,
                trigger=submission.trigger.value,
                started_at=submission.started_at,
            )
            for page in submission.pages:
                page_ids[page.url] = await uow.seo.upsert_page(
                    page_id=self._ids.new_id(),
                    site_id=site_id,
                    url=page.url,
                    canonical_url=page.canonical_url,
                    blog_id=page.blog_id,
                    page_type=page.page_type,
                    indexable=page.indexable,
                    content_sha256=page.content_sha256,
                    audited_at=submission.completed_at,
                )
            for finding in submission.findings:
                recorded = await uow.seo.add_finding(
                    finding_id=self._ids.new_id(),
                    run_id=run_id,
                    page_id=page_ids.get(finding.page_url or ""),
                    rule_code=finding.rule_code,
                    severity=finding.severity.value,
                    message=finding.message,
                    evidence=finding.evidence,
                    fingerprint=finding.fingerprint or "",
                )
                findings_recorded += int(recorded)
            await uow.seo.complete_run(
                run_id=run_id,
                completed_at=submission.completed_at,
                report=submission.summary,
            )

        counts = Counter(finding.severity.value for finding in submission.findings)
        return SeoAuditResult(
            site_id=site_id,
            run_id=run_id,
            pages_recorded=len(page_ids),
            findings_recorded=findings_recorded,
            errors=counts["error"],
            warnings=counts["warning"],
            information=counts["info"],
        )

    async def overview(
        self,
        *,
        principal: Principal,
        site_url: str,
        correlation_id: str | None = None,
    ) -> SeoOverview:
        self._gate(principal, correlation_id)
        async with self._uow.read() as uow:
            result = await uow.seo.overview(base_url=site_url.rstrip("/"))
        if result is None:
            raise_error(
                ErrorCategory.REQUEST_INVALID,
                correlation_id=correlation_id,
                safe_details={"reason": "SEO_SITE_NOT_FOUND"},
            )
        return result


__all__ = ["SeoService"]
