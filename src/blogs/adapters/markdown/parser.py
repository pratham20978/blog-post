"""Markdown parsing. Nothing here renders.

What the domain actually needs from a ``.md`` file is small: the frontmatter
metadata, the heading anchors that make pins and markers checkable, and a word
count. All three come from a real CommonMark token stream rather than regular
expressions — a ``#`` inside a fenced code block is not a heading, and a regex
cannot tell the difference:

    ```python
    # this is a comment, not a section
    ```

The stored bytes are the source, so the article is served exactly as authored
and the content hash stays honest.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import date, datetime
from typing import Any
from urllib.parse import urlsplit

import frontmatter
from markdown_it import MarkdownIt
from markdown_it.token import Token
from pydantic import ValidationError

from blogs.contracts.blog import BlogDifficulty, BlogTier, MarkdownDocument, MarkdownHeading
from blogs.contracts.common import ErrorCategory
from blogs.core.errors import BlogPlatformError

_WORD = re.compile(r"[\w'-]+", re.UNICODE)
_NON_SLUG = re.compile(r"[^a-z0-9]+")
_FENCED_CODE = re.compile(r"^(?:```|~~~)[\s\S]*?^(?:```|~~~)\s*$", re.MULTILINE)
_MARKDOWN_IMAGE = re.compile(
    r"!\[([^\]]*)\]\(\s*<?([^\s)>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)
_HTML_IMAGE = re.compile(r"<img\b[^>]*?\bsrc\s*=\s*[\"']([^\"']+)[\"'][^>]*>", re.I)
_HTML_ALT = re.compile(r"\balt\s*=\s*[\"']([^\"']*)[\"']", re.I)


def slugify(value: str, *, max_length: int = 120) -> str:
    """Deterministic, ASCII, hyphen-separated.

    NFKD-folds accents rather than dropping them, so "Café Décor" becomes
    ``cafe-decor`` instead of ``caf-cor``. Truncates on a hyphen boundary so a
    cut slug does not end mid-word.
    """
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = _NON_SLUG.sub("-", ascii_only).strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("-", 1)[0].strip("-")
    return slug


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_key_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    items = value if isinstance(value, list | tuple) else [value]
    keys = []
    for item in items:
        key = slugify(str(item))
        if key:
            keys.append(key)
    # Deduplicated, order preserved: two frontmatter entries that slugify to the
    # same key would otherwise violate the blog_categories primary key.
    return tuple(dict.fromkeys(keys))


def _as_string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    items = value if isinstance(value, list | tuple) else [value]
    return tuple(
        dict.fromkeys(text for item in items if (text := str(item).strip()))
    )


def _as_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError as exc:
        raise BlogPlatformError(
            ErrorCategory.MARKDOWN_INVALID,
            safe_details={"reason": "BAD_EDITORIAL_DATE", "value": str(value)},
        ) from exc


def _valid_image_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.netloc)
        and not any(character.isspace() or character in "<>{}" for character in value)
    )


def _first_body_image(body: str) -> tuple[str, str] | None:
    prose = _FENCED_CODE.sub("", body)
    candidates: list[tuple[int, str, str]] = []
    for match in _MARKDOWN_IMAGE.finditer(prose):
        candidates.append((match.start(), match.group(2), match.group(1).strip()))
    for match in _HTML_IMAGE.finditer(prose):
        alt = _HTML_ALT.search(match.group(0))
        candidates.append(
            (match.start(), match.group(1), alt.group(1).strip() if alt else "")
        )
    for _, url, alt in sorted(candidates):
        if _valid_image_url(url):
            return url, alt
    return None


class MarkdownItParser:
    def __init__(self, *, max_bytes: int) -> None:
        self._max_bytes = max_bytes
        # "commonmark" rather than "gfm-like": the parse is only ever used to
        # find headings and count words, and a smaller rule set is a smaller
        # surface for a pathological document.
        self._md = MarkdownIt("commonmark")

    def parse(self, source: bytes) -> MarkdownDocument:
        if len(source) > self._max_bytes:
            raise BlogPlatformError(
                ErrorCategory.MARKDOWN_TOO_LARGE,
                safe_details={"max_bytes": self._max_bytes, "actual_bytes": len(source)},
            )
        try:
            text = source.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BlogPlatformError(
                ErrorCategory.MARKDOWN_INVALID, safe_details={"reason": "NOT_UTF8"}
            ) from exc

        try:
            post = frontmatter.loads(text)
        except Exception as exc:  # any YAML failure means a bad file
            raise BlogPlatformError(
                ErrorCategory.MARKDOWN_INVALID, safe_details={"reason": "BAD_FRONTMATTER"}
            ) from exc

        body = post.content
        meta = post.metadata

        headings = self._headings(body)
        title = _as_str(meta.get("title")) or (headings[0].title if headings else None)

        body_cover = _first_body_image(body)
        cover_url = _as_str(meta.get("cover_image_url") or meta.get("cover_image"))
        if cover_url is None and body_cover is not None:
            cover_url = body_cover[0]
        cover_alt = _as_str(meta.get("cover_image_alt"))
        if cover_url is not None and cover_alt is None:
            cover_alt = (
                _as_str(body_cover[1])
                if body_cover is not None and body_cover[0] == cover_url
                else None
            )
            cover_alt = cover_alt or title or "Article cover"

        try:
            tier = _as_str(meta.get("tier"))
            difficulty = _as_str(meta.get("difficulty"))
            return MarkdownDocument(
                title=title,
                summary=_as_str(meta.get("summary")) or _as_str(meta.get("description")),
                slug=slugify(_as_str(meta.get("slug")) or "") or None,
                category_keys=_as_key_tuple(meta.get("categories") or meta.get("category")),
                series_key=slugify(_as_str(meta.get("series")) or "") or None,
                series_position=(
                    int(str(meta["series_position"]))
                    if str(meta.get("series_position", "")).strip().isdigit()
                    else None
                ),
                cover_image_url=cover_url,
                cover_image_alt=cover_alt,
                tag_keys=_as_key_tuple(meta.get("tags")),
                tier=BlogTier(tier.upper()) if tier else None,
                difficulty=BlogDifficulty(difficulty.lower()) if difficulty else None,
                prerequisites=_as_string_tuple(meta.get("prerequisites")),
                canonical_url=_as_str(meta.get("canonical_url")),
                published_on=_as_date(meta.get("date")),
                content_updated_on=_as_date(meta.get("updated")),
                body=body,
                headings=headings,
                word_count=len(_WORD.findall(body)),
                content_sha256=hashlib.sha256(body.encode("utf-8")).hexdigest(),
            )
        except (ValidationError, ValueError) as exc:
            raise BlogPlatformError(
                ErrorCategory.MARKDOWN_INVALID,
                safe_details={"reason": "BAD_FRONTMATTER_METADATA"},
            ) from exc

    def _headings(self, body: str) -> tuple[MarkdownHeading, ...]:
        """Walk the token stream, collecting headings with their source spans.

        markdown-it reports a line range per token, which is turned into
        character offsets so a marker or a pin can address a position inside the
        exact bytes that were stored. Each section runs to the start of the next
        heading, so ``char_end`` covers the section rather than just its title.
        """
        tokens: list[Token] = self._md.parse(body)
        # Cumulative offset of the start of each line, so a line number becomes
        # a character position in one lookup instead of a re-scan per heading.
        line_starts = [0]
        for line in body.splitlines(keepends=True):
            line_starts.append(line_starts[-1] + len(line))

        def offset(line: int) -> int:
            return line_starts[min(line, len(line_starts) - 1)]

        found: list[tuple[int, int, str, int]] = []  # level, char_start, title, end_line
        for index, token in enumerate(tokens):
            if token.type != "heading_open" or token.map is None:
                continue
            inline = tokens[index + 1] if index + 1 < len(tokens) else None
            title = (inline.content if inline else "").strip()
            if not title:
                continue
            found.append((int(token.tag[1:]), offset(token.map[0]), title, token.map[1]))

        headings: list[MarkdownHeading] = []
        seen: dict[str, int] = {}
        for position, (level, char_start, title, _) in enumerate(found):
            base = slugify(title, max_length=180) or f"section-{position + 1}"
            # Two headings with the same text get -2, -3 … the same disambiguation
            # every static site generator uses, so anchors stay predictable.
            count = seen.get(base, 0) + 1
            seen[base] = count
            anchor = base if count == 1 else f"{base}-{count}"

            char_end = (
                found[position + 1][1] if position + 1 < len(found) else len(body)
            )
            headings.append(
                MarkdownHeading(
                    anchor=anchor,
                    level=level,
                    title=title,
                    char_start=char_start,
                    char_end=char_end,
                )
            )
        return tuple(headings)
