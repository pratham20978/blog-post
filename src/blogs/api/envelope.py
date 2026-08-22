"""The wire envelope and the one place HTTP status codes live.

``core/errors.py`` is transport-agnostic on purpose: services raise the same
errors whether or not an HTTP request is in flight. The mapping from a domain
error to a status code is a property of *this* transport, so it lives here and
nowhere else.

The wire shape is ``{success, message, data, error}``, implemented once.
"""

from __future__ import annotations

from blogs.contracts.common import APIResponse, ErrorCategory, ErrorEnvelope

_C = ErrorCategory

#: Total by construction: every category maps, so a new category cannot reach
#: production without someone choosing its status. A ``.get(..., 500)`` default
#: here would let that decision be skipped silently, and
#: ``test_error_catalog_is_total`` fails the build if a member is missing.
HTTP_STATUS_BY_ERROR_CATEGORY: dict[ErrorCategory, int] = {
    # 401: the credential is missing, wrong, or spent. Retrying with a good one
    # would work, which is what separates these from the 403s below.
    _C.AUTH_TOKEN_INVALID: 401,
    _C.AUTH_TOKEN_EXPIRED: 401,
    _C.AUTH_TOKEN_REVOKED: 401,
    _C.AUTH_REQUIRED: 401,
    _C.REFRESH_TOKEN_INVALID: 401,
    _C.REFRESH_TOKEN_EXPIRED: 401,
    _C.REFRESH_TOKEN_REUSED: 401,
    _C.ACTOR_TOKEN_INVALID: 401,
    _C.ADMIN_CREDENTIALS_INVALID: 401,
    _C.ADMIN_PASSWORD_NOT_SET: 401,
    _C.ADMIN_LOCKED_OUT: 429,
    _C.OTP_INVALID: 401,
    _C.OTP_EXPIRED: 401,
    _C.OAUTH_EMAIL_UNVERIFIED: 401,
    # 429, not 401: the credential was fine, the caller is simply too early.
    _C.OTP_THROTTLED: 429,
    _C.OTP_ATTEMPTS_EXCEEDED: 429,
    _C.RATE_LIMITED: 429,
    _C.OAUTH_PROVIDER_UNKNOWN: 404,
    # 400: the callback could not be tied to a flow this server started.
    _C.OAUTH_STATE_INVALID: 400,
    # 502: we reached the provider and it did not cooperate — an upstream
    # failure, not the caller's mistake.
    _C.OAUTH_EXCHANGE_FAILED: 502,
    # 403: authenticated, and still not allowed. Retrying changes nothing.
    _C.ACCESS_DENIED: 403,
    _C.ADMIN_REQUIRED: 403,
    _C.USER_INACTIVE: 403,
    _C.USER_NOT_FOUND: 404,
    # 404 covers drafts and archives too: telling an outsider that a slug
    # exists but is unpublished leaks the editorial pipeline.
    _C.BLOG_NOT_FOUND: 404,
    _C.BLOG_NOT_PUBLISHED: 404,
    # 409: the request is well formed and the current state conflicts with it.
    _C.SLUG_CONFLICT: 409,
    _C.COMMENT_ALREADY_EXISTS: 409,
    _C.CATALOG_NAME_TAKEN: 409,
    _C.SECTION_REFERENCED_BY_PIN: 409,
    # 422: well formed, but semantically impossible to carry out.
    _C.MARKDOWN_INVALID: 422,
    _C.SECTION_ANCHOR_UNKNOWN: 422,
    _C.CATEGORY_UNKNOWN: 422,
    _C.SERIES_UNKNOWN: 422,
    _C.COMMENT_DEPTH_INVALID: 422,
    _C.PIN_SELF_REFERENCE: 422,
    # 413: the specific status for a body that exceeds the limit.
    _C.MARKDOWN_TOO_LARGE: 413,
    _C.COMMENT_NOT_FOUND: 404,
    _C.MARKER_NOT_FOUND: 404,
    _C.CATALOG_NOT_FOUND: 404,
    _C.PIN_NOT_FOUND: 404,
    # 503: ours, and temporary. The caller should come back.
    _C.STORAGE_UNAVAILABLE: 503,
    _C.DATABASE_UNAVAILABLE: 503,
    # 500, not 404: the article exists and its bytes do not. That is our gap,
    # not a missing resource.
    _C.STORAGE_OBJECT_NOT_FOUND: 500,
    _C.REQUEST_INVALID: 400,
    _C.INTERNAL_ERROR: 500,
}


def status_for(category: ErrorCategory) -> int:
    """Look up a status. Raises ``KeyError`` for an unmapped category.

    Deliberately not ``.get(category, 500)``: an unmapped category is a gap in
    this table, and it should surface in the test suite rather than become a
    silent 500 in production.
    """
    return HTTP_STATUS_BY_ERROR_CATEGORY[category]


def success[T](data: T, *, message: str = "OK") -> APIResponse[T]:
    return APIResponse[T](success=True, message=message, data=data, error=None)


def failure(error: ErrorEnvelope) -> APIResponse[None]:
    """Not generic: a failure carries no data, so there is no T to infer."""
    return APIResponse[None](success=False, message=error.safe_message, data=None, error=error)
