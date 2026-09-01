"""The adapter for a deployment with no email provider.

It refuses rather than pretending. A null object that accepted every message
and dropped it would make ``request_otp`` answer "a code is on its way" when
nothing was sent, and the failure would surface as users reporting that sign-in
is broken — with a clean log and a 200 response to argue otherwise.

Refusing costs one error category and turns an invisible fault into a visible
one at the moment of the mistake.
"""

from __future__ import annotations

from collections.abc import Sequence

from blogs.contracts.common import ErrorCategory
from blogs.core.errors import BlogPlatformError
from blogs.ports.services import EmailMessage, EmailResult


class UnconfiguredEmailSender:
    async def send(self, message: EmailMessage) -> EmailResult:
        raise BlogPlatformError(
            ErrorCategory.EMAIL_NOT_CONFIGURED,
            safe_details={"reason": "NO_PROVIDER"},
        )

    async def send_many(
        self, messages: Sequence[EmailMessage]
    ) -> tuple[EmailResult, ...]:
        raise BlogPlatformError(
            ErrorCategory.EMAIL_NOT_CONFIGURED,
            safe_details={"reason": "NO_PROVIDER", "recipients": len(messages)},
        )
