"""Articles, their sections, and the taxonomy they hang off.

**Markdown is the only representation.** The source ``.md`` is what is stored
and what is served; there is no rendered HTML anywhere. Doc 00 §30 stops this
work at the HTTP port with no UI in scope, so choosing an HTML shape would be
deciding a presentation question on behalf of a client that does not exist yet.

Markdown is still *parsed* — for frontmatter metadata, for the heading anchors
that make pin targets and section markers validatable, and for the word count
F1 will need to normalise dwell time — but never re-emitted in another format.

Tags here are author-supplied, normalized keys. A future vocabulary service can
review and reassign them, but storing the source metadata now keeps the article
contract complete and gives downstream search a stable, indexed shape.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Self
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator

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


class BlogTier(StrEnum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


class BlogDifficulty(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


def _is_http_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.netloc)
        and not any(character.isspace() or character in "<>{}" for character in value)
    )


class BlogMetadata(ContractModel):
    """Typed metadata shared by list, detail, parser, and authoring inputs."""

    cover_image_url: str | None = None
    cover_image_alt: str | None = None
    tag_keys: tuple[KeyStr, ...] = ()
    tier: BlogTier | None = None
    difficulty: BlogDifficulty | None = None
    prerequisites: tuple[NonEmptyStr, ...] = ()
    canonical_url: str | None = None
    published_on: date | None = None
    content_updated_on: date | None = None

    @field_validator("cover_image_url", "canonical_url")
    @classmethod
    def _http_urls_only(cls, value: str | None) -> str | None:
        if value is not None and not _is_http_url(value):
            raise ValueError("must be an absolute http(s) URL")
        return value

    @field_validator("tag_keys")
    @classmethod
    def _deduplicated_tags(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("tag_keys must not contain duplicates")
        return value

    @model_validator(mode="after")
    def _cover_pair(self) -> Self:
        if (self.cover_image_url is None) != (self.cover_image_alt is None):
            raise ValueError("cover_image_url and cover_image_alt must be supplied together")
        return self


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


class BlogSummary(BlogMetadata):
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
    unique_reader_count: int = Field(default=0, ge=0)
    member_view_count: int = Field(default=0, ge=0)
    like_count: int = Field(default=0, ge=0)
    published_at: datetime | None = None
    updated_at: datetime


class BlogDetail(BlogMetadata):
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
    unique_reader_count: int = Field(default=0, ge=0)
    member_view_count: int = Field(default=0, ge=0)
    like_count: int = Field(default=0, ge=0)
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


class PublishBlogCommand(BlogMetadata):
    """Metadata accompanying an uploaded ``.md``. Anything also present in the
    frontmatter is overridden by what is given here."""

    title: NonEmptyStr | None = None
    summary: str | None = None
    slug: KeyStr | None = None
    category_keys: tuple[KeyStr, ...] | None = None
    series_key: KeyStr | None = None
    series_position: int | None = Field(default=None, ge=0)
    status: BlogStatus = BlogStatus.PUBLISHED


class UpdateBlogPatch(ContractModel):
    """A partial update. ``None`` means "leave alone"; there is deliberately no
    way to express "set back to null" for fields where that is meaningless.

    A source replacement is authoritative for editorial metadata. Values given
    here override the source; omitted values leave a metadata-only update alone.
    """

    title: NonEmptyStr | None = None
    summary: str | None = None
    category_keys: tuple[KeyStr, ...] | None = None
    series_key: KeyStr | None = None
    series_position: int | None = Field(default=None, ge=0)
    status: BlogStatus | None = None
    cover_image_url: str | None = None
    cover_image_alt: str | None = None
    tag_keys: tuple[KeyStr, ...] | None = None
    tier: BlogTier | None = None
    difficulty: BlogDifficulty | None = None
    prerequisites: tuple[NonEmptyStr, ...] | None = None
    canonical_url: str | None = None
    published_on: date | None = None
    content_updated_on: date | None = None

    @field_validator("cover_image_url", "canonical_url")
    @classmethod
    def _http_urls_only(cls, value: str | None) -> str | None:
        if value is not None and not _is_http_url(value):
            raise ValueError("must be an absolute http(s) URL")
        return value

    @field_validator("tag_keys")
    @classmethod
    def _deduplicated_tags(
        cls, value: tuple[str, ...] | None
    ) -> tuple[str, ...] | None:
        if value is not None and len(value) != len(set(value)):
            raise ValueError("tag_keys must not contain duplicates")
        return value

    @model_validator(mode="after")
    def _cover_pair(self) -> Self:
        if (self.cover_image_url is None) != (self.cover_image_alt is None):
            raise ValueError("cover_image_url and cover_image_alt must be supplied together")
        return self


class BlogFilter(ContractModel):
    """List-view filters for category, series, and publication status."""

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


class MarkdownDocument(BlogMetadata):
    """The parser's whole output.

    ``body`` is the source with frontmatter stripped — the exact bytes that get
    stored and hashed.
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
