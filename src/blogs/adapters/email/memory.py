"""An in-memory email sender, for tests.

Not a mock. It implements the port with the same semantics the real adapter
has — including the one that is easy to get wrong, where a provider refusal is
reported per recipient rather than raised — so a test exercises the caller's
real branching instead of asserting that a method was called.

``outbox`` is the thing tests read. ``fail_next`` and ``refuse`` exist so the
unhappy paths are reachable without patching anything.
"""

from __future__ import annotations

from collections.abc import Sequence

from blogs.contracts.common import ErrorCategory
from blogs.core.errors import BlogPlatformError
from blogs.ports.services import EmailMessage, EmailResult


class InMemoryEmailSender:
    def __init__(self) -> None:
        self.outbox: list[EmailMessage] = []
        #: Raise ``EMAIL_SEND_FAILED`` on the next call, then reset.
        self.fail_next = False
        #: Addresses the "provider" rejects. Reported in the result, never
        #: raised — one bad address must not sink a batch.
        self.refuse: set[str] = set()

    def _guard(self) -> None:
        if self.fail_next:
            self.fail_next = False
            raise BlogPlatformError(
                ErrorCategory.EMAIL_SEND_FAILED, safe_details={"reason": "UNREACHABLE"}
            )

    def _deliver(self, message: EmailMessage) -> EmailResult:
        if message.to in self.refuse:
            return EmailResult(to=message.to, sent=False, detail="HTTP_422_refused")
        self.outbox.append(message)
        return EmailResult(to=message.to, sent=True, detail=f"test-{len(self.outbox)}")

    async def send(self, message: EmailMessage) -> EmailResult:
        self._guard()
        return self._deliver(message)

    async def send_many(
        self, messages: Sequence[EmailMessage]
    ) -> tuple[EmailResult, ...]:
        self._guard()
        return tuple(self._deliver(m) for m in messages)

    # ── Test helpers ────────────────────────────────────────────────────────

    def last_to(self, address: str) -> EmailMessage | None:
        for message in reversed(self.outbox):
            if message.to == address:
                return message
        return None
