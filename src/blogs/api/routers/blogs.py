"""Reading articles. Open to anonymous callers by design."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, Request, Response

from blogs.api.deps import Assembled, CorrelationId, CurrentPrincipal
from blogs.api.envelope import success
from blogs.contracts.blog import (
    BlogContent,
    BlogDetail,
    BlogFilter,
    BlogSection,
    BlogStatus,
    BlogSummary,
    ReferencePin,
)
from blogs.contracts.common import APIResponse, Page
from blogs.core.errors import NotModified

router = APIRouter(tags=["blogs"])


@router.get("/blogs")
async def list_blogs(
    assembled: Assembled,
    caller: CurrentPrincipal,
    category: Annotated[str | None, Query()] = None,
    series_id: Annotated[str | None, Query()] = None,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int | None, Query(ge=1, le=100)] = None,
) -> APIResponse[Page[BlogSummary]]:
    """The feed.

    ``status`` is not a parameter: this endpoint only ever serves published
    articles. Letting a caller ask for drafts would put the check in the wrong
    place, so admin listings are a separate, gated route.
    """
    page = await assembled.blog_service.list(
        filter=BlogFilter(
            category_key=category, series_id=series_id, status=BlogStatus.PUBLISHED
        ),
        cursor=cursor,
        limit=limit,
    )
    return success(page)


@router.get("/blogs/{slug}")
async def get_blog(
    slug: str,
    assembled: Assembled,
    caller: CurrentPrincipal,
    correlation: CorrelationId,
) -> APIResponse[BlogDetail]:
    blog = await assembled.blog_service.get_by_slug(
        slug=slug, principal=caller, correlation_id=correlation
    )
    return success(blog)


@router.get(
    "/blogs/{slug}/content",
    responses={304: {"description": "Cached copy is current; no body is sent."}},
)
async def get_blog_content(
    slug: str,
    request: Request,
    response: Response,
    assembled: Assembled,
    caller: CurrentPrincipal,
    correlation: CorrelationId,
) -> APIResponse[BlogContent]:
    """The article body, as Markdown.

    The ETag is the content hash, so it is both strong and free — and the
    conditional check happens before the object store is touched, which is what
    lets an unchanged article be answered without any I/O at all. That is the
    caching story for anonymous readers without a cache server.

    The 304 leaves via ``NotModified`` rather than as a returned ``Response``,
    so this signature stays a single concrete type instead of degrading to a
    union that neither the type checker nor OpenAPI can describe.
    """
    blog = await assembled.blog_service.get_by_slug(
        slug=slug, principal=caller, correlation_id=correlation
    )
    etag = f'"{blog.content_sha256}"'

    if request.headers.get("if-none-match") == etag:
        raise NotModified(etag)

    content = await assembled.blog_service.get_content(
        slug=slug, principal=caller, correlation_id=correlation
    )
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=60"
    response.headers["Content-Language"] = "en"
    return success(content)


@router.get("/blogs/{slug}/sections")
async def get_blog_sections(
    slug: str,
    assembled: Assembled,
    caller: CurrentPrincipal,
    correlation: CorrelationId,
) -> APIResponse[tuple[BlogSection, ...]]:
    """The article's headings — the anchors a marker or a pin may address."""
    blog = await assembled.blog_service.get_by_slug(
        slug=slug, principal=caller, correlation_id=correlation
    )
    return success(blog.sections)


@router.get("/blogs/{slug}/references")
async def get_blog_references(
    slug: str,
    assembled: Assembled,
    caller: CurrentPrincipal,
    correlation: CorrelationId,
    inbound: Annotated[bool, Query()] = False,
) -> APIResponse[tuple[ReferencePin, ...]]:
    """Reference pins. Outbound by default; ``inbound=true`` for what cites this."""
    blog = await assembled.blog_service.get_by_slug(
        slug=slug, principal=caller, correlation_id=correlation
    )
    pins = await assembled.interaction_service.list_pins(
        blog_id=blog.id, inbound=inbound
    )
    return success(pins)
