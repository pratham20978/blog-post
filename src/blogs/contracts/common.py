"""The contract floor: strictness, identifiers, closed sets, and the envelope.

This module imports Pydantic and the standard library and nothing else, ever.
Every other contract module imports from here.for why this package may not reach anything.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal, Self

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

ActorId = _Uuid   # this is to refer the the user who didin't log in we just make it based on the mac or ip the suer has ont he distice system 


tags = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=64)]
#tags we are not going to hard code at here right here now 


# other thign s staisfy yrr




class ProcessingStage(StrEnum):
    """Where in this system's pipeline a failure happened."""

    AUTH = "AUTH"
    NOTIFY = "NOTIFY"
    # other etc


class Retryability(StrEnum):
    RETRYABLE = "RETRYABLE"
    NOT_RETRYABLE = "NOT_RETRYABLE"
    POLICY_DEPENDENT = "POLICY_DEPENDENT"


class ErrorCategory(StrEnum):
    """Named by domain, never by former service (R15).

    The five processes this system was merged from are gone; a category named
    after one would outlive the thing it was named for.
    """

    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_REVOKED = "AUTH_TOKEN_REVOKED"
    AUTH_CREDENTIALS_INVALID = "AUTH_CREDENTIALS_INVALID"

    DEVICE_NOT_FOUND = "DEVICE_NOT_FOUND"

    USER_NOT_FOUND = "USER_NOT_FOUND"
    TENANT_INACTIVE = "TENANT_INACTIVE"

    ACCESS_DENIED = "ACCESS_DENIED"

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
