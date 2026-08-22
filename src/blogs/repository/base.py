"""Shared machinery for the SQL adapters.

Two things live here: a base that holds the connection, and the translation
from a PostgreSQL integrity error into a domain error.

That translation is the reason constraints were worth declaring. The schema
refuses a second admin, a second root comment, a reply to a reply; this maps
each refusal onto the ``ErrorCategory`` the caller should see. The alternative —
SELECT first, then INSERT — is a race in every case, and reads the same right
up until two requests arrive together.
"""

from __future__ import annotations

import base64
import binascii
import json
from datetime import datetime
from typing import Any

from psycopg import AsyncConnection, errors
from psycopg.rows import DictRow

from blogs.contracts.common import ErrorCategory
from blogs.core.errors import BlogPlatformError

#: Constraint name → what the caller should be told. Keyed by constraint rather
#: than by table so two constraints on one table stay distinguishable, which is
#: exactly the case for ``comments``.
CONSTRAINT_ERRORS: dict[str, ErrorCategory] = {
    "users_single_admin": ErrorCategory.ACCESS_DENIED,
    "users_email_normalized_key": ErrorCategory.REQUEST_INVALID,
    "blogs_slug_key": ErrorCategory.SLUG_CONFLICT,
    "comments_one_root_per_user_blog": ErrorCategory.COMMENT_ALREADY_EXISTS,
    "comments_parent_is_root": ErrorCategory.COMMENT_DEPTH_INVALID,
    "comments_depth_matches_parent": ErrorCategory.COMMENT_DEPTH_INVALID,
    "catalogs_name_per_user": ErrorCategory.CATALOG_NAME_TAKEN,
    "catalogs_one_default": ErrorCategory.CATALOG_NAME_TAKEN,
    "reference_pins_not_self": ErrorCategory.PIN_SELF_REFERENCE,
    "blog_categories_category_key_fkey": ErrorCategory.CATEGORY_UNKNOWN,
    "blogs_series_id_fkey": ErrorCategory.SERIES_UNKNOWN,
}

def translate_integrity_error(
    exc: errors.IntegrityError,
    *,
    overrides: dict[str, ErrorCategory] | None = None,
) -> BlogPlatformError:
    """Turn a constraint violation into the error the caller should see.

    ``overrides`` exists because a foreign key can fail from either end and the
    two mean opposite things:

    * inserting a pin whose anchor does not exist → ``SECTION_ANCHOR_UNKNOWN``
    * removing a section some pin still targets   → ``SECTION_REFERENCED_BY_PIN``

    PostgreSQL reports the same ``constraint_name`` for both, and
    ``diag.table_name`` does not separate them either — it names the table the
    constraint belongs to, which is the referencing table in both directions.
    Sniffing the message text would work and would break the first time a
    PostgreSQL release rewords it.

    So the direction comes from the only place that reliably knows it: the call
    site. ``pins.create`` knows a violation means a bad anchor;
    ``sections.replace_all`` knows it means the section is pinned. Each passes
    its own reading.

    Falls back to ``REQUEST_INVALID`` rather than to a 500: an unmapped
    integrity error is still the caller having asked for something the schema
    forbids, and reporting it as an internal fault would send them to look in
    the wrong place.
    """
    constraint = getattr(exc.diag, "constraint_name", None) or ""

    category = (overrides or {}).get(constraint) or CONSTRAINT_ERRORS.get(constraint)
    if category is not None:
        return BlogPlatformError(category, safe_details={"constraint": constraint})

    return BlogPlatformError(
        ErrorCategory.REQUEST_INVALID,
        safe_details={"constraint": constraint or "unknown"},
    )


class SqlRepository:
    """Holds the connection the unit of work opened. Nothing else."""

    __slots__ = ("_conn",)

    def __init__(self, conn: AsyncConnection[DictRow]) -> None:
        self._conn = conn

    async def _fetch_one(self, sql: str, params: dict[str, Any] | None = None) -> DictRow | None:
        cursor = await self._conn.execute(sql, params)
        return await cursor.fetchone()

    async def _fetch_all(self, sql: str, params: dict[str, Any] | None = None) -> list[DictRow]:
        cursor = await self._conn.execute(sql, params)
        return await cursor.fetchall()

    async def _execute(self, sql: str, params: dict[str, Any] | None = None) -> int:
        cursor = await self._conn.execute(sql, params)
        return cursor.rowcount


# ---------------------------------------------------------------------------
# Cursors
#
# Keyset pagination needs the sort key of the last row round-tripped through the
# client. Base64 of JSON, not because it is secret — it plainly is not — but so
# it is opaque enough that nobody builds a client that parses and increments it,
# which would couple every future index change to a deployed frontend.
# ---------------------------------------------------------------------------


def encode_cursor(values: dict[str, Any]) -> str:
    payload = json.dumps(values, separators=(",", ":"), default=str)
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> dict[str, Any]:
    """Raises ``BlogPlatformError(REQUEST_INVALID)`` on anything malformed.

    A bad cursor is a bad request, not a crash — clients do truncate them.
    """
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii"))
        parsed = json.loads(decoded)
    except (ValueError, binascii.Error, UnicodeDecodeError) as exc:
        raise BlogPlatformError(
            ErrorCategory.REQUEST_INVALID, safe_details={"reason": "MALFORMED_CURSOR"}
        ) from exc
    if not isinstance(parsed, dict):
        raise BlogPlatformError(
            ErrorCategory.REQUEST_INVALID, safe_details={"reason": "MALFORMED_CURSOR"}
        )
    return parsed


def as_utc(value: datetime) -> datetime:
    """Guard against a naive datetime reaching a ``timestamptz`` column.

    psycopg would accept it and let the server apply its own timezone, which is
    how "expired an hour early" bugs are born. Everything here is UTC by
    foundation §9, so a naive value is a bug worth failing on.
    """
    if value.tzinfo is None:
        raise ValueError(f"naive datetime reached the database layer: {value!r}")
    return value
