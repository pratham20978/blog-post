"""The Markdown parser, the slug rules, the policy matrix, and password hashing."""

from __future__ import annotations

import pytest

from blogs.adapters.markdown.parser import MarkdownItParser, slugify
from blogs.adapters.tokens.passwords import ScryptPasswordHasher
from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import AnonymousPrincipal, Principal, UserPrincipal
from blogs.core.errors import BlogPlatformError
from blogs.services.policy import DefaultAuthorizationPolicy, require

_A = "00000000-0000-7000-8000-000000000001"
_U = "00000000-0000-7000-8000-000000000002"

ANON: Principal = AnonymousPrincipal(actor_id=_A)
USER: Principal = UserPrincipal(actor_id=_A, user_id=_U, is_admin=False)
ADMIN: Principal = UserPrincipal(actor_id=_A, user_id=_U, is_admin=True)


@pytest.fixture
def parser() -> MarkdownItParser:
    return MarkdownItParser(max_bytes=1_000_000)


class TestSlugify:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Retrieval Without Embeddings", "retrieval-without-embeddings"),
            # NFKD folding, not dropping: "caf-dcor" would be the naive result.
            ("Café Décor", "cafe-decor"),
            ("  Spaces   Everywhere  ", "spaces-everywhere"),
            ("Punctuation!!! Here???", "punctuation-here"),
            ("--leading-and-trailing--", "leading-and-trailing"),
            ("", ""),
        ],
    )
    def test_slugify(self, raw: str, expected: str) -> None:
        assert slugify(raw) == expected

    def test_truncation_lands_on_a_word_boundary(self) -> None:
        slug = slugify(" ".join(["alpha"] * 40), max_length=30)
        assert len(slug) <= 30
        assert not slug.endswith("-")
        # Cut between words, so no fragment like "alph" survives.
        assert all(part == "alpha" for part in slug.split("-"))


class TestMarkdownParsing:
    def test_headings_inside_a_code_fence_are_not_sections(
        self, parser: MarkdownItParser
    ) -> None:
        """The reason this uses a CommonMark parser instead of a regex."""
        source = b"""# Real Heading

```python
# not a heading
## also not a heading
```

## Second Real Heading
"""
        document = parser.parse(source)
        assert [h.title for h in document.headings] == [
            "Real Heading",
            "Second Real Heading",
        ]

    def test_duplicate_headings_get_distinct_anchors(
        self, parser: MarkdownItParser
    ) -> None:
        document = parser.parse(b"## Setup\n\ntext\n\n## Setup\n\nmore\n")
        assert [h.anchor for h in document.headings] == ["setup", "setup-2"]

    def test_section_spans_cover_the_body_not_just_the_title(
        self, parser: MarkdownItParser
    ) -> None:
        document = parser.parse(b"## One\n\nbody of one\n\n## Two\n\nbody of two\n")
        first = document.headings[0]
        assert "body of one" in document.body[first.char_start : first.char_end]
        assert "body of two" not in document.body[first.char_start : first.char_end]

    def test_frontmatter_tags_are_discarded(self, parser: MarkdownItParser) -> None:
        """Tags are F4's. A field stored under a definition nobody agreed would
        look authoritative to whoever found it next."""
        document = parser.parse(
            b"---\ntitle: T\ntags: [rag, llm]\ncategories: [AI]\n---\n\nbody\n"
        )
        assert not hasattr(document, "tags")
        assert "tags" not in document.model_dump()
        assert document.category_keys == ("ai",)

    def test_title_falls_back_to_the_first_heading(
        self, parser: MarkdownItParser
    ) -> None:
        assert parser.parse(b"# From The Heading\n\ntext\n").title == "From The Heading"

    def test_duplicate_categories_are_collapsed(self, parser: MarkdownItParser) -> None:
        """Two entries that slugify alike would violate the composite key."""
        document = parser.parse(b"---\ntitle: T\ncategories: [AI, ai, 'A I']\n---\n\nx\n")
        assert document.category_keys == ("ai", "a-i")

    def test_content_hash_ignores_frontmatter(self, parser: MarkdownItParser) -> None:
        """The hash is over the stored body, so metadata edits do not
        invalidate every reader's cached copy."""
        a = parser.parse(b"---\ntitle: One\n---\n\nsame body\n")
        b = parser.parse(b"---\ntitle: Two\n---\n\nsame body\n")
        assert a.content_sha256 == b.content_sha256

    def test_oversized_input_is_refused(self) -> None:
        small = MarkdownItParser(max_bytes=10)
        with pytest.raises(BlogPlatformError) as exc:
            small.parse(b"x" * 100)
        assert exc.value.category is ErrorCategory.MARKDOWN_TOO_LARGE

    def test_non_utf8_is_refused(self, parser: MarkdownItParser) -> None:
        with pytest.raises(BlogPlatformError) as exc:
            parser.parse(b"\xff\xfe not utf-8")
        assert exc.value.category is ErrorCategory.MARKDOWN_INVALID


