"""SEO audit ingestion and overview, mounted under the secret admin prefix."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from blogs.api.deps import AdminUser, Assembled, CorrelationId
from blogs.api.envelope import success
from blogs.contracts.common import APIResponse
from blogs.contracts.seo import SeoAuditResult, SeoAuditSubmission, SeoOverview

router = APIRouter(tags=["seo"])


@router.post("/admin/seo/audits")
async def record_audit(
    submission: SeoAuditSubmission,
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
) -> APIResponse[SeoAuditResult]:
    result = await assembled.seo_service.record_audit(
        principal=admin,
        submission=submission,
        correlation_id=correlation,
    )
    return success(result, message="SEO audit recorded")


@router.get("/admin/seo/overview")
async def overview(
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
    site_url: Annotated[str, Query(min_length=8)],
) -> APIResponse[SeoOverview]:
    result = await assembled.seo_service.overview(
        principal=admin,
        site_url=site_url,
        correlation_id=correlation,
    )
    return success(result)
