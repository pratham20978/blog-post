"""Typed editorial metadata round-trips and backfills on real PostgreSQL."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from psycopg.errors import CheckViolation, UniqueViolation

from blogs.adapters.markdown.parser import MarkdownItParser
from blogs.contracts.blog import (
    BlogDifficulty,
    BlogStatus,
    BlogTier,
    PublishBlogCommand,
    UpdateBlogPatch,
)
from blogs.contracts.identity import UserPrincipal
from blogs.database.backfill_metadata import apply, collect
from blogs.services.blog_service import BlogService
from blogs.services.policy import DefaultAuthorizationPolicy

pytestmark = pytest.mark.asyncio

NOW = datetime(2026, 9, 8, 12, 0, tzinfo=UTC)


async def _admin(uow, ids) -> str:  # type: ignore[no-untyped-def]
    async with uow.begin() as work:
        user = await work.users.create(
            user_id=ids.new_id(),
            email="metadata-admin@example.com",
            display_name="Metadata Admin",
            is_admin=True,
            email_verified_at=NOW,
        )
    return user.id


async def _admin_principal(uow, ids) -> UserPrincipal:  # type: ignore[no-untyped-def]
    return UserPrincipal(
        actor_id=ids.new_id(), user_id=await _admin(uow, ids), is_admin=True
    )


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


class TestTypedMetadata:
    async def test_explicit_publish_metadata_overrides_frontmatter(
        self, database, uow, ids, blogs
    ) -> None:  # type: ignore[no-untyped-def]
        admin = await _admin_principal(uow, ids)
        source = b"""---
title: Source title
summary: Source summary
tags: [source]
tier: L1
difficulty: beginner
cover_image: https://cdn.example.com/source.png
cover_image_alt: Source cover
date: 2026-09-01
---

## Source heading

Body.
"""
        result = await blogs.publish_from_markdown(
            principal=admin,
            source=source,
            command=PublishBlogCommand(
                title="Admin title",
                summary="Admin summary",
                tag_keys=("override",),
                tier=BlogTier.L3,
                difficulty=BlogDifficulty.ADVANCED,
                cover_image_url="https://cdn.example.com/admin.png",
                cover_image_alt="Admin cover",
            ),
        )

        assert result.blog.title == "Admin title"
        assert result.blog.summary == "Admin summary"
        assert result.blog.tag_keys == ("override",)
        assert result.blog.tier is BlogTier.L3
        assert result.blog.cover_image_url == "https://cdn.example.com/admin.png"
        async with database.connection() as conn:
            cursor = await conn.execute(
                "SELECT payload FROM outbox_events WHERE event_name = 'BlogPublished'"
            )
            event = await cursor.fetchone()
        assert event is not None
        assert event["payload"]["cover_image_url"] == result.blog.cover_image_url
        assert event["payload"]["tag_keys"] == ["override"]
        assert event["payload"]["tier"] == "L3"
        assert event["payload"]["published_on"] == "2026-09-01"

    async def test_replacing_source_replaces_metadata_content_and_headings(
        self, uow, ids, blogs
    ) -> None:  # type: ignore[no-untyped-def]
        admin = await _admin_principal(uow, ids)
        first = await blogs.publish_from_markdown(
            principal=admin,
            source=b"""---
title: First title
summary: First summary
tags: [old-tag]
cover_image: https://cdn.example.com/old.png
cover_image_alt: Old cover
updated: 2026-09-01
---

## Old heading

Old body.
""",
            command=PublishBlogCommand(),
        )

        updated = await blogs.update(
            principal=admin,
            blog_id=first.blog.id,
            patch=UpdateBlogPatch(),
            source=b"""---
title: Replacement title
description: Replacement description
tags: [new-tag]
tier: L2
difficulty: intermediate
prerequisites: [SQL]
updated: 2026-09-08
---

## New heading

