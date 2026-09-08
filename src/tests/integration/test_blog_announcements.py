"""Campaign staging, recipient eligibility, preferences, and first-publish events."""

from __future__ import annotations

from datetime import timedelta

import pytest

from blogs.adapters.markdown.parser import MarkdownItParser
from blogs.adapters.objectstore.memory_store import InMemoryObjectStore
from blogs.contracts.blog import BlogStatus, PublishBlogCommand, UpdateBlogPatch
from blogs.contracts.events import BlogPublished
from blogs.contracts.identity import UserPrincipal, UserStatus
from blogs.services.announcement_service import AnnouncementService
from blogs.services.blog_service import BlogService
from blogs.services.policy import DefaultAuthorizationPolicy

pytestmark = pytest.mark.asyncio


async def _admin(uow, ids, clock) -> UserPrincipal:  # type: ignore[no-untyped-def]
    actor_id = ids.new_id()
    async with uow.begin() as work:
        user = await work.users.create(
            user_id=ids.new_id(),
            email="admin@example.com",
            display_name="Admin",
            is_admin=True,
            email_verified_at=clock.now(),
        )
        await work.actors.create(actor_id=actor_id, user_agent=None, client_ip=None)
    return UserPrincipal(actor_id=actor_id, user_id=user.id, is_admin=True)


async def _user(
    uow, ids, clock, email: str, *, verified: bool = True, enabled: bool = True
):  # type: ignore[no-untyped-def]
    async with uow.begin() as work:
        user = await work.users.create(
            user_id=ids.new_id(),
            email=email,
            display_name=None,
            is_admin=False,
            email_verified_at=clock.now() if verified else None,
        )
        if not enabled:
            await work.users.set_blog_email_preference(
                user_id=user.id, enabled=False, at=clock.now()
            )
    return user


def _event(ids, clock, admin_id: str) -> BlogPublished:  # type: ignore[no-untyped-def]
    return BlogPublished(
        id=ids.new_id(),
        occurred_at=clock.now(),
        blog_id=ids.new_id(),
        slug="new-research",
        title="New Research",
        summary="A careful explanation.",
        cover_image_url="https://media.canery.in/cover.png",
        cover_image_alt="Research diagram",
        tag_keys=("research", "technology"),
        tier="L2",  # type: ignore[arg-type]
        difficulty="intermediate",  # type: ignore[arg-type]
        author_id=admin_id,
        published_at=clock.now(),
    )


def _service(uow, ids, clock) -> AnnouncementService:  # type: ignore[no-untyped-def]
    return AnnouncementService(
        uow=uow,
        clock=clock,
        ids=ids,
        policy=DefaultAuthorizationPolicy(),
        public_site_url="https://canery.in/",
        token_secret="test-secret-value-at-least-32-bytes",
    )


async def test_campaign_targets_only_eligible_default_enabled_readers(
    uow, ids, clock
) -> None:  # type: ignore[no-untyped-def]
    admin = await _admin(uow, ids, clock)
    eligible = await _user(uow, ids, clock, "eligible@example.com")
    await _user(uow, ids, clock, "unverified@example.com", verified=False)
    await _user(uow, ids, clock, "disabled@example.com", enabled=False)
    suspended = await _user(uow, ids, clock, "suspended@example.com")
    async with uow.begin() as work:
        await work.users.set_status(suspended.id, UserStatus.SUSPENDED)
        # The campaign FK requires the published article represented by the event.
        event = _event(ids, clock, admin.user_id)
        await work.blogs.insert(
            blog_id=event.blog_id,
            slug=event.slug,
            title=event.title,
            summary=event.summary,
            author_id=admin.user_id,
            series_id=None,
            series_position=None,
            markdown_uri="s3://blogs/new.md",
            content_sha256=bytes(range(32)),
            word_count=238,
            status=BlogStatus.PUBLISHED,
            published_at=clock.now(),
            cover_image_url=event.cover_image_url,
            cover_image_alt=event.cover_image_alt,
            tag_keys=event.tag_keys,
            tier=event.tier,
            difficulty=event.difficulty,
        )

    service = _service(uow, ids, clock)
    assert await service.stage_published(event) is True
    assert await service.stage_published(event) is False

    async with uow.read() as work:
        rows = await work.announcements._fetch_all(
            "SELECT user_id, recipient_email FROM blog_announcement_deliveries"
        )
        preference = await work.users.get_blog_email_preference(eligible.id)
    assert [(str(row["user_id"]), row["recipient_email"]) for row in rows] == [
        (eligible.id, "eligible@example.com")
    ]
    assert preference is not None and preference.blog_announcements_enabled is True


async def test_unsubscribe_cancels_queued_delivery(uow, ids, clock) -> None:  # type: ignore[no-untyped-def]
    admin = await _admin(uow, ids, clock)
    reader = await _user(uow, ids, clock, "reader@example.com")
    event = _event(ids, clock, admin.user_id)
    async with uow.begin() as work:
        await work.blogs.insert(
            blog_id=event.blog_id,
            slug=event.slug,
            title=event.title,
            summary=event.summary,
            author_id=admin.user_id,
            series_id=None,
            series_position=None,
            markdown_uri="s3://blogs/new.md",
            content_sha256=bytes(range(32)),
            word_count=238,
            status=BlogStatus.PUBLISHED,
            published_at=clock.now(),
            cover_image_url=event.cover_image_url,
            cover_image_alt=event.cover_image_alt,
        )
    service = _service(uow, ids, clock)
    await service.stage_published(event)
    principal = UserPrincipal(actor_id=ids.new_id(), user_id=reader.id, is_admin=False)
    preference = await service.set_preference(principal=principal, enabled=False)
    assert preference.blog_announcements_enabled is False
    async with uow.read() as work:
        row = await work.announcements._fetch_one(
            "SELECT status FROM blog_announcement_deliveries WHERE user_id = %(user)s",
            {"user": reader.id},
        )
    assert row["status"] == "cancelled"


async def test_draft_transition_emits_blog_published_once(uow, ids, clock) -> None:  # type: ignore[no-untyped-def]
    admin = await _admin(uow, ids, clock)
    blogs = BlogService(
        uow=uow,
        clock=clock,
        ids=ids,
        object_store=InMemoryObjectStore(),
        markdown=MarkdownItParser(max_bytes=1_000_000),
        policy=DefaultAuthorizationPolicy(),
        default_page_size=20,
        max_page_size=100,
    )
    draft = await blogs.publish_from_markdown(
        principal=admin,
        source=b"---\ntitle: First Publish\n---\n\nBody.\n",
        command=PublishBlogCommand(status=BlogStatus.DRAFT),
    )
    await blogs.update(
        principal=admin,
        blog_id=draft.blog.id,
        patch=UpdateBlogPatch(status=BlogStatus.PUBLISHED),
    )
    clock.advance(timedelta(minutes=1))
    await blogs.update(
        principal=admin,
        blog_id=draft.blog.id,
        patch=UpdateBlogPatch(title="Edited after publication"),
    )

    async with uow.read() as work:
        row = await work.outbox._fetch_one(
            "SELECT count(*) AS n FROM outbox_events "
            "WHERE event_name = 'BlogPublished' AND aggregate_id = %(blog)s",
            {"blog": draft.blog.id},
        )
    assert row["n"] == 1