class TestPolicyMatrix:
    """Every verb against every principal kind. Cheap to be exhaustive because
    the policy is pure — which is the reason it is a separate object."""

    ADMIN_ONLY = (
        "can_publish",
        "can_edit_blog",
        "can_archive_blog",
        "can_manage_pins",
        "can_manage_taxonomy",
        "can_read_analytics",
        "can_moderate",
    )
    USER_ONLY = ("can_comment", "can_mark", "can_save")

    @pytest.fixture
    def policy(self) -> DefaultAuthorizationPolicy:
        return DefaultAuthorizationPolicy()

    @pytest.mark.parametrize("verb", ADMIN_ONLY)
    def test_admin_only_verbs(self, policy: DefaultAuthorizationPolicy, verb: str) -> None:
        assert getattr(policy, verb)(ADMIN) is True
        assert getattr(policy, verb)(USER) is False
        assert getattr(policy, verb)(ANON) is False

    @pytest.mark.parametrize("verb", USER_ONLY)
    def test_signed_in_verbs(self, policy: DefaultAuthorizationPolicy, verb: str) -> None:
        assert getattr(policy, verb)(ADMIN) is True
        assert getattr(policy, verb)(USER) is True
        assert getattr(policy, verb)(ANON) is False

    def test_anonymous_visitors_may_generate_engagement(
        self, policy: DefaultAuthorizationPolicy
    ) -> None:
        """The whole point of the actor id. Without this every account would
        start genuinely cold."""
        assert policy.can_record_engagement(ANON) is True

    def test_refusals_distinguish_sign_in_from_permission(self) -> None:
        """401 for anonymous because retrying with credentials works; 403 for a
        signed-in non-admin because it will not."""
        with pytest.raises(BlogPlatformError) as anon_exc:
            require(False, principal=ANON)
        assert anon_exc.value.category is ErrorCategory.AUTH_REQUIRED

        with pytest.raises(BlogPlatformError) as user_exc:
            require(False, principal=USER)
        assert user_exc.value.category is ErrorCategory.ADMIN_REQUIRED


class TestPasswordHashing:
    def test_round_trip(self, passwords: ScryptPasswordHasher) -> None:
        stored = passwords.hash("correct horse battery staple")
        assert passwords.verify("correct horse battery staple", stored) is True
        assert passwords.verify("wrong", stored) is False

    def test_identical_passwords_hash_differently(
        self, passwords: ScryptPasswordHasher
    ) -> None:
        """Per-password salt: otherwise the database reveals which accounts
        share a password, and one cracked hash breaks all of them."""
        assert passwords.hash("same") != passwords.hash("same")

    def test_absent_hash_verifies_false_without_raising(
        self, passwords: ScryptPasswordHasher
    ) -> None:
        assert passwords.verify("anything", None) is False

    def test_stored_length_matches_the_schema_check(
        self, passwords: ScryptPasswordHasher
    ) -> None:
        """migration 006 CHECKs octet_length(password_hash) = 48."""
        assert len(passwords.hash("x")) == 48
