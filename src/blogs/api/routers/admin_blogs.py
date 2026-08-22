"""Authoring. Every route here is admin-only, enforced by the ``AdminUser``
dependency before the handler body runs."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, Form, Query, UploadFile

from blogs.api.deps import AdminUser, Assembled, CorrelationId
from blogs.api.envelope import success
from blogs.contracts.blog import (
    BlogDetail,
    BlogFilter,
    BlogStatus,
    BlogSummary,
    Category,
    PublishBlogCommand,
    ReferencePin,
    Series,
    UpdateBlogPatch,
)
from blogs.contracts.common import APIResponse, ContractModel, KeyStr, NonEmptyStr, Page

router = APIRouter(prefix="/admin", tags=["admin"])


def _csv_keys(value: str | None) -> tuple[str, ...]:
    """Multipart has no native list type, so repeated keys arrive comma-joined."""
    if not value:
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


@router.post("/blogs", status_code=201)
async def publish_blog(
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
    file: Annotated[UploadFile, File(description="The article source, a .md file")],
    title: Annotated[str | None, Form()] = None,
    summary: Annotated[str | None, Form()] = None,
    slug: Annotated[str | None, Form()] = None,
    categories: Annotated[str | None, Form()] = None,
    series: Annotated[str | None, Form()] = None,
    series_position: Annotated[int | None, Form()] = None,
    status: Annotated[BlogStatus, Form()] = BlogStatus.PUBLISHED,
) -> APIResponse[BlogDetail]:
    """Publish an article from an uploaded Markdown file.

    Anything given here overrides the file's frontmatter, so a mistake in the
    document can be corrected at upload without editing and re-uploading it.
    """
    source = await file.read()
    result = await assembled.blog_service.publish_from_markdown(
        principal=admin,
        source=source,
        command=PublishBlogCommand(
            title=title,
            summary=summary,
            slug=slug,
            category_keys=_csv_keys(categories),
            series_key=series,
            series_position=series_position,
            status=status,
        ),
        correlation_id=correlation,
    )
    return success(result.blog, message="Published.")


@router.patch("/blogs/{blog_id}")
async def update_blog(
    blog_id: str,
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
    file: Annotated[UploadFile | None, File()] = None,
    title: Annotated[str | None, Form()] = None,
    summary: Annotated[str | None, Form()] = None,
    categories: Annotated[str | None, Form()] = None,
    series: Annotated[str | None, Form()] = None,
    series_position: Annotated[int | None, Form()] = None,
    status: Annotated[BlogStatus | None, Form()] = None,
) -> APIResponse[BlogDetail]:
    """Amend metadata, replace the source, or both.

    There is no tag parameter, and there will not be one even after F4 lands:
    foundation §6.1 gives F4 the only write path to tags-on-blog.
    """
    source = await file.read() if file is not None else None
    blog = await assembled.blog_service.update(
        principal=admin,
        blog_id=blog_id,
        patch=UpdateBlogPatch(
            title=title,
            summary=summary,
            category_keys=_csv_keys(categories) if categories is not None else None,
            series_key=series,
            series_position=series_position,
            status=status,
        ),
        source=source,
        correlation_id=correlation,
    )
    return success(blog, message="Updated.")


@router.delete("/blogs/{blog_id}")
async def archive_blog(
    blog_id: str,
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
) -> APIResponse[dict[str, str]]:
    """Retire an article.

    DELETE archives rather than destroys. Comments, markers, catalog entries and
    the engagement log all reference this article, and removing the row would
    either cascade them away or leave the log pointing at nothing.
    """
    await assembled.blog_service.archive(
        principal=admin, blog_id=blog_id, correlation_id=correlation
    )
    return success({"blog_id": blog_id, "status": "archived"}, message="Archived.")


@router.get("/blogs")
async def list_all_blogs(
    admin: AdminUser,
    assembled: Assembled,
    status: Annotated[BlogStatus, Query()] = BlogStatus.DRAFT,
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int | None, Query(ge=1, le=100)] = None,
) -> APIResponse[Page[BlogSummary]]:
    """The admin listing, which is the only way to see drafts and archives."""
    page = await assembled.blog_service.list(
        filter=BlogFilter(status=status), cursor=cursor, limit=limit
    )
    return success(page)


# ── Reference pins ──────────────────────────────────────────────────────────


class PinBody(ContractModel):
    source_blog_id: NonEmptyStr
    target_blog_id: NonEmptyStr
    target_anchor: NonEmptyStr
    note: str | None = None


@router.post("/pins", status_code=201)
async def create_pin(
    body: PinBody,
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
) -> APIResponse[ReferencePin]:
    """Point at an exact section of another article.

    The anchor is checked against ``blog_sections`` by a foreign key, so a pin
    to a heading that does not exist is refused rather than stored and
    discovered broken by a reader.
    """
    pin = await assembled.interaction_service.create_pin(
        principal=admin,
        source_blog_id=body.source_blog_id,
        target_blog_id=body.target_blog_id,
        target_anchor=body.target_anchor,
        note=body.note,
        correlation_id=correlation,
    )
    return success(pin, message="Pinned.")


@router.delete("/pins/{pin_id}")
async def delete_pin(
    pin_id: str,
    admin: AdminUser,
    assembled: Assembled,
    correlation: CorrelationId,
) -> APIResponse[dict[str, str]]:
    await assembled.interaction_service.delete_pin(
        principal=admin, pin_id=pin_id, correlation_id=correlation
    )
    return success({"pin_id": pin_id}, message="Removed.")


# ── Taxonomy ────────────────────────────────────────────────────────────────


class CategoryBody(ContractModel):
    key: KeyStr
    label: NonEmptyStr
    description: str | None = None


class SeriesBody(ContractModel):
    key: KeyStr
    title: NonEmptyStr
    description: str | None = None


@router.put("/categories")
async def upsert_category(
    body: CategoryBody, admin: AdminUser, assembled: Assembled
) -> APIResponse[Category]:
    async with assembled.uow.begin() as uow:
        category = await uow.taxonomy.upsert_category(
            key=body.key, label=body.label, description=body.description
        )
    return success(category)


@router.put("/series")
async def upsert_series(
    body: SeriesBody, admin: AdminUser, assembled: Assembled
) -> APIResponse[Series]:
    async with assembled.uow.begin() as uow:
        series = await uow.taxonomy.upsert_series(
            series_id=assembled.ids.new_id(),
            key=body.key,
            title=body.title,
            description=body.description,
        )
    return success(series)
