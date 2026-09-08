"""The Resend adapter's HTTP boundary, without calling the real provider."""

from __future__ import annotations

import json

import httpx
import pytest

from blogs.adapters.email import ResendEmailSender
from blogs.contracts.common import ErrorCategory
from blogs.core.errors import BlogPlatformError
from blogs.ports.services import EmailMessage

pytestmark = pytest.mark.asyncio


async def test_send_uses_the_verified_sender_and_exact_recipient() -> None:
    requests: list[httpx.Request] = []

    async def accept(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"id": "email_123"})

    sender = ResendEmailSender(
        api_key="re_secret",
        sender="Canerly <auth@canery.in>",
        transport=httpx.MockTransport(accept),
    )
    try:
        result = await sender.send(
            EmailMessage(
                to="reader@example.com",
                subject="Your Canery sign-in code",
                text="Your code is 123456",
                html="<p>Your code is <strong>123456</strong></p>",
            )
        )
    finally:
        await sender.aclose()

    assert result.sent is True
    assert result.detail == "email_123"
    assert len(requests) == 1
    assert requests[0].headers["authorization"] == "Bearer re_secret"
    payload = json.loads(requests[0].content)
    assert payload == {
        "from": "Canerly <auth@canery.in>",
        "to": ["reader@example.com"],
        "subject": "Your Canery sign-in code",
        "text": "Your code is 123456",
        "html": "<p>Your code is <strong>123456</strong></p>",
    }


async def test_provider_refusal_is_returned_without_exposing_its_body() -> None:
    async def refuse(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422,
            json={"name": "validation_error", "message": "reader@example.com was refused"},
        )

    sender = ResendEmailSender(
        api_key="re_secret",
        sender="Canerly <auth@canery.in>",
        transport=httpx.MockTransport(refuse),
    )
    try:
        result = await sender.send(
            EmailMessage(to="reader@example.com", subject="Code", text="123456")
        )
    finally:
        await sender.aclose()

    assert result.sent is False
    assert result.detail == "HTTP_422_validation_error"
    assert "reader@example.com" not in (result.detail or "")


async def test_provider_timeout_becomes_a_safe_domain_error() -> None:
    async def timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("provider timed out", request=request)

    sender = ResendEmailSender(
        api_key="re_secret",
        sender="Canerly <auth@canery.in>",
        transport=httpx.MockTransport(timeout),
    )
    try:
        with pytest.raises(BlogPlatformError) as caught:
            await sender.send(
                EmailMessage(to="reader@example.com", subject="Code", text="123456")
            )
    finally:
        await sender.aclose()

    assert caught.value.category is ErrorCategory.EMAIL_SEND_FAILED
    assert caught.value.safe_details == {"reason": "UNREACHABLE"}
