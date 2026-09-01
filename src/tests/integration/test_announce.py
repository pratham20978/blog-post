"""Announcing a published article to a spreadsheet of addresses.

Runs against real Postgres and a real publish, because the two things most
worth proving are both about state: that a draft cannot be announced, and that
a partial failure is reported precisely enough to retry.
"""

from __future__ import annotations

import io

import pytest
from openpyxl import Workbook

from blogs.adapters.email import InMemoryEmailSender
from blogs.adapters.markdown.parser import MarkdownItParser
from blogs.contracts.blog import BlogStatus, PublishBlogCommand
from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import AnonymousPrincipal, UserPrincipal
from blogs.core.errors import BlogPlatformError
from blogs.services.announce_service import AnnounceService
from blogs.services.blog_service import BlogService
from blogs.services.policy import DefaultAuthorizationPolicy

pytestmark = pytest.mark.asyncio

ARTICLE = b"""---
title: "A Published Article"
summary: "Worth telling people about."
---

Body text.
"""


def addresses(*values: str) -> bytes:
    book = Workbook()
    active = book.active
    assert active is not None
    active.append(["Email"])
    for value in values:
        active.append([value])
    buffer = io.BytesIO()
    book.save(buffer)
    return buffer.getvalue()


@pytest.fixture
def blogs(uow, clock, ids, object_store):  # type: ignore[no-untyped-def]
    return BlogService(
        uow=uow,
        clock=clock,
        ids=ids,
        object_store=object_store,
        markdown=MarkdownItParser(max_bytes=1_000_000),
        policy=DefaultAuthorizationPolicy(),
        default_page_size=20,
        max_page_size=100,
    )


@pytest.fixture
def mail() -> InMemoryEmailSender:
    return InMemoryEmailSender()


@pytest.fixture
def announce(uow, mail):  # type: ignore[no-untyped-def]
    return AnnounceService(
        uow=uow,
        email=mail,
        policy=DefaultAuthorizationPolicy(),
        site_url="https://canerly.test/",
        max_recipients=100,
    )


async def _admin(uow, ids) -> UserPrincipal:  # type: ignore[no-untyped-def]
    async with uow.begin() as work:
        user = await work.users.create(
            user_id=ids.new_id(),
            email="admin@example.com",
            display_name="Admin",
            is_admin=True,
            email_verified_at=None,
        )
    return UserPrincipal(actor_id=ids.new_id(), user_id=user.id, is_admin=True)


async def _publish(blogs, admin, status=BlogStatus.PUBLISHED):  # type: ignore[no-untyped-def]
    result = await blogs.publish_from_markdown(
        principal=admin, source=ARTICLE, command=PublishBlogCommand(status=status)
    )
    return result.blog


class TestAnnounce:
    async def test_sends_one_message_per_recipient(self, uow, ids, blogs, announce, mail):  # type: ignore[no-untyped-def]
        admin = await _admin(uow, ids)
        blog = await _publish(blogs, admin)

        result = await announce.announce(
            principal=admin,
            blog_id=blog.id,
            sheet=addresses("a@example.com", "b@example.com", "c@example.com"),
        )

        assert result.sent == 3
        assert result.failed == 0
        assert len(mail.outbox) == 3
        # One address per message. A single message addressed to all three
        # would disclose the whole list to everyone on it.
        assert [m.to for m in mail.outbox] == [
            "a@example.com",
            "b@example.com",
            "c@example.com",
        ]

    async def test_the_link_is_absolute_and_points_at_the_site(  # type: ignore[no-untyped-def]
        self, uow, ids, blogs, announce, mail
    ):
        admin = await _admin(uow, ids)
        blog = await _publish(blogs, admin)
        await announce.announce(
            principal=admin, blog_id=blog.id, sheet=addresses("a@example.com")
        )

        message = mail.outbox[-1]
        # Not the API origin, and not a relative path — neither is clickable
        # from an inbox.
        assert f"https://canerly.test/blogs/{blog.slug}" in message.text
        assert message.html and f"https://canerly.test/blogs/{blog.slug}" in message.html

    async def test_a_draft_cannot_be_announced(self, uow, ids, blogs, announce, mail):  # type: ignore[no-untyped-def]
        admin = await _admin(uow, ids)
        draft = await _publish(blogs, admin, status=BlogStatus.DRAFT)

        # Announcing a draft would leak it, and every recipient would land on a
        # 404 — the link resolves only for published articles.
        with pytest.raises(BlogPlatformError) as caught:
            await announce.announce(
                principal=admin, blog_id=draft.id, sheet=addresses("a@example.com")
            )
        assert caught.value.category is ErrorCategory.BLOG_NOT_PUBLISHED
        assert mail.outbox == []

    async def test_a_partial_failure_names_the_addresses_to_retry(  # type: ignore[no-untyped-def]
        self, uow, ids, blogs, announce, mail
    ):
        admin = await _admin(uow, ids)
        blog = await _publish(blogs, admin)
        mail.refuse.add("bounces@example.com")

        result = await announce.announce(
            principal=admin,
            blog_id=blog.id,
            sheet=addresses("a@example.com", "bounces@example.com", "c@example.com"),
        )

        # The other two must still go out. One bad address in a list of
        # hundreds cannot be allowed to abandon the rest.
        assert result.sent == 2
        assert result.failed == 1
        assert result.failures == ("bounces@example.com",)

    async def test_an_empty_sheet_is_refused(self, uow, ids, blogs, announce):  # type: ignore[no-untyped-def]
        admin = await _admin(uow, ids)
        blog = await _publish(blogs, admin)

        with pytest.raises(BlogPlatformError) as caught:
            await announce.announce(
                principal=admin, blog_id=blog.id, sheet=addresses()
            )
        assert caught.value.category is ErrorCategory.REQUEST_INVALID

    async def test_a_reader_cannot_announce(self, uow, ids, blogs, announce, mail):  # type: ignore[no-untyped-def]
        admin = await _admin(uow, ids)
        blog = await _publish(blogs, admin)

        # Same authority as publishing: mailing thousands of people is at least
        # as consequential as putting the article up.
        with pytest.raises(BlogPlatformError):
            await announce.announce(
                principal=AnonymousPrincipal(actor_id=ids.new_id()),
                blog_id=blog.id,
                sheet=addresses("a@example.com"),
            )
        assert mail.outbox == []

    async def test_an_unknown_article_is_not_found(self, uow, ids, announce):  # type: ignore[no-untyped-def]
        admin = await _admin(uow, ids)
        with pytest.raises(BlogPlatformError) as caught:
            await announce.announce(
                principal=admin,
                blog_id=ids.new_id(),
                sheet=addresses("a@example.com"),
            )
        assert caught.value.category is ErrorCategory.BLOG_NOT_FOUND
