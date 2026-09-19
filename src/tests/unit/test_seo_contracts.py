from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from blogs.contracts.seo import (
    SeoAuditSubmission,
    SeoFindingInput,
    SeoPageInput,
    SeoSeverity,
)


def test_finding_fingerprint_is_stable() -> None:
    left = SeoFindingInput(
        page_url="https://canery.in/blogs/example",
        rule_code="CANONICAL_MISSING",
        severity=SeoSeverity.ERROR,
        message="Canonical URL is missing",
    )
    right = SeoFindingInput(
        page_url="https://canery.in/blogs/example",
        rule_code="CANONICAL_MISSING",
        severity=SeoSeverity.WARNING,
        message="Canonical URL is missing",
    )

    assert left.fingerprint == right.fingerprint
    assert left.fingerprint is not None
    assert len(left.fingerprint) == 64


def test_submission_normalises_site_origin_and_requires_aware_time() -> None:
    now = datetime(2026, 9, 15, tzinfo=UTC)
    submission = SeoAuditSubmission(
        site_url="https://canery.in/",
        brand_name="Canery",
        started_at=now,
        completed_at=now,
    )
    assert submission.site_url == "https://canery.in"

    with pytest.raises(ValidationError):
        SeoAuditSubmission(
            site_url="https://canery.in/blogs",
            brand_name="Canery",
            started_at=now.replace(tzinfo=None),
            completed_at=now.replace(tzinfo=None),
        )


def test_submission_rejects_pages_from_another_origin() -> None:
    now = datetime(2026, 9, 15, tzinfo=UTC)
    with pytest.raises(ValidationError):
        SeoAuditSubmission(
            site_url="https://canery.in",
            brand_name="Canery",
            started_at=now,
            completed_at=now,
            pages=(SeoPageInput(url="https://example.com/blogs/copied"),),
        )
