"""Driven ports for comments, markers and catalogs."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from blogs.contracts.common import Page
from blogs.contracts.interaction import (
    Catalog,
    CatalogItem,
    Comment,
    CommentThread,
    Marker,
    MarkerAnchor,
    RecentView,
)


class CommentRepository(Protocol):
    async def get(self, comment_id: str) -> Comment | None: ...

    async def create_root(
        self, *, comment_id: str, blog_id: str, user_id: str, body: str
    ) -> Comment:
        """Raises ``CommentAlreadyExists`` — one root per user per article, and
        the partial unique index is what decides it."""
        ...

    async def create_reply(
        self,
        *,
        comment_id: str,
        blog_id: str,
        user_id: str,
        parent_comment_id: str,
        body: str,
    ) -> Comment:
        """Raises ``CommentDepthInvalid`` when the parent is itself a reply or
        belongs to another article. Enforced by a composite foreign key, so it
        holds regardless of what this method checks first."""
        ...

    async def update_body(self, *, comment_id: str, user_id: str, body: str) -> Comment | None:
        """Scoped by ``user_id`` so authorship is part of the query rather than
        a separate read the caller might forget to compare."""
        ...

    async def soft_delete(
        self, *, comment_id: str, deleted_by: str, now: datetime, as_admin: bool
    ) -> bool:
        """Tombstone a comment. A non-admin may only delete their own."""
        ...

    async def list_threads(
        self, *, blog_id: str, cursor: str | None, limit: int
    ) -> Page[CommentThread]:
        """Roots newest-first, each with its replies attached.

        Single-level threading is what makes this two indexed queries rather
        than a recursive CTE.
        """
        ...

    async def count_for_blog(self, blog_id: str) -> int: ...


class MarkerRepository(Protocol):
    async def upsert(
        self,
        *,
        user_id: str,
        blog_id: str,
        anchor: MarkerAnchor,
        progress_ratio: float | None,
        now: datetime,
    ) -> Marker:
        """One per user per article: placing again moves it."""
        ...

    async def get(self, *, user_id: str, blog_id: str) -> Marker | None: ...

    async def delete(self, *, user_id: str, blog_id: str) -> bool: ...

    async def list_for_user(self, *, user_id: str, limit: int) -> tuple[Marker, ...]: ...


class CatalogRepository(Protocol):
    async def get(self, catalog_id: str) -> Catalog | None: ...

    async def create(
        self, *, catalog_id: str, user_id: str, name: str, is_default: bool
    ) -> Catalog:
        """Raises ``CatalogNameTaken`` on a case-insensitive duplicate."""
        ...

    async def ensure_default(self, *, user_id: str, catalog_id: str) -> Catalog:
        """Return the user's default catalog, creating it if absent.

        Idempotent under concurrency: two simultaneous saves by a user with no
        catalog both end up with the same one, because the partial unique index
        makes the loser's insert fail and it re-reads.
        """
        ...

    async def rename(self, *, catalog_id: str, user_id: str, name: str) -> Catalog | None: ...

    async def delete(self, *, catalog_id: str, user_id: str) -> bool: ...

    async def list_for_user(self, user_id: str) -> tuple[Catalog, ...]: ...

    async def add_item(
        self, *, catalog_id: str, blog_id: str, note: str | None
    ) -> CatalogItem:
        """Idempotent: saving an article already in the catalog is not an error."""
        ...

    async def remove_item(self, *, catalog_id: str, blog_id: str) -> bool: ...

    async def list_items(
        self, *, catalog_id: str, cursor: str | None, limit: int
    ) -> Page[CatalogItem]: ...


class RecentViewRepository(Protocol):
    async def record(
        self, *, actor_id: str, user_id: str | None, blog_id: str, now: datetime
    ) -> None:
        """Upsert the projection. Called in the same transaction as the
        engagement append, so the two cannot disagree."""
        ...

    async def list_for_actor(self, *, actor_id: str, limit: int) -> tuple[RecentView, ...]: ...

    async def list_for_user(self, *, user_id: str, limit: int) -> tuple[RecentView, ...]: ...

    async def attribute_to_user(self, *, actor_id: str, user_id: str) -> int:
        """Backfill ``user_id`` for an actor that just signed in."""
        ...
