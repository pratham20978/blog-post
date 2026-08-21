"""The wire envelope and the one place HTTP status codes live.

``core/errors.py`` is transport-agnostic on purpose: agents and services raise
the same errors whether or not an HTTP request is in flight. The mapping from a
domain error to a status code is a property of *this* transport, so it lives
here and nowhere else.

The wire shape is ``{success, message, data, error}`` — unchanged from the old
stack, so the frontend's ``ApiClient.parseResponse`` needs no change. What
changed is that it is implemented once instead of five times.
"""

from __future__ import annotations

from ai_auditor.contracts.common import APIResponse, ErrorCategory, ErrorEnvelope

_C = ErrorCategory

#: Total by construction: every category maps, so a new category cannot reach
#: production without someone choosing its status. A ``.get(..., 500)`` default
#: here would let that decision be skipped silently.
HTTP_STATUS_BY_ERROR_CATEGORY: dict[ErrorCategory, int] = {
    _C.AUTH_TOKEN_INVALID: 401,
    _C.AUTH_TOKEN_EXPIRED: 401,
    _C.AUTH_TOKEN_REVOKED: 401,
    _C.AUTH_CREDENTIALS_INVALID: 401,
    _C.SESSION_NOT_FOUND: 404,
    _C.SESSION_EXPIRED: 401,
    _C.DEVICE_NOT_FOUND: 404,
    _C.TENANT_NOT_FOUND: 404,
    _C.TENANT_INACTIVE: 403,
    # 404, not 403: confirming a resource exists in another tenant is itself a
    # cross-tenant leak.
    _C.TENANT_MISMATCH: 404,
    _C.ACCESS_DENIED: 403,
    _C.ACTOR_NOT_FOUND: 404,
    _C.ACTOR_INACTIVE: 403,
    _C.PROJECT_NOT_FOUND: 404,
    _C.PROJECT_ARCHIVED: 409,
    _C.SPRINT_NOT_FOUND: 404,
    # 409, not 422: the request is well formed and the project's mode is the
    # thing that conflicts with it.
    _C.SPRINT_MODE_DISABLED: 409,
    _C.CONVERSATION_NOT_FOUND: 404,
    _C.CONVERSATION_ARCHIVED: 409,
    _C.CONVERSATION_KIND_INVALID: 409,
    _C.THREAD_PARENT_INVALID: 422,
    _C.THREAD_ALREADY_CLOSED: 409,
    _C.SCOPE_SHAPE_INVALID: 422,
    _C.INSTRUCTION_NOT_FOUND: 404,
    _C.MEMORY_ENTRY_NOT_FOUND: 404,
    # Not 404: the account exists, so this is a gap on our side.
    _C.SETTINGS_NOT_FOUND: 500,
    _C.EXPORT_NOT_FOUND: 404,
    # 202: accepted and still being produced. The caller should come back.
    _C.EXPORT_NOT_READY: 202,
    _C.DOCUMENT_NOT_FOUND: 404,
    _C.DOCUMENT_SCOPE_INVALID: 422,
    _C.DOCUMENT_VERSION_CONFLICT: 409,
    _C.PARSE_FORMAT_UNSUPPORTED: 415,
    _C.PARSE_FILE_UNREADABLE: 422,
    _C.PARSE_NO_PARSER_REGISTERED: 415,
    _C.RENDER_NO_RENDERER_REGISTERED: 422,
    _C.RENDER_FAILED: 500,
    _C.STORAGE_UNAVAILABLE: 503,
    _C.STORAGE_OBJECT_NOT_FOUND: 404,
    _C.EMBEDDING_UNAVAILABLE: 503,
    _C.EMBEDDING_ARITY_MISMATCH: 500,
    _C.EMBEDDING_DIM_MISMATCH: 500,
    _C.EMBEDDING_MODEL_VERSION_CONFLICT: 500,
    _C.RETRIEVAL_FAILED: 503,
    _C.RETRIEVAL_RERANK_UNAVAILABLE: 503,
    _C.DEPENDENCY_UNRESOLVABLE_REFERENCE: 422,
    _C.DEPENDENCY_TYPE_NOT_ALLOWED: 422,
    _C.DECISION_TRANSITION_INVALID: 409,
    _C.DECISION_APPROVAL_MISSING: 409,
    _C.TEMPLATE_NOT_FOUND: 503,
    _C.PROFILE_FILE_INVALID: 500,
    _C.PROFILE_DUPLICATE: 500,
    _C.PROFILE_NO_ACTIVE: 422,
    _C.PROFILE_AMBIGUOUS_ACTIVE: 500,
    _C.PROFILE_REFERENCE_UNRESOLVABLE: 500,
    _C.AGENT_RUN_NOT_FOUND: 404,
    _C.AGENT_RUN_TRANSITION_INVALID: 409,
    _C.AGENT_CHECKPOINT_MISSING: 409,
    _C.LLM_TIMEOUT: 504,
    _C.LLM_UNAVAILABLE: 503,
    _C.LLM_OUTPUT_INVALID: 502,
    _C.TOOL_NOT_REGISTERED: 500,
    _C.TOOL_EXECUTION_FAILED: 500,
    _C.CACHE_UNAVAILABLE: 503,
    _C.BUS_PUBLISH_FAILED: 500,
    _C.MAIL_UNAVAILABLE: 503,
    _C.MAIL_REJECTED: 502,
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
