"""The contract floor: strictness, identifiers, closed sets, and the envelope.

This module imports Pydantic and the standard library and nothing else, ever.
Every other contract module imports from here.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, StringConstraints, model_validator

# ---------------------------------------------------------------------------
# The base
# ---------------------------------------------------------------------------


class ContractModel(BaseModel):
    """Base for every contract in the system. Strictness is decided once, here.

    ``extra="forbid"`` alone would have caught the ``document.yaml`` /
    ``structured.yaml`` divergence at the first integration test: with
    ``ignore``, a renamed field arrives, is silently dropped, and the consumer
    reads a default.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=False,
    )


# ---------------------------------------------------------------------------
# Semantic aliases — identifiers stop being strings
#
# Several of these share a pattern. That is deliberate: the value is in the name
# appearing at the signature, not in runtime discrimination. Do not collapse
# them into one UuidStr.
# ---------------------------------------------------------------------------

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

_UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
_Uuid = Annotated[str, StringConstraints(strip_whitespace=True, pattern=_UUID_PATTERN)]

UserId = _Uuid

#: Whoever is acting, logged in or not. An anonymous reader gets a server-issued
#: actor id so engagement has a subject before there is an account; on login the
#: actor is merged into the user (see ``services.auth_service``).
ActorId = _Uuid

BlogId = _Uuid
SectionId = _Uuid
CommentId = _Uuid
CatalogId = _Uuid
PinId = _Uuid
SeriesId = _Uuid
EventId = _Uuid
ChallengeId = _Uuid
TokenId = _Uuid

#: Lowercase, hyphen-separated. Used for category keys and blog slugs alike;
#: foundation §9 fixes this shape and the DB re-checks it.
KeyStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, min_length=1, max_length=120,
        pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$",
    ),
]

#: Anchors are slugs derived from heading text, so they share the key shape but
#: may be longer and may carry a disambiguating numeric suffix.
AnchorStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, min_length=1, max_length=200,
        pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$",
    ),
]

EmailStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, to_lower=True, min_length=3, max_length=320,
        pattern=r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$",
    ),
]


# ---------------------------------------------------------------------------
# The closed sets behind every error
# ---------------------------------------------------------------------------


class ProcessingStage(StrEnum):
    """Where in this system's pipeline a failure happened."""

    AUTH = "AUTH"
    ACCESS = "ACCESS"
    VALIDATE = "VALIDATE"
    PERSIST = "PERSIST"
    STORAGE = "STORAGE"
    PUBLISH = "PUBLISH"
    COMPOSE = "COMPOSE"


class Retryability(StrEnum):
    RETRYABLE = "RETRYABLE"
    NOT_RETRYABLE = "NOT_RETRYABLE"
    POLICY_DEPENDENT = "POLICY_DEPENDENT"


