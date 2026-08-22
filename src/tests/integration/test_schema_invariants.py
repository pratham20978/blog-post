"""The invariants the schema enforces, asserted as violations.

Doc 01 states these as rules. A rule the application merely remembers to check
is a rule with a race and a bypass; these tests confirm the database refuses
them regardless of which code path writes.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from blogs.contracts.blog import BlogSection, BlogStatus
from blogs.contracts.common import ErrorCategory
from blogs.core.errors import BlogPlatformError
from blogs.repository.uow import SqlUnitOfWorkFactory

pytestmark = pytest.mark.asyncio

NOW = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)


async def _seed(uow: SqlUnitOfWorkFactory, ids) -> tuple[str, str, str]:  # type: ignore[no-untyped-def]
    """An admin, a reader, and one published article."""
    async with uow.begin() as work:
        admin = await work.users.create(
            user_id=ids.new_id(),
            email="admin@example.com",
            display_name="Admin",
            is_admin=True,
            email_verified_at=NOW,
        )
        reader = await work.users.create(
            user_id=ids.new_id(),
            email="reader@example.com",
            display_name=None,
            is_admin=False,
            email_verified_at=NOW,
        )
        await work.taxonomy.upsert_category(key="ai", label="AI", description=None)
        blog = await work.blogs.insert(
            blog_id=ids.new_id(),
            slug="a-post",
            title="A Post",
            summary=None,
            author_id=admin.id,
            series_id=None,
            series_position=None,
            markdown_uri="s3://blogs/a.md",
            content_sha256=bytes(range(32)),
            word_count=476,
            status=BlogStatus.PUBLISHED,
            published_at=NOW,
        )
        await work.sections.replace_all(
            blog_id=blog.id,
            sections=(
                BlogSection(
                    anchor="intro", ordinal=0, level=2, title="Intro",
                    char_start=0, char_end=50,
                ),
            ),
        )
    return admin.id, reader.id, blog.id


class TestSingleAdmin:
    async def test_a_second_admin_is_refused(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """`users_single_admin`, a partial unique index on a constant."""
        await _seed(uow, ids)
        with pytest.raises(BlogPlatformError) as exc:
            async with uow.begin() as work:
                await work.users.create(
                    user_id=ids.new_id(),
                    email="second-admin@example.com",
                    display_name=None,
                    is_admin=True,
                    email_verified_at=NOW,
                )
        assert exc.value.category is ErrorCategory.ACCESS_DENIED

    async def test_readers_are_unlimited(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        await _seed(uow, ids)
        async with uow.begin() as work:
            for n in range(3):
                await work.users.create(
                    user_id=ids.new_id(),
                    email=f"reader{n}@example.com",
                    display_name=None,
                    is_admin=False,
                    email_verified_at=None,
                )


class TestEmailUniqueness:
    async def test_case_and_whitespace_do_not_create_a_second_account(
        self, uow, ids
    ) -> None:  # type: ignore[no-untyped-def]
        """Uniqueness holds against the generated column, so it cannot be
        defeated by a caller that forgot to normalise."""
        await _seed(uow, ids)
        with pytest.raises(BlogPlatformError):
            async with uow.begin() as work:
                await work.users.create(
                    user_id=ids.new_id(),
                    email="  READER@Example.COM  ",
                    display_name=None,
                    is_admin=False,
                    email_verified_at=None,
                )


class TestCommentThreading:
    async def test_one_root_comment_per_user_per_article(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        _, reader, blog = await _seed(uow, ids)
        async with uow.begin() as work:
            await work.comments.create_root(
                comment_id=ids.new_id(), blog_id=blog, user_id=reader, body="first"
            )
        with pytest.raises(BlogPlatformError) as exc:
            async with uow.begin() as work:
                await work.comments.create_root(
                    comment_id=ids.new_id(), blog_id=blog, user_id=reader, body="second"
                )
        assert exc.value.category is ErrorCategory.COMMENT_ALREADY_EXISTS

    async def test_deleting_yours_frees_the_slot(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """The unique index excludes tombstones, so this must work."""
        _, reader, blog = await _seed(uow, ids)
        async with uow.begin() as work:
            first = await work.comments.create_root(
                comment_id=ids.new_id(), blog_id=blog, user_id=reader, body="first"
            )
            await work.comments.soft_delete(
                comment_id=first.id, deleted_by=reader, now=NOW, as_admin=False
            )
            await work.comments.create_root(
                comment_id=ids.new_id(), blog_id=blog, user_id=reader, body="replacement"
            )

    async def test_a_reply_to_a_reply_is_unrepresentable(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """The composite foreign key, not an application check."""
        _, reader, blog = await _seed(uow, ids)
        async with uow.begin() as work:
            root = await work.comments.create_root(
                comment_id=ids.new_id(), blog_id=blog, user_id=reader, body="root"
            )
            reply = await work.comments.create_reply(
                comment_id=ids.new_id(),
                blog_id=blog,
                user_id=reader,
                parent_comment_id=root.id,
                body="reply",
            )
            assert reply.depth == 1

        with pytest.raises(BlogPlatformError) as exc:
            async with uow.begin() as work:
                await work.comments.create_reply(
                    comment_id=ids.new_id(),
                    blog_id=blog,
                    user_id=reader,
                    parent_comment_id=reply.id,
                    body="nested",
                )
        assert exc.value.category is ErrorCategory.COMMENT_DEPTH_INVALID

    async def test_a_reply_cannot_cross_articles(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """The FK carries blog_id, so a parent on another article fails too."""
        admin, reader, blog = await _seed(uow, ids)
        async with uow.begin() as work:
            other = await work.blogs.insert(
                blog_id=ids.new_id(),
                slug="other-post",
                title="Other",
                summary=None,
                author_id=admin,
                series_id=None,
                series_position=None,
                markdown_uri="s3://blogs/b.md",
                content_sha256=bytes(range(32)),
                word_count=10,
                status=BlogStatus.PUBLISHED,
                published_at=NOW,
            )
            root = await work.comments.create_root(
                comment_id=ids.new_id(), blog_id=blog, user_id=reader, body="root"
            )
        with pytest.raises(BlogPlatformError):
            async with uow.begin() as work:
                await work.comments.create_reply(
                    comment_id=ids.new_id(),
                    blog_id=other.id,
                    user_id=reader,
                    parent_comment_id=root.id,
                    body="wrong article",
                )


class TestMarkersAndCatalogs:
    async def test_a_marker_moves_rather_than_multiplies(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        from blogs.contracts.interaction import OffsetAnchor, SectionAnchor

        _, reader, blog = await _seed(uow, ids)
        async with uow.begin() as work:
            await work.markers.upsert(
                user_id=reader,
                blog_id=blog,
                anchor=SectionAnchor(anchor="intro"),
                progress_ratio=0.2,
                now=NOW,
            )
            second = await work.markers.upsert(
                user_id=reader,
                blog_id=blog,
                anchor=OffsetAnchor(char_offset=900),
                progress_ratio=0.9,
                now=NOW,
            )
        assert second.anchor.kind == "offset"
        async with uow.read() as work:
            assert len(await work.markers.list_for_user(user_id=reader, limit=10)) == 1

    async def test_only_one_default_catalog_per_user(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        _, reader, _ = await _seed(uow, ids)
        async with uow.begin() as work:
            first = await work.catalogs.ensure_default(
                user_id=reader, catalog_id=ids.new_id()
            )
        async with uow.begin() as work:
            again = await work.catalogs.ensure_default(
                user_id=reader, catalog_id=ids.new_id()
            )
        assert first.id == again.id

    async def test_catalog_names_are_unique_case_insensitively(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        _, reader, _ = await _seed(uow, ids)
        async with uow.begin() as work:
            await work.catalogs.create(
                catalog_id=ids.new_id(), user_id=reader, name="Reading List",
                is_default=False,
            )
        with pytest.raises(BlogPlatformError) as exc:
            async with uow.begin() as work:
                await work.catalogs.create(
                    catalog_id=ids.new_id(), user_id=reader, name="  reading list  ",
                    is_default=False,
                )
        assert exc.value.category is ErrorCategory.CATALOG_NAME_TAKEN


class TestReferencePins:
    async def test_a_pin_cannot_target_a_missing_section(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        admin, _, blog = await _seed(uow, ids)
        async with uow.begin() as work:
            source = await work.blogs.insert(
                blog_id=ids.new_id(),
                slug="source-post",
                title="Source",
                summary=None,
                author_id=admin,
                series_id=None,
                series_position=None,
                markdown_uri="s3://blogs/c.md",
                content_sha256=bytes(range(32)),
                word_count=10,
                status=BlogStatus.PUBLISHED,
                published_at=NOW,
            )
        with pytest.raises(BlogPlatformError) as exc:
            async with uow.begin() as work:
                await work.pins.create(
                    pin_id=ids.new_id(),
                    source_blog_id=source.id,
                    target_blog_id=blog,
                    target_anchor="no-such-section",
                    note=None,
                    created_by=admin,
                )
        assert exc.value.category is ErrorCategory.SECTION_ANCHOR_UNKNOWN

    async def test_a_pin_cannot_reference_its_own_article(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        admin, _, blog = await _seed(uow, ids)
        with pytest.raises(BlogPlatformError) as exc:
            async with uow.begin() as work:
                await work.pins.create(
                    pin_id=ids.new_id(),
                    source_blog_id=blog,
                    target_blog_id=blog,
                    target_anchor="intro",
                    note=None,
                    created_by=admin,
                )
        assert exc.value.category is ErrorCategory.PIN_SELF_REFERENCE

    async def test_an_edit_cannot_silently_orphan_a_pin(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """Re-publishing without a pinned heading is refused, loudly.

        This is what a reference pin is *for*: the alternative is a
        cross-reference that quietly stops resolving.
        """
        admin, _, blog = await _seed(uow, ids)
        async with uow.begin() as work:
            source = await work.blogs.insert(
                blog_id=ids.new_id(),
                slug="citing-post",
                title="Citing",
                summary=None,
                author_id=admin,
                series_id=None,
                series_position=None,
                markdown_uri="s3://blogs/d.md",
                content_sha256=bytes(range(32)),
                word_count=10,
                status=BlogStatus.PUBLISHED,
                published_at=NOW,
            )
            await work.pins.create(
                pin_id=ids.new_id(),
                source_blog_id=source.id,
                target_blog_id=blog,
                target_anchor="intro",
                note=None,
                created_by=admin,
            )

        with pytest.raises(BlogPlatformError) as exc:
            async with uow.begin() as work:
                await work.sections.replace_all(
                    blog_id=blog,
                    sections=(
                        BlogSection(
                            anchor="renamed", ordinal=0, level=2, title="Renamed",
                            char_start=0, char_end=10,
                        ),
                    ),
                )
        assert exc.value.category is ErrorCategory.SECTION_REFERENCED_BY_PIN

    async def test_an_unrelated_edit_still_works(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """Only the pinned heading is protected; adding sections is fine."""
        admin, _, blog = await _seed(uow, ids)
        async with uow.begin() as work:
            source = await work.blogs.insert(
                blog_id=ids.new_id(), slug="citing-2", title="Citing", summary=None,
                author_id=admin, series_id=None, series_position=None,
                markdown_uri="s3://blogs/e.md", content_sha256=bytes(range(32)),
                word_count=10, status=BlogStatus.PUBLISHED, published_at=NOW,
            )
            await work.pins.create(
                pin_id=ids.new_id(), source_blog_id=source.id, target_blog_id=blog,
                target_anchor="intro", note=None, created_by=admin,
            )
        async with uow.begin() as work:
            await work.sections.replace_all(
                blog_id=blog,
                sections=(
                    BlogSection(anchor="intro", ordinal=0, level=2, title="Intro",
                                char_start=0, char_end=60),
                    BlogSection(anchor="new-part", ordinal=1, level=2, title="New Part",
                                char_start=60, char_end=90),
                ),
            )
        async with uow.read() as work:
            assert len(await work.sections.list_for(blog)) == 2


class TestBlogRules:
    async def test_slug_collisions_are_refused(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        admin, _, _ = await _seed(uow, ids)
        with pytest.raises(BlogPlatformError) as exc:
            async with uow.begin() as work:
                await work.blogs.insert(
                    blog_id=ids.new_id(), slug="a-post", title="Duplicate", summary=None,
                    author_id=admin, series_id=None, series_position=None,
                    markdown_uri="s3://blogs/f.md", content_sha256=bytes(range(32)),
                    word_count=10, status=BlogStatus.PUBLISHED, published_at=NOW,
                )
        assert exc.value.category is ErrorCategory.SLUG_CONFLICT

    async def test_reading_minutes_is_derived_not_supplied(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """476 words at the validated 238 wpm is exactly 2 minutes."""
        _, _, blog = await _seed(uow, ids)
        async with uow.read() as work:
            stored = await work.blogs.get(blog)
        assert stored is not None
        assert stored.word_count == 476
        assert stored.reading_minutes == 2

    async def test_an_unknown_category_is_refused(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        _, _, blog = await _seed(uow, ids)
        with pytest.raises(BlogPlatformError) as exc:
            async with uow.begin() as work:
                await work.blogs.set_categories(
                    blog_id=blog, category_keys=("not-a-real-category",)
                )
        assert exc.value.category is ErrorCategory.CATEGORY_UNKNOWN

    async def test_archiving_keeps_comments_and_engagement(self, uow, ids) -> None:  # type: ignore[no-untyped-def]
        """Deletion is an archive precisely so this history survives."""
        _, reader, blog = await _seed(uow, ids)
        async with uow.begin() as work:
            await work.comments.create_root(
                comment_id=ids.new_id(), blog_id=blog, user_id=reader, body="kept"
            )
            assert await work.blogs.archive(blog_id=blog, at=NOW) is True
        async with uow.read() as work:
            stored = await work.blogs.get(blog)
            assert stored is not None and stored.status is BlogStatus.ARCHIVED
            assert await work.comments.count_for_blog(blog) == 1
