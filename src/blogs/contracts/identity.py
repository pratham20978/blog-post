"""Who is acting, and what they were issued.

The central idea: **every** caller has an ``actor_id``, logged in or not. An
anonymous reader is handed a server-issued actor on first contact, so the
engagement log has a subject before there is an account, and reads, engagement
and recent views take one code path rather than an authenticated one plus an
anonymous special case bolted on later.

On login the anonymous actor is merged into the user (see
``services.auth_service.MergeAnonymousActor``), so the account arrives with the
history it accumulated before signing up.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field

from blogs.contracts.common import (
    ActorId,
    ContractModel,
    EmailStr,
    NonEmptyStr,
    TokenId,
    UserId,
)


class AuthPurpose(StrEnum):
    LOGIN = "login"
    SIGNUP = "signup"


class UserStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class OAuthProviderName(StrEnum):
    GOOGLE = "google"
    GITHUB = "github"


# ---------------------------------------------------------------------------
# Principals
# ---------------------------------------------------------------------------


class AnonymousPrincipal(ContractModel):
    """A reader we have issued an actor token to but who has not signed in."""

    kind: Literal["anonymous"] = "anonymous"
    actor_id: ActorId

    @property
    def user_id(self) -> None:
        return None

    @property
    def is_admin(self) -> bool:
        return False


class UserPrincipal(ContractModel):
    """A signed-in account. ``actor_id`` is retained so engagement written
    before and after login shares one subject."""

    kind: Literal["user"] = "user"
    actor_id: ActorId
    user_id: UserId
    is_admin: bool = False


Principal = Annotated[AnonymousPrincipal | UserPrincipal, Field(discriminator="kind")]


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


class User(ContractModel):
    id: UserId
    email: EmailStr
    display_name: str | None = None
    is_admin: bool
    status: UserStatus
    email_verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class OAuthIdentity(ContractModel):
    user_id: UserId
    provider: OAuthProviderName
    provider_subject: NonEmptyStr
    email_at_provider: str | None = None
    linked_at: datetime


class OAuthProfile(ContractModel):
    """What an OAuth provider told us about the person who just signed in."""

    provider: OAuthProviderName
    subject: NonEmptyStr
    email: EmailStr | None = None
    email_verified: bool = False
    display_name: str | None = None


# ---------------------------------------------------------------------------
# Issued credentials
# ---------------------------------------------------------------------------


class TokenPair(ContractModel):
    """What a completed sign-in hands back.

    The access token verifies by signature alone — no database read on any
    authenticated request. Only ``/auth/refresh`` and ``/auth/revoke`` touch the
    ``refresh_tokens`` table.
    """

    access_token: NonEmptyStr
    refresh_token: NonEmptyStr
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int
    actor_token: NonEmptyStr


class AccessTokenClaims(ContractModel):
    user_id: UserId
    actor_id: ActorId
    is_admin: bool
    token_id: TokenId
    issued_at: datetime
    expires_at: datetime


class RefreshTokenRecord(ContractModel):
    """One row of the refresh registry.

    A ``family_id`` groups every token descended from one sign-in. Presenting a
    token that was already consumed means the token leaked, because the honest
    client would have moved on to its successor — so the whole family dies.
    """

    id: TokenId
    user_id: UserId
    family_id: TokenId
    issued_at: datetime
    expires_at: datetime
    consumed_at: datetime | None = None
    replaced_by_id: TokenId | None = None
    revoked_at: datetime | None = None
    revoked_reason: str | None = None


class AnonymousActor(ContractModel):
    id: ActorId
    created_at: datetime
    last_seen_at: datetime
    merged_into_user_id: UserId | None = None
    merged_at: datetime | None = None


class OtpChallenge(ContractModel):
    """The stored half of a one-time code. The code itself is never persisted —
    only ``sha256(pepper || code)`` — and never leaves the process that made it.
    """

    id: str
    email: EmailStr
    purpose: AuthPurpose
    expires_at: datetime
    attempts: int
    max_attempts: int
    consumed_at: datetime | None = None
    created_at: datetime


class OtpIssued(ContractModel):
    """Returned by ``RequestOtp``. Carries a ``token_ref`` only: foundation §7
    forbids putting the code itself on the event bus."""

    token_ref: str
    expires_at: datetime
    resend_after: datetime
