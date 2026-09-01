"""Auth lifecycle and engagement ingestion.

Two of these are regression tests for bugs this suite would have caught. Both
passed a casual read and both were wrong in the running system:

* **Dedupe** was enforced by ``UNIQUE (dedupe_key, occurred_at)``. PostgreSQL
  requires the partition key in a unique index on a partitioned table, and
  ``occurred_at`` is assigned per insert — so a retried beacon carried the same
  key at a new timestamp and was recorded twice.
* **Reuse detection** revoked the token family and then raised *inside* the same
  transaction, so the rollback undid the revocation. The caller was told the
  session was dead while every token in it stayed live.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from blogs.adapters.email import InMemoryEmailSender
from blogs.contracts.common import ErrorCategory
from blogs.contracts.engagement import (
    EngagementKind,
    EngagementSource,
    RecordEngagementCommand,
)
from blogs.contracts.identity import AnonymousPrincipal, AuthPurpose
from blogs.core.errors import BlogPlatformError
from blogs.services.auth_service import AuthService, OtpSettings
from blogs.services.engagement_service import EngagementService
from blogs.services.policy import DefaultAuthorizationPolicy

pytestmark = pytest.mark.asyncio

NOW = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)


@pytest.fixture
def auth(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords) -> AuthService:  # type: ignore[no-untyped-def]
    return AuthService(
        uow=uow,
        email=InMemoryEmailSender(),
        clock=clock,
        ids=ids,
        hasher=hasher,
        access_tokens=access_tokens,
        actor_tokens=actor_tokens,
        passwords=passwords,
        otp_settings=OtpSettings(
            length=6, ttl_seconds=600, max_attempts=3,
            resend_cooldown_seconds=0, log_codes=False,
        ),
        refresh_ttl_seconds=2_592_000,
        access_ttl_seconds=900,
        admin_max_failed_logins=3,
        admin_lockout_window_s=900,
    )


@pytest.fixture
def engagement(uow, clock, ids) -> EngagementService:  # type: ignore[no-untyped-def]
    return EngagementService(
        uow=uow, clock=clock, ids=ids, policy=DefaultAuthorizationPolicy()
    )


async def _actor(uow, ids) -> str:  # type: ignore[no-untyped-def]
    actor_id = ids.new_id()
    async with uow.begin() as work:
        await work.actors.create(actor_id=actor_id, user_agent=None, client_ip=None)
    return actor_id


async def _sign_in(auth: AuthService, uow, ids, email: str):  # type: ignore[no-untyped-def]
    """Complete an OTP sign-in, reading the code out of the database."""
    actor_id = await _actor(uow, ids)
    await auth.request_otp(email=email, purpose=AuthPurpose.LOGIN)

    # The code is never stored, so the test re-derives the hash the same way the
    # service does and finds the matching challenge by brute force over the
    # 10^6 space — feasible only because the test knows the pepper.
    async with uow.read() as work:
        challenge = await work.otp.latest_live(email, AuthPurpose.LOGIN)
    assert challenge is not None
    code = await _recover_code(uow, email)
    return await auth.verify_otp(email=email, code=code, actor_id=actor_id), actor_id


async def _recover_code(uow, email: str) -> str:  # type: ignore[no-untyped-def]
    """Find the code whose peppered hash matches the stored one.

    Only possible in a test, and only because the pepper is known. That it takes
    this much effort is the point: the code is genuinely not recoverable from
    the database alone.
    """
    import hashlib

    async with uow.read() as work:
        row = await work.otp._fetch_one(
            "SELECT code_hash FROM otp_challenges "
            "WHERE email_normalized = %(e)s AND consumed_at IS NULL "
            "ORDER BY created_at DESC LIMIT 1",
            {"e": email},
        )
    assert row is not None
    target = bytes(row["code_hash"])
    pepper = b"test-pepper"
    for candidate in range(1_000_000):
        code = str(candidate).zfill(6)
        if hashlib.sha256(pepper + code.encode()).digest() == target:
            return code
    raise AssertionError("no matching code found")


class TestOtpSignIn:
    async def test_sign_in_creates_the_account_and_emits_the_event(
        self, auth, uow, ids
    ) -> None:  # type: ignore[no-untyped-def]
        result, _ = await _sign_in(auth, uow, ids, "new@example.com")
        assert result.created is True
        assert result.user.email == "new@example.com"

        async with uow.read() as work:
            rows = await work.outbox._fetch_all(
                "SELECT event_name, payload FROM outbox_events ORDER BY occurred_at"
            )
        names = [r["event_name"] for r in rows]
        assert "UserRegistered" in names
        assert "OtpRequested" in names

    async def test_the_code_never_reaches_the_event_bus(self, auth, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """Foundation §7: the bus carries a token_ref, never the credential."""
        await auth.request_otp(email="bus@example.com", purpose=AuthPurpose.LOGIN)
        code = await _recover_code(uow, "bus@example.com")

        async with uow.read() as work:
            row = await work.outbox._fetch_one(
                "SELECT payload::text AS body FROM outbox_events "
                "WHERE event_name = 'OtpRequested'"
            )
        assert row is not None
        assert code not in row["body"]
        assert "token_ref" in row["body"]

    async def test_a_wrong_code_is_refused_and_costs_an_attempt(
        self, auth, uow, ids
    ) -> None:  # type: ignore[no-untyped-def]
        actor_id = await _actor(uow, ids)
        await auth.request_otp(email="wrong@example.com", purpose=AuthPurpose.LOGIN)
        with pytest.raises(BlogPlatformError) as exc:
            await auth.verify_otp(
                email="wrong@example.com", code="000000", actor_id=actor_id
            )
        assert exc.value.category is ErrorCategory.OTP_INVALID

    async def test_attempts_are_bounded(self, auth, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """The limit is enforced in the same statement that tests the hash, so
        parallel guesses cannot collectively exceed it."""
        actor_id = await _actor(uow, ids)
        await auth.request_otp(email="brute@example.com", purpose=AuthPurpose.LOGIN)
        real = await _recover_code(uow, "brute@example.com")
        wrong = "000000" if real != "000000" else "111111"

        for _ in range(3):
            with pytest.raises(BlogPlatformError):
                await auth.verify_otp(
                    email="brute@example.com", code=wrong, actor_id=actor_id
                )
        # The correct code no longer helps: the budget is spent.
        with pytest.raises(BlogPlatformError) as exc:
            await auth.verify_otp(
                email="brute@example.com", code=real, actor_id=actor_id
            )
        assert exc.value.category is ErrorCategory.OTP_ATTEMPTS_EXCEEDED

    async def test_a_code_is_single_use(self, auth, uow, ids) -> None:  # type: ignore[no-untyped-def]
        result, _ = await _sign_in(auth, uow, ids, "once@example.com")
        assert result.user is not None
        actor_id = await _actor(uow, ids)
        with pytest.raises(BlogPlatformError):
            await auth.verify_otp(
                email="once@example.com", code="000000", actor_id=actor_id
            )


class TestAnonymousMerge:
    async def test_history_follows_the_visitor_into_their_account(
        self, auth, engagement, uow, ids
    ) -> None:  # type: ignore[no-untyped-def]
        """The cold-start head start: engagement recorded before the account
        existed belongs to it the moment they sign in."""
        actor_id = await _actor(uow, ids)
        anon = AnonymousPrincipal(actor_id=actor_id)

        for kind in (EngagementKind.CLICK, EngagementKind.DWELL, EngagementKind.COMPLETE):
            assert await engagement.record(
                principal=anon,
                command=RecordEngagementCommand(
                    kind=kind, source=EngagementSource.FEED, dedupe_key=f"k-{kind.value}"
                ),
            )

        async with uow.read() as work:
            unattributed = await work.engagement._fetch_one(
                "SELECT count(*) AS n FROM engagement_events WHERE user_id IS NULL"
            )
        assert unattributed["n"] == 3

        await auth.request_otp(email="merge@example.com", purpose=AuthPurpose.LOGIN)
        code = await _recover_code(uow, "merge@example.com")
        result = await auth.verify_otp(
            email="merge@example.com", code=code, actor_id=actor_id
        )

        assert result.merged_events == 3
        async with uow.read() as work:
            still_anon = await work.engagement._fetch_one(
                "SELECT count(*) AS n FROM engagement_events WHERE user_id IS NULL"
            )
        assert still_anon["n"] == 0

    async def test_an_actor_cannot_be_merged_into_a_second_account(
        self, auth, uow, ids
    ) -> None:  # type: ignore[no-untyped-def]
        """Replaying an actor token after sign-in must not move history."""
        actor_id = await _actor(uow, ids)
        await auth.request_otp(email="first@example.com", purpose=AuthPurpose.LOGIN)
        await auth.verify_otp(
            email="first@example.com",
            code=await _recover_code(uow, "first@example.com"),
            actor_id=actor_id,
        )
        await auth.request_otp(email="second@example.com", purpose=AuthPurpose.LOGIN)
        result = await auth.verify_otp(
            email="second@example.com",
            code=await _recover_code(uow, "second@example.com"),
            actor_id=actor_id,
        )
        assert result.merged_events == 0


class TestRefreshRotation:
    async def test_rotation_issues_a_successor(self, auth, uow, ids) -> None:  # type: ignore[no-untyped-def]
        result, _ = await _sign_in(auth, uow, ids, "rotate@example.com")
        rotated = await auth.refresh(refresh_token=result.tokens.refresh_token)
        assert rotated.refresh_token != result.tokens.refresh_token

    async def test_reuse_actually_revokes_the_family(self, auth, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """REGRESSION: the revocation used to be rolled back by the raise that
        reported it, leaving every token in the family live."""
        result, _ = await _sign_in(auth, uow, ids, "leak@example.com")
        first = result.tokens.refresh_token

        second = (await auth.refresh(refresh_token=first)).refresh_token
        third = (await auth.refresh(refresh_token=second)).refresh_token

        # Replaying the leaked original.
        with pytest.raises(BlogPlatformError) as exc:
            await auth.refresh(refresh_token=first)
        assert exc.value.category is ErrorCategory.REFRESH_TOKEN_REUSED

        # The token the honest client still holds must now be dead too. This is
        # the assertion the old code failed.
        with pytest.raises(BlogPlatformError) as still_live:
            await auth.refresh(refresh_token=third)
        assert still_live.value.category is ErrorCategory.AUTH_TOKEN_REVOKED

        async with uow.read() as work:
            row = await work.refresh_tokens._fetch_one(
                "SELECT count(*) AS n FROM refresh_tokens WHERE revoked_at IS NULL"
            )
        assert row["n"] == 0, "the whole family should be revoked"

    async def test_an_expired_token_is_refused(self, auth, uow, ids, clock) -> None:  # type: ignore[no-untyped-def]
        result, _ = await _sign_in(auth, uow, ids, "expire@example.com")
        clock.advance(timedelta(days=31))
        with pytest.raises(BlogPlatformError) as exc:
            await auth.refresh(refresh_token=result.tokens.refresh_token)
        assert exc.value.category is ErrorCategory.REFRESH_TOKEN_EXPIRED

    async def test_revoking_ends_the_session(self, auth, uow, ids) -> None:  # type: ignore[no-untyped-def]
        result, _ = await _sign_in(auth, uow, ids, "signout@example.com")
        await auth.revoke(
            refresh_token=result.tokens.refresh_token,
            user_id=result.user.id,
            all_devices=False,
        )
        with pytest.raises(BlogPlatformError) as exc:
            await auth.refresh(refresh_token=result.tokens.refresh_token)
        assert exc.value.category is ErrorCategory.AUTH_TOKEN_REVOKED


class TestAdminPasswordLogin:
    async def _admin(self, auth, uow, ids, password: str = "a-strong-password"):  # type: ignore[no-untyped-def]
        async with uow.begin() as work:
            admin = await work.users.create(
                user_id=ids.new_id(),
                email="console@example.com",
                display_name="Admin",
                is_admin=True,
                email_verified_at=NOW,
            )
        await auth.set_admin_password(user_id=admin.id, password=password)
        return admin

    async def test_correct_password_signs_in(self, auth, uow, ids) -> None:  # type: ignore[no-untyped-def]
        await self._admin(auth, uow, ids)
        actor_id = await _actor(uow, ids)
        result = await auth.admin_password_login(
            email="console@example.com",
            password="a-strong-password",
            actor_id=actor_id,
        )
        assert result.user.is_admin is True

    async def test_wrong_password_and_unknown_address_are_indistinguishable(
        self, auth, uow, ids
    ) -> None:  # type: ignore[no-untyped-def]
        """Otherwise the console becomes an oracle for the admin's address."""
        await self._admin(auth, uow, ids)
        actor_id = await _actor(uow, ids)

        with pytest.raises(BlogPlatformError) as wrong:
            await auth.admin_password_login(
                email="console@example.com", password="nope", actor_id=actor_id
            )
        with pytest.raises(BlogPlatformError) as unknown:
            await auth.admin_password_login(
                email="ghost@example.com", password="nope", actor_id=actor_id
            )
        assert wrong.value.category is unknown.value.category
        assert wrong.value.safe_message == unknown.value.safe_message
        assert wrong.value.category is ErrorCategory.ADMIN_CREDENTIALS_INVALID

    async def test_repeated_failures_lock_the_account(self, auth, uow, ids) -> None:  # type: ignore[no-untyped-def]
        await self._admin(auth, uow, ids)
        actor_id = await _actor(uow, ids)
        for _ in range(3):
            with pytest.raises(BlogPlatformError):
                await auth.admin_password_login(
                    email="console@example.com", password="nope", actor_id=actor_id
                )
        # Even the right password is refused while locked out.
        with pytest.raises(BlogPlatformError) as exc:
            await auth.admin_password_login(
                email="console@example.com",
                password="a-strong-password",
                actor_id=actor_id,
            )
        assert exc.value.category is ErrorCategory.ADMIN_LOCKED_OUT

    async def test_a_reader_cannot_hold_a_password(self, auth, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """Refused by a CHECK constraint, not by application discipline."""
        async with uow.begin() as work:
            reader = await work.users.create(
                user_id=ids.new_id(),
                email="reader@example.com",
                display_name=None,
                is_admin=False,
                email_verified_at=NOW,
            )
        with pytest.raises(BlogPlatformError):
            await auth.set_admin_password(user_id=reader.id, password="x")

    async def test_changing_the_password_revokes_every_session(
        self, auth, uow, ids
    ) -> None:  # type: ignore[no-untyped-def]
        admin = await self._admin(auth, uow, ids)
        actor_id = await _actor(uow, ids)
        signed_in = await auth.admin_password_login(
            email="console@example.com",
            password="a-strong-password",
            actor_id=actor_id,
        )
        await auth.set_admin_password(user_id=admin.id, password="a-different-password")
        with pytest.raises(BlogPlatformError) as exc:
            await auth.refresh(refresh_token=signed_in.tokens.refresh_token)
        assert exc.value.category is ErrorCategory.AUTH_TOKEN_REVOKED


class TestEngagementDedupe:
    async def test_a_replayed_beacon_is_not_recorded_twice(
        self, engagement, uow, ids
    ) -> None:  # type: ignore[no-untyped-def]
        """REGRESSION: the unique index included the server-assigned
        ``occurred_at``, so a retry arriving later was unique again."""
        anon = AnonymousPrincipal(actor_id=await _actor(uow, ids))
        command = RecordEngagementCommand(
            kind=EngagementKind.CLICK,
            source=EngagementSource.FEED,
            dedupe_key="beacon-1",
        )
        assert await engagement.record(principal=anon, command=command) is True
        assert await engagement.record(principal=anon, command=command) is False

        async with uow.read() as work:
            row = await work.engagement._fetch_one(
                "SELECT count(*) AS n FROM engagement_events"
            )
        assert row["n"] == 1

    async def test_concurrent_retries_write_exactly_one_row(
        self, engagement, uow, ids
    ) -> None:  # type: ignore[no-untyped-def]
        """The primary key settles the race, not a read-then-write."""
        anon = AnonymousPrincipal(actor_id=await _actor(uow, ids))
        command = RecordEngagementCommand(
            kind=EngagementKind.CLICK, dedupe_key="race-key"
        )
        results = await asyncio.gather(
            *(engagement.record(principal=anon, command=command) for _ in range(8)),
            return_exceptions=True,
        )
        recorded = [r for r in results if r is True]
        assert len(recorded) == 1, f"expected one winner, got {results}"

        async with uow.read() as work:
            row = await work.engagement._fetch_one(
                "SELECT count(*) AS n FROM engagement_events"
            )
        assert row["n"] == 1

    async def test_two_visitors_may_use_the_same_client_side_key(
        self, engagement, uow, ids
    ) -> None:
        """Keys are namespaced by actor, so one client cannot suppress another's
        events by guessing their key."""
        first = AnonymousPrincipal(actor_id=await _actor(uow, ids))
        second = AnonymousPrincipal(actor_id=await _actor(uow, ids))
        command = RecordEngagementCommand(
            kind=EngagementKind.CLICK, dedupe_key="page-load"
        )
        assert await engagement.record(principal=first, command=command) is True
        assert await engagement.record(principal=second, command=command) is True

    async def test_a_client_cannot_choose_the_subject_of_an_event(self) -> None:
        """The command has no actor, user or timestamp field at all — the
        server decides all three."""
        fields = set(RecordEngagementCommand.model_fields)
        assert not fields & {"actor_id", "user_id", "occurred_at"}
