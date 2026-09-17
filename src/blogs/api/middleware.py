"""Identity resolution — the one place a caller becomes a ``Principal``.

Every request passes through here exactly once, and this is where the questions
"who is this?" and "is this token real?" are answered:

1. **Correlation id.** Taken from the header or minted, so every log line and
   every error envelope for this request shares one traceable id.

2. **Who is calling.** Resolution is lazy. A route that declares the
   ``principal`` dependency verifies its access/actor token or mints an actor;
   a public route, health check, or 404 never needs an identity and therefore
   never writes one. The middleware only carries a newly issued token back in
   the response header.

3. **Where uniqueness comes from.** The actor id is a **server-generated
   UUIDv7**, inserted under a primary key, and handed back inside a token this
   server signed. A client never chooses it and cannot forge one: an
   ``X-Actor-Token`` we did not sign fails verification. That matters because
   the actor id is the subject of every engagement row — a forgeable id would
   let anyone write history attributed to someone else, and F1's affinity and
   F2's segmentation are computed from exactly those rows.

Credential failures arise inside the dependency rather than middleware, so
Starlette's registered exception handlers can shape them normally.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

CORRELATION_HEADER = "X-Correlation-ID"
ACTOR_HEADER = "X-Actor-Token"


class IdentityMiddleware(BaseHTTPMiddleware):
    """Carries request metadata and any lazily issued actor token."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        header = request.headers.get(CORRELATION_HEADER)
        correlation = header.strip() if header and header.strip() else uuid4().hex
        request.state.correlation_id = correlation

        request.state.principal = None
        request.state.issued_actor_token = None

        response = await call_next(request)

        response.headers[CORRELATION_HEADER] = correlation
        issued = getattr(request.state, "issued_actor_token", None)
        if issued:
            # Returned on the response that minted it. The client stores this
            # and sends it from then on, which is what lets one visitor keep a
            # single identity across requests instead of becoming a new actor
            # on every page.
            response.headers[ACTOR_HEADER] = issued
        return response
