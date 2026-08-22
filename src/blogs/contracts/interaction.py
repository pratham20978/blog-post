"""What a reader does with an article: comment, mark a position, save it.

All three are user-only. An anonymous visitor reads and generates engagement;
these require an account (see ``services.policy``).
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from blogs.contracts.common import (
    AnchorStr,
    BlogId,
    CatalogId,
    CommentId,
    ContractModel,
    NonEmptyStr,
    UserId,
)

CommentBody = Annotated[str, Field(min_length=1, max_length=10_000)]
CatalogName = Annotated[str, Field(min_length=1, max_length=120)]


class Comment(ContractModel):
    """Threads are single-level: ``depth`` is 0 or 1 and nothing else.

    A user gets exactly one depth-0 comment per article. Replies are exempt from
    that rule. Both facts are enforced in the schema — a partial unique index
    for the first, a composite foreign key for the second — so neither depends
    on application code remembering to check.
    """

    id: CommentId
    blog_id: BlogId
    user_id: UserId
    parent_comment_id: CommentId | None = None
    depth: int = Field(ge=0, le=1)
    body: CommentBody
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class CommentThread(ContractModel):
    """A root comment with its replies, which is the only shape a single-level
    thread can take. No recursion, no materialised path, no depth cap."""

    root: Comment
    replies: tuple[Comment, ...] = ()


# ---------------------------------------------------------------------------
# Marker anchors — doc 01 open question 3, answered as a closed union
# ---------------------------------------------------------------------------


class SectionAnchor(ContractModel):
    """Position expressed as a heading plus an offset inside that section.

    The default, because it survives edits: inserting a paragraph above shifts
    every character offset in the document but leaves the heading alone. The
    anchor is validated against ``blog_sections``, so a marker cannot point at a
    section that does not exist.
    """

    kind: Literal["section"] = "section"
    anchor: AnchorStr
    offset_in_section: int = Field(default=0, ge=0)


class OffsetAnchor(ContractModel):
    """A raw character offset into the Markdown body.

    The fallback for a document with no headings. Brittle across edits by
    nature, which is exactly why it is not the default.
    """

    kind: Literal["offset"] = "offset"
    char_offset: int = Field(ge=0)


class RangeAnchor(ContractModel):
    """A span, not a point — a highlight rather than a bookmark.

    Present now so that F1's highlight-to-search entry point has a shape to
    reuse instead of inventing a second, incompatible one later.
    """

    kind: Literal["range"] = "range"
    start_anchor: AnchorStr
    start_offset: int = Field(default=0, ge=0)
    end_anchor: AnchorStr
    end_offset: int = Field(default=0, ge=0)


MarkerAnchor = Annotated[
    SectionAnchor | OffsetAnchor | RangeAnchor, Field(discriminator="kind")
]


class Marker(ContractModel):
    """One per user per article — updating moves it rather than adding one.

    ``progress_ratio`` is stored beside the anchor rather than derived from it
    so a "continue reading" list never has to interpret the anchor payload.
    """

    user_id: UserId
    blog_id: BlogId
    anchor: MarkerAnchor
    progress_ratio: float | None = Field(default=None, ge=0.0, le=1.0)
    updated_at: datetime


# ---------------------------------------------------------------------------
# Catalogs
# ---------------------------------------------------------------------------


class Catalog(ContractModel):
    id: CatalogId
    user_id: UserId
    name: CatalogName
    #: Saving without naming a catalog lands here. A partial unique index keeps
    #: a user from ever having two.
    is_default: bool = False
    item_count: int = Field(default=0, ge=0)
    created_at: datetime
    updated_at: datetime


class CatalogItem(ContractModel):
    catalog_id: CatalogId
    blog_id: BlogId
    added_at: datetime
    note: str | None = None


class RecentView(ContractModel):
    """A projection maintained alongside the engagement log.

    Keyed by actor rather than user, so an anonymous reader has recent views
    too and merging on login is a matter of filling in ``user_id``.
    """

    blog_id: BlogId
    title: NonEmptyStr
    slug: NonEmptyStr
    last_viewed_at: datetime
    view_count: int = Field(ge=1)
