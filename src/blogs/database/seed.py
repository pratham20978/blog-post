"""Load sample content, through the real publish path.

Nothing here writes a ``blogs`` row directly, and that is the whole point.
``BlogService.publish_from_markdown`` resolves the slug with its ``-2``/``-3``
disambiguation, stores the bytes content-addressed in the object store, counts
words, hashes the body, and writes ``blog_sections`` — and those section anchors
are what markers and reference pins are foreign-keyed against. A hand-written
``INSERT`` produces rows that look right in ``psql`` and break every deep link,
every table of contents, and every marker the moment a reader touches one.

So this module is deliberately thin: it reads ``seed/blogs/*.md``, upserts the
taxonomy those files reference, and calls the same service the admin console
calls.

Idempotent by check. Re-running skips any slug that already resolves, so it is
safe against a database that already has content — including one where somebody
has since edited a seeded article, which is left alone rather than reverted.

``--replace`` inverts that for the case where the row *is* stale: it rewrites
the existing article in place through ``BlogService.update`` rather than
inserting a second one. Same row, same id, so comments, markers and engagement
rows keep pointing at something real.

Usage::

    python -m blogs.database.seed
    python -m blogs.database.seed --dir /path/to/seed
    python -m blogs.database.seed --status draft   # stage without publishing
    python -m blogs.database.seed --replace        # overwrite existing slugs
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

from blogs.adapters.markdown.parser import MarkdownItParser
from blogs.bootstrap import Container, build_container, close_container
from blogs.contracts.blog import BlogStatus, PublishBlogCommand, UpdateBlogPatch
from blogs.contracts.identity import UserPrincipal
from blogs.core.logging import configure_logging
from blogs.core.settings import Settings

logger = logging.getLogger(__name__)

#: ``src/blogs/database/seed.py`` → repository root.
DEFAULT_SEED_DIR = Path(__file__).resolve().parents[3] / "seed"


class SeedError(RuntimeError):
    """The seed cannot proceed. Always something about the environment."""


@dataclass(frozen=True, slots=True)
class CategorySeed:
    key: str
    label: str
    description: str | None


@dataclass(frozen=True, slots=True)
class SeriesSeed:
    key: str
    title: str
    description: str | None


@dataclass(frozen=True, slots=True)
class CommentSeed:
    """A sample thread. ``replies`` attach to the root written by ``author``.

    One root comment per person per article is a schema constraint, so each
    article gets at most one root from any given address.
    """

    slug: str
    author: str
    body: str
    replies: tuple[tuple[str, str], ...] = ()


# ── What gets seeded ────────────────────────────────────────────────────────
#
# Mirrors `web/src/shared/fixtures/taxonomy.ts`. The article frontmatter
# references these by key, and `_resolve_series` raises SERIES_UNKNOWN rather
# than creating a missing one — so they have to exist first.

CATEGORIES: tuple[CategorySeed, ...] = (
    CategorySeed("engineering", "Engineering", "How the system is built."),
    CategorySeed("research", "Research", "Work in progress."),
    CategorySeed("infrastructure", "Infrastructure", "What it runs on."),
    CategorySeed("product", "Product", "What we chose to build."),
    CategorySeed("open-source", "Open Source", None),
)

SERIES: tuple[SeriesSeed, ...] = (
    SeriesSeed(
        "foundations",
        "Foundations",
        "The decisions underneath everything else — contracts, identity, and the "
        "shape of the data.",
    ),
    SeriesSeed(
        "retrieval",
        "Retrieval",
        "Search and ranking without reaching for embeddings.",
    ),
    # Deliberately left with nothing published: the feed derives "upcoming
    # series" from exactly this case, and without one that rail never renders.
    SeriesSeed(
        "operating-the-platform",
        "Operating the Platform",
        "Running it in production. Starts soon.",
    ),
)

#: Sample readers, so the comment threads have more than one voice. Created
#: only if absent — an address that already has an account is reused, never
#: overwritten.
READERS: tuple[tuple[str, str], ...] = (
    ("ada@example.com", "Ada"),
    ("grace@example.com", "Grace"),
    ("alan@example.com", "Alan"),
)

COMMENTS: tuple[CommentSeed, ...] = (
    CommentSeed(
        slug="one-comment-per-person",
        author="ada@example.com",
        body=(
            "The unrepresentable-state argument is the right one, but it does "
            "put the rule in the hardest place to change later. Was a partial "
            "unique index considered instead of the composite key?"
        ),
        replies=(
            (
                "grace@example.com",
                "A partial index gets you the same guarantee without pinning "
                "the reply shape, so it would have been the lighter option. "
                "The composite key buys the one-level thread as well, which is "
                "the part a check in the service kept getting wrong.",
            ),
        ),
    ),
    CommentSeed(
        slug="keyset-pagination",
        author="grace@example.com",
        body=(
            "Worth adding that the drift is worst exactly where people notice "
            "it least — page two of an append-heavy feed, where a duplicate "
            "reads as the UI being slow rather than wrong."
        ),
    ),
    CommentSeed(
        slug="identity-before-the-account",
        author="alan@example.com",
        body=(
            "The merge-on-signup is the part I would have skipped and "
            "regretted. Losing pre-signup history is invisible in testing "
            "because you always test signed in."
        ),
        replies=(
            (
                "ada@example.com",
                "Same. It only shows up as \"the recommendations are bad for "
                "new users\", which is a symptom nobody traces back to the "
                "actor token.",
            ),
        ),
    ),
    CommentSeed(
        slug="errors-are-a-contract",
        author="ada@example.com",
        body=(
            "Closing the category set is what makes this work. An open set of "
            "error strings is a contract in name only — every caller ends up "
            "matching on the message text."
        ),
    ),
)


async def seed(
    container: Container, *, seed_dir: Path, status: BlogStatus, replace: bool
) -> None:
    """Taxonomy, then articles, then comments — in that order, by necessity."""
    admin = await _admin_principal(container)

    await _seed_taxonomy(container)
    written = await _seed_blogs(
        container, seed_dir=seed_dir, admin=admin, status=status, replace=replace
    )
    await _seed_comments(container)

    logger.info("seed complete", extra={"written": written})


async def _admin_principal(container: Container) -> UserPrincipal:
    """The author every seeded article is attributed to.

    ``publish_from_markdown`` only reads ``user_id`` off the principal, so the
    actor is a fresh id rather than a real anonymous-actor row — nothing this
    script writes is keyed on it.
    """
    async with container.uow.read() as uow:
        admin = await uow.users.get_admin()

    if admin is None:
        raise SeedError(
            "no admin account exists, and every article needs an author. "
            "Set BLOGS_ADMIN_EMAIL in .env and start the API once so the "
            "bootstrap can seed the admin, then run this again."
        )

    return UserPrincipal(actor_id=container.ids.new_id(), user_id=admin.id, is_admin=True)


async def _seed_taxonomy(container: Container) -> None:
    """Upsert categories and series. Both are keyed, so this is safe to repeat.

    ``upsert_series`` conflicts on ``key`` and keeps the existing row's id, so
    re-running never orphans the articles already pointing at a series.
    """
    async with container.uow.begin() as uow:
        for category in CATEGORIES:
            await uow.taxonomy.upsert_category(
                key=category.key, label=category.label, description=category.description
            )

        for series in SERIES:
            await uow.taxonomy.upsert_series(
                series_id=container.ids.new_id(),
                key=series.key,
                title=series.title,
                description=series.description,
            )

    logger.info(
        "taxonomy upserted",
        extra={"categories": len(CATEGORIES), "series": len(SERIES)},
    )


async def _seed_blogs(
    container: Container,
    *,
    seed_dir: Path,
    admin: UserPrincipal,
    status: BlogStatus,
    replace: bool,
) -> int:
    """Publish each Markdown file, or update it in place under ``--replace``."""
    directory = seed_dir / "blogs"
    if not directory.is_dir():
        raise SeedError(f"no seed directory at {directory}")

    files = sorted(directory.glob("*.md"))
    if not files:
        raise SeedError(f"no .md files in {directory}")

    written = 0

    for path in files:
        # The filename is the intended slug, and the frontmatter repeats it.
        # Checking here rather than catching a conflict keeps the object store
        # clean: `publish_from_markdown` writes the bytes *before* it commits,
        # so a refused insert would still have left an orphan behind.
        async with container.uow.read() as uow:
            existing = await uow.blogs.get_by_slug(path.stem)

        source = path.read_bytes()

        if existing is not None:
            if not replace:
                logger.info("skipping, slug already taken", extra={"slug": path.stem})
                continue

            await _replace_blog(container, admin=admin, blog_id=existing.id, source=source)
            written += 1
            logger.info("replaced", extra={"slug": path.stem})
            continue

        result = await container.blog_service.publish_from_markdown(
            principal=admin,
            source=source,
            # Everything else comes from the file's frontmatter. Only status is
            # forced, so `--status draft` can stage a set without publishing it.
            command=PublishBlogCommand(status=status),
        )
        written += 1
        logger.info(
            "published", extra={"slug": result.blog.slug, "title": result.blog.title}
        )

    return written


async def _replace_blog(
    container: Container, *, admin: UserPrincipal, blog_id: str, source: bytes
) -> None:
    """Rewrite an existing article from a seed file.

    ``update`` takes an explicit patch and does not read frontmatter — that is
    correct for the admin console, where a form supplies the fields. Here the
    file is the only input, so the frontmatter is parsed with the same parser
    the publish path uses and turned into the patch. Parsing it any other way
    would let the two disagree.

    The status is deliberately left alone: replacing the body of an article
    somebody has since archived should not quietly republish it.
    """
    # The container does not expose its parser, so one is built here with the
    # same limit. Same class, same rules — the alternative is a second
    # frontmatter reader in this file that could disagree with the real one.
    parser = MarkdownItParser(max_bytes=container.settings.max_markdown_bytes)
    document = parser.parse(source)

    await container.blog_service.update(
        principal=admin,
        blog_id=blog_id,
        patch=UpdateBlogPatch(
            title=document.title,
            summary=document.summary,
            category_keys=document.category_keys,
            series_key=document.series_key,
            series_position=document.series_position,
        ),
        source=source,
    )


async def _seed_comments(container: Container) -> None:
    """Sample threads, on articles that have none.

    Skipping any article that already has a comment keeps this idempotent
    without fighting the one-root-per-person constraint, and means a real
    discussion is never joined by a seeded one.
    """
    readers = await _ensure_readers(container)

    for seeded in COMMENTS:
        async with container.uow.read() as uow:
            blog = await uow.blogs.get_by_slug(seeded.slug)

        if blog is None:
            logger.info("no such article; skipping comments", extra={"slug": seeded.slug})
            continue

        existing = await container.interaction_service.list_comments(blog_id=blog.id)
        if existing.items:
            logger.info("article already has comments", extra={"slug": seeded.slug})
            continue

        root = await container.interaction_service.comment(
            principal=readers[seeded.author], blog_id=blog.id, body=seeded.body
        )

        for author, body in seeded.replies:
            await container.interaction_service.comment(
                principal=readers[author],
                blog_id=blog.id,
                body=body,
                parent_comment_id=root.id,
            )

        logger.info(
            "comments seeded",
            extra={"slug": seeded.slug, "replies": len(seeded.replies)},
        )


async def _ensure_readers(container: Container) -> dict[str, UserPrincipal]:
    """Sample accounts, created only where the address is free.

    ``email_verified_at`` is set because these stand in for people who signed in
    with a code, and an unverified account is a different state with different
    behaviour.
    """
    principals: dict[str, UserPrincipal] = {}

    for email, display_name in READERS:
        async with container.uow.begin() as uow:
            user = await uow.users.get_by_email(email)
            if user is None:
                user = await uow.users.create(
                    user_id=container.ids.new_id(),
                    email=email,
                    display_name=display_name,
                    is_admin=False,
                    email_verified_at=container.clock.now(),
                )
                logger.info("reader created", extra={"email": email})

        principals[email] = UserPrincipal(
            actor_id=container.ids.new_id(), user_id=user.id, is_admin=user.is_admin
        )

    return principals


async def _run(seed_dir: Path, status: BlogStatus, replace: bool) -> None:
    settings = Settings()
    configure_logging(level=logging.INFO)

    container = await build_container(settings)

    # `build_container` re-configures logging to DEBUG whenever `BLOGS_DEBUG`
    # is set, which is the right default for the API and useless here: the
    # CommonMark tokeniser emits a line per block rule per line of every
    # article, burying the one thing this script has to say.
    for noisy in ("markdown_it", "urllib3", "minio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    try:
        await seed(container, seed_dir=seed_dir, status=status, replace=replace)
    finally:
        await close_container(container)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_SEED_DIR,
        help=f"directory holding blogs/*.md (default: {DEFAULT_SEED_DIR})",
    )
    parser.add_argument(
        "--status",
        choices=[status.value for status in BlogStatus],
        default=BlogStatus.PUBLISHED.value,
        help="status to publish under (default: published)",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="rewrite articles whose slug already exists, instead of skipping them",
    )
    args = parser.parse_args(argv)

    try:
        asyncio.run(_run(args.dir, BlogStatus(args.status), args.replace))
    except SeedError as error:
        print(f"seed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