New body.
""",
        )

        assert updated.title == "Replacement title"
        assert updated.summary == "Replacement description"
        assert updated.cover_image_url is None
        assert updated.cover_image_alt is None
        assert updated.tag_keys == ("new-tag",)
        assert updated.prerequisites == ("SQL",)
        assert updated.content_updated_on == date(2026, 9, 8)
        assert [section.anchor for section in updated.sections] == ["new-heading"]

    async def test_repository_round_trip(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        admin = await _admin(uow, ids)
        async with uow.begin() as work:
            blog = await work.blogs.insert(
                blog_id=ids.new_id(),
                slug="typed-metadata",
                title="Typed Metadata",
                summary="Every source property has a typed home.",
                author_id=admin,
                series_id=None,
                series_position=None,
                markdown_uri="s3://blogs/typed.md",
                content_sha256=bytes(range(32)),
                word_count=238,
                status=BlogStatus.PUBLISHED,
                published_at=NOW,
                cover_image_url="https://cdn.example.com/typed.png",
                cover_image_alt="A typed metadata record connected to a Markdown file",
                tag_keys=("databases", "metadata"),
                tier=BlogTier.L2,
                difficulty=BlogDifficulty.INTERMEDIATE,
                prerequisites=("SQL", "Markdown"),
                canonical_url="https://canery.in/blogs/typed-metadata",
                published_on=date(2026, 9, 1),
                content_updated_on=date(2026, 9, 8),
            )

        assert blog.cover_image_url == "https://cdn.example.com/typed.png"
        assert blog.tag_keys == ("databases", "metadata")
        assert blog.tier is BlogTier.L2
        assert blog.difficulty is BlogDifficulty.INTERMEDIATE
        assert blog.prerequisites == ("SQL", "Markdown")
        assert blog.published_on == date(2026, 9, 1)

    async def test_database_constraints_and_indexes(self, database, uow, ids) -> None:  # type: ignore[no-untyped-def]
        admin = await _admin(uow, ids)
        async with uow.begin() as work:
            blog = await work.blogs.insert(
                blog_id=ids.new_id(),
                slug="metadata-invariants",
                title="Metadata invariants",
                summary=None,
                author_id=admin,
                series_id=None,
                series_position=None,
                markdown_uri="s3://blogs/invariants.md",
                content_sha256=bytes(range(32)),
                word_count=1,
                status=BlogStatus.DRAFT,
                published_at=None,
            )
            other = await work.blogs.insert(
                blog_id=ids.new_id(),
                slug="other-metadata-invariants",
                title="Other metadata invariants",
                summary=None,
                author_id=admin,
                series_id=None,
                series_position=None,
                markdown_uri="s3://blogs/other-invariants.md",
                content_sha256=bytes(reversed(range(32))),
                word_count=1,
                status=BlogStatus.DRAFT,
                published_at=None,
            )

        invalid_updates = (
            "UPDATE blogs SET tag_keys = ARRAY['duplicate', 'duplicate'] WHERE id = %s",
            "UPDATE blogs SET tier = 'L5' WHERE id = %s",
            "UPDATE blogs SET difficulty = 'expert' WHERE id = %s",
            "UPDATE blogs SET cover_image_url = "
            "'https://cdn.example.com/unpaired.png' WHERE id = %s",
            "UPDATE blogs SET canonical_url = 'https://<site>/unresolved' WHERE id = %s",
            "UPDATE blogs SET prerequisites = ARRAY[''] WHERE id = %s",
        )
        for statement in invalid_updates:
            with pytest.raises(CheckViolation):
                async with database.transaction() as conn:
                    await conn.execute(statement, (blog.id,))  # type: ignore[arg-type]

        async with database.transaction() as conn:
            await conn.execute(
                "UPDATE blogs SET canonical_url = %s WHERE id = %s",
                ("https://canery.in/blogs/one-canonical", blog.id),
            )
        with pytest.raises(UniqueViolation):
            async with database.transaction() as conn:
                await conn.execute(
                    "UPDATE blogs SET canonical_url = %s WHERE id = %s",
                    ("https://canery.in/blogs/one-canonical", other.id),
                )

        async with database.connection() as conn:
            cursor = await conn.execute(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = current_schema() AND tablename = 'blogs'
                """
            )
            indexes = {row["indexname"] for row in await cursor.fetchall()}
        assert "blogs_tag_keys_gin" in indexes
        assert "blogs_canonical_url_unique" in indexes

    async def test_metadata_backfill_is_idempotent(
        self, database, uow, ids, object_store
    ) -> None:  # type: ignore[no-untyped-def]
        admin = await _admin(uow, ids)
        source = b"""---
title: Legacy
description: Filled from the canonical source
tags: [databases, migrations]
tier: L1
difficulty: beginner
prerequisites: [SQL]
canonical_url: https://canery.in/blogs/legacy
date: 2026-09-01
updated: 2026-09-07
---

# Legacy

![Rows becoming typed columns](https://cdn.example.com/legacy.png)
"""
        uri = await object_store.put(
            key="legacy.md", data=source, content_type="text/markdown"
        )
        async with uow.begin() as work:
            blog = await work.blogs.insert(
                blog_id=ids.new_id(),
                slug="legacy",
                title="Legacy",
                summary=None,
                author_id=admin,
                series_id=None,
                series_position=None,
                markdown_uri=uri,
                content_sha256=bytes(range(32)),
                word_count=10,
                status=BlogStatus.PUBLISHED,
                published_at=NOW,
            )

        patches = await collect(
            database=database,
            store=object_store,
            parser=MarkdownItParser(max_bytes=1_000_000),
        )
        assert await apply(database=database, patches=patches) == 1
        assert await apply(database=database, patches=patches) == 0

        async with uow.read() as work:
            stored = await work.blogs.get(blog.id)
        assert stored is not None
        assert stored.summary == "Filled from the canonical source"
        assert stored.cover_image_url == "https://cdn.example.com/legacy.png"
        assert stored.tag_keys == ("databases", "migrations")
        assert stored.canonical_url == "https://canery.in/blogs/legacy"
        assert stored.content_updated_on == date(2026, 9, 7)
