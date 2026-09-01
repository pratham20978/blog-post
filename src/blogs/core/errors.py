"""The domain error catalogue, transport-agnostic.

Services raise these whether or not an HTTP request is in flight; the mapping
from a category to a status code is a property of the transport and lives in
``api/envelope.py`` instead.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import NoReturn

from pydantic import JsonValue

from blogs.contracts.common import (
    ErrorCategory,
    ErrorEnvelope,
    ProcessingStage,
    Retryability,
)

_C = ErrorCategory
_S = ProcessingStage
_R = Retryability


@dataclass(frozen=True, slots=True)
class ErrorDescriptor:
    """One row of the catalogue.

    ``frozen`` because the catalogue is data, and data that can be mutated at
    runtime is configuration nobody versioned.
    """

    stage: ProcessingStage
    retryability: Retryability
    safe_message: str


#: Total by construction: every ``ErrorCategory`` maps. ``test_error_catalog``
#: asserts it, so a new category cannot reach production without someone
#: choosing what it means to the caller.
ERROR_CATALOG: dict[ErrorCategory, ErrorDescriptor] = {
    # ── Auth ────────────────────────────────────────────────────────────────
    _C.AUTH_TOKEN_INVALID: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "The supplied credentials are not valid."
    ),
    _C.AUTH_TOKEN_EXPIRED: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "The access token has expired. Refresh and retry."
    ),
    _C.AUTH_TOKEN_REVOKED: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "This credential has been revoked."
    ),
    _C.AUTH_REQUIRED: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "This action requires you to sign in."
    ),
    # The three OTP failures are distinct answers because the caller acts
    # differently on each: retype, request a new code, or wait.
    _C.OTP_INVALID: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "That code is not correct."
    ),
    _C.OTP_EXPIRED: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "That code has expired. Request a new one."
    ),
    _C.OTP_ATTEMPTS_EXCEEDED: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "Too many incorrect attempts. Request a new code."
    ),
    _C.OTP_THROTTLED: ErrorDescriptor(
        _S.AUTH, _R.RETRYABLE, "A code was requested recently. Wait before requesting another."
    ),
    _C.OAUTH_PROVIDER_UNKNOWN: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "That sign-in provider is not supported."
    ),
    _C.OAUTH_STATE_INVALID: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "The sign-in attempt could not be verified. Start again."
    ),
    _C.OAUTH_EXCHANGE_FAILED: ErrorDescriptor(
        _S.AUTH, _R.RETRYABLE, "The sign-in provider could not complete the request."
    ),
    _C.OAUTH_EMAIL_UNVERIFIED: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "The provider has not verified that email address."
    ),
    _C.REFRESH_TOKEN_INVALID: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "The refresh token is not valid. Sign in again."
    ),
    _C.REFRESH_TOKEN_EXPIRED: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "The refresh token has expired. Sign in again."
    ),
    # Deliberately says nothing about token families: the caller who triggered
    # this is as likely to be the attacker as the owner.
    _C.REFRESH_TOKEN_REUSED: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "This session is no longer valid. Sign in again."
    ),
    _C.ACTOR_TOKEN_INVALID: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "The visitor token is not valid."
    ),
    # One message for a bad address and a bad password alike. Distinguishing
    # them would confirm which admin address exists to anyone who found the
    # console.
    _C.ADMIN_CREDENTIALS_INVALID: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "Those credentials are not valid."
    ),
    _C.ADMIN_LOCKED_OUT: ErrorDescriptor(
        _S.AUTH, _R.RETRYABLE, "Too many failed attempts. Try again later."
    ),
    _C.ADMIN_PASSWORD_NOT_SET: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "This account cannot sign in with a password."
    ),
    # ── Access ──────────────────────────────────────────────────────────────
    _C.ACCESS_DENIED: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "You do not have access to this resource."
    ),
    _C.ADMIN_REQUIRED: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "This action is restricted to the site administrator."
    ),
    _C.USER_NOT_FOUND: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "That account does not exist."
    ),
    # An account is suspended, never deleted, so "gone" and "inactive" are
    # different answers and the caller can act on the difference.
    _C.USER_INACTIVE: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "That account is no longer active."
    ),
    # ── Content ─────────────────────────────────────────────────────────────
    _C.BLOG_NOT_FOUND: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "That article does not exist."
    ),
    _C.BLOG_NOT_PUBLISHED: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "That article is not published."
    ),
    _C.SLUG_CONFLICT: ErrorDescriptor(
        _S.PERSIST, _R.RETRYABLE, "An article with that address already exists."
    ),
    _C.MARKDOWN_INVALID: ErrorDescriptor(
        _S.VALIDATE, _R.NOT_RETRYABLE, "The Markdown file could not be read."
    ),
    _C.MARKDOWN_TOO_LARGE: ErrorDescriptor(
        _S.VALIDATE, _R.NOT_RETRYABLE, "The Markdown file is larger than the allowed size."
    ),
    _C.SECTION_ANCHOR_UNKNOWN: ErrorDescriptor(
        _S.VALIDATE, _R.NOT_RETRYABLE, "That article has no section with that anchor."
    ),
    _C.SECTION_REFERENCED_BY_PIN: ErrorDescriptor(
        _S.PERSIST,
        _R.NOT_RETRYABLE,
        "This edit removes a section that another article references. "
        "Remove the reference pin first, or keep the heading.",
    ),
    _C.CATEGORY_UNKNOWN: ErrorDescriptor(
        _S.VALIDATE, _R.NOT_RETRYABLE, "That category does not exist."
    ),
    _C.SERIES_UNKNOWN: ErrorDescriptor(
        _S.VALIDATE, _R.NOT_RETRYABLE, "That series does not exist."
    ),
    # ── Interaction ─────────────────────────────────────────────────────────
    _C.COMMENT_NOT_FOUND: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "That comment does not exist."
    ),
    _C.COMMENT_ALREADY_EXISTS: ErrorDescriptor(
        _S.PERSIST, _R.NOT_RETRYABLE, "You have already commented on this article. Edit it instead."
    ),
    _C.COMMENT_DEPTH_INVALID: ErrorDescriptor(
        _S.VALIDATE, _R.NOT_RETRYABLE, "Replies can only be made to a top-level comment."
    ),
    _C.MARKER_NOT_FOUND: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "You have no saved position in this article."
    ),
    _C.CATALOG_NOT_FOUND: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "That collection does not exist."
    ),
    _C.CATALOG_NAME_TAKEN: ErrorDescriptor(
        _S.PERSIST, _R.NOT_RETRYABLE, "You already have a collection with that name."
    ),
    _C.PIN_NOT_FOUND: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "That reference pin does not exist."
    ),
    _C.PIN_SELF_REFERENCE: ErrorDescriptor(
        _S.VALIDATE, _R.NOT_RETRYABLE, "An article cannot pin a reference to itself."
    ),
    # ── Infrastructure ──────────────────────────────────────────────────────
    _C.STORAGE_UNAVAILABLE: ErrorDescriptor(
        _S.STORAGE, _R.RETRYABLE, "Article storage is temporarily unavailable."
    ),
    _C.STORAGE_OBJECT_NOT_FOUND: ErrorDescriptor(
        _S.STORAGE, _R.NOT_RETRYABLE, "The stored article content could not be found."
    ),
    _C.DATABASE_UNAVAILABLE: ErrorDescriptor(
        _S.PERSIST, _R.RETRYABLE, "The service is temporarily unable to reach its database."
    ),
    _C.EMAIL_NOT_CONFIGURED: ErrorDescriptor(
        # Two constraints on this wording. It must stay vague — "no email
        # provider is configured" describes our deployment, and a stranger at a
        # sign-in form has no use for that; the operator gets the detail from
        # the startup warning and the logs. And it must read correctly for
        # every caller, because the same category is raised for a sign-in code
        # and for an announcement to a mailing list. Anything that advises the
        # reader what to do next is wrong for one of them.
        _S.PUBLISH,
        _R.NOT_RETRYABLE,
        "Email is not available right now.",
    ),
    _C.EMAIL_SEND_FAILED: ErrorDescriptor(
        _S.PUBLISH, _R.RETRYABLE, "The message could not be sent. Try again shortly."
    ),
    # ── Generic ─────────────────────────────────────────────────────────────
    _C.RATE_LIMITED: ErrorDescriptor(
        _S.ACCESS, _R.RETRYABLE, "Too many requests. Try again shortly."
    ),
    _C.REQUEST_INVALID: ErrorDescriptor(
        _S.COMPOSE,
        _R.NOT_RETRYABLE,
        "The request is missing a required value or contains an invalid value.",
    ),
    _C.INTERNAL_ERROR: ErrorDescriptor(
        _S.COMPOSE,
        _R.POLICY_DEPENDENT,
        "The service could not complete the request because of an internal error.",
    ),
}


class BlogPlatformError(Exception):
    """A domain error that converts to a caller-safe envelope.

    ``correlation_id`` is optional at the raise site and required in the
    envelope. A repository three layers down should not have to be handed the
    request id to report that a slug is taken, but every envelope that reaches
    a caller must still carry one — so the raiser may omit it and the transport
    stamps it on the way out (``api.errors.register_exception_handlers``).
    """

    def __init__(
        self,
        category: ErrorCategory,
        *,
        correlation_id: str | None = None,
        safe_message: str | None = None,
        safe_details: Mapping[str, JsonValue] | None = None,
    ) -> None:
        descriptor = ERROR_CATALOG[category]
        self.category = category
        self.stage = descriptor.stage
        self.retryability = descriptor.retryability
        self.correlation_id = correlation_id
        self.safe_message = safe_message or descriptor.safe_message
        self.safe_details: dict[str, JsonValue] = dict(safe_details or {})
        super().__init__(self.safe_message)

    def to_envelope(self, *, correlation_id: str | None = None) -> ErrorEnvelope:
        resolved = self.correlation_id or correlation_id
        if not resolved:
            raise ValueError(
                "an error envelope requires a correlation id: pass one here or at the raise site"
            )
        return ErrorEnvelope(
            category=self.category,
            safe_message=self.safe_message,
            retryability=self.retryability,
            stage=self.stage,
            safe_details=self.safe_details,
            correlation_id=resolved,
        )


class NotModified(Exception):  # noqa: N818 — a cache outcome, not an error
    """The caller's cached copy is still current.

    Not a failure, so it has no ``ErrorCategory`` and never becomes an error
    envelope — a 304 carries no body at all.

    It is an exception purely so a route can stop early while still declaring
    one honest return type. Returning the 304 instead would force the signature
    to ``APIResponse[T] | Response``, which is neither checkable nor
    expressible as an OpenAPI schema, and would push the route into ``Any``.
    """

    def __init__(self, etag: str) -> None:
        self.etag = etag
        super().__init__(etag)


def raise_error(
    category: ErrorCategory,
    *,
    correlation_id: str | None = None,
    safe_message: str | None = None,
    safe_details: Mapping[str, JsonValue] | None = None,
) -> NoReturn:
    """Raise from the catalogue.

    Typed ``NoReturn`` so the checker knows control does not continue — which is
    what lets a caller write ``raise_error(...)`` instead of ``raise
    BlogPlatformError(...)`` without confusing narrowing.
    """
    raise BlogPlatformError(
        category,
        correlation_id=correlation_id,
        safe_message=safe_message,
        safe_details=safe_details,
    )
