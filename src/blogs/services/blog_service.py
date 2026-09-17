"""Authoring and reading articles.

The publish path has one ordering decision worth stating: **the object store is
written before the database commits.** Object stores are not transactional, so
one of the two failure modes has to be chosen, and they are not equally bad.

* Object first — a crash leaves bytes in MinIO that no row references. Garbage,
  collectable, invisible to readers.
* Row first — a crash leaves an article whose content cannot be fetched. Every
  read of it fails, and nothing in the database reveals why.

Content-addressing makes the first option cheap: the key is the hash of the
bytes, so re-publishing the same content overwrites itself and a retry after a
crash is idempotent rather than a second copy.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from blogs.contracts.blog import (
    BlogContent,
    BlogDetail,
    BlogFilter,
    BlogSection,
    BlogStatus,
    BlogSummary,
    MarkdownDocument,
    PublishBlogCommand,
    UpdateBlogPatch,
)
from blogs.contracts.common import ErrorCategory, Page
from blogs.contracts.events import BlogArchived, BlogPublished, BlogUpdated
from blogs.contracts.identity import Principal, UserPrincipal
from blogs.core.clock import Clock
from blogs.core.errors import raise_error
from blogs.core.ids import IdGenerator
from blogs.ports.services import AuthorizationPolicy, MarkdownParser, ObjectStore
from blogs.ports.uow import UnitOfWorkFactory
from blogs.services.policy import require

logger = logging.getLogger(__name__)

#: How many "-2", "-3" suffixes to try before giving up and letting the unique
#: index decide. Bounded so a pathological title cannot spin.
_MAX_SLUG_ATTEMPTS = 50


@dataclass(frozen=True, slots=True)
class PublishResult:
    blog: BlogDetail
    created: bool


class BlogService:
    def __init__(
        self,
        *,
        uow: UnitOfWorkFactory,
        clock: Clock,
        ids: IdGenerator,
        object_store: ObjectStore,
        markdown: MarkdownParser,
        policy: AuthorizationPolicy,
        default_page_size: int,
        max_page_size: int,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._ids = ids
        self._store = object_store
        self._markdown = markdown
        self._policy = policy
        self._default_page_size = default_page_size
        self._max_page_size = max_page_size

    # ── Authoring ───────────────────────────────────────────────────────────

    async def publish_from_markdown(
        self,
        *,
        principal: Principal,
        source: bytes,
        command: PublishBlogCommand,
        correlation_id: str | None = None,
    ) -> PublishResult:
        require(
            self._policy.can_publish(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)

        document = self._markdown.parse(source)
        title = command.title or document.title
        if not title:
            raise_error(
                ErrorCategory.MARKDOWN_INVALID,
                correlation_id=correlation_id,
                safe_details={"reason": "NO_TITLE"},
            )

        now = self._clock.now()
        blog_id = self._ids.new_id()
        categories = (
            command.category_keys
            if command.category_keys is not None
            else document.category_keys
        )
        series_key = command.series_key or document.series_key
        summary = self._command_value(command, "summary", document.summary)
        series_position = self._command_value(
            command, "series_position", document.series_position
        )
        cover_image_url = self._command_value(
            command, "cover_image_url", document.cover_image_url
        )
        cover_image_alt = self._command_value(
            command, "cover_image_alt", document.cover_image_alt
        )
        tag_keys = self._command_value(command, "tag_keys", document.tag_keys)
        tier = self._command_value(command, "tier", document.tier)
        difficulty = self._command_value(command, "difficulty", document.difficulty)
        prerequisites = self._command_value(
            command, "prerequisites", document.prerequisites
        )
        canonical_url = self._command_value(
            command, "canonical_url", document.canonical_url
        )
        published_on = self._command_value(command, "published_on", document.published_on)
        if command.status is BlogStatus.PUBLISHED and published_on is None:
            published_on = now.date()
        content_updated_on = self._command_value(
            command, "content_updated_on", document.content_updated_on
        ) or published_on

        async with self._uow.read() as uow:
            slug = await self._resolve_slug(
                uow, requested=command.slug or document.slug, title=title
            )

        # Written before the commit — see the module docstring.
        markdown_uri = await self._store.put(
            key=f"blogs/{blog_id}/{document.content_sha256}.md",
            data=source,
            content_type="text/markdown; charset=utf-8",
        )

        async with self._uow.begin() as uow:
            series_id = await self._resolve_series(
                uow, series_key, correlation_id=correlation_id
            )
            published_at = now if command.status is BlogStatus.PUBLISHED else None

            await uow.blogs.insert(
                blog_id=blog_id,
                slug=slug,
                title=title,
                summary=summary,
                author_id=principal.user_id,
                series_id=series_id,
                series_position=series_position,
                cover_image_url=cover_image_url,
                cover_image_alt=cover_image_alt,
                tag_keys=tag_keys,
                tier=tier,
                difficulty=difficulty,
                prerequisites=prerequisites,
                canonical_url=canonical_url,
                published_on=published_on,
                content_updated_on=content_updated_on,
                markdown_uri=markdown_uri,
                content_sha256=bytes.fromhex(document.content_sha256),
                word_count=document.word_count,
                status=command.status,
                published_at=published_at,
            )
            await uow.blogs.set_categories(blog_id=blog_id, category_keys=categories)
            await uow.sections.replace_all(
                blog_id=blog_id, sections=self._sections_of(document)
            )

            if command.status is BlogStatus.PUBLISHED:
                # Staged in the same transaction as the article, so the event
                # exists if and only if the article does.
                await uow.outbox.add(
                    BlogPublished(
                        id=self._ids.new_id(),
                        occurred_at=now,
                        blog_id=blog_id,
                        slug=slug,
                        title=title,
                        summary=summary,
                        cover_image_url=cover_image_url,
                        cover_image_alt=cover_image_alt,
                        tag_keys=tag_keys,
                        tier=tier,
                        difficulty=difficulty,
                        prerequisites=prerequisites,
                        canonical_url=canonical_url,
                        published_on=published_on,
                        content_updated_on=content_updated_on,
                        category_keys=categories,
                        series_id=series_id,
                        author_id=principal.user_id,
                        published_at=published_at or now,
                    ),
                    aggregate_type="blog",
                    aggregate_id=blog_id,
                )

            stored = await uow.blogs.get(blog_id)

        assert stored is not None
        return PublishResult(blog=stored, created=True)

    async def update(
        self,
        *,
        principal: Principal,
        blog_id: str,
        patch: UpdateBlogPatch,
        source: bytes | None = None,
        correlation_id: str | None = None,
    ) -> BlogDetail:
        require(
            self._policy.can_edit_blog(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        now = self._clock.now()
        changed: list[str] = []

        document: MarkdownDocument | None = None
        markdown_uri: str | None = None
        if source is not None:
            document = self._markdown.parse(source)
            markdown_uri = await self._store.put(
                key=f"blogs/{blog_id}/{document.content_sha256}.md",
                data=source,
                content_type="text/markdown; charset=utf-8",
            )

        async with self._uow.begin() as uow:
            existing = await uow.blogs.get(blog_id)
            if existing is None:
                raise_error(ErrorCategory.BLOG_NOT_FOUND, correlation_id=correlation_id)

            source_authoritative = document is not None
            series_key = (
                patch.series_key
                if patch.series_key is not None
                else document.series_key if document is not None else None
            )
            series_id = await self._resolve_series(
                uow, series_key, correlation_id=correlation_id
            )

            def value(field: str):  # type: ignore[no-untyped-def]
                explicit = getattr(patch, field)
                if explicit is not None:
                    return explicit
                return getattr(document, field) if document is not None else None

            title = value("title")
            summary = value("summary")
            series_position = value("series_position")
            cover_image_url = value("cover_image_url")
            cover_image_alt = value("cover_image_alt")
            tag_keys = value("tag_keys")
            tier = value("tier")
            difficulty = value("difficulty")
            prerequisites = value("prerequisites")
            canonical_url = value("canonical_url")
            published_on = value("published_on")
            content_updated_on = value("content_updated_on")

            if source_authoritative:
                if existing.status is BlogStatus.PUBLISHED and published_on is None:
                    published_on = existing.published_on or now.date()
                content_updated_on = content_updated_on or now.date()
            elif patch.status is BlogStatus.PUBLISHED and existing.published_on is None:
                published_on = now.date()

            comparable = {
                "title": title,
                "summary": summary,
                "series_id": series_id,
                "series_position": series_position,
                "cover_image_url": cover_image_url,
                "cover_image_alt": cover_image_alt,
                "tag_keys": tag_keys,
                "tier": tier,
                "difficulty": difficulty,
                "prerequisites": prerequisites,
                "canonical_url": canonical_url,
                "published_on": published_on,
                "content_updated_on": content_updated_on,
                "status": patch.status,
            }
            for field, candidate in comparable.items():
                if candidate is not None and candidate != getattr(existing, field):
                    changed.append(field)
            if source_authoritative:
                for field in (
                    "summary",
                    "series_id",
                    "series_position",
                    "cover_image_url",
                    "cover_image_alt",
                    "tag_keys",
                    "tier",
                    "difficulty",
                    "prerequisites",
                    "canonical_url",
                    "published_on",
                    "content_updated_on",
                ):
                    if field not in changed and comparable[field] != getattr(existing, field):
                        changed.append(field)

            await uow.blogs.update_metadata(
                blog_id=blog_id,
                title=title,
                summary=summary,
                series_id=series_id,
                series_position=series_position,
                cover_image_url=cover_image_url,
                cover_image_alt=cover_image_alt,
                tag_keys=tag_keys,
                tier=tier,
                difficulty=difficulty,
                prerequisites=prerequisites,
                canonical_url=canonical_url,
                published_on=published_on,
                content_updated_on=content_updated_on,
                source_authoritative=source_authoritative,
                status=patch.status,
                published_at=now,
            )

            category_keys = (
                patch.category_keys
                if patch.category_keys is not None
                else document.category_keys if document is not None else None
            )
            if category_keys is not None:
                await uow.blogs.set_categories(
                    blog_id=blog_id, category_keys=category_keys
                )
                if category_keys != existing.category_keys:
                    changed.append("category_keys")

            if document is not None and markdown_uri is not None:
                await uow.blogs.update_content(
                    blog_id=blog_id,
                    markdown_uri=markdown_uri,
                    content_sha256=bytes.fromhex(document.content_sha256),
                    word_count=document.word_count,
                )
                # May raise SECTION_REFERENCED_BY_PIN if the edit drops a
                # heading another article points into. That refusal is the
                # feature, not an obstacle to work around.
                await uow.sections.replace_all(
                    blog_id=blog_id, sections=self._sections_of(document)
                )
                changed.append("content")

            updated = await uow.blogs.get(blog_id)
            assert updated is not None

            first_publish = (
                existing.published_at is None
                and updated.status is BlogStatus.PUBLISHED
            )
            if first_publish:
                await uow.outbox.add(
                    BlogPublished(
                        id=self._ids.new_id(),
                        occurred_at=now,
                        blog_id=updated.id,
                        slug=updated.slug,
                        title=updated.title,
                        summary=updated.summary,
                        cover_image_url=updated.cover_image_url,
                        cover_image_alt=updated.cover_image_alt,
                        tag_keys=updated.tag_keys,
                        tier=updated.tier,
                        difficulty=updated.difficulty,
                        prerequisites=updated.prerequisites,
                        canonical_url=updated.canonical_url,
                        published_on=updated.published_on,
                        content_updated_on=updated.content_updated_on,
                        category_keys=updated.category_keys,
                        series_id=updated.series_id,
                        author_id=updated.author_id,
                        published_at=updated.published_at or now,
                    ),
                    aggregate_type="blog",
                    aggregate_id=blog_id,
                )

            if changed:
                await uow.outbox.add(
                    BlogUpdated(
                        id=self._ids.new_id(),
                        occurred_at=now,
                        blog_id=blog_id,
                        changed_fields=tuple(changed),
                        updated_at=now,
                    ),
                    aggregate_type="blog",
                    aggregate_id=blog_id,
                )

        return updated

    async def archive(
        self, *, principal: Principal, blog_id: str, correlation_id: str | None = None
    ) -> None:
        """Retire an article without destroying what refers to it."""
        require(
            self._policy.can_archive_blog(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        now = self._clock.now()
        async with self._uow.begin() as uow:
            if not await uow.blogs.archive(blog_id=blog_id, at=now):
                raise_error(ErrorCategory.BLOG_NOT_FOUND, correlation_id=correlation_id)
            await uow.outbox.add(
                BlogArchived(
                    id=self._ids.new_id(),
                    occurred_at=now,
                    blog_id=blog_id,
                    archived_at=now,
                ),
                aggregate_type="blog",
                aggregate_id=blog_id,
            )

    # ── Reading ─────────────────────────────────────────────────────────────

    async def list(
        self, *, filter: BlogFilter, cursor: str | None = None, limit: int | None = None
    ) -> Page[BlogSummary]:
        resolved = min(limit or self._default_page_size, self._max_page_size)
        async with self._uow.read() as uow:
            return await uow.blogs.list(filter=filter, cursor=cursor, limit=resolved)

    async def get_by_slug(
        self,
        *,
        slug: str,
        principal: Principal | None = None,
        correlation_id: str | None = None,
    ) -> BlogDetail:
        async with self._uow.read() as uow:
            blog = await uow.blogs.get_by_slug(slug)
        if blog is None:
            raise_error(ErrorCategory.BLOG_NOT_FOUND, correlation_id=correlation_id)
        self._assert_visible(blog, principal, correlation_id=correlation_id)
        return blog

    async def get_content(
        self,
        *,
        slug: str,
        principal: Principal | None = None,
        correlation_id: str | None = None,
    ) -> BlogContent:
        """Fetch the article body, exactly as authored.

        ``content_sha256`` doubles as the ETag: it is a hash of these bytes and
        the bytes never change under a given hash, so a conditional request can
        be answered without touching the object store at all.
        """
        blog = await self.get_by_slug(
            slug=slug, principal=principal, correlation_id=correlation_id
        )
        markdown = (await self._store.get(blog.markdown_uri)).decode("utf-8")
        return BlogContent(
            blog_id=blog.id,
            slug=blog.slug,
            content_sha256=blog.content_sha256,
            markdown=markdown,
        )

    # ── Internals ───────────────────────────────────────────────────────────

    def _assert_visible(
        self,
        blog: BlogDetail,
        principal: Principal | None,
        *,
        correlation_id: str | None,
    ) -> None:
        """Drafts and archives are the admin's alone.

        Reported as ``BLOG_NOT_FOUND`` rather than as a refusal: confirming that
        a slug exists but is unpublished tells an outsider what is coming next.
        """
        if blog.status is BlogStatus.PUBLISHED:
            return
        if principal is not None and self._policy.can_edit_blog(principal):
            return
        raise_error(ErrorCategory.BLOG_NOT_FOUND, correlation_id=correlation_id)

    @staticmethod
    def _sections_of(document: MarkdownDocument) -> tuple[BlogSection, ...]:
        return tuple(
            BlogSection(
                anchor=heading.anchor,
                ordinal=ordinal,
                level=heading.level,
                title=heading.title,
                char_start=heading.char_start,
                char_end=heading.char_end,
            )
            for ordinal, heading in enumerate(document.headings)
        )

    async def _resolve_slug(self, uow, *, requested: str | None, title: str) -> str:  # type: ignore[no-untyped-def]
        """Pick a free slug, suffixing on collision.

        Advisory only — the unique index is the actual guarantee, and
        ``insert`` translates a collision into ``SLUG_CONFLICT``. This just
        means the common case succeeds on the first attempt.
        """
        from blogs.adapters.markdown.parser import slugify

        base = requested or slugify(title)
        if not base:
            base = f"post-{self._ids.new_id()[:8]}"
        if not await uow.blogs.slug_exists(base):
            return base
        for suffix in range(2, _MAX_SLUG_ATTEMPTS + 2):
            candidate = f"{base}-{suffix}"
            if not await uow.blogs.slug_exists(candidate):
                return candidate
        return f"{base}-{self._ids.new_id()[:8]}"

    async def _resolve_series(  # type: ignore[no-untyped-def]
        self, uow, series_key: str | None, *, correlation_id: str | None
    ) -> str | None:
        if series_key is None:
            return None
        series = await uow.taxonomy.get_series_by_key(series_key)
        if series is None:
            raise_error(
                ErrorCategory.SERIES_UNKNOWN,
                correlation_id=correlation_id,
                safe_details={"series_key": series_key},
            )
        return series.id

    @staticmethod
    def _command_value(command: PublishBlogCommand, field: str, fallback):  # type: ignore[no-untyped-def]
        """Use an explicit multipart value, including an empty tuple, otherwise
        take the value parsed from the canonical Markdown source."""
        return getattr(command, field) if field in command.model_fields_set else fallback


__all__ = ["BlogService", "PublishResult"]
