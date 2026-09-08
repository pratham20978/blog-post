"""Delivery of the sign-in code.

The bug worth guarding against is not "email fails" — it is email failing
*quietly*. ``request_otp`` returning success while nothing was sent produces a
clean 200, a clean log, and a user waiting forever for a code. Every test here
is about that failure being impossible to reach.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

import pytest

from blogs.adapters.email import InMemoryEmailSender, UnconfiguredEmailSender
from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import AuthPurpose
from blogs.core.errors import BlogPlatformError
from blogs.services.auth_service import AuthService, OtpSettings

pytestmark = pytest.mark.asyncio

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=UTC)


def _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, email, **otp):  # type: ignore[no-untyped-def]
    otp_values = {
        "length": 6,
        "ttl_seconds": 600,
        "max_attempts": 3,
        "resend_cooldown_seconds": 0,
        "log_codes": False,
    }
    otp_values.update(otp)
    return AuthService(
        uow=uow,
        email=email,
        clock=clock,
        ids=ids,
        hasher=hasher,
        access_tokens=access_tokens,
        actor_tokens=actor_tokens,
        passwords=passwords,
        otp_settings=OtpSettings(**otp_values),
        refresh_ttl_seconds=2_592_000,
        access_ttl_seconds=900,
    )


def _code_from(message) -> str:  # type: ignore[no-untyped-def]
    match = re.search(r"\b\d{6}\b", message.text)
    assert match is not None
    return match.group(0)


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
        code = _code_from(message)

        result = await auth.verify_otp(
            email="reader@example.com",
            code=code,
            actor_id=ids.new_id(),
            purpose=AuthPurpose.LOGIN,
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
        code = _code_from(mail.outbox[-1])
        # Only the hash is stored, so the plaintext must appear nowhere in the row.
        assert code not in repr(challenge)

    async def test_both_parts_carry_the_code(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        mail = InMemoryEmailSender()
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)
        await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)

        message = mail.outbox[-1]
        code = _code_from(message)
        # A text part is mandatory: an HTML-only message is unreadable in a
        # plain-text client and scores badly with spam filters.
        assert code in message.text
        assert message.html and code in message.html

    @pytest.mark.parametrize(
        ("purpose", "subject", "instruction"),
        [
            (
                AuthPurpose.LOGIN,
                "Your Canery sign-in code",
                "Use this code to sign in to Canery:",
            ),
            (
                AuthPurpose.SIGNUP,
                "Your Canery signup code",
                "Use this code to create your Canery account:",
            ),
        ],
    )
    async def test_each_purpose_has_distinct_multipart_copy(  # type: ignore[no-untyped-def]
        self,
        uow,
        clock,
        ids,
        hasher,
        access_tokens,
        actor_tokens,
        passwords,
        purpose,
        subject,
        instruction,
    ):
        mail = InMemoryEmailSender()
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)

        await auth.request_otp(email="reader@example.com", purpose=purpose)

        message = mail.outbox[-1]
        assert message.subject == subject
        assert instruction in message.text
        assert message.html and instruction in message.html
        assert _code_from(message) not in message.subject

    async def test_a_code_only_verifies_for_the_purpose_that_issued_it(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        mail = InMemoryEmailSender()
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)
        await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.SIGNUP)
        code = _code_from(mail.outbox[-1])

        with pytest.raises(BlogPlatformError) as caught:
            await auth.verify_otp(
                email="reader@example.com",
                code=code,
                actor_id=ids.new_id(),
                purpose=AuthPurpose.LOGIN,
            )
        assert caught.value.category is ErrorCategory.OTP_INVALID

        result = await auth.verify_otp(
            email="reader@example.com",
            code=code,
            actor_id=ids.new_id(),
            purpose=AuthPurpose.SIGNUP,
        )
        assert result.created is True

    @pytest.mark.parametrize("purpose", list(AuthPurpose))
    async def test_both_purposes_keep_unified_account_creation(  # type: ignore[no-untyped-def]
        self,
        uow,
        clock,
        ids,
        hasher,
        access_tokens,
        actor_tokens,
        passwords,
        purpose,
    ):
        mail = InMemoryEmailSender()
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)
        await auth.request_otp(email="new@example.com", purpose=purpose)

        result = await auth.verify_otp(
            email="new@example.com",
            code=_code_from(mail.outbox[-1]),
            actor_id=ids.new_id(),
            purpose=purpose,
        )

        assert result.created is True
        assert result.user.email == "new@example.com"

    async def test_an_expired_emailed_code_is_refused(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        mail = InMemoryEmailSender()
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)
        await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)
        code = _code_from(mail.outbox[-1])
        clock.advance(timedelta(minutes=11))

        with pytest.raises(BlogPlatformError) as caught:
            await auth.verify_otp(
                email="reader@example.com",
                code=code,
                actor_id=ids.new_id(),
                purpose=AuthPurpose.LOGIN,
            )
        assert caught.value.category is ErrorCategory.OTP_EXPIRED

    async def test_resend_obeys_the_cooldown_then_issues_a_new_message(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords
    ):
        mail = InMemoryEmailSender()
        auth = _build(
            uow,
            clock,
            ids,
            hasher,
            access_tokens,
            actor_tokens,
            passwords,
            mail,
            resend_cooldown_seconds=60,
        )
        await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)

        with pytest.raises(BlogPlatformError) as caught:
            await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)
        assert caught.value.category is ErrorCategory.OTP_THROTTLED
        assert len(mail.outbox) == 1

        clock.advance(timedelta(seconds=61))
        await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)
        assert len(mail.outbox) == 2

    async def test_real_delivery_mode_does_not_log_the_code(  # type: ignore[no-untyped-def]
        self, uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, caplog
    ):
        mail = InMemoryEmailSender()
        auth = _build(uow, clock, ids, hasher, access_tokens, actor_tokens, passwords, mail)
        await auth.request_otp(email="reader@example.com", purpose=AuthPurpose.LOGIN)

        assert _code_from(mail.outbox[-1]) not in caplog.text

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
