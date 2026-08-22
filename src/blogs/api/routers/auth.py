"""Sign in, refresh, sign out.

Note what ``/otp/request`` returns: the same response whether or not the address
has an account. Differing would turn this endpoint into an account-enumeration
oracle, and the caller has no legitimate use for the distinction.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, Response

from blogs.api.deps import (
    ACTOR_HEADER,
    Assembled,
    ClientIp,
    CorrelationId,
    CurrentPrincipal,
    CurrentUser,
    UserAgent,
)
from blogs.api.envelope import success
from blogs.contracts.common import APIResponse, ContractModel, EmailStr, ErrorCategory, NonEmptyStr
from blogs.contracts.identity import (
    AuthPurpose,
    OAuthProviderName,
    OtpIssued,
    Principal,
    TokenPair,
    User,
)
from blogs.core.errors import raise_error

router = APIRouter(prefix="/auth", tags=["auth"])


class OtpRequestBody(ContractModel):
    email: EmailStr
    purpose: AuthPurpose = AuthPurpose.LOGIN


class OtpVerifyBody(ContractModel):
    email: EmailStr
    code: NonEmptyStr


class RefreshBody(ContractModel):
    refresh_token: NonEmptyStr


class RevokeBody(ContractModel):
    refresh_token: str | None = None
    all_devices: bool = False


class OtpRequestAccepted(ContractModel):
    """Deliberately free of anything that varies with account existence."""

    expires_at: str
    resend_after: str


@router.post("/otp/request")
async def request_otp(
    body: OtpRequestBody,
    assembled: Assembled,
    correlation: CorrelationId,
    ip: ClientIp,
) -> APIResponse[OtpRequestAccepted]:
    issued: OtpIssued = await assembled.auth_service.request_otp(
        email=body.email,
        purpose=body.purpose,
        client_ip=ip,
        correlation_id=correlation,
    )
    # token_ref is withheld: it is the handle F2 uses to find the challenge on
    # the bus, and the client has no use for it.
    return success(
        OtpRequestAccepted(
            expires_at=issued.expires_at.isoformat(),
            resend_after=issued.resend_after.isoformat(),
        ),
        message="If that address can sign in, a code is on its way.",
    )


@router.post("/otp/verify")
async def verify_otp(
    body: OtpVerifyBody,
    caller: CurrentPrincipal,
    assembled: Assembled,
    correlation: CorrelationId,
    ip: ClientIp,
    agent: UserAgent,
    response: Response,
) -> APIResponse[TokenPair]:
    """Exchange a code for tokens, inheriting the visitor's history.

    ``caller.actor_id`` is the anonymous actor this browser has been using. It
    is handed to the service so everything read before signing up is attributed
    to the new account — the cold-start head start.
    """
    result = await assembled.auth_service.verify_otp(
        email=body.email,
        code=body.code,
        actor_id=caller.actor_id,
        user_agent=agent,
        client_ip=ip,
        correlation_id=correlation,
    )
    response.headers[ACTOR_HEADER] = result.tokens.actor_token
    return success(
        result.tokens,
        message=(
            f"Signed in. {result.merged_events} earlier interactions were added "
            "to your account."
            if result.merged_events
            else "Signed in."
        ),
    )


@router.get("/oauth/{provider}/start")
async def start_oauth(
    provider: OAuthProviderName,
    assembled: Assembled,
    correlation: CorrelationId,
    redirect_path: Annotated[str, Query()] = "/",
) -> APIResponse[dict[str, str]]:
    """Begin the authorization-code flow.

    The ``state`` returned to the caller is signed and carries the PKCE
    verifier, so this server keeps no pending-flow table — consistent with
    foundation §3's refusal of server-side session state.
    """
    url, state = await assembled.auth_service_oauth.start(
        provider=provider, redirect_path=redirect_path, correlation_id=correlation
    )
    return success({"authorization_url": url, "state": state})


@router.get("/oauth/{provider}/callback")
async def complete_oauth(
    provider: OAuthProviderName,
    caller: CurrentPrincipal,
    assembled: Assembled,
    correlation: CorrelationId,
    ip: ClientIp,
    agent: UserAgent,
    response: Response,
    code: Annotated[str, Query()],
    state: Annotated[str, Query()],
) -> APIResponse[TokenPair]:
    profile = await assembled.auth_service_oauth.complete(
        provider=provider, code=code, state=state, correlation_id=correlation
    )
    result = await assembled.auth_service.complete_oauth(
        profile=profile,
        actor_id=caller.actor_id,
        user_agent=agent,
        client_ip=ip,
        correlation_id=correlation,
    )
    response.headers[ACTOR_HEADER] = result.tokens.actor_token
    return success(result.tokens, message="Signed in.")


@router.post("/refresh")
async def refresh(
    body: RefreshBody,
    assembled: Assembled,
    correlation: CorrelationId,
    ip: ClientIp,
    agent: UserAgent,
) -> APIResponse[TokenPair]:
    tokens = await assembled.auth_service.refresh(
        refresh_token=body.refresh_token,
        user_agent=agent,
        client_ip=ip,
        correlation_id=correlation,
    )
    return success(tokens)


@router.post("/revoke")
async def revoke(
    body: RevokeBody, user: CurrentUser, assembled: Assembled
) -> APIResponse[dict[str, int]]:
    revoked = await assembled.auth_service.revoke(
        refresh_token=body.refresh_token,
        user_id=user.user_id,
        all_devices=body.all_devices,
    )
    return success({"revoked": revoked}, message="Signed out.")


@router.get("/me")
async def me(
    caller: CurrentPrincipal, assembled: Assembled, correlation: CorrelationId
) -> APIResponse[User | Principal]:
    """Who the server thinks you are.

    Answers for an anonymous caller too, returning the actor. A client can
    therefore always ask, and does not need a separate "am I logged in" flag
    that could drift out of step with the token it holds.
    """
    from blogs.contracts.identity import UserPrincipal

    if not isinstance(caller, UserPrincipal):
        return success(caller, message="Not signed in.")

    async with assembled.uow.read() as uow:
        user = await uow.users.get(caller.user_id)
    if user is None:
        raise_error(ErrorCategory.USER_NOT_FOUND, correlation_id=correlation)
    return success(user)



__all__ = ["router"]
