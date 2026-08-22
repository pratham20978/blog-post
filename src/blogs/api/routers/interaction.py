"""Comments, markers, catalogs, engagement and recent views.

The split that matters: engagement and recent views accept an anonymous caller,
everything else requires an account. That is the unauthenticated path made
concrete — a visitor generates the history their future account will inherit.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from blogs.api.deps import (
    Assembled,
    ClientIp,
    CorrelationId,
    CurrentPrincipal,
    CurrentUser,
)
from blogs.api.envelope import success
from blogs.contracts.common import APIResponse, ContractModel, NonEmptyStr, Page
from blogs.contracts.engagement import RecordEngagementCommand
from blogs.contracts.interaction import (
    Catalog,
    CatalogItem,
    Comment,
    CommentThread,
    Marker,
    MarkerAnchor,
    RecentView,
)

router = APIRouter(tags=["interaction"])


# ── Engagement — open to everyone ───────────────────────────────────────────


@router.post("/engagement", status_code=202)
async def record_engagement(
    body: RecordEngagementCommand,
    caller: CurrentPrincipal,
    assembled: Assembled,
    correlation: CorrelationId,
    ip: ClientIp,
) -> APIResponse[dict[str, bool]]:
    """Record one interaction.

    202, not 201: the write is accepted and the caller is not waiting on
    anything downstream. A duplicate reports ``recorded: false`` rather than an
    error — at-least-once beacons make that the normal case, not a fault.

    Note the command carries no actor, user or timestamp; the server supplies
    all three. A client that could set them could write engagement as anyone.
    """
    recorded = await assembled.engagement_service.record(
        principal=caller, command=body, client_ip=ip, correlation_id=correlation
    )
    return success({"recorded": recorded})


@router.get("/me/recent")
async def recent_views(
    caller: CurrentPrincipal,
    assembled: Assembled,
    limit: Annotated[int | None, Query(ge=1, le=50)] = None,
) -> APIResponse[tuple[RecentView, ...]]:
    """Recently read articles — by account when signed in, by actor otherwise.

    An anonymous visitor gets their own history back, and after signing in the
    same list is there, because the merge rewrote the rows rather than starting
    a new set.
    """
    views = await assembled.engagement_service.recent_views(
        principal=caller, limit=limit
    )
    return success(views)


# ── Comments ────────────────────────────────────────────────────────────────


class CommentBody(ContractModel):
    body: NonEmptyStr
    parent_comment_id: str | None = None


@router.get("/blogs/{blog_id}/comments")
async def list_comments(
    blog_id: str,
    assembled: Assembled,
    caller: CurrentPrincipal,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int | None, Query(ge=1, le=100)] = None,
) -> APIResponse[Page[CommentThread]]:
    """Root comments with their replies. Readable by anyone."""
    page = await assembled.interaction_service.list_comments(
        blog_id=blog_id, cursor=cursor, limit=limit
    )
    return success(page)


@router.post("/blogs/{blog_id}/comments", status_code=201)
async def create_comment(
    blog_id: str,
    body: CommentBody,
    user: CurrentUser,
    assembled: Assembled,
    correlation: CorrelationId,
) -> APIResponse[Comment]:
    """Comment, or reply to a comment.

    One root comment per person per article, and a reply may only attach to a
    root. Both are refused by the schema, so this route does not re-check them.
    """
    comment = await assembled.interaction_service.comment(
        principal=user,
        blog_id=blog_id,
        body=body.body,
        parent_comment_id=body.parent_comment_id,
        correlation_id=correlation,
    )
    return success(comment)


@router.patch("/comments/{comment_id}")
async def edit_comment(
    comment_id: str,
    body: CommentBody,
    user: CurrentUser,
    assembled: Assembled,
    correlation: CorrelationId,
) -> APIResponse[Comment]:
    comment = await assembled.interaction_service.edit_comment(
        principal=user, comment_id=comment_id, body=body.body, correlation_id=correlation
    )
    return success(comment)


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    user: CurrentUser,
    assembled: Assembled,
    correlation: CorrelationId,
) -> APIResponse[dict[str, str]]:
    """Delete your own comment; the admin may delete any."""
    await assembled.interaction_service.delete_comment(
        principal=user, comment_id=comment_id, correlation_id=correlation
    )
    return success({"comment_id": comment_id}, message="Deleted.")


# ── Markers ─────────────────────────────────────────────────────────────────


class MarkerBody(ContractModel):
    anchor: MarkerAnchor
    progress_ratio: float | None = None


@router.put("/blogs/{blog_id}/marker")
async def place_marker(
    blog_id: str,
    body: MarkerBody,
    user: CurrentUser,
    assembled: Assembled,
    correlation: CorrelationId,
) -> APIResponse[Marker]:
    """Save where you stopped.

    PUT, because there is exactly one marker per person per article and placing
    it again moves it. A section anchor is checked against the article's real
    headings, so a marker cannot point nowhere.
    """
    marker = await assembled.interaction_service.place_marker(
        principal=user,
        blog_id=blog_id,
        anchor=body.anchor,
        progress_ratio=body.progress_ratio,
        correlation_id=correlation,
    )
    return success(marker)


@router.get("/blogs/{blog_id}/marker")
async def get_marker(
    blog_id: str, user: CurrentUser, assembled: Assembled, correlation: CorrelationId
) -> APIResponse[Marker]:
    marker = await assembled.interaction_service.get_marker(
        principal=user, blog_id=blog_id, correlation_id=correlation
    )
    return success(marker)


@router.delete("/blogs/{blog_id}/marker")
async def delete_marker(
    blog_id: str, user: CurrentUser, assembled: Assembled, correlation: CorrelationId
) -> APIResponse[dict[str, str]]:
    await assembled.interaction_service.delete_marker(
        principal=user, blog_id=blog_id, correlation_id=correlation
    )
    return success({"blog_id": blog_id}, message="Marker removed.")


@router.get("/me/markers")
async def list_markers(
    user: CurrentUser, assembled: Assembled, correlation: CorrelationId
) -> APIResponse[tuple[Marker, ...]]:
    """Everywhere you left off — the "continue reading" list."""
    markers = await assembled.interaction_service.list_markers(
        principal=user, correlation_id=correlation
    )
    return success(markers)


# ── Catalogs ────────────────────────────────────────────────────────────────


class CatalogBody(ContractModel):
    name: NonEmptyStr


class SaveBody(ContractModel):
    blog_id: NonEmptyStr
    catalog_id: str | None = None
    note: str | None = None


@router.get("/me/catalogs")
async def list_catalogs(
    user: CurrentUser, assembled: Assembled, correlation: CorrelationId
) -> APIResponse[tuple[Catalog, ...]]:
    catalogs = await assembled.interaction_service.list_catalogs(
        principal=user, correlation_id=correlation
    )
    return success(catalogs)


@router.post("/me/catalogs", status_code=201)
async def create_catalog(
    body: CatalogBody, user: CurrentUser, assembled: Assembled, correlation: CorrelationId
) -> APIResponse[Catalog]:
    catalog = await assembled.interaction_service.create_catalog(
        principal=user, name=body.name, correlation_id=correlation
    )
    return success(catalog)


@router.post("/me/saves", status_code=201)
async def save_article(
    body: SaveBody, user: CurrentUser, assembled: Assembled, correlation: CorrelationId
) -> APIResponse[CatalogItem]:
    """Save an article, creating the default collection on first use."""
    item = await assembled.interaction_service.save_to_catalog(
        principal=user,
        blog_id=body.blog_id,
        catalog_id=body.catalog_id,
        note=body.note,
        correlation_id=correlation,
    )
    return success(item, message="Saved.")


@router.get("/me/catalogs/{catalog_id}/items")
async def list_catalog_items(
    catalog_id: str,
    user: CurrentUser,
    assembled: Assembled,
    correlation: CorrelationId,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int | None, Query(ge=1, le=100)] = None,
) -> APIResponse[Page[CatalogItem]]:
    page = await assembled.interaction_service.list_catalog_items(
        principal=user,
        catalog_id=catalog_id,
        cursor=cursor,
        limit=limit,
        correlation_id=correlation,
    )
    return success(page)


@router.delete("/me/catalogs/{catalog_id}/items/{blog_id}")
async def remove_catalog_item(
    catalog_id: str,
    blog_id: str,
    user: CurrentUser,
    assembled: Assembled,
    correlation: CorrelationId,
) -> APIResponse[dict[str, str]]:
    await assembled.interaction_service.remove_from_catalog(
        principal=user,
        catalog_id=catalog_id,
        blog_id=blog_id,
        correlation_id=correlation,
    )
    return success({"catalog_id": catalog_id, "blog_id": blog_id}, message="Removed.")
