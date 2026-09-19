"""Contracts for SEO audits and their durable history.

The plugin submits observations, not instructions to publish. Keeping that
boundary in the contract makes a scheduled audit safe to run unattended: it
can record a problem, but only the existing editorial path can change a post.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from urllib.parse import urlsplit

from pydantic import Field, JsonValue, field_validator, model_validator

from blogs.contracts.common import BlogId, ContractModel, NonEmptyStr


class SeoRunKind(StrEnum):
    LOCAL = "local"
    LIVE = "live"
    SEARCH_CONSOLE = "search_console"
    AI_VISIBILITY = "ai_visibility"
    FULL = "full"


class SeoRunTrigger(StrEnum):
    MANUAL = "manual"
    PLUGIN = "plugin"
    SCHEDULED = "scheduled"
    CI = "ci"


class SeoSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


def _normalise_origin(value: str) -> str:
    candidate = value.strip().rstrip("/")
    parsed = urlsplit(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("must be an absolute http(s) origin")
    if parsed.path or parsed.query or parsed.fragment:
        raise ValueError("must be an origin without a path, query, or fragment")
    return candidate


def _absolute_url(value: str | None) -> str | None:
    if value is None:
        return None
    candidate = value.strip()
    parsed = urlsplit(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("must be an absolute http(s) URL")
    return candidate


class SeoPageInput(ContractModel):
    url: str
    canonical_url: str | None = None
    blog_id: BlogId | None = None
    page_type: str = "other"
    indexable: bool = True
    content_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")

    @field_validator("url", "canonical_url")
    @classmethod
    def _urls_are_absolute(cls, value: str | None) -> str | None:
        return _absolute_url(value)

    @field_validator("page_type")
    @classmethod
    def _known_page_type(cls, value: str) -> str:
        if value not in {"home", "article", "series", "category", "other"}:
            raise ValueError("unknown page_type")
        return value


class SeoFindingInput(ContractModel):
    page_url: str | None = None
    rule_code: str = Field(pattern=r"^[A-Z][A-Z0-9_]{2,63}$")
    severity: SeoSeverity
    message: NonEmptyStr
    evidence: dict[str, JsonValue] = Field(default_factory=dict)
    fingerprint: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")

    @field_validator("page_url")
    @classmethod
    def _page_url_is_absolute(cls, value: str | None) -> str | None:
        return _absolute_url(value)

    @model_validator(mode="after")
    def _stable_fingerprint(self) -> SeoFindingInput:
        if self.fingerprint is None:
            basis = "\x1f".join(
                (self.page_url or "", self.rule_code, self.message.strip())
            )
            object.__setattr__(self, "fingerprint", sha256(basis.encode()).hexdigest())
        return self


class SeoAuditSubmission(ContractModel):
    site_url: str
    brand_name: NonEmptyStr
    search_console_property: str | None = None
    timezone: NonEmptyStr = "UTC"
    kind: SeoRunKind = SeoRunKind.LOCAL
    trigger: SeoRunTrigger = SeoRunTrigger.PLUGIN
    started_at: datetime
    completed_at: datetime
    pages: tuple[SeoPageInput, ...] = ()
    findings: tuple[SeoFindingInput, ...] = ()
    summary: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("site_url")
    @classmethod
    def _site_is_origin(cls, value: str) -> str:
        return _normalise_origin(value)

    @model_validator(mode="after")
    def _time_moves_forward(self) -> SeoAuditSubmission:
        if self.started_at.tzinfo is None or self.completed_at.tzinfo is None:
            raise ValueError("audit timestamps must include a timezone")
        if self.completed_at < self.started_at:
            raise ValueError("completed_at must not precede started_at")
        origin = urlsplit(self.site_url)
        expected_origin = (origin.scheme, origin.netloc)
        page_urls = [page.url for page in self.pages]
        if len(page_urls) != len(set(page_urls)):
            raise ValueError("audit pages must have unique URLs")
        observed_urls = page_urls + [
            finding.page_url
            for finding in self.findings
            if finding.page_url is not None
        ]
        for observed in observed_urls:
            parsed = urlsplit(observed)
            if (parsed.scheme, parsed.netloc) != expected_origin:
                raise ValueError("audit page URLs must belong to site_url")
        return self


class SeoAuditResult(ContractModel):
    site_id: str
    run_id: str
    pages_recorded: int = Field(ge=0)
    findings_recorded: int = Field(ge=0)
    errors: int = Field(ge=0)
    warnings: int = Field(ge=0)
    information: int = Field(ge=0)


class SeoOverview(ContractModel):
    site_id: str
    site_url: str
    last_run_at: datetime | None = None
    total_runs: int = Field(ge=0)
    open_errors: int = Field(ge=0)
    open_warnings: int = Field(ge=0)
    tracked_pages: int = Field(ge=0)


__all__ = [
    "SeoAuditResult",
    "SeoAuditSubmission",
    "SeoFindingInput",
    "SeoOverview",
    "SeoPageInput",
    "SeoRunKind",
    "SeoRunTrigger",
    "SeoSeverity",
]
