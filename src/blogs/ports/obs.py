"""Observability and notification — both with a NoOp implementation.

The NoOp is not politeness; it removes a branch from every call site. The old
repo has around 78 tracer call sites. Seventy-eight ``if tracer:`` guards is
seventy-eight places to forget one, and a forgotten guard is invisible until you
go looking for a trace that was never written.

Bootstrap wires the NoOp when the relevant keys are unset. Never ``None``.
"""

from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self

from pydantic import JsonValue

from ai_auditor.contracts.common import NonEmptyStr


class Span(Protocol):
    """A unit of traced work. Used as an async context manager."""

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    def set_output(self, output: dict[str, JsonValue]) -> None: ...


class Tracer(Protocol):
    """Trace metadata is required, not optional.

    Without ``tenant_id`` / ``project_id`` / ``run_id`` on every trace there is
    one undifferentiated firehose across all tenants and no way to debug a single
    customer. The parameters are keyword-only and non-defaulted for that reason.
    """

    def span(
        self,
        name: NonEmptyStr,
        *,
        metadata: dict[str, JsonValue],
    ) -> Span: ...

    def event(self, name: NonEmptyStr, *, metadata: dict[str, JsonValue]) -> None: ...


class Mailer(Protocol):
    """What is left of sns-service after the merge."""

    async def send(
        self,
        *,
        to: tuple[NonEmptyStr, ...],
        subject: NonEmptyStr,
        body: str,
        template_key: str | None = None,
        template_context: dict[str, JsonValue] | None = None,
    ) -> None: ...
