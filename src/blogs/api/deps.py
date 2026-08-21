from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import uuid4

from fastapi import Depends, Header, Request

from blogs.contracts.common import (
    ConversationId,
    ErrorCategory,
)
from blogs.contracts.identity import Actor, TenantScope
from blogs.core.errors import raise_error

if TYPE_CHECKING:
    from blogs.bootstrap import Container

CORRELATION_HEADER = "X-Correlation-ID"


def correlation_id(
    header: Annotated[str | None, Header(alias=CORRELATION_HEADER)] = None,
) -> str:
    """Per-request id, supplied or minted.

    Minted rather than left empty so every error envelope has one. An envelope
    with no correlation id is an error nobody can trace back to a log line.
    """
    if header and header.strip():
        return header.strip()
    return uuid4().hex


async def current_actor(
    request: Request,
    correlation: Annotated[str, Depends(correlation_id)],
) -> Actor:
    """Resolve the caller.

    OPEN-ARCH-05 — the token scheme is undecided (bearer in ``localStorage`` today
    vs httpOnly cookies plus a short-lived WS ticket). Until it is settled this
    reads a pre-resolved actor placed on ``request.state`` by the auth middleware,
    so the decision changes one module rather than every route.
    """
    actor = getattr(request.state, "actor", None)
    if not isinstance(actor, Actor):
        raise_error(ErrorCategory.AUTH_TOKEN_INVALID, correlation_id=correlation)
    return actor


async def tenant_scope(actor: Annotated[Actor, Depends(current_actor)]) -> TenantScope:
    """The value every repository method requires as its first keyword argument.

    Derived from the actor, never from a request parameter. A client-supplied
    ``tenant_id`` is the simplest possible cross-tenant read, and it is not
    reachable from here.
    """
    return actor.to_scope()


CorrelationId = Annotated[str, Depends(correlation_id)]
CurrentActor = Annotated[Actor, Depends(current_actor)]
Scope = Annotated[TenantScope, Depends(tenant_scope)]


def container(request: Request) -> Container:
    """The assembled application, from ``app.state``.

    Imported lazily inside the function: ``bootstrap`` imports adapters,
    repositories and services, and importing it at module scope would put that
    whole graph behind ``import ai_auditor.api.deps``.
    """
    from ai_auditor.bootstrap import Container

    assembled = request.app.state.container
    if not isinstance(assembled, Container):
        raise RuntimeError("application container is not assembled")
    return assembled


Assembled = Annotated["Container", Depends(container)]


async def workspace_scope(
    container: Assembled,
    scope: Annotated[TenantScope, Depends(tenant_scope)],
    correlation: Annotated[str, Depends(correlation_id)],
    level: ScopeLevel = ScopeLevel.TENANT,
    project_id: ProjectId | None = None,
    sprint_id: SprintId | None = None,
    conversation_id: ConversationId | None = None,
) -> WorkspaceScope:
    """The address a scoped read or write is about, verified.

    Deliberately asymmetric: each level takes **one** id and the rest are *derived*.

    * ``tenant`` — nothing.
    * ``actor`` — the acting actor. There is no parameter, so reading somebody else's
      personal memory is not expressible rather than merely refused.
    * ``project`` — ``project_id``.
    * ``sprint`` — ``sprint_id``; the project comes from the sprint.
    * ``conversation`` — ``conversation_id``; the project *and* the sprint come from
      the conversation.

    Deriving rather than accepting is the point. A caller that could send both a
    ``conversation_id`` and a ``sprint_id`` could send a mismatched pair, and the
    resulting scope would be a valid-looking address that matches no stored row —
    reads silently returning nothing, which is the hardest kind of bug to see. The
    ``workspace_scope`` properties on ``Sprint`` and ``Conversation`` are what make
    the derived version a one-liner.

    Every id is checked through ``AccessService`` on the way, so an address outside
    this tenant is a 404 before it ever reaches a query.
    """
    access = container.access_service
    match level:
        case ScopeLevel.TENANT:
            return WorkspaceScope.at_tenant(scope.tenant_id)
        case ScopeLevel.ACTOR:
            return WorkspaceScope.at_actor(scope.tenant_id, scope.actor_id)
        case ScopeLevel.PROJECT:
            project = _required(project_id, "project_id", correlation=correlation)
            verified = await access.ensure_project(
                scope=scope, project_id=project, correlation_id=correlation
            )
            return verified.workspace_scope
        case ScopeLevel.SPRINT:
            sprint = _required(sprint_id, "sprint_id", correlation=correlation)
            return (
                await access.ensure_sprint(
                    scope=scope, sprint_id=sprint, correlation_id=correlation
                )
            ).workspace_scope
        case ScopeLevel.CONVERSATION:
            conversation = _required(conversation_id, "conversation_id", correlation=correlation)
            return (
                await access.ensure_conversation(
                    scope=scope, conversation_id=conversation, correlation_id=correlation
                )
            ).workspace_scope


def _required(value: str | None, name: str, *, correlation: str) -> str:
    """The id this level cannot do without.

    Refused here rather than by ``WorkspaceScope``'s validator, so the message names
    the query parameter the caller actually sent instead of the column it maps to.
    """
    if value is None:
        raise_error(
            ErrorCategory.REQUEST_INVALID,
            correlation_id=correlation,
            safe_details={"reason": "MISSING_SCOPE_ID", "parameter": name},
        )
    return value


At = Annotated[WorkspaceScope, Depends(workspace_scope)]
