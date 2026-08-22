"""Driven ports for accounts and the credentials that create them.

Every method returns a contract model or a primitive, never a database row. A
repository that leaked a ``dict`` would put the column names of one adapter into
the type signature every service reads, and swapping the adapter would then be a
rewrite rather than a substitution.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from blogs.contracts.identity import (
    AnonymousActor,
    AuthPurpose,
    OAuthProviderName,
    OtpChallenge,
    RefreshTokenRecord,
    User,
    UserStatus,
)


class UserRepository(Protocol):
    async def get(self, user_id: str) -> User | None: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def create(
        self,
        *,
        user_id: str,
        email: str,
        display_name: str | None,
        is_admin: bool,
        email_verified_at: datetime | None,
    ) -> User:
        """Insert an account.

        Raises ``EmailAlreadyRegistered`` on a duplicate address and
        ``AdminAlreadyExists`` when ``is_admin`` collides with the existing
        single admin — both surfaced from the constraint rather than from a
        pre-check, because a pre-check is a race.
        """
        ...

    async def set_status(self, user_id: str, status: UserStatus) -> None: ...

    async def mark_email_verified(self, user_id: str, at: datetime) -> None: ...

    async def get_admin(self) -> User | None:
        """The single admin, if one has been seeded."""
        ...

    async def get_password_hash(self, user_id: str) -> bytes | None:
        """The stored password hash, or ``None`` if the account has none.

        Kept off the ``User`` contract so it cannot be serialised into a
        response by accident.
        """
        ...

    async def set_password(
        self, *, user_id: str, password_hash: bytes, at: datetime
    ) -> None:
        """Set or rotate a password. A no-op for a non-admin, by constraint."""
        ...


class AdminLoginAttemptRepository(Protocol):
    """The admin sign-in audit log, and the lockout computed from it."""

    async def record(
        self,
        *,
        attempt_id: str,
        email: str,
        succeeded: bool,
        at: datetime,
        client_ip: str | None,
        user_agent: str | None,
    ) -> None:
        """``at`` comes from the injected clock, never the column default — the
        lockout window is measured against that same clock."""
        ...

    async def recent_failures(self, *, email: str, since: datetime) -> int:
        """Consecutive failures since the last success within the window."""
        ...

    async def delete_older_than(self, before: datetime) -> int: ...


class OAuthIdentityRepository(Protocol):
    async def find_user_id(
        self, provider: OAuthProviderName, provider_subject: str
    ) -> str | None: ...

    async def link(
        self,
        *,
        identity_id: str,
        user_id: str,
        provider: OAuthProviderName,
        provider_subject: str,
        email_at_provider: str | None,
    ) -> None: ...


class OtpChallengeRepository(Protocol):
    async def create(
        self,
        *,
        challenge_id: str,
        email: str,
        purpose: AuthPurpose,
        code_hash: bytes,
        expires_at: datetime,
        max_attempts: int,
        client_ip: str | None,
    ) -> OtpChallenge: ...

    async def latest_live(self, email: str, purpose: AuthPurpose) -> OtpChallenge | None:
        """The newest unconsumed challenge, expired or not.

        Expiry is not filtered here: the caller must be able to tell "expired"
        from "never existed" to answer with the right error, and to enforce the
        resend cooldown against the last request whether or not it lapsed.
        """
        ...

    async def consume_if_matching(
        self, *, email: str, purpose: AuthPurpose, code_hash: bytes, now: datetime
    ) -> tuple[OtpChallenge | None, str]:
        """Atomically verify and burn a code.

        Returns the challenge and one of ``matched``, ``mismatch``, ``expired``,
        ``exhausted``, ``missing``. The attempt counter increments in the same
        statement under a row lock, so parallel guesses cannot each read the
        same count and collectively exceed the limit.
        """
        ...

    async def delete_expired(self, before: datetime) -> int: ...


class RefreshTokenRepository(Protocol):
    async def create(
        self,
        *,
        token_id: str,
        user_id: str,
        family_id: str,
        token_hash: bytes,
        expires_at: datetime,
        user_agent: str | None,
        client_ip: str | None,
    ) -> RefreshTokenRecord: ...

    async def find_by_hash(self, token_hash: bytes) -> RefreshTokenRecord | None: ...

    async def consume(
        self, *, token_id: str, replaced_by_id: str, now: datetime
    ) -> bool:
        """Mark a token rotated. False if it was already consumed or revoked.

        The boolean is the reuse check: losing this race means another request
        already rotated the same token, which is exactly the condition that
        must revoke the family.
        """
        ...

    async def revoke_family(self, family_id: str, *, reason: str, now: datetime) -> int: ...

    async def revoke_all_for_user(self, user_id: str, *, reason: str, now: datetime) -> int: ...

    async def delete_expired(self, before: datetime) -> int: ...


class AnonymousActorRepository(Protocol):
    async def create(
        self, *, actor_id: str, user_agent: str | None, client_ip: str | None
    ) -> AnonymousActor: ...

    async def get(self, actor_id: str) -> AnonymousActor | None: ...

    async def touch(self, actor_id: str, at: datetime) -> None:
        """Move ``last_seen_at``. Best-effort: a missed touch costs nothing."""
        ...

    async def mark_merged(self, *, actor_id: str, user_id: str, at: datetime) -> None: ...
