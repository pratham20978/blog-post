
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


ERROR_CATALOG: dict[ErrorCategory, ErrorDescriptor] = {
    # ── Auth ────────────────────────────────────────────────────────────────
    _C.AUTH_TOKEN_INVALID: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "The supplied credentials are not valid."
    ),
    _C.AUTH_TOKEN_EXPIRED: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "The session has expired. Sign in again."
    ),
    _C.AUTH_TOKEN_REVOKED: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "This session has been revoked."
    ),
    _C.AUTH_CREDENTIALS_INVALID: ErrorDescriptor(
        _S.AUTH, _R.NOT_RETRYABLE, "The supplied credentials are not valid."
    ),

    # ── Access ──────────────────────────────────────────────────────────────
    _C.ACCESS_DENIED: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "You do not have access to this resource."
    ),
    # ── Actors ──────────────────────────────────────────────────────────────
    _C.ACTOR_NOT_FOUND: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "That participant does not exist."
    ),
    # An actor is deactivated, never deleted, so "gone" and "inactive" are
    # different answers and the caller can act on the difference.
    _C.ACTOR_INACTIVE: ErrorDescriptor(
        _S.ACCESS, _R.NOT_RETRYABLE, "That participant is no longer active."
    ),
    # ── Generic ─────────────────────────────────────────────────────────────
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


class AIAuditorError(Exception):
    """A request-scoped error that converts to a caller-safe envelope."""

    def __init__(
        self,
        category: ErrorCategory,
        *,
        correlation_id: str,
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

    def to_envelope(self) -> ErrorEnvelope:
        return ErrorEnvelope(
            category=self.category,
            safe_message=self.safe_message,
            retryability=self.retryability,
            stage=self.stage,
            safe_details=self.safe_details,
            correlation_id=self.correlation_id,
        )


def raise_error(
    category: ErrorCategory,
    *,
    correlation_id: str,
    safe_message: str | None = None,
    safe_details: Mapping[str, JsonValue] | None = None,
) -> NoReturn:
    """Raise from the catalogue.

    Typed ``NoReturn`` so the checker knows control does not continue — which is
    what lets a caller write ``raise_error(...)`` instead of ``raise
    AIAuditorError(...)`` without confusing narrowing.
    """
    raise AIAuditorError(
        category,
        correlation_id=correlation_id,
        safe_message=safe_message,
        safe_details=safe_details,
    )
