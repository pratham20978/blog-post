"""Articles, their sections, and the taxonomy they hang off.

**Markdown is the only representation.** The source ``.md`` is what is stored
and what is served; there is no rendered HTML anywhere. Doc 00 §30 stops this
work at the HTTP port with no UI in scope, so choosing an HTML shape would be
deciding a presentation question on behalf of a client that does not exist yet.

Markdown is still *parsed* — for frontmatter metadata, for the heading anchors
that make pin targets and section markers validatable, and for the word count
F1 will need to normalise dwell time — but never re-emitted in another format.

No tags anywhere. F4 owns the canonical vocabulary and the weighting model
behind it; until that is settled the column, the index and the ``tag_keys``
field on ``BlogPublished`` do not exist here. Frontmatter ``tags:`` is parsed
and discarded, so nothing half-defined leaks into a contract other features
would then have to honour.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from blogs.contracts.common import (
    AnchorStr,
    BlogId,
    ContractModel,
    KeyStr,
    NonEmptyStr,
    PinId,
    SeriesId,
    UserId,
)


class BlogStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    #: Deletion is an archive. Comments, markers and engagement rows keep
    #: pointing at something real, and F1/F2 references never dangle.
    ARCHIVED = "archived"


class Category(ContractModel):
    key: KeyStr
    label: NonEmptyStr
    description: str | None = None


class Series(ContractModel):
    id: SeriesId
    key: KeyStr
    title: NonEmptyStr
    description: str | None = None


class BlogSection(ContractModel):
    """One heading in the article, extracted at publish time.

    Persisting these is what makes a reference pin's target and a marker's
    anchor *validatable* rather than a free string that may point nowhere.
    ``char_start``/``char_end`` are offsets into the stored Markdown body.
    """

    anchor: AnchorStr
    ordinal: int = Field(ge=0)
    level: int = Field(ge=1, le=6)
    title: NonEmptyStr
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)


class BlogSummary(ContractModel):
    """The list-view shape. Deliberately excludes body content."""

    id: BlogId
    slug: KeyStr
    title: NonEmptyStr
    summary: str | None = None
    status: BlogStatus
    series_id: SeriesId | None = None
    series_position: int | None = None
    category_keys: tuple[KeyStr, ...] = ()
    word_count: int = Field(ge=0)
    reading_minutes: int = Field(ge=0)
    published_at: datetime | None = None
    updated_at: datetime


class BlogDetail(ContractModel):
    """The read-one shape: metadata and structure, not body text.

    ``content_sha256`` is the ETag — content-addressed and immutable, so an
    anonymous reader caches for free and no Redis is needed.
    """

    id: BlogId
    slug: KeyStr
    title: NonEmptyStr
    summary: str | None = None
    status: BlogStatus
    author_id: UserId
    series_id: SeriesId | None = None
    series_position: int | None = None
    category_keys: tuple[KeyStr, ...] = ()
    sections: tuple[BlogSection, ...] = ()
    markdown_uri: NonEmptyStr
    content_sha256: NonEmptyStr
    word_count: int = Field(ge=0)
    reading_minutes: int = Field(ge=0)
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class BlogContent(ContractModel):
    """The article body, exactly as authored.

    This is the stored ``.md`` byte-for-byte, not a re-serialisation of it: the
    ETag is a hash of these bytes, so anything else would make the hash a lie.
    """

    blog_id: BlogId
    slug: KeyStr
    content_sha256: NonEmptyStr
    markdown: str


class PublishBlogCommand(ContractModel):
    """Metadata accompanying an uploaded ``.md``. Anything also present in the
    frontmatter is overridden by what is given here."""

    title: NonEmptyStr | None = None
    summary: str | None = None
    slug: KeyStr | None = None
    category_keys: tuple[KeyStr, ...] = ()
    series_key: KeyStr | None = None
    series_position: int | None = Field(default=None, ge=0)
    status: BlogStatus = BlogStatus.PUBLISHED


class UpdateBlogPatch(ContractModel):
    """A partial update. ``None`` means "leave alone"; there is deliberately no
    way to express "set back to null" for fields where that is meaningless.

    Note there is no tag field, and when F4 introduces one there still will not
    be: foundation §6.1 gives F4 the only write path to tags-on-blog.
    """

    title: NonEmptyStr | None = None
    summary: str | None = None
    category_keys: tuple[KeyStr, ...] | None = None
    series_key: KeyStr | None = None
    series_position: int | None = Field(default=None, ge=0)
    status: BlogStatus | None = None


class BlogFilter(ContractModel):
    """List-view filters. Without tags this is category, series and status."""

    category_key: KeyStr | None = None
    series_id: SeriesId | None = None
    status: BlogStatus = BlogStatus.PUBLISHED
    published_before: datetime | None = None


class ReferencePin(ContractModel):
    """An admin's pointer from one article to an exact section of another."""

    id: PinId
    source_blog_id: BlogId
    target_blog_id: BlogId
    target_anchor: AnchorStr
    note: str | None = None
    created_by: UserId
    created_at: datetime


class MarkdownHeading(ContractModel):
    anchor: AnchorStr
    level: int = Field(ge=1, le=6)
    title: NonEmptyStr
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)


class MarkdownDocument(ContractModel):
    """The parser's whole output.

    ``body`` is the source with frontmatter stripped — the exact bytes that get
    stored and hashed. Frontmatter ``tags`` never appears here.
    """

    title: NonEmptyStr | None = None
    summary: str | None = None
    slug: KeyStr | None = None
    category_keys: tuple[KeyStr, ...] = ()
    series_key: KeyStr | None = None
    series_position: int | None = None
    body: str
    headings: tuple[MarkdownHeading, ...] = ()
    word_count: int = Field(ge=0)
    content_sha256: NonEmptyStr