class ErrorCategory(StrEnum):
    """Named by domain, never by former service.

    Every member must appear in ``core.errors.ERROR_CATALOG`` and in
    ``api.envelope.HTTP_STATUS_BY_ERROR_CATEGORY``. Both are total by
    construction and a test asserts it, so adding a member here without
    choosing its meaning and its status fails the suite.
    """

    # ── Auth ────────────────────────────────────────────────────────────────
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_REVOKED = "AUTH_TOKEN_REVOKED"
    AUTH_REQUIRED = "AUTH_REQUIRED"

    OTP_INVALID = "OTP_INVALID"
    OTP_EXPIRED = "OTP_EXPIRED"
    OTP_ATTEMPTS_EXCEEDED = "OTP_ATTEMPTS_EXCEEDED"
    OTP_THROTTLED = "OTP_THROTTLED"

    OAUTH_PROVIDER_UNKNOWN = "OAUTH_PROVIDER_UNKNOWN"
    OAUTH_STATE_INVALID = "OAUTH_STATE_INVALID"
    OAUTH_EXCHANGE_FAILED = "OAUTH_EXCHANGE_FAILED"
    OAUTH_EMAIL_UNVERIFIED = "OAUTH_EMAIL_UNVERIFIED"

    REFRESH_TOKEN_INVALID = "REFRESH_TOKEN_INVALID"
    REFRESH_TOKEN_EXPIRED = "REFRESH_TOKEN_EXPIRED"
    #: A token presented twice. The first use rotated it, so a second means the
    #: token leaked — the whole family is revoked and this is returned.
    REFRESH_TOKEN_REUSED = "REFRESH_TOKEN_REUSED"

    ACTOR_TOKEN_INVALID = "ACTOR_TOKEN_INVALID"

    #: Wrong email or wrong password at the admin console. One category for
    #: both, so the response cannot be used to discover which half was right.
    ADMIN_CREDENTIALS_INVALID = "ADMIN_CREDENTIALS_INVALID"
    ADMIN_LOCKED_OUT = "ADMIN_LOCKED_OUT"
    #: The admin exists but has no password set, so console sign-in is not yet
    #: possible for them.
    ADMIN_PASSWORD_NOT_SET = "ADMIN_PASSWORD_NOT_SET"

    # ── Access ──────────────────────────────────────────────────────────────
    ACCESS_DENIED = "ACCESS_DENIED"
    ADMIN_REQUIRED = "ADMIN_REQUIRED"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_INACTIVE = "USER_INACTIVE"

    # ── Content ─────────────────────────────────────────────────────────────
    BLOG_NOT_FOUND = "BLOG_NOT_FOUND"
    BLOG_NOT_PUBLISHED = "BLOG_NOT_PUBLISHED"
    SLUG_CONFLICT = "SLUG_CONFLICT"
    MARKDOWN_INVALID = "MARKDOWN_INVALID"
    MARKDOWN_TOO_LARGE = "MARKDOWN_TOO_LARGE"
    SECTION_ANCHOR_UNKNOWN = "SECTION_ANCHOR_UNKNOWN"
    #: An edit would have removed a heading that another article pins into.
    #: Surfaced rather than silently allowed: a dangling cross-reference is the
    #: exact failure reference pins exist to prevent.
    SECTION_REFERENCED_BY_PIN = "SECTION_REFERENCED_BY_PIN"
    CATEGORY_UNKNOWN = "CATEGORY_UNKNOWN"
    SERIES_UNKNOWN = "SERIES_UNKNOWN"

    # ── Interaction ─────────────────────────────────────────────────────────
    COMMENT_NOT_FOUND = "COMMENT_NOT_FOUND"
    COMMENT_ALREADY_EXISTS = "COMMENT_ALREADY_EXISTS"
    COMMENT_DEPTH_INVALID = "COMMENT_DEPTH_INVALID"
    MARKER_NOT_FOUND = "MARKER_NOT_FOUND"
    CATALOG_NOT_FOUND = "CATALOG_NOT_FOUND"
    CATALOG_NAME_TAKEN = "CATALOG_NAME_TAKEN"
    PIN_NOT_FOUND = "PIN_NOT_FOUND"
    PIN_SELF_REFERENCE = "PIN_SELF_REFERENCE"

    # ── Infrastructure ──────────────────────────────────────────────────────
    STORAGE_UNAVAILABLE = "STORAGE_UNAVAILABLE"
    STORAGE_OBJECT_NOT_FOUND = "STORAGE_OBJECT_NOT_FOUND"
    DATABASE_UNAVAILABLE = "DATABASE_UNAVAILABLE"

    # ── Generic ─────────────────────────────────────────────────────────────
    RATE_LIMITED = "RATE_LIMITED"
    REQUEST_INVALID = "REQUEST_INVALID"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorEnvelope(ContractModel):
    """The error half of the wire shape. Every field here is caller-safe."""

    category: ErrorCategory
    safe_message: NonEmptyStr
    retryability: Retryability
    stage: ProcessingStage
    safe_details: dict[str, JsonValue] = Field(default_factory=dict)
    correlation_id: NonEmptyStr


class APIResponse[T](ContractModel):
    success: bool
    message: NonEmptyStr
    data: T | None = None
    error: ErrorEnvelope | None = None

    @model_validator(mode="after")
    def _consistency(self) -> Self:
        if self.success and self.error is not None:
            raise ValueError("success response cannot carry an error")
        if not self.success and self.error is None:
            raise ValueError("failure response must carry an error")
        return self


class Page[T](ContractModel):
    """Keyset pagination, never OFFSET.

    An OFFSET page over an append-heavy table both drifts (a row inserted during
    paging shifts every later page) and degrades linearly with depth. The cursor
    is an opaque encoding of the sort key of the last row returned.
    """

    items: tuple[T, ...]
    next_cursor: str | None = None
    has_more: bool = False
