"""Exception handlers, registered before any router.

Everything that escapes a route leaves through here, so a failure is always
shaped like the success envelope. Three sources are handled:

* ``BlogPlatformError`` — a domain refusal, already caller-safe.
* ``RequestValidationError`` — pydantic rejected the request body.
* anything else — an unexpected fault, logged in full and reported as a generic
  500. The distinction matters: an internal message can name a table, a column,
  or the contents of a variable, and none of that belongs in a response.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from blogs.api.deps import CORRELATION_HEADER, correlation_id_of
from blogs.api.envelope import failure, status_for
from blogs.contracts.common import ErrorCategory, ErrorEnvelope, ProcessingStage, Retryability
from blogs.core.errors import ERROR_CATALOG, BlogPlatformError, NotModified

logger = logging.getLogger(__name__)


def _respond(envelope: ErrorEnvelope, status: int) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content=failure(envelope).model_dump(mode="json"),
        # Echoed so a caller can quote it in a bug report without having to
        # have sent one themselves.
        headers={CORRELATION_HEADER: envelope.correlation_id},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotModified)
    async def _not_modified(request: Request, exc: NotModified) -> Response:
        """A 304 must carry no body, so this is a bare Response, not an envelope.

        Handled here rather than returned from the route so route signatures
        stay single-typed — see ``NotModified``.
        """
        return Response(status_code=304, headers={"ETag": exc.etag})

    @app.exception_handler(BlogPlatformError)
    async def _domain(request: Request, exc: BlogPlatformError) -> JSONResponse:
        # The raise site may have had no correlation id — a repository three
        # layers down should not need one to report a taken slug — so the
        # transport stamps it here, where the request is in scope.
        envelope = exc.to_envelope(correlation_id=correlation_id_of(request))
        logger.info(
            "request refused",
            extra={
                "category": envelope.category.value,
                "path": request.url.path,
                "correlation": envelope.correlation_id,
            },
        )
        return _respond(envelope, status_for(exc.category))

    @app.exception_handler(RequestValidationError)
    async def _validation(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        descriptor = ERROR_CATALOG[ErrorCategory.REQUEST_INVALID]
        # Field locations and messages only. Pydantic's `input` echoes the
        # submitted value, which for /auth endpoints is a one-time code.
        fields = [
            {"field": ".".join(str(p) for p in err.get("loc", ())), "reason": err.get("msg")}
            for err in exc.errors()[:10]
        ]
        envelope = ErrorEnvelope(
            category=ErrorCategory.REQUEST_INVALID,
            safe_message=descriptor.safe_message,
            retryability=descriptor.retryability,
            stage=descriptor.stage,
            safe_details={"fields": fields},
            correlation_id=correlation_id_of(request),
        )
        return _respond(envelope, status_for(ErrorCategory.REQUEST_INVALID))

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception) -> JSONResponse:
        correlation = correlation_id_of(request)
        # The full exception goes to the log, where the correlation id ties it
        # to the opaque response the caller received.
        logger.exception(
            "unhandled error", extra={"path": request.url.path, "correlation": correlation}
        )
        envelope = ErrorEnvelope(
            category=ErrorCategory.INTERNAL_ERROR,
            safe_message=ERROR_CATALOG[ErrorCategory.INTERNAL_ERROR].safe_message,
            retryability=Retryability.POLICY_DEPENDENT,
            stage=ProcessingStage.COMPOSE,
            safe_details={},
            correlation_id=correlation,
        )
        return _respond(envelope, 500)
