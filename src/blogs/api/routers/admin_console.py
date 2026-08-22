"""Admin sign-in, mounted only under the secret console prefix.

This router is never registered at a guessable path. Its full URL is
``{BLOGS_ADMIN_PATH_PREFIX}/auth/login``, and the prefix is a secret the admin
holds — so a scanner walking ``/admin``, ``/wp-admin``, ``/administrator`` finds
nothing, and there is no login form at a discoverable URL to attack.

To be clear about what that is and is not worth: **the prefix is obscurity, not
authentication.** Anyone who learns the path still faces the password, the
lockout, and ``require_admin`` on every subsequent request. What it removes is
the automated background noise — the credential-stuffing traffic that finds
login forms by scanning — which is most of what an admin panel on the open
internet actually receives.

The layers, in the order an attacker meets them:

1. the secret path — stops scanners finding the surface at all
2. the password — scrypt, memory-hard, with a lockout after repeated failures
3. the signed access token — checked by ``require_admin`` on every admin request
4. ``is_admin`` in the database — one row, guaranteed by a partial unique index
"""

from __future__ import annotations

from fastapi import APIRouter, Response

from blogs.api.deps import (
    ACTOR_HEADER,
    AdminUser,
    Assembled,
    ClientIp,
    CorrelationId,
    CurrentPrincipal,
    UserAgent,
)
from blogs.api.envelope import success
from blogs.contracts.common import APIResponse, ContractModel, EmailStr, NonEmptyStr
from blogs.contracts.identity import TokenPair, User

router = APIRouter(tags=["admin-console"])


class AdminLoginBody(ContractModel):
    email: EmailStr
    password: NonEmptyStr


class ChangePasswordBody(ContractModel):
    current_password: NonEmptyStr
    new_password: NonEmptyStr


@router.post("/auth/login")
async def admin_login(
    body: AdminLoginBody,
    caller: CurrentPrincipal,
    assembled: Assembled,
    correlation: CorrelationId,
    ip: ClientIp,
    agent: UserAgent,
    response: Response,
) -> APIResponse[TokenPair]:
    """Sign in to the console with email and password.

    Every failure — unknown address, no password set, wrong password — answers
    identically, so this cannot be used to discover which admin address exists.
    """
    result = await assembled.auth_service.admin_password_login(
        email=body.email,
        password=body.password,
        actor_id=caller.actor_id,
        user_agent=agent,
        client_ip=ip,
        correlation_id=correlation,
    )
    response.headers[ACTOR_HEADER] = result.tokens.actor_token
    # Belt and braces: this response carries credentials, so no cache anywhere
    # on the path is allowed to keep it.
    response.headers["Cache-Control"] = "no-store"
    return success(result.tokens, message="Signed in to the console.")


@router.post("/auth/password")
async def change_admin_password(
    body: ChangePasswordBody,
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
    ip: ClientIp,
    agent: UserAgent,
) -> APIResponse[dict[str, str]]:
    """Rotate the console password.

    The current password is re-checked even though the caller already holds a
    valid admin token: without that, a stolen token could be escalated into
    permanent access by simply changing the password. Every existing session is
    revoked on success, this one included.
    """
    async with assembled.uow.read() as uow:
        user = await uow.users.get(admin.user_id)
    assert user is not None

    await assembled.auth_service.admin_password_login(
        email=user.email,
        password=body.current_password,
        actor_id=admin.actor_id,
        user_agent=agent,
        client_ip=ip,
        correlation_id=correlation,
    )
    await assembled.auth_service.set_admin_password(
        user_id=admin.user_id, password=body.new_password, correlation_id=correlation
    )
    return success(
        {"user_id": admin.user_id},
        message="Password changed. Every session has been signed out.",
    )


@router.get("/session")
async def admin_session(admin: AdminUser, assembled: Assembled) -> APIResponse[User]:
    """Confirm the console session is live, and who it belongs to.

    Also the cheapest way for the console UI to check that the secret prefix it
    was given is still the right one.
    """
    async with assembled.uow.read() as uow:
        user = await uow.users.get(admin.user_id)
    assert user is not None
    return success(user)
