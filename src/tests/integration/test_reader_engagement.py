"""Qualified reads, immutable guest classification, likes, and recoil analytics."""

from __future__ import annotations

import asyncio
from datetime import timedelta

import pytest

from blogs.contracts.blog import BlogStatus
from blogs.contracts.engagement import EngagementKind, EngagementSource, RecordEngagementCommand
from blogs.contracts.identity import AnonymousPrincipal, UserPrincipal
from blogs.services.engagement_service import EngagementService
from blogs.services.policy import DefaultAuthorizationPolicy

pytestmark = pytest.mark.asyncio


@pytest.fixture
def engagement(uow, clock, ids) -> EngagementService:  # type: ignore[no-untyped-def]
    return EngagementService(
        uow=uow, clock=clock, ids=ids, policy=DefaultAuthorizationPolicy()
    )


async def _seed_blog(uow, ids, clock):  # type: ignore[no-untyped-def]
    async with uow.begin() as work:
        admin = await work.users.create(
            user_id=ids.new_id(),
            email="admin@example.com",
            display_name="Admin",
            is_admin=True,
            email_verified_at=clock.now(),
        )
        blog = await work.blogs.insert(
            blog_id=ids.new_id(),
            slug="qualified-reading",
            title="Qualified Reading",
            summary="A test article.",
            author_id=admin.id,
            series_id=None,
            series_position=None,
            markdown_uri="s3://blogs/read.md",
            content_sha256=bytes(range(32)),
            word_count=238,
            status=BlogStatus.PUBLISHED,
            published_at=clock.now(),
        )
    return blog


async def _reader(uow, ids, clock, number: int) -> UserPrincipal:  # type: ignore[no-untyped-def]
    actor_id = ids.new_id()
    async with uow.begin() as work:
        user = await work.users.create(
            user_id=ids.new_id(),
            email=f"reader{number}@example.com",
            display_name=None,
            is_admin=False,
            email_verified_at=clock.now(),
        )
        await work.actors.create(actor_id=actor_id, user_agent=None, client_ip=None)
        await work.actors.mark_merged(actor_id=actor_id, user_id=user.id, at=clock.now())
    return UserPrincipal(actor_id=actor_id, user_id=user.id, is_admin=False)


def _read(blog_id: str, key: str) -> RecordEngagementCommand:
    return RecordEngagementCommand(
        blog_id=blog_id,
        kind=EngagementKind.READ,
        source=EngagementSource.DIRECT,
        dedupe_key=key,
    )


async def test_member_and_guest_views_are_counted_separately(
    engagement, uow, ids, clock
) -> None:  # type: ignore[no-untyped-def]
    blog = await _seed_blog(uow, ids, clock)
    member = await _reader(uow, ids, clock, 1)
    guest_actor = ids.new_id()
    async with uow.begin() as work:
        await work.actors.create(actor_id=guest_actor, user_agent=None, client_ip=None)
    guest = AnonymousPrincipal(actor_id=guest_actor)

    assert await engagement.record(principal=guest, command=_read(blog.id, "guest-1"))
    assert await engagement.record(principal=member, command=_read(blog.id, "member-1"))
    assert await engagement.record(principal=member, command=_read(blog.id, "member-2"))

    summary = await engagement.summary(principal=guest, blog_id=blog.id)
    assert summary.member_view_count == 2
    assert summary.like_count == 0
    assert summary.liked_by_me is None
    async with uow.read() as work:
        row = await work.engagement_stats._fetch_one(
            "SELECT member_view_count, guest_view_count FROM blog_engagement_stats "
            "WHERE blog_id = %(blog)s",
            {"blog": blog.id},
        )
    assert row == {"member_view_count": 2, "guest_view_count": 1}


async def test_beacon_replay_does_not_increment_view_projection(
    engagement, uow, ids, clock
) -> None:  # type: ignore[no-untyped-def]
    blog = await _seed_blog(uow, ids, clock)
    member = await _reader(uow, ids, clock, 1)
    command = _read(blog.id, "same-visit")
    assert await engagement.record(principal=member, command=command) is True
    assert await engagement.record(principal=member, command=command) is False
    summary = await engagement.summary(principal=member, blog_id=blog.id)
    assert summary.member_view_count == 1


async def test_guest_read_stays_guest_after_account_attribution(
    engagement, uow, ids, clock
) -> None:  # type: ignore[no-untyped-def]
    blog = await _seed_blog(uow, ids, clock)
    actor_id = ids.new_id()
    async with uow.begin() as work:
        await work.actors.create(actor_id=actor_id, user_agent=None, client_ip=None)
    guest = AnonymousPrincipal(actor_id=actor_id)
    await engagement.record(principal=guest, command=_read(blog.id, "before-signup"))

    async with uow.begin() as work:
        user = await work.users.create(
            user_id=ids.new_id(),
            email="later@example.com",
            display_name=None,
            is_admin=False,
            email_verified_at=clock.now(),
        )
        await work.engagement.attribute_to_user(actor_id=actor_id, user_id=user.id)
        await work.recent_views.attribute_to_user(actor_id=actor_id, user_id=user.id)
        await work.actors.mark_merged(actor_id=actor_id, user_id=user.id, at=clock.now())

    async with uow.read() as work:
        event = await work.engagement._fetch_one(
            "SELECT user_id, authenticated_at_event FROM engagement_events "
            "WHERE kind = 'read'"
        )
        stats = await work.engagement_stats._fetch_one(
            "SELECT member_view_count, guest_view_count FROM blog_engagement_stats "
            "WHERE blog_id = %(blog)s",
            {"blog": blog.id},
        )
    assert str(event["user_id"]) == user.id
    assert event["authenticated_at_event"] is False
    assert stats == {"member_view_count": 0, "guest_view_count": 1}


async def test_like_put_and_delete_are_idempotent_under_concurrency(
    engagement, uow, ids, clock
) -> None:  # type: ignore[no-untyped-def]
    blog = await _seed_blog(uow, ids, clock)
    member = await _reader(uow, ids, clock, 1)

    liked = await asyncio.gather(
        *(engagement.like(principal=member, blog_id=blog.id, liked=True) for _ in range(4))
    )
    assert all(result.like_count == 1 for result in liked)
    assert (await engagement.summary(principal=member, blog_id=blog.id)).liked_by_me is True

    removed = await asyncio.gather(
        *(engagement.like(principal=member, blog_id=blog.id, liked=False) for _ in range(4))
    )
    assert all(result.like_count == 0 for result in removed)


async def test_recoil_is_returning_members_over_unique_members(
    engagement, uow, ids, clock
) -> None:  # type: ignore[no-untyped-def]
    blog = await _seed_blog(uow, ids, clock)
    returning = await _reader(uow, ids, clock, 1)
    one_time = await _reader(uow, ids, clock, 2)
    for index in range(2):
        await engagement.record(
            principal=returning, command=_read(blog.id, f"return-{index}")
        )
    await engagement.record(principal=one_time, command=_read(blog.id, "once"))

    async with uow.read() as work:
        kpis = await work.analytics.blog_kpis(
            blog_id=blog.id,
            window_start=clock.now() - timedelta(days=1),
            window_end=clock.now() + timedelta(days=1),
        )
    assert kpis is not None
    assert kpis.member_views == 3
    assert kpis.member_unique_readers == 2
    assert kpis.returning_member_readers == 1
    assert kpis.recoil_rate == 0.5
