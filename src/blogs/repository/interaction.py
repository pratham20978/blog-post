"""SQL adapters for comments, markers, catalogs and recent views."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from psycopg import errors
from psycopg.rows import DictRow
from psycopg.types.json import Jsonb
from pydantic import TypeAdapter

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
from blogs.repository.base import (
    SqlRepository,
    as_utc,
    decode_cursor,
    encode_cursor,
    translate_integrity_error,
)

#: Validates the stored jsonb back into the discriminated union on the way out.
#: A marker written before an anchor kind existed would fail here rather than
#: silently deserialise into the wrong shape.
_ANCHOR_ADAPTER: TypeAdapter[MarkerAnchor] = TypeAdapter(MarkerAnchor)

_COMMENT_COLUMNS = """
    id, blog_id, user_id, parent_comment_id, depth, body,
    created_at, updated_at, deleted_at
"""


def _to_comment(row: DictRow) -> Comment:
    return Comment(
        id=str(row["id"]),
        blog_id=str(row["blog_id"]),
        user_id=str(row["user_id"]),
        parent_comment_id=(
            str(row["parent_comment_id"]) if row["parent_comment_id"] else None
        ),
        depth=row["depth"],
        body=row["body"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        deleted_at=row["deleted_at"],
    )


class SqlCommentRepository(SqlRepository):
    async def get(self, comment_id: str) -> Comment | None:
        row = await self._fetch_one(
            f"SELECT {_COMMENT_COLUMNS} FROM comments WHERE id = %(id)s", {"id": comment_id}
        )
        return _to_comment(row) if row else None

    async def create_root(
        self, *, comment_id: str, blog_id: str, user_id: str, body: str
    ) -> Comment:
        try:
            row = await self._fetch_one(
                f"""
                INSERT INTO comments (id, blog_id, user_id, depth, body)
                VALUES (%(id)s, %(blog)s, %(user)s, 0, %(body)s)
                RETURNING {_COMMENT_COLUMNS}
                """,
                {"id": comment_id, "blog": blog_id, "user": user_id, "body": body},
            )
        except errors.IntegrityError as exc:
            raise translate_integrity_error(exc) from exc
        assert row is not None
        return _to_comment(row)

    async def create_reply(
        self,
        *,
        comment_id: str,
        blog_id: str,
        user_id: str,
        parent_comment_id: str,
        body: str,
    ) -> Comment:
        # No pre-check that the parent is a root: the composite foreign key
        # decides, and a check here would be both redundant and a race.
        try:
            row = await self._fetch_one(
                f"""
                INSERT INTO comments
                    (id, blog_id, user_id, parent_comment_id, depth, body)
                VALUES (%(id)s, %(blog)s, %(user)s, %(parent)s, 1, %(body)s)
                RETURNING {_COMMENT_COLUMNS}
                """,
                {
                    "id": comment_id,
                    "blog": blog_id,
                    "user": user_id,
                    "parent": parent_comment_id,
                    "body": body,
                },
            )
        except errors.IntegrityError as exc:
            raise translate_integrity_error(exc) from exc
        assert row is not None
        return _to_comment(row)

    async def update_body(
        self, *, comment_id: str, user_id: str, body: str
    ) -> Comment | None:
        row = await self._fetch_one(
            f"""
            UPDATE comments SET body = %(body)s
            WHERE id = %(id)s AND user_id = %(user)s AND deleted_at IS NULL
            RETURNING {_COMMENT_COLUMNS}
            """,
            {"id": comment_id, "user": user_id, "body": body},
        )
        return _to_comment(row) if row else None

    async def soft_delete(
        self, *, comment_id: str, deleted_by: str, now: datetime, as_admin: bool
    ) -> bool:
        # Ownership is part of the predicate for a normal user, so "not yours"
        # and "not there" are one query rather than a read followed by a compare
        # somebody could omit.
        ownership = "" if as_admin else " AND user_id = %(by)s"
        affected = await self._execute(
            f"""
            UPDATE comments SET deleted_at = %(now)s, deleted_by = %(by)s
            WHERE id = %(id)s AND deleted_at IS NULL{ownership}
            """,
            {"id": comment_id, "by": deleted_by, "now": as_utc(now)},
        )
        return affected == 1

    async def list_threads(
        self, *, blog_id: str, cursor: str | None, limit: int
    ) -> Page[CommentThread]:
        params: dict[str, Any] = {"blog": blog_id, "limit": limit + 1}
        clauses = ["blog_id = %(blog)s", "depth = 0", "deleted_at IS NULL"]
        if cursor:
            keys = decode_cursor(cursor)
            clauses.append("(created_at, id) < (%(cur_at)s::timestamptz, %(cur_id)s::uuid)")
            params["cur_at"] = keys.get("created_at")
            params["cur_id"] = keys.get("id")

        roots = await self._fetch_all(
            f"""
            SELECT {_COMMENT_COLUMNS} FROM comments
            WHERE {" AND ".join(clauses)}
            ORDER BY created_at DESC, id DESC
            LIMIT %(limit)s
            """,
            params,
        )
        has_more = len(roots) > limit
        page_roots = roots[:limit]
        if not page_roots:
            return Page[CommentThread](items=(), next_cursor=None, has_more=False)

        # Two queries, not N+1: every reply for the whole page in one pass.
        # Single-level threading is what makes this possible without recursion.
        replies = await self._fetch_all(
            f"""
            SELECT {_COMMENT_COLUMNS} FROM comments
            WHERE parent_comment_id = ANY(%(parents)s::uuid[]) AND deleted_at IS NULL
            ORDER BY created_at
            """,
            {"parents": [str(r["id"]) for r in page_roots]},
        )
        by_parent: dict[str, list[Comment]] = {}
        for row in replies:
            by_parent.setdefault(str(row["parent_comment_id"]), []).append(_to_comment(row))

        threads = tuple(
            CommentThread(
                root=_to_comment(root),
                replies=tuple(by_parent.get(str(root["id"]), ())),
            )
            for root in page_roots
        )
        next_cursor = None
        if has_more:
            last = page_roots[-1]
            next_cursor = encode_cursor(
                {"created_at": last["created_at"].isoformat(), "id": str(last["id"])}
            )
        return Page[CommentThread](
            items=threads, next_cursor=next_cursor, has_more=has_more
        )

    async def count_for_blog(self, blog_id: str) -> int:
        row = await self._fetch_one(
            "SELECT count(*) AS n FROM comments "
            "WHERE blog_id = %(id)s AND deleted_at IS NULL",
            {"id": blog_id},
        )
        return int(row["n"]) if row else 0


class SqlMarkerRepository(SqlRepository):
    async def upsert(
        self,
        *,
        user_id: str,
        blog_id: str,
        anchor: MarkerAnchor,
        progress_ratio: float | None,
        now: datetime,
    ) -> Marker:
        row = await self._fetch_one(
            """
            INSERT INTO markers (user_id, blog_id, anchor, progress_ratio, updated_at)
            VALUES (%(user)s, %(blog)s, %(anchor)s, %(ratio)s, %(now)s)
            ON CONFLICT (user_id, blog_id) DO UPDATE SET
                anchor         = EXCLUDED.anchor,
                progress_ratio = EXCLUDED.progress_ratio,
                updated_at     = EXCLUDED.updated_at
            RETURNING user_id, blog_id, anchor, progress_ratio, updated_at
            """,
            {
                "user": user_id,
                "blog": blog_id,
                "anchor": Jsonb(anchor.model_dump(mode="json")),
                "ratio": progress_ratio,
                "now": as_utc(now),
            },
        )
        assert row is not None
        return self._to_marker(row)

    @staticmethod
    def _to_marker(row: DictRow) -> Marker:
        return Marker(
            user_id=str(row["user_id"]),
            blog_id=str(row["blog_id"]),
            anchor=_ANCHOR_ADAPTER.validate_python(row["anchor"]),
            progress_ratio=row["progress_ratio"],
            updated_at=row["updated_at"],
        )

    async def get(self, *, user_id: str, blog_id: str) -> Marker | None:
        row = await self._fetch_one(
            "SELECT user_id, blog_id, anchor, progress_ratio, updated_at FROM markers "
            "WHERE user_id = %(user)s AND blog_id = %(blog)s",
            {"user": user_id, "blog": blog_id},
        )
        return self._to_marker(row) if row else None

    async def delete(self, *, user_id: str, blog_id: str) -> bool:
        return await self._execute(
            "DELETE FROM markers WHERE user_id = %(user)s AND blog_id = %(blog)s",
            {"user": user_id, "blog": blog_id},
        ) == 1

    async def list_for_user(self, *, user_id: str, limit: int) -> tuple[Marker, ...]:
        rows = await self._fetch_all(
            "SELECT user_id, blog_id, anchor, progress_ratio, updated_at FROM markers "
            "WHERE user_id = %(user)s ORDER BY updated_at DESC LIMIT %(limit)s",
            {"user": user_id, "limit": limit},
        )
        return tuple(self._to_marker(r) for r in rows)


def _to_catalog(row: DictRow) -> Catalog:
    return Catalog(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        name=row["name"],
        is_default=row["is_default"],
        item_count=int(row.get("item_count") or 0),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


_CATALOG_COLUMNS = "id, user_id, name, is_default, created_at, updated_at"

#: The same columns qualified for a join. Written out rather than derived from
#: the string above with split/strip: deriving SQL by string surgery is exactly
#: the shape that makes an interpolation impossible to audit, and
#: test_sql_safety rejects it.
_CATALOG_COLUMNS_QUALIFIED = (
    "c.id, c.user_id, c.name, c.is_default, c.created_at, c.updated_at"
)


class SqlCatalogRepository(SqlRepository):
    async def get(self, catalog_id: str) -> Catalog | None:
        row = await self._fetch_one(
            f"SELECT {_CATALOG_COLUMNS} FROM catalogs WHERE id = %(id)s", {"id": catalog_id}
        )
        return _to_catalog(row) if row else None

    async def create(
        self, *, catalog_id: str, user_id: str, name: str, is_default: bool
    ) -> Catalog:
        try:
            row = await self._fetch_one(
                f"""
                INSERT INTO catalogs (id, user_id, name, is_default)
                VALUES (%(id)s, %(user)s, %(name)s, %(default)s)
                RETURNING {_CATALOG_COLUMNS}
                """,
                {"id": catalog_id, "user": user_id, "name": name, "default": is_default},
            )
        except errors.IntegrityError as exc:
            raise translate_integrity_error(exc) from exc
        assert row is not None
        return _to_catalog(row)

    async def ensure_default(self, *, user_id: str, catalog_id: str) -> Catalog:
        """Get or create the user's default catalog.

        ``ON CONFLICT DO NOTHING`` against the partial unique index, then read
        back. Two concurrent first-saves therefore converge on one catalog
        rather than one of them failing.
        """
        await self._execute(
            """
            INSERT INTO catalogs (id, user_id, name, is_default)
            VALUES (%(id)s, %(user)s, 'Saved', true)
            ON CONFLICT DO NOTHING
            """,
            {"id": catalog_id, "user": user_id},
        )
        row = await self._fetch_one(
            f"SELECT {_CATALOG_COLUMNS} FROM catalogs "
            "WHERE user_id = %(user)s AND is_default",
            {"user": user_id},
        )
        assert row is not None
        return _to_catalog(row)

    async def rename(self, *, catalog_id: str, user_id: str, name: str) -> Catalog | None:
        try:
            row = await self._fetch_one(
                f"""
                UPDATE catalogs SET name = %(name)s
                WHERE id = %(id)s AND user_id = %(user)s
                RETURNING {_CATALOG_COLUMNS}
                """,
                {"id": catalog_id, "user": user_id, "name": name},
            )
        except errors.IntegrityError as exc:
            raise translate_integrity_error(exc) from exc
        return _to_catalog(row) if row else None

    async def delete(self, *, catalog_id: str, user_id: str) -> bool:
        return await self._execute(
            "DELETE FROM catalogs WHERE id = %(id)s AND user_id = %(user)s "
            "AND NOT is_default",
            {"id": catalog_id, "user": user_id},
        ) == 1

    async def list_for_user(self, user_id: str) -> tuple[Catalog, ...]:
        rows = await self._fetch_all(
            f"""
            SELECT {_CATALOG_COLUMNS_QUALIFIED},
                   count(i.blog_id) AS item_count
            FROM catalogs c
            LEFT JOIN catalog_items i ON i.catalog_id = c.id
            WHERE c.user_id = %(user)s
            GROUP BY c.id
            ORDER BY c.is_default DESC, lower(c.name)
            """,
            {"user": user_id},
        )
        return tuple(_to_catalog(r) for r in rows)

    async def add_item(
        self, *, catalog_id: str, blog_id: str, note: str | None
    ) -> CatalogItem:
        # Saving twice is not an error — it is a user tapping the button again.
        row = await self._fetch_one(
            """
            INSERT INTO catalog_items (catalog_id, blog_id, note)
            VALUES (%(cat)s, %(blog)s, %(note)s)
            ON CONFLICT (catalog_id, blog_id) DO UPDATE
                SET note = COALESCE(EXCLUDED.note, catalog_items.note)
            RETURNING catalog_id, blog_id, added_at, note
            """,
            {"cat": catalog_id, "blog": blog_id, "note": note},
        )
        assert row is not None
        return CatalogItem(
            catalog_id=str(row["catalog_id"]),
            blog_id=str(row["blog_id"]),
            added_at=row["added_at"],
            note=row["note"],
        )

    async def remove_item(self, *, catalog_id: str, blog_id: str) -> bool:
        return await self._execute(
            "DELETE FROM catalog_items WHERE catalog_id = %(cat)s AND blog_id = %(blog)s",
            {"cat": catalog_id, "blog": blog_id},
        ) == 1

    async def list_items(
        self, *, catalog_id: str, cursor: str | None, limit: int
    ) -> Page[CatalogItem]:
        params: dict[str, Any] = {"cat": catalog_id, "limit": limit + 1}
        clauses = ["catalog_id = %(cat)s"]
        if cursor:
            keys = decode_cursor(cursor)
            clauses.append("(added_at, blog_id) < (%(cur_at)s::timestamptz, %(cur_id)s::uuid)")
            params["cur_at"] = keys.get("added_at")
            params["cur_id"] = keys.get("blog_id")

        rows = await self._fetch_all(
            f"""
            SELECT catalog_id, blog_id, added_at, note FROM catalog_items
            WHERE {" AND ".join(clauses)}
            ORDER BY added_at DESC, blog_id DESC
            LIMIT %(limit)s
            """,
            params,
        )
        has_more = len(rows) > limit
        page_rows = rows[:limit]
        next_cursor = None
        if has_more and page_rows:
            last = page_rows[-1]
            next_cursor = encode_cursor(
                {"added_at": last["added_at"].isoformat(), "blog_id": str(last["blog_id"])}
            )
        return Page[CatalogItem](
            items=tuple(
                CatalogItem(
                    catalog_id=str(r["catalog_id"]),
                    blog_id=str(r["blog_id"]),
                    added_at=r["added_at"],
                    note=r["note"],
                )
                for r in page_rows
            ),
            next_cursor=next_cursor,
            has_more=has_more,
        )


class SqlRecentViewRepository(SqlRepository):
    async def record(
        self, *, actor_id: str, user_id: str | None, blog_id: str, now: datetime
    ) -> None:
        await self._execute(
            """
            INSERT INTO recent_views
                (actor_id, blog_id, user_id, first_viewed_at, last_viewed_at, view_count)
            VALUES (%(actor)s, %(blog)s, %(user)s, %(now)s, %(now)s, 1)
            ON CONFLICT (actor_id, blog_id) DO UPDATE SET
                last_viewed_at = EXCLUDED.last_viewed_at,
                view_count     = recent_views.view_count + 1,
                -- Never un-attribute: once an actor is known to be a user, a
                -- later anonymous-looking write must not blank it.
                user_id        = COALESCE(EXCLUDED.user_id, recent_views.user_id)
            """,
            {"actor": actor_id, "blog": blog_id, "user": user_id, "now": as_utc(now)},
        )

    async def _list(self, where: str, params: dict[str, Any]) -> tuple[RecentView, ...]:
        rows = await self._fetch_all(
            f"""
            SELECT r.blog_id, r.last_viewed_at, r.view_count, b.title, b.slug
            FROM recent_views r
            JOIN blogs b ON b.id = r.blog_id
            WHERE {where} AND b.status = 'published'
            ORDER BY r.last_viewed_at DESC
            LIMIT %(limit)s
            """,
            params,
        )
        return tuple(
            RecentView(
                blog_id=str(r["blog_id"]),
                title=r["title"],
                slug=r["slug"],
                last_viewed_at=r["last_viewed_at"],
                view_count=r["view_count"],
            )
            for r in rows
        )

    async def list_for_actor(self, *, actor_id: str, limit: int) -> tuple[RecentView, ...]:
        return await self._list("r.actor_id = %(actor)s", {"actor": actor_id, "limit": limit})

    async def list_for_user(self, *, user_id: str, limit: int) -> tuple[RecentView, ...]:
        return await self._list("r.user_id = %(user)s", {"user": user_id, "limit": limit})

    async def attribute_to_user(self, *, actor_id: str, user_id: str) -> int:
        return await self._execute(
            """
            UPDATE recent_views SET user_id = %(user)s
            WHERE actor_id = %(actor)s AND user_id IS NULL
            """,
            {"actor": actor_id, "user": user_id},
        )
