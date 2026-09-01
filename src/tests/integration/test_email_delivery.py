"""Delivery of the sign-in code.

The bug worth guarding against is not "email fails" — it is email failing
*quietly*. ``request_otp`` returning success while nothing was sent produces a
clean 200, a clean log, and a user waiting forever for a code. Every test here
is about that failure being impossible to reach.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from blogs.adapters.email import InMemoryEmailSender, UnconfiguredEmailSender
from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import AuthPurpose
from blogs.core.errors import BlogPlatformError
from blogs.services.auth_service import AuthService, OtpSettings

pytestmark = pytest.mark.asyncio

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=UTC)


def _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, email, **otp):  # type: ignore[no-untyped-def]
    return AuthService(
        uow=uow,
        email=email,
        clock=clock,
        ids=ids,
        hasher=hasher,
        access_tokens=access_tokens,
        actor_tokens=actor_tokens,
        passwords=passwords,
        otp_settings=OtpSettings(
            length=6,
            ttl_seconds=600,
            max_attempts=3,
            resend_cooldown_seconds=0,
            log_codes=False,
            **otp,
        ),
        refresh_ttl_seconds=2_592_000,
        access_ttl_seconds=900,
    )


class TestOtpDelivery:
    async def test_the_code_is_emailed_and_actually_works(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        mail = InMemoryEmailSender()
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)

        await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)

        message = mail.last_to("reader@example.com")
        assert message is not None

        # The code in the email must be the code the challenge accepts. Asserting
        # only that *an* email was sent would pass while mailing the wrong digits.
        code = "".join(c for c in message.subject if c.isdigit())
        assert len(code) == 6

        result = await auth.verify_otp(
            email="reader@example.com", code=code, actor_id=ids.new_id()
        )
        assert result.tokens.access_token

    async def test_the_code_is_never_in_the_stored_challenge(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        mail = InMemoryEmailSender()
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)
        await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)

        async with uow.read() as work:
            challenge = await work.otp.latest_live("reader@example.com", AuthPurpose.LOGIN)

        assert challenge is not None
        code = "".join(c for c in mail.outbox[-1].subject if c.isdigit())
        # Only the hash is stored, so the plaintext must appear nowhere in the row.
        assert code not in repr(challenge)

    async def test_both_parts_carry_the_code(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        mail = InMemoryEmailSender()
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)
        await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)

        message = mail.outbox[-1]
        code = "".join(c for c in message.subject if c.isdigit())
        # A text part is mandatory: an HTML-only message is unreadable in a
        # plain-text client and scores badly with spam filters.
        assert code in message.text
        assert message.html and code in message.html

    async def test_an_unreachable_provider_is_reported_not_swallowed(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        mail = InMemoryEmailSender()
        mail.fail_next = True
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)

        with pytest.raises(BlogPlatformError) as caught:
            await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)
        assert caught.value.category is ErrorCategory.EMAIL_SEND_FAILED

    async def test_a_refused_address_is_reported_not_swallowed(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        mail = InMemoryEmailSender()
        mail.refuse.add("bounces@example.com")
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)

        # The provider answered, and said no. That is still a failure to deliver
        # and the caller must not be told a code is on its way.
        with pytest.raises(BlogPlatformError) as caught:
            await auth.request_otp(email="bounces@example.com", purpose=AuthPurpose.LOGIN)
        assert caught.value.category is ErrorCategory.EMAIL_SEND_FAILED

    async def test_no_provider_at_all_is_refused_when_codes_are_not_logged(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        auth = _build(
            uow, clock, ids, hasher, access_tokens, actor_tokens, passwords,
            UnconfiguredEmailSender(),
        )

        with pytest.raises(BlogPlatformError) as caught:
            await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)
        assert caught.value.category is ErrorCategory.EMAIL_NOT_CONFIGURED

    async def test_no_provider_is_tolerated_when_codes_are_logged(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        # The development path: the log line is the delivery channel, so a
        # missing provider must not break local sign-in.
        auth = AuthService(
            uow=uow,
            email=UnconfiguredEmailSender(),
            clock=clock,
            ids=ids,
            hasher=hasher,
            access_tokens=access_tokens,
            actor_tokens=actor_tokens,
            passwords=passwords,
            otp_settings=OtpSettings(
                length=6, ttl_seconds=600, max_attempts=3,
                resend_cooldown_seconds=0, log_codes=True,
            ),
            refresh_ttl_seconds=2_592_000,
            access_ttl_seconds=900,
        )

        issued = await auth.request_otp(
            email="reader@example.com", purpose=AuthPurpose.LOGIN
        )
        assert issued.token_ref
