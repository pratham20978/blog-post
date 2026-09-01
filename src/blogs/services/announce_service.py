"""Announcing a published article to a list of addresses.

One-shot by design, per the decision on record: the spreadsheet is read, the
mail goes out, and nothing is stored. No subscriber table, no unsubscribe
state, no send history.

That is a deliberate trade and it has a cost worth stating plainly, because it
is not visible from the code: **an unsubscribe request cannot be honoured by
this system.** There is nowhere to record it, so the same address will be
included again the next time the same sheet is uploaded. Whoever maintains the
sheet has to remove them by hand. If announcements become a regular thing
rather than an occasional one, that stops being acceptable and the subscriber
table is the fix.

What this service *does* guarantee:

* only a **published** article can be announced — announcing a draft would leak
  it, and the link would 404 for every recipient
* **one message per recipient**, so nobody learns who else is on the list
* a **partial failure is reported, not hidden** — the caller gets the count and
  the failed addresses back, so a retry can target only those
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from blogs.adapters.email.recipients import read_recipients
from blogs.contracts.blog import BlogStatus
from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import Principal, UserPrincipal
from blogs.core.errors import raise_error
from blogs.ports.services import AuthorizationPolicy, EmailMessage, EmailSender
from blogs.ports.uow import UnitOfWorkFactory
from blogs.services.policy import require

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AnnounceResult:
    blog_id: str
    slug: str
    sent: int
    failed: int
    #: Non-address cells in the sheet, and repeated addresses. Surfaced so a
    #: sheet with the wrong column is obvious from the response.
    skipped_cells: int
    duplicates: int
    #: Which addresses did not get through, so a retry can target them. Capped:
    #: a wholesale provider outage should not return five thousand strings.
    failures: tuple[str, ...]


#: How many failed addresses to name in the response.
_MAX_REPORTED_FAILURES = 50


class AnnounceService:
    def __init__(
        self,
        *,
        uow: UnitOfWorkFactory,
        email: EmailSender,
        policy: AuthorizationPolicy,
        site_url: str,
        max_recipients: int,
    ) -> None:
        self._uow = uow
        self._email = email
        self._policy = policy
        self._site_url = site_url.rstrip("/")
        self._max_recipients = max_recipients

    async def announce(
        self,
        *,
        principal: Principal,
        blog_id: str,
        sheet: bytes,
        correlation_id: str | None = None,
    ) -> AnnounceResult:
        # Same permission as publishing: telling several thousand people about
        # an article is at least as consequential as putting it up.
        require(
            self._policy.can_publish(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)

        async with self._uow.read() as uow:
            blog = await uow.blogs.get(blog_id)

        if blog is None:
            raise_error(ErrorCategory.BLOG_NOT_FOUND, correlation_id=correlation_id)

        if blog.status is not BlogStatus.PUBLISHED:
            # A draft has no public URL. Every recipient would get a 404, and
            # the article would be disclosed early to anyone who looked.
            raise_error(
                ErrorCategory.BLOG_NOT_PUBLISHED,
                correlation_id=correlation_id,
                safe_details={"status": blog.status.value},
            )

        parsed = read_recipients(sheet, limit=self._max_recipients)
        if not parsed.addresses:
            raise_error(
                ErrorCategory.REQUEST_INVALID,
                correlation_id=correlation_id,
                safe_message="No email addresses were found in that sheet.",
                safe_details={"cells_examined": parsed.skipped},
            )

        url = f"{self._site_url}/blogs/{blog.slug}"
        summary = blog.summary or ""

        messages = [
            EmailMessage(
                to=address,
                subject=blog.title,
                text=_TEXT.format(title=blog.title, summary=summary, url=url),
                html=_HTML.format(title=blog.title, summary=summary, url=url),
            )
            for address in parsed.addresses
        ]

        results = await self._email.send_many(messages)

        failures = tuple(r.to for r in results if not r.sent)
        sent = sum(1 for r in results if r.sent)

        logger.info(
            "announcement sent",
            extra={
                "blog_id": blog.id,
                "slug": blog.slug,
                "sent": sent,
                "failed": len(failures),
                "actor": principal.user_id,
            },
        )

        return AnnounceResult(
            blog_id=blog.id,
            slug=blog.slug,
            sent=sent,
            failed=len(failures),
            skipped_cells=parsed.skipped,
            duplicates=parsed.duplicates,
            failures=failures[:_MAX_REPORTED_FAILURES],
        )


_TEXT = """{title}

{summary}

Read it: {url}
"""

_HTML = """\
<div style="font-family:system-ui,-apple-system,sans-serif;font-size:15px;
            color:#0a0a0a;line-height:1.6;max-width:34em">
  <h1 style="font-size:24px;font-weight:600;margin:0 0 12px">{title}</h1>
  <p style="color:#6b6b6b;margin:0 0 20px">{summary}</p>
  <p><a href="{url}" style="color:#0a0a0a">Read it &rarr;</a></p>
</div>
"""


__all__ = ["AnnounceResult", "AnnounceService"]
