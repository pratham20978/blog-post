"""Identity resolution — the one place a caller becomes a ``Principal``.

Every request passes through here exactly once, and this is where the questions
"who is this?" and "is this token real?" are answered:

1. **Correlation id.** Taken from the header or minted, so every log line and
   every error envelope for this request shares one traceable id.

2. **Who is calling.** In priority order:

   * ``Authorization: Bearer <access token>`` → the JWT signature is verified,
     and the ``sub`` (user id), ``act`` (actor id) and ``adm`` (admin flag)
     claims become a ``UserPrincipal``. **No database read** — the signature is
     the proof, which is what makes foundation §3's "stateless" true.
   * ``X-Actor-Token: <actor token>`` → a separately-signed token whose ``sub``
     is an anonymous actor id, giving an ``AnonymousPrincipal``.
   * neither → a brand new anonymous actor is minted, inserted into
     ``anonymous_actors``, and its signed token returned in ``X-Actor-Token``.

3. **Where uniqueness comes from.** The actor id is a **server-generated
   UUIDv7**, inserted under a primary key, and handed back inside a token this
   server signed. A client never chooses it and cannot forge one: an
   ``X-Actor-Token`` we did not sign fails verification. That matters because
   the actor id is the subject of every engagement row — a forgeable id would
   let anyone write history attributed to someone else, and F1's affinity and
   F2's segmentation are computed from exactly those rows.

**Why failures are stored rather than raised.** An exception thrown inside
middleware propagates *outside* Starlette's ``ExceptionMiddleware``, so the
registered handlers never see it and a caller with an expired token would get a
bare unshaped 500. So a bad credential is recorded on ``request.state`` and
re-raised by the ``principal`` dependency, which runs inside handler scope and
produces the proper envelope. Routes that never ask for a principal — the
health probes — are unaffected either way.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from blogs.core.errors import BlogPlatformError
from blogs.services.actor_service import ActorService

logger = logging.getLogger(__name__)

CORRELATION_HEADER = "X-Correlation-ID"
ACTOR_HEADER = "X-Actor-Token"

#: Paths that never need an identity. Minting an anonymous actor for every
#: liveness probe would add a row per second and make ``anonymous_actors``
#: mostly a log of Kubernetes.
_ANONYMOUS_EXEMPT = frozenset(
    {"/healthz", "/readyz", "/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"}
)


class IdentityMiddleware(BaseHTTPMiddleware):
    """Resolves the caller once, before any route runs."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        header = request.headers.get(CORRELATION_HEADER)
        correlation = header.strip() if header and header.strip() else uuid4().hex
        request.state.correlation_id = correlation

        request.state.principal = None
        request.state.auth_error = None
        request.state.issued_actor_token = None

        if request.url.path not in _ANONYMOUS_EXEMPT:
            await self._resolve(request)

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

    async def _resolve(self, request: Request) -> None:
        container = getattr(request.app.state, "container", None)
        if container is None:
            # Assembly failed or is still in progress. Leave the request
            # unidentified; the dependency turns that into a clean error rather
            # than an AttributeError deep in a route.
            return

        actor_service: ActorService = container.actor_service
        try:
            resolved = await actor_service.resolve(
                authorization=request.headers.get("authorization"),
                actor_token=request.headers.get(ACTOR_HEADER),
            )
        except BlogPlatformError as exc:
            # Deferred, not raised — see the module docstring.
            request.state.auth_error = exc
            return

        request.state.principal = resolved.principal
        if resolved.issued_actor_token:
            request.state.issued_actor_token = resolved.issued_actor_token
