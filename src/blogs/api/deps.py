"""Request-scoped dependencies.

Three things every route needs: a correlation id, the assembled container, and
the caller's ``Principal``. Nothing else — there is no tenant, project or
workspace scope in this system, and the ladder of scoped addresses that used to
live in this module belonged to a different application.

``principal`` is the interesting one, because it always succeeds for a reader.
An unauthenticated visitor is issued an actor and comes back as an
``AnonymousPrincipal``; ``current_user`` is the dependency that demands an
account, and ``require_admin`` the one that demands the admin. Routes therefore
declare what they need instead of re-deriving it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import uuid4

from fastapi import Depends, Header, Request

from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import Principal, UserPrincipal
from blogs.core.errors import BlogPlatformError, raise_error

if TYPE_CHECKING:
    from blogs.bootstrap import Container

CORRELATION_HEADER = "X-Correlation-ID"
ACTOR_HEADER = "X-Actor-Token"


def correlation_id(request: Request) -> str:
    """The per-request id, as set by ``IdentityMiddleware``.

    Minted there rather than here so that a request failing *before* the
    dependency graph resolves still has one — an error envelope without a
    correlation id is an error nobody can trace back to a log line.
    """
    return correlation_id_of(request)


def correlation_id_of(request: Request) -> str:
    """The id for a request that may have failed before dependencies resolved."""
    existing = getattr(request.state, "correlation_id", None)
    return existing if isinstance(existing, str) and existing else uuid4().hex


def container(request: Request) -> Container:
    """The assembled application, from ``app.state``.

    Imported lazily inside the function: ``bootstrap`` imports adapters,
    repositories and services, and importing it at module scope would put that
    whole graph behind ``import blogs.api.deps``.
    """
    from blogs.bootstrap import Container as _Container

    assembled = request.app.state.container
    if not isinstance(assembled, _Container):
        raise RuntimeError("application container is not assembled")
    return assembled


Assembled = Annotated["Container", Depends(container)]
CorrelationId = Annotated[str, Depends(correlation_id)]


async def principal(request: Request, correlation: CorrelationId) -> Principal:
    """The caller, as resolved by ``IdentityMiddleware``.

    This does not re-derive anything. Identity is decided once per request, in
    ``api/middleware.py``, and read here — so a route cannot end up with a
    different answer from a log line about the same request.

    What it *does* do is raise. A bad credential is deferred by the middleware
    (an exception thrown there escapes Starlette's handlers and becomes an
    unshaped 500), so the failure surfaces here, inside handler scope, where it
    turns into a proper envelope.
    """
    error = getattr(request.state, "auth_error", None)
    if isinstance(error, BlogPlatformError):
        raise error

    resolved = getattr(request.state, "principal", None)
    if resolved is None:
        # The middleware runs on every non-exempt path, so this means the
        # container was not assembled — a startup fault, not a caller mistake.
        raise RuntimeError(
            "no principal on the request: IdentityMiddleware did not run or "
            "the application container is not assembled"
        )
    return resolved


CurrentPrincipal = Annotated[Principal, Depends(principal)]


async def current_user(caller: CurrentPrincipal, correlation: CorrelationId) -> UserPrincipal:
    """Demand an account.

    401 rather than 403 for an anonymous caller: signing in would make the same
    request succeed, and the client needs to know that.
    """
    if not isinstance(caller, UserPrincipal):
        raise_error(ErrorCategory.AUTH_REQUIRED, correlation_id=correlation)
    return caller


CurrentUser = Annotated[UserPrincipal, Depends(current_user)]


async def require_admin(user: CurrentUser, correlation: CorrelationId) -> UserPrincipal:
    """Demand the single admin.

    403 here, because the caller is authenticated and still not permitted —
    retrying will not help, and saying 401 would invite a pointless re-login.
    """
    if not user.is_admin:
        raise_error(ErrorCategory.ADMIN_REQUIRED, correlation_id=correlation)
    return user


AdminUser = Annotated[UserPrincipal, Depends(require_admin)]


def client_ip(request: Request) -> str | None:
    """The caller's address, as far as it can be trusted.

    ``X-Forwarded-For`` is not read. It is client-controlled unless a proxy is
    known to overwrite it, and this application does not know what sits in front
    of it — trusting it would let anyone forge the address the OTP throttle is
    keyed on. When a trusted proxy is introduced, that fact belongs here.
    """
    return request.client.host if request.client else None


ClientIp = Annotated[str | None, Depends(client_ip)]


def user_agent(
    value: Annotated[str | None, Header(alias="User-Agent")] = None,
) -> str | None:
    return value[:500] if value else None


UserAgent = Annotated[str | None, Depends(user_agent)]
