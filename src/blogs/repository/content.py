"""SQL adapters for articles, sections, taxonomy and reference pins."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from psycopg import errors
from psycopg.rows import DictRow

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
from blogs.contracts.common import ErrorCategory, Page
from blogs.core.errors import BlogPlatformError
from blogs.repository.base import (
    SqlRepository,
    as_utc,
    decode_cursor,
    encode_cursor,
    translate_integrity_error,
)

_BLOG_COLUMNS = """
    b.id, b.slug, b.title, b.summary, b.author_id, b.series_id, b.series_position,
    b.markdown_uri, b.content_sha256, b.word_count, b.reading_minutes,
    b.status, b.published_at, b.archived_at, b.created_at, b.updated_at
"""

# Categories come back as an aggregated array rather than as extra rows, so
# reading one article is one round trip instead of two. FILTER drops the NULL a
# LEFT JOIN produces for an article with no categories, which would otherwise
# become a one-element array containing null.
_CATEGORY_AGG = """
    COALESCE(
        array_agg(bc.category_key ORDER BY bc.category_key)
            FILTER (WHERE bc.category_key IS NOT NULL),
        ARRAY[]::text[]
    ) AS category_keys
"""


def _categories(row: DictRow) -> tuple[str, ...]:
    return tuple(row.get("category_keys") or ())


def _to_detail(row: DictRow, sections: tuple[BlogSection, ...] = ()) -> BlogDetail:
    return BlogDetail(
        id=str(row["id"]),
        slug=row["slug"],
        title=row["title"],
        summary=row["summary"],
        status=BlogStatus(row["status"]),
        author_id=str(row["author_id"]),
        series_id=str(row["series_id"]) if row["series_id"] else None,
        series_position=row["series_position"],
        category_keys=_categories(row),
        sections=sections,
        markdown_uri=row["markdown_uri"],
        content_sha256=bytes(row["content_sha256"]).hex(),
        word_count=row["word_count"],
        reading_minutes=row["reading_minutes"],
        published_at=row["published_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _to_summary(row: DictRow) -> BlogSummary:
    return BlogSummary(
        id=str(row["id"]),
        slug=row["slug"],
        title=row["title"],
        summary=row["summary"],
        status=BlogStatus(row["status"]),
        series_id=str(row["series_id"]) if row["series_id"] else None,
        series_position=row["series_position"],
        category_keys=_categories(row),
        word_count=row["word_count"],
        reading_minutes=row["reading_minutes"],
        published_at=row["published_at"],
        updated_at=row["updated_at"],
    )


def _to_section(row: DictRow) -> BlogSection:
    return BlogSection(
        anchor=row["anchor"],
        ordinal=row["ordinal"],
        level=row["level"],
        title=row["title"],
        char_start=row["char_start"],
        char_end=row["char_end"],
    )


class SqlBlogRepository(SqlRepository):
    async def _one(self, where: str, params: dict[str, Any]) -> BlogDetail | None:
        row = await self._fetch_one(
            f"""
            SELECT {_BLOG_COLUMNS}, {_CATEGORY_AGG}
            FROM blogs b
            LEFT JOIN blog_categories bc ON bc.blog_id = b.id
            WHERE {where}
            GROUP BY b.id
            """,
            params,
        )
        if row is None:
            return None
        sections = await self._fetch_all(
            "SELECT anchor, ordinal, level, title, char_start, char_end "
            "FROM blog_sections WHERE blog_id = %(id)s ORDER BY ordinal",
            {"id": row["id"]},
        )
        return _to_detail(row, tuple(_to_section(s) for s in sections))

    async def get(self, blog_id: str) -> BlogDetail | None:
        return await self._one("b.id = %(id)s", {"id": blog_id})

    async def get_by_slug(self, slug: str) -> BlogDetail | None:
        return await self._one("b.slug = %(slug)s", {"slug": slug})

    async def slug_exists(self, slug: str) -> bool:
        row = await self._fetch_one(
            "SELECT 1 AS hit FROM blogs WHERE slug = %(slug)s", {"slug": slug}
        )
        return row is not None

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
        try:
            row = await self._fetch_one(
                f"""
                INSERT INTO blogs
                    (id, slug, title, summary, author_id, series_id, series_position,
                     markdown_uri, content_sha256, word_count, status, published_at)
                VALUES
                    (%(id)s, %(slug)s, %(title)s, %(summary)s, %(author)s,
                     %(series)s, %(pos)s, %(uri)s, %(sha)s, %(words)s,
                     %(status)s, %(published)s)
                RETURNING {_BLOG_COLUMNS.replace("b.", "")}
                """,
                {
                    "id": blog_id,
                    "slug": slug,
                    "title": title,
                    "summary": summary,
                    "author": author_id,
                    "series": series_id,
                    "pos": series_position,
                    "uri": markdown_uri,
                    "sha": content_sha256,
                    "words": word_count,
                    "status": status.value,
                    "published": as_utc(published_at) if published_at else None,
                },
            )
        except errors.IntegrityError as exc:
            raise translate_integrity_error(exc) from exc
        assert row is not None
        row["category_keys"] = []
        return _to_detail(row)

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
    ) -> BlogDetail | None:
        # COALESCE per column so "not supplied" means "leave alone" without
        # building the SET clause by string concatenation.
        try:
            row = await self._fetch_one(
                """
                UPDATE blogs SET
                    title           = COALESCE(%(title)s, title),
                    summary         = COALESCE(%(summary)s, summary),
                    series_id       = COALESCE(%(series)s, series_id),
                    series_position = COALESCE(%(pos)s, series_position),
                    status          = COALESCE(%(status)s, status),
                    published_at    = CASE
                        WHEN %(status)s = 'published' AND published_at IS NULL
                        THEN %(published)s ELSE published_at END
                WHERE id = %(id)s
                RETURNING id
                """,
                {
                    "id": blog_id,
                    "title": title,
                    "summary": summary,
                    "series": series_id,
                    "pos": series_position,
                    "status": status.value if status else None,
                    "published": as_utc(published_at) if published_at else None,
                },
            )
        except errors.IntegrityError as exc:
            raise translate_integrity_error(exc) from exc
        if row is None:
            return None
        return await self.get(blog_id)

    async def update_content(
        self, *, blog_id: str, markdown_uri: str, content_sha256: bytes, word_count: int
    ) -> None:
        await self._execute(
            """
            UPDATE blogs
            SET markdown_uri = %(uri)s, content_sha256 = %(sha)s, word_count = %(words)s
            WHERE id = %(id)s
            """,
            {"uri": markdown_uri, "sha": content_sha256, "words": word_count, "id": blog_id},
        )

    async def archive(self, *, blog_id: str, at: datetime) -> bool:
        affected = await self._execute(
            """
            UPDATE blogs SET status = 'archived', archived_at = %(at)s
            WHERE id = %(id)s AND status <> 'archived'
            """,
            {"at": as_utc(at), "id": blog_id},
        )
        return affected == 1

    async def list(
        self, *, filter: BlogFilter, cursor: str | None, limit: int
    ) -> Page[BlogSummary]:
        """Keyset-paginated, newest first.

        The predicate is a row comparison on ``(published_at, id)`` rather than
        an OFFSET: it uses the ``blogs_feed`` index directly, costs the same at
        page 1 and page 500, and cannot skip or repeat a row when something is
        published mid-scroll.
        """
        params: dict[str, Any] = {"status": filter.status.value, "limit": limit + 1}
        clauses = ["b.status = %(status)s"]

        if filter.category_key is not None:
            clauses.append(
                "EXISTS (SELECT 1 FROM blog_categories x "
                "WHERE x.blog_id = b.id AND x.category_key = %(category)s)"
            )
            params["category"] = filter.category_key
        if filter.series_id is not None:
            clauses.append("b.series_id = %(series)s")
            params["series"] = filter.series_id
        if filter.published_before is not None:
            clauses.append("b.published_at < %(before)s")
            params["before"] = as_utc(filter.published_before)

        if cursor:
            keys = decode_cursor(cursor)
            if "published_at" not in keys or "id" not in keys:
                raise BlogPlatformError(
                    ErrorCategory.REQUEST_INVALID, safe_details={"reason": "MALFORMED_CURSOR"}
                )
            clauses.append(
                "(b.published_at, b.id) < (%(cur_published)s::timestamptz, %(cur_id)s::uuid)"
            )
            params["cur_published"] = keys["published_at"]
            params["cur_id"] = keys["id"]

        rows = await self._fetch_all(
            f"""
            SELECT {_BLOG_COLUMNS}, {_CATEGORY_AGG}
            FROM blogs b
            LEFT JOIN blog_categories bc ON bc.blog_id = b.id
            WHERE {" AND ".join(clauses)}
            GROUP BY b.id
            ORDER BY b.published_at DESC, b.id DESC
            LIMIT %(limit)s
            """,
            params,
        )

        # One extra row was requested purely to answer "is there more?" without
        # a second COUNT query over the same predicate.
        has_more = len(rows) > limit
        page_rows = rows[:limit]
        next_cursor = None
        if has_more and page_rows:
            last = page_rows[-1]
            next_cursor = encode_cursor(
                {"published_at": last["published_at"].isoformat(), "id": str(last["id"])}
            )
        return Page[BlogSummary](
            items=tuple(_to_summary(r) for r in page_rows),
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def set_categories(self, *, blog_id: str, category_keys: tuple[str, ...]) -> None:
        await self._execute(
            "DELETE FROM blog_categories WHERE blog_id = %(id)s", {"id": blog_id}
        )
        if not category_keys:
            return
        try:
            await self._execute(
                """
                INSERT INTO blog_categories (blog_id, category_key)
                SELECT %(id)s, unnest(%(keys)s::text[])
                """,
                {"id": blog_id, "keys": list(category_keys)},
            )
        except errors.IntegrityError as exc:
            raise translate_integrity_error(exc) from exc

    async def categories_for(self, blog_id: str) -> tuple[str, ...]:
        rows = await self._fetch_all(
            "SELECT category_key FROM blog_categories WHERE blog_id = %(id)s "
            "ORDER BY category_key",
            {"id": blog_id},
        )
        return tuple(r["category_key"] for r in rows)


class SqlBlogSectionRepository(SqlRepository):
    async def replace_all(self, *, blog_id: str, sections: tuple[BlogSection, ...]) -> None:
        """Swap the headings for the ones just parsed.

        Deletes only what the new set does not contain, so a heading another
        article pins into survives an unrelated edit. If the edit genuinely
        removes a pinned heading the RESTRICT foreign key refuses, and that
        refusal reaches the admin as ``SECTION_REFERENCED_BY_PIN`` — which is
        the entire job of a reference pin.
        """
        anchors = [s.anchor for s in sections]
        try:
            await self._execute(
                "DELETE FROM blog_sections "
                "WHERE blog_id = %(id)s AND NOT (anchor = ANY(%(anchors)s::text[]))",
                {"id": blog_id, "anchors": anchors},
            )
            for section in sections:
                await self._execute(
                    """
                    INSERT INTO blog_sections
                        (blog_id, anchor, ordinal, level, title, char_start, char_end)
                    VALUES (%(id)s, %(anchor)s, %(ordinal)s, %(level)s,
                            %(title)s, %(start)s, %(end)s)
                    ON CONFLICT (blog_id, anchor) DO UPDATE SET
                        ordinal    = EXCLUDED.ordinal,
                        level      = EXCLUDED.level,
                        title      = EXCLUDED.title,
                        char_start = EXCLUDED.char_start,
                        char_end   = EXCLUDED.char_end
                    """,
                    {
                        "id": blog_id,
                        "anchor": section.anchor,
                        "ordinal": section.ordinal,
                        "level": section.level,
                        "title": section.title,
                        "start": section.char_start,
                        "end": section.char_end,
                    },
                )
        except errors.IntegrityError as exc:
            # From this direction the anchor FK means a pin still points at a
            # heading this edit would remove.
            raise translate_integrity_error(
                exc,
                overrides={
                    "reference_pins_target_blog_id_target_anchor_fkey": (
                        ErrorCategory.SECTION_REFERENCED_BY_PIN
                    ),
                },
            ) from exc

    async def list_for(self, blog_id: str) -> tuple[BlogSection, ...]:
        rows = await self._fetch_all(
            "SELECT anchor, ordinal, level, title, char_start, char_end "
            "FROM blog_sections WHERE blog_id = %(id)s ORDER BY ordinal",
            {"id": blog_id},
        )
        return tuple(_to_section(r) for r in rows)

    async def exists(self, *, blog_id: str, anchor: str) -> bool:
        row = await self._fetch_one(
            "SELECT 1 AS hit FROM blog_sections WHERE blog_id = %(id)s AND anchor = %(a)s",
            {"id": blog_id, "a": anchor},
        )
        return row is not None


class SqlTaxonomyRepository(SqlRepository):
    async def list_categories(self) -> tuple[Category, ...]:
        rows = await self._fetch_all(
            "SELECT key, label, description FROM categories ORDER BY key"
        )
        return tuple(
            Category(key=r["key"], label=r["label"], description=r["description"])
            for r in rows
        )

    async def get_category(self, key: str) -> Category | None:
        row = await self._fetch_one(
            "SELECT key, label, description FROM categories WHERE key = %(k)s", {"k": key}
        )
        if row is None:
            return None
        return Category(key=row["key"], label=row["label"], description=row["description"])

    async def upsert_category(
        self, *, key: str, label: str, description: str | None
    ) -> Category:
        row = await self._fetch_one(
            """
            INSERT INTO categories (key, label, description)
            VALUES (%(k)s, %(l)s, %(d)s)
            ON CONFLICT (key) DO UPDATE
                SET label = EXCLUDED.label, description = EXCLUDED.description
            RETURNING key, label, description
            """,
            {"k": key, "l": label, "d": description},
        )
        assert row is not None
        return Category(key=row["key"], label=row["label"], description=row["description"])

    async def list_series(self) -> tuple[Series, ...]:
        rows = await self._fetch_all(
            "SELECT id, key, title, description FROM series ORDER BY key"
        )
        return tuple(
            Series(
                id=str(r["id"]), key=r["key"], title=r["title"], description=r["description"]
            )
            for r in rows
        )

    async def get_series_by_key(self, key: str) -> Series | None:
        row = await self._fetch_one(
            "SELECT id, key, title, description FROM series WHERE key = %(k)s", {"k": key}
        )
        if row is None:
            return None
        return Series(
            id=str(row["id"]),
            key=row["key"],
            title=row["title"],
            description=row["description"],
        )

    async def upsert_series(
        self, *, series_id: str, key: str, title: str, description: str | None
    ) -> Series:
        row = await self._fetch_one(
            """
            INSERT INTO series (id, key, title, description)
            VALUES (%(id)s, %(k)s, %(t)s, %(d)s)
            ON CONFLICT (key) DO UPDATE
                SET title = EXCLUDED.title, description = EXCLUDED.description
            RETURNING id, key, title, description
            """,
            {"id": series_id, "k": key, "t": title, "d": description},
        )
        assert row is not None
        return Series(
            id=str(row["id"]),
            key=row["key"],
            title=row["title"],
            description=row["description"],
        )


_PIN_COLUMNS = (
    "id, source_blog_id, target_blog_id, target_anchor, note, created_by, created_at"
)


def _to_pin(row: DictRow) -> ReferencePin:
    return ReferencePin(
        id=str(row["id"]),
        source_blog_id=str(row["source_blog_id"]),
        target_blog_id=str(row["target_blog_id"]),
        target_anchor=row["target_anchor"],
        note=row["note"],
        created_by=str(row["created_by"]),
        created_at=row["created_at"],
    )


class SqlReferencePinRepository(SqlRepository):
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
        try:
            row = await self._fetch_one(
                f"""
                INSERT INTO reference_pins
                    (id, source_blog_id, target_blog_id, target_anchor, note, created_by)
                VALUES (%(id)s, %(src)s, %(tgt)s, %(anchor)s, %(note)s, %(by)s)
                RETURNING {_PIN_COLUMNS}
                """,
                {
                    "id": pin_id,
                    "src": source_blog_id,
                    "tgt": target_blog_id,
                    "anchor": target_anchor,
                    "note": note,
                    "by": created_by,
                },
            )
        except errors.IntegrityError as exc:
            # From this direction the anchor FK means "no such section on the
            # target article" — the opposite of what it means in replace_all.
            raise translate_integrity_error(
                exc,
                overrides={
                    "reference_pins_target_blog_id_target_anchor_fkey": (
                        ErrorCategory.SECTION_ANCHOR_UNKNOWN
                    ),
                    "reference_pins_target_blog_id_fkey": ErrorCategory.BLOG_NOT_FOUND,
                    "reference_pins_source_blog_id_fkey": ErrorCategory.BLOG_NOT_FOUND,
                },
            ) from exc
        assert row is not None
        return _to_pin(row)

    async def delete(self, pin_id: str) -> bool:
        return await self._execute(
            "DELETE FROM reference_pins WHERE id = %(id)s", {"id": pin_id}
        ) == 1

    async def list_for_source(self, blog_id: str) -> tuple[ReferencePin, ...]:
        rows = await self._fetch_all(
            f"SELECT {_PIN_COLUMNS} FROM reference_pins "
            "WHERE source_blog_id = %(id)s ORDER BY created_at",
            {"id": blog_id},
        )
        return tuple(_to_pin(r) for r in rows)

    async def list_for_target(self, blog_id: str) -> tuple[ReferencePin, ...]:
        rows = await self._fetch_all(
            f"SELECT {_PIN_COLUMNS} FROM reference_pins "
            "WHERE target_blog_id = %(id)s ORDER BY created_at",
            {"id": blog_id},
        )
        return tuple(_to_pin(r) for r in rows)
