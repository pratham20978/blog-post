"""Resend, over its HTTP API.

Chosen for one property that matters while F2 is unbuilt: ``onboarding@resend.dev``
sends to the account owner's own inbox with no DNS, no domain verification and
no warm-up. The whole OTP path is testable the moment an API key exists, and
moving to a real sending domain later is a change to ``BLOGS_EMAIL_FROM`` alone.

Two things here are deliberate rather than incidental:

* **One message per recipient, always.** The batch endpoint takes an array of
  independent messages, not one message with many addresses, so nobody on an
  announcement ever sees who else received it.
* **A provider refusal is data, not an exception.** One bad address in a
  three-hundred-address announcement must not abandon the other two hundred and
  ninety-nine. Only an unreachable provider raises.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from typing import Any

import httpx

from blogs.contracts.common import ErrorCategory
from blogs.core.errors import BlogPlatformError
from blogs.ports.services import EmailMessage, EmailResult

logger = logging.getLogger(__name__)

_API = "https://api.resend.com"

#: Resend's documented ceiling for one batch call.
_BATCH_LIMIT = 100

#: Batches are sent concurrently, but not unboundedly — a few hundred parallel
#: connections to one provider is how you get rate-limited rather than fast.
_MAX_CONCURRENT_BATCHES = 4


class ResendEmailSender:
    def __init__(
        self,
        *,
        api_key: str,
        sender: str,
        reply_to: str | None = None,
        timeout_s: float = 15.0,
    ) -> None:
        self._sender = sender
        self._reply_to = reply_to
        self._client = httpx.AsyncClient(
            base_url=_API,
            timeout=timeout_s,
            headers={
                "authorization": f"Bearer {api_key}",
                "content-type": "application/json",
            },
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    def _payload(self, message: EmailMessage) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "from": self._sender,
            # A one-element list, not a bare string: same shape for one
            # recipient as for many, so there is no second code path to get
            # wrong.
            "to": [message.to],
            "subject": message.subject,
            "text": message.text,
        }
        if message.html:
            payload["html"] = message.html
        if self._reply_to:
            payload["reply_to"] = self._reply_to
        return payload

    async def send(self, message: EmailMessage) -> EmailResult:
        try:
            response = await self._client.post("/emails", json=self._payload(message))
        except httpx.HTTPError as exc:
            # Unreachable provider. This one raises: the caller asked for a
            # single message and there is no partial outcome to report.
            logger.warning("email provider unreachable", extra={"error": str(exc)})
            raise BlogPlatformError(
                ErrorCategory.EMAIL_SEND_FAILED, safe_details={"reason": "UNREACHABLE"}
            ) from exc

        return self._result_for(message.to, response)

    async def send_many(
        self, messages: Sequence[EmailMessage]
    ) -> tuple[EmailResult, ...]:
        if not messages:
            return ()

        chunks = [
            list(messages[i : i + _BATCH_LIMIT])
            for i in range(0, len(messages), _BATCH_LIMIT)
        ]
        limit = asyncio.Semaphore(_MAX_CONCURRENT_BATCHES)

        async def run(chunk: list[EmailMessage]) -> list[EmailResult]:
            async with limit:
                return await self._send_batch(chunk)

        # `gather` rather than a loop: a three-hundred-address announcement is
        # three sequential round trips instead of three hundred.
        batches = await asyncio.gather(*(run(chunk) for chunk in chunks))
        return tuple(result for batch in batches for result in batch)

    async def _send_batch(self, chunk: list[EmailMessage]) -> list[EmailResult]:
        try:
            response = await self._client.post(
                "/emails/batch", json=[self._payload(m) for m in chunk]
            )
        except httpx.HTTPError as exc:
            # Reported per address rather than raised. The caller is sending to
            # many people and needs to know exactly who missed out, so it can
            # retry those and only those.
            logger.warning(
                "email batch unreachable",
                extra={"error": str(exc), "recipients": len(chunk)},
            )
            return [EmailResult(to=m.to, sent=False, detail="UNREACHABLE") for m in chunk]

        if response.status_code >= 400:
            reason = _reason_from(response)
            logger.warning(
                "email batch refused",
                extra={"status": response.status_code, "recipients": len(chunk)},
            )
            return [EmailResult(to=m.to, sent=False, detail=reason) for m in chunk]

        # Resend answers `{"data": [{"id": ...}, ...]}` in request order. If the
        # shape is not what we expect, the mail may well have been sent — so
        # this reports success without an id rather than inventing a failure
        # that would prompt a duplicate send.
        ids = _ids_from(response)
        return [
            EmailResult(to=m.to, sent=True, detail=ids[i] if i < len(ids) else None)
            for i, m in enumerate(chunk)
        ]

    def _result_for(self, to: str, response: httpx.Response) -> EmailResult:
        if response.status_code >= 400:
            return EmailResult(to=to, sent=False, detail=_reason_from(response))
        ids = _ids_from(response)
        return EmailResult(to=to, sent=True, detail=ids[0] if ids else None)


def _reason_from(response: httpx.Response) -> str:
    """A short, loggable reason — never the provider's full body.

    Provider errors quote the payload back, which for us includes recipient
    addresses. Those belong in neither a log line nor an API response.
    """
    try:
        body = response.json()
        name = body.get("name") or body.get("error") or ""
    except ValueError:
        name = ""
    return f"HTTP_{response.status_code}{f'_{name}' if name else ''}"[:64]


def _ids_from(response: httpx.Response) -> list[str]:
    try:
        body = response.json()
    except ValueError:
        return []
    if isinstance(body, dict):
        data = body.get("data")
        if isinstance(data, list):
            return [str(item.get("id")) for item in data if isinstance(item, dict)]
        if isinstance(body.get("id"), str):
            return [body["id"]]
    return []
