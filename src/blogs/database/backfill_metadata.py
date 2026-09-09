"""Backfill typed blog metadata from the canonical Markdown objects.

Run after migration 009. The default is a read-only dry run; pass ``--apply``
to write. All objects are fetched and parsed before a transaction starts, so a
missing or malformed article cannot leave a half-backfilled database.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import dataclass
from datetime import date

from blogs.adapters.markdown.parser import MarkdownItParser
from blogs.adapters.objectstore.minio_store import MinioObjectStore
from blogs.contracts.blog import BlogDifficulty, BlogTier
from blogs.core.logging import configure_logging
from blogs.core.settings import Settings
from blogs.database.session import Database
from blogs.ports.services import ObjectStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MetadataPatch:
    blog_id: str
    slug: str
    summary: str | None
    cover_image_url: str | None
    cover_image_alt: str | None
    tag_keys: tuple[str, ...]
    tier: BlogTier | None
    difficulty: BlogDifficulty | None
    prerequisites: tuple[str, ...]
    canonical_url: str | None
    published_on: date | None
    content_updated_on: date | None


async def collect(
    *, database: Database, store: ObjectStore, parser: MarkdownItParser
) -> tuple[MetadataPatch, ...]:
    async with database.connection() as conn:
        cursor = await conn.execute(
            "SELECT id, slug, markdown_uri, published_at, updated_at "
            "FROM blogs ORDER BY created_at, id"
        )
        rows = await cursor.fetchall()

    patches: list[MetadataPatch] = []
    failures: list[str] = []
    for row in rows:
        try:
            document = parser.parse(await store.get(row["markdown_uri"]))
            patches.append(
                MetadataPatch(
                    blog_id=str(row["id"]),
                    slug=row["slug"],
                    summary=document.summary,
                    cover_image_url=document.cover_image_url,
                    cover_image_alt=document.cover_image_alt,
                    tag_keys=document.tag_keys,
                    tier=document.tier,
                    difficulty=document.difficulty,
                    prerequisites=document.prerequisites,
                    canonical_url=document.canonical_url,
                    published_on=(
                        document.published_on
                        or (row["published_at"].date() if row["published_at"] else None)
                    ),
                    content_updated_on=(
                        document.content_updated_on
                        or document.published_on
                        or row["updated_at"].date()
                    ),
                )
            )
        except Exception as exc:  # report every bad object before refusing writes
            failures.append(f"{row['slug']}: {type(exc).__name__}: {exc}")

    if failures:
        raise RuntimeError("metadata backfill refused:\n  " + "\n  ".join(failures))
    return tuple(patches)


async def apply(*, database: Database, patches: tuple[MetadataPatch, ...]) -> int:
    changed = 0
    async with database.transaction() as conn:
        for patch in patches:
            cursor = await conn.execute(
                """
                UPDATE blogs SET
                    summary = COALESCE(summary, %(summary)s),
                    cover_image_url = CASE WHEN cover_image_url IS NULL
                        THEN %(cover_url)s ELSE cover_image_url END,
                    cover_image_alt = CASE WHEN cover_image_url IS NULL
                        THEN %(cover_alt)s ELSE cover_image_alt END,
                    tag_keys = CASE WHEN cardinality(tag_keys) = 0
                        THEN %(tags)s::text[] ELSE tag_keys END,
                    tier = COALESCE(tier, %(tier)s),
                    difficulty = COALESCE(difficulty, %(difficulty)s),
                    prerequisites = CASE WHEN cardinality(prerequisites) = 0
                        THEN %(prerequisites)s::text[] ELSE prerequisites END,
                    canonical_url = COALESCE(canonical_url, %(canonical_url)s),
                    published_on = COALESCE(published_on, %(published_on)s),
                    content_updated_on = COALESCE(content_updated_on,
                                                  %(content_updated_on)s)
                WHERE id = %(id)s
                  -- Every parameter here is cast explicitly. Postgres analyses
                  -- an UPDATE's WHERE clause *before* its SET clause, so at
                  -- this point a bare parameter has no type yet and `IS NOT
                  -- NULL` gives it none — the COALESCE above that would resolve
                  -- it is read too late. Without the casts the statement fails
                  -- to parse: "could not determine data type of parameter $1".
                  AND (
                    (summary IS NULL AND %(summary)s::text IS NOT NULL)
                    OR (cover_image_url IS NULL
                        AND %(cover_url)s::text IS NOT NULL)
                    OR (cardinality(tag_keys) = 0 AND cardinality(%(tags)s::text[]) > 0)
                    OR (tier IS NULL AND %(tier)s::text IS NOT NULL)
                    OR (difficulty IS NULL AND %(difficulty)s::text IS NOT NULL)
                    OR (cardinality(prerequisites) = 0
                        AND cardinality(%(prerequisites)s::text[]) > 0)
                    OR (canonical_url IS NULL
                        AND %(canonical_url)s::text IS NOT NULL)
                    OR (published_on IS NULL AND %(published_on)s::date IS NOT NULL)
                    OR (content_updated_on IS NULL
                        AND %(content_updated_on)s::date IS NOT NULL)
                  )
                """,
                {
                    "id": patch.blog_id,
                    "summary": patch.summary,
                    "cover_url": patch.cover_image_url,
                    "cover_alt": patch.cover_image_alt,
                    "tags": list(patch.tag_keys),
                    "tier": patch.tier.value if patch.tier else None,
                    "difficulty": patch.difficulty.value if patch.difficulty else None,
                    "prerequisites": list(patch.prerequisites),
                    "canonical_url": patch.canonical_url,
                    "published_on": patch.published_on,
                    "content_updated_on": patch.content_updated_on,
                },
            )
            changed += cursor.rowcount
    return changed


async def _run(*, write: bool) -> int:
    configure_logging(level=logging.INFO)
    settings = Settings()
    database = Database(settings.database_url, min_size=1, max_size=2)
    store = MinioObjectStore(
        endpoint=settings.object_store_endpoint,
        access_key=settings.object_store_access_key.get_secret_value(),
        secret_key=settings.object_store_secret_key.get_secret_value(),
        bucket=settings.object_store_bucket,
        secure=settings.object_store_secure,
        region=settings.object_store_region,
    )
    parser = MarkdownItParser(max_bytes=settings.max_markdown_bytes)

    await database.open()
    try:
        patches = await collect(database=database, store=store, parser=parser)
        for patch in patches:
            print(f"  {'apply' if write else 'would inspect'}  {patch.slug}")
        if not write:
            print(f"dry run complete: {len(patches)} article(s); no writes")
            return 0
        changed = await apply(database=database, patches=patches)
        print(f"metadata backfill complete: {changed} article(s)")
        return 0
    except Exception as exc:
        print(f"error: {exc}")
        return 1
    finally:
        await database.close()


def main() -> int:
    parser = argparse.ArgumentParser(prog="blogs.database.backfill_metadata")
    parser.add_argument(
        "--apply", action="store_true", help="write updates (default is dry-run)"
    )
    args = parser.parse_args()
    return asyncio.run(_run(write=args.apply))


if __name__ == "__main__":
    raise SystemExit(main())
