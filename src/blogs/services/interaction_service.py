"""Comments, markers, catalogs and reference pins.

Grouped because they share one shape: a signed-in reader acting on an article
they can see. Each use case checks the policy, confirms the article is visible,
and lets the schema enforce the invariant — a second root comment, a reply to a
reply, a second default catalog are all refused by an index or a foreign key,
and the repository turns that refusal into the right error.
"""

from __future__ import annotations

import logging

from blogs.contracts.blog import BlogStatus, ReferencePin
from blogs.contracts.common import ErrorCategory, Page
from blogs.contracts.identity import Principal, UserPrincipal
from blogs.contracts.interaction import (
    Catalog,
    CatalogItem,
    Comment,
    CommentThread,
    Marker,
    MarkerAnchor,
    RangeAnchor,
    SectionAnchor,
)
from blogs.core.clock import Clock
from blogs.core.errors import raise_error
from blogs.core.ids import IdGenerator
from blogs.ports.services import AuthorizationPolicy
from blogs.ports.uow import UnitOfWorkFactory
from blogs.services.policy import require

logger = logging.getLogger(__name__)


class InteractionService:
    def __init__(
        self,
        *,
        uow: UnitOfWorkFactory,
        clock: Clock,
        ids: IdGenerator,
        policy: AuthorizationPolicy,
        default_page_size: int = 20,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._ids = ids
        self._policy = policy
        self._default_page_size = default_page_size

    # ── Comments ────────────────────────────────────────────────────────────

    async def comment(
        self,
        *,
        principal: Principal,
        blog_id: str,
        body: str,
        parent_comment_id: str | None = None,
        correlation_id: str | None = None,
    ) -> Comment:
        require(
            self._policy.can_comment(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)

        async with self._uow.begin() as uow:
            await self._assert_readable(uow, blog_id, correlation_id=correlation_id)
            if parent_comment_id is None:
                return await uow.comments.create_root(
                    comment_id=self._ids.new_id(),
                    blog_id=blog_id,
                    user_id=principal.user_id,
                    body=body,
                )
            # No check that the parent is a root: the composite foreign key
            # decides, atomically, and a pre-check here would be a race.
            return await uow.comments.create_reply(
                comment_id=self._ids.new_id(),
                blog_id=blog_id,
                user_id=principal.user_id,
                parent_comment_id=parent_comment_id,
                body=body,
            )

    async def edit_comment(
        self,
        *,
        principal: Principal,
        comment_id: str,
        body: str,
        correlation_id: str | None = None,
    ) -> Comment:
        require(
            self._policy.can_comment(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)
        async with self._uow.begin() as uow:
            updated = await uow.comments.update_body(
                comment_id=comment_id, user_id=principal.user_id, body=body
            )
        if updated is None:
            # Ownership is part of the UPDATE predicate, so "not yours" and
            # "not there" arrive as the same miss — and are reported the same
            # way, which is also what stops this being a probe for who wrote what.
            raise_error(ErrorCategory.COMMENT_NOT_FOUND, correlation_id=correlation_id)
        return updated

    async def delete_comment(
        self, *, principal: Principal, comment_id: str, correlation_id: str | None = None
    ) -> None:
        require(
            self._policy.can_comment(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)
        async with self._uow.begin() as uow:
            deleted = await uow.comments.soft_delete(
                comment_id=comment_id,
                deleted_by=principal.user_id,
                now=self._clock.now(),
                as_admin=self._policy.can_moderate(principal),
            )
        if not deleted:
            raise_error(ErrorCategory.COMMENT_NOT_FOUND, correlation_id=correlation_id)

    async def list_comments(
        self, *, blog_id: str, cursor: str | None = None, limit: int | None = None
    ) -> Page[CommentThread]:
        async with self._uow.read() as uow:
            return await uow.comments.list_threads(
                blog_id=blog_id,
                cursor=cursor,
                limit=limit or self._default_page_size,
            )

    # ── Markers ─────────────────────────────────────────────────────────────

    async def place_marker(
        self,
        *,
        principal: Principal,
        blog_id: str,
        anchor: MarkerAnchor,
        progress_ratio: float | None = None,
        correlation_id: str | None = None,
    ) -> Marker:
        """Save where the reader stopped. Placing again moves it."""
        require(
            self._policy.can_mark(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)

        async with self._uow.begin() as uow:
            await self._assert_readable(uow, blog_id, correlation_id=correlation_id)
            await self._assert_anchors_exist(
                uow, blog_id=blog_id, anchor=anchor, correlation_id=correlation_id
            )
            return await uow.markers.upsert(
                user_id=principal.user_id,
                blog_id=blog_id,
                anchor=anchor,
                progress_ratio=progress_ratio,
                now=self._clock.now(),
            )

    async def get_marker(
        self, *, principal: Principal, blog_id: str, correlation_id: str | None = None
    ) -> Marker:
        require(
            self._policy.can_mark(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)
        async with self._uow.read() as uow:
            marker = await uow.markers.get(user_id=principal.user_id, blog_id=blog_id)
        if marker is None:
            raise_error(ErrorCategory.MARKER_NOT_FOUND, correlation_id=correlation_id)
        return marker

    async def delete_marker(
        self, *, principal: Principal, blog_id: str, correlation_id: str | None = None
    ) -> None:
        require(
            self._policy.can_mark(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)
        async with self._uow.begin() as uow:
            if not await uow.markers.delete(user_id=principal.user_id, blog_id=blog_id):
                raise_error(ErrorCategory.MARKER_NOT_FOUND, correlation_id=correlation_id)

    async def list_markers(
        self, *, principal: Principal, correlation_id: str | None = None
    ) -> tuple[Marker, ...]:
        require(
            self._policy.can_mark(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)
        async with self._uow.read() as uow:
            return await uow.markers.list_for_user(user_id=principal.user_id, limit=100)

    # ── Catalogs ────────────────────────────────────────────────────────────

    async def save_to_catalog(
        self,
        *,
        principal: Principal,
        blog_id: str,
        catalog_id: str | None = None,
        note: str | None = None,
        correlation_id: str | None = None,
    ) -> CatalogItem:
        """Save an article, creating the default collection on first use."""
        require(
            self._policy.can_save(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)

        async with self._uow.begin() as uow:
            await self._assert_readable(uow, blog_id, correlation_id=correlation_id)

            if catalog_id is None:
                catalog = await uow.catalogs.ensure_default(
                    user_id=principal.user_id, catalog_id=self._ids.new_id()
                )
            else:
                catalog = await uow.catalogs.get(catalog_id)
                # Ownership checked explicitly here rather than folded into the
                # query: saving into somebody else's collection must be a
                # refusal, not a silent no-op.
                if catalog is None or catalog.user_id != principal.user_id:
                    raise_error(
                        ErrorCategory.CATALOG_NOT_FOUND, correlation_id=correlation_id
                    )
            return await uow.catalogs.add_item(
                catalog_id=catalog.id, blog_id=blog_id, note=note
            )

    async def create_catalog(
        self, *, principal: Principal, name: str, correlation_id: str | None = None
    ) -> Catalog:
        require(
            self._policy.can_save(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)
        async with self._uow.begin() as uow:
            return await uow.catalogs.create(
                catalog_id=self._ids.new_id(),
                user_id=principal.user_id,
                name=name,
                is_default=False,
            )

    async def list_catalogs(
        self, *, principal: Principal, correlation_id: str | None = None
    ) -> tuple[Catalog, ...]:
        require(
            self._policy.can_save(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)
        async with self._uow.read() as uow:
            return await uow.catalogs.list_for_user(principal.user_id)

    async def list_catalog_items(
        self,
        *,
        principal: Principal,
        catalog_id: str,
        cursor: str | None = None,
        limit: int | None = None,
        correlation_id: str | None = None,
    ) -> Page[CatalogItem]:
        require(
            self._policy.can_save(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)
        async with self._uow.read() as uow:
            catalog = await uow.catalogs.get(catalog_id)
            if catalog is None or catalog.user_id != principal.user_id:
                raise_error(
                    ErrorCategory.CATALOG_NOT_FOUND, correlation_id=correlation_id
                )
            return await uow.catalogs.list_items(
                catalog_id=catalog_id,
                cursor=cursor,
                limit=limit or self._default_page_size,
            )

    async def remove_from_catalog(
        self,
        *,
        principal: Principal,
        catalog_id: str,
        blog_id: str,
        correlation_id: str | None = None,
    ) -> None:
        require(
            self._policy.can_save(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)
        async with self._uow.begin() as uow:
            catalog = await uow.catalogs.get(catalog_id)
            if catalog is None or catalog.user_id != principal.user_id:
                raise_error(
                    ErrorCategory.CATALOG_NOT_FOUND, correlation_id=correlation_id
                )
            await uow.catalogs.remove_item(catalog_id=catalog_id, blog_id=blog_id)

    # ── Reference pins (admin) ──────────────────────────────────────────────

    async def create_pin(
        self,
        *,
        principal: Principal,
        source_blog_id: str,
        target_blog_id: str,
        target_anchor: str,
        note: str | None = None,
        correlation_id: str | None = None,
    ) -> ReferencePin:
        require(
            self._policy.can_manage_pins(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        assert isinstance(principal, UserPrincipal)
        async with self._uow.begin() as uow:
            return await uow.pins.create(
                pin_id=self._ids.new_id(),
                source_blog_id=source_blog_id,
                target_blog_id=target_blog_id,
                target_anchor=target_anchor,
                note=note,
                created_by=principal.user_id,
            )

    async def delete_pin(
        self, *, principal: Principal, pin_id: str, correlation_id: str | None = None
    ) -> None:
        require(
            self._policy.can_manage_pins(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        async with self._uow.begin() as uow:
            if not await uow.pins.delete(pin_id):
                raise_error(ErrorCategory.PIN_NOT_FOUND, correlation_id=correlation_id)

    async def list_pins(
        self, *, blog_id: str, inbound: bool = False
    ) -> tuple[ReferencePin, ...]:
        async with self._uow.read() as uow:
            if inbound:
                return await uow.pins.list_for_target(blog_id)
            return await uow.pins.list_for_source(blog_id)

    # ── Internals ───────────────────────────────────────────────────────────

    async def _assert_readable(  # type: ignore[no-untyped-def]
        self, uow, blog_id: str, *, correlation_id: str | None
    ) -> None:
        blog = await uow.blogs.get(blog_id)
        if blog is None or blog.status is not BlogStatus.PUBLISHED:
            # Draft and archived articles report as missing rather than as
            # forbidden: confirming an unpublished slug exists leaks the
            # editorial pipeline.
            raise_error(ErrorCategory.BLOG_NOT_FOUND, correlation_id=correlation_id)

    async def _assert_anchors_exist(  # type: ignore[no-untyped-def]
        self,
        uow,
        *,
        blog_id: str,
        anchor: MarkerAnchor,
        correlation_id: str | None,
    ) -> None:
        """Refuse a marker that points at a heading the article does not have.

        Only the section-shaped anchors carry a heading; an ``OffsetAnchor`` has
        nothing to check, which is part of why it is the fallback rather than
        the default.
        """
        anchors: tuple[str, ...]
        if isinstance(anchor, SectionAnchor):
            anchors = (anchor.anchor,)
        elif isinstance(anchor, RangeAnchor):
            anchors = (anchor.start_anchor, anchor.end_anchor)
        else:
            return

        for value in anchors:
            if not await uow.sections.exists(blog_id=blog_id, anchor=value):
                raise_error(
                    ErrorCategory.SECTION_ANCHOR_UNKNOWN,
                    correlation_id=correlation_id,
                    safe_details={"anchor": value},
                )
