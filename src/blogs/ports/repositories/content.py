"""Driven ports for articles, their structure and their groupings."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from blogs.contracts.blog import (
    BlogDetail,
    BlogFilter,
    BlogSection,
    BlogStatus,
    BlogSummary,
    Category,
    ReferencePin,
    Series,
)
from blogs.contracts.common import Page


class BlogRepository(Protocol):
    async def get(self, blog_id: str) -> BlogDetail | None: ...

    async def get_by_slug(self, slug: str) -> BlogDetail | None: ...

    async def slug_exists(self, slug: str) -> bool:
        """Advisory only.

        Uniqueness is the index's job; this exists so the publish path can pick
        a free suffix on the first try instead of colliding and retrying. A
        caller that treated it as a guarantee would have a race.
        """
        ...

    async def insert(
        self,
        *,
        blog_id: str,
        slug: str,
        title: str,
        summary: str | None,
        author_id: str,
        series_id: str | None,
        series_position: int | None,
        markdown_uri: str,
        content_sha256: bytes,
        word_count: int,
        status: BlogStatus,
        published_at: datetime | None,
    ) -> BlogDetail:
        """Raises ``SlugConflict`` when the slug is taken."""
        ...

    async def update_metadata(
        self,
        *,
        blog_id: str,
        title: str | None,
        summary: str | None,
        series_id: str | None,
        series_position: int | None,
        status: BlogStatus | None,
        published_at: datetime | None,
    ) -> BlogDetail | None: ...

    async def update_content(
        self,
        *,
        blog_id: str,
        markdown_uri: str,
        content_sha256: bytes,
        word_count: int,
    ) -> None: ...

    async def archive(self, *, blog_id: str, at: datetime) -> bool:
        """Deletion is an archive.

        Removing the row would take comments, markers and catalog entries with
        it and leave the engagement log pointing at nothing. Retirement is a
        status change; a true purge is a separate, explicit operation.
        """
        ...

    async def list(
        self, *, filter: BlogFilter, cursor: str | None, limit: int
    ) -> Page[BlogSummary]:
        """Keyset-paginated on ``(published_at, id)`` descending."""
        ...

    async def set_categories(self, *, blog_id: str, category_keys: tuple[str, ...]) -> None:
        """Replace the whole set. Raises ``CategoryUnknown`` for an unknown key."""
        ...

    async def categories_for(self, blog_id: str) -> tuple[str, ...]: ...


class BlogSectionRepository(Protocol):
    async def replace_all(
        self, *, blog_id: str, sections: tuple[BlogSection, ...]
    ) -> None:
        """Swap an article's headings for the ones just parsed.

        Raises ``SectionReferencedByPin`` when the replacement would drop a
        heading another article pins into — the database refuses it, and that
        refusal is the whole point of a reference pin.
        """
        ...

    async def list_for(self, blog_id: str) -> tuple[BlogSection, ...]: ...

    async def exists(self, *, blog_id: str, anchor: str) -> bool: ...


class TaxonomyRepository(Protocol):
    async def list_categories(self) -> tuple[Category, ...]: ...

    async def get_category(self, key: str) -> Category | None: ...

    async def upsert_category(
        self, *, key: str, label: str, description: str | None
    ) -> Category: ...

    async def list_series(self) -> tuple[Series, ...]: ...

    async def get_series_by_key(self, key: str) -> Series | None: ...

    async def upsert_series(
        self, *, series_id: str, key: str, title: str, description: str | None
    ) -> Series: ...


class ReferencePinRepository(Protocol):
    async def create(
        self,
        *,
        pin_id: str,
        source_blog_id: str,
        target_blog_id: str,
        target_anchor: str,
        note: str | None,
        created_by: str,
    ) -> ReferencePin:
        """Raises ``PinSelfReference`` and ``SectionAnchorUnknown``, both of
        which the schema refuses independently of this call."""
        ...

    async def delete(self, pin_id: str) -> bool: ...

    async def list_for_source(self, blog_id: str) -> tuple[ReferencePin, ...]: ...

    async def list_for_target(self, blog_id: str) -> tuple[ReferencePin, ...]:
        """Inbound pins — what F4's overlap detection surfaces to the admin."""
        ...
