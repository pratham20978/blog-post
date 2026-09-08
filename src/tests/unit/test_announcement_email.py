"""New-blog email copy, safety headers, and retry identity."""

from datetime import UTC, datetime

import pytest

from blogs.contracts.announcement import AnnouncementDelivery
from blogs.core.clock import FrozenClock
from blogs.core.errors import BlogPlatformError
from blogs.core.ids import Uuid7Generator
from blogs.services.announcement_service import AnnouncementService, render_announcement
from blogs.services.policy import DefaultAuthorizationPolicy


def _delivery(**overrides: object) -> AnnouncementDelivery:
    values: dict[str, object] = {
        "id": "00000000-0000-7000-8000-000000000001",
        "campaign_id": "00000000-0000-7000-8000-000000000002",
        "user_id": "00000000-0000-7000-8000-000000000003",
        "recipient_email": "reader@example.com",
        "attempts": 1,
        "title": "Proofs & Programs",
        "summary": "Research <without> shortcuts.",
        "cover_image_url": "https://media.canery.in/cover.png?a=1&b=2",
        "cover_image_alt": "A proof <tree>",
        "tag_keys": ("mathematics", "technology"),
        "tier": "L2",
        "difficulty": "intermediate",
        "article_url": "https://canery.in/blogs/proofs-and-programs",
    }
    values.update(overrides)
    return AnnouncementDelivery.model_validate(values)


def test_announcement_contains_metadata_and_multipart_copy() -> None:
    message = render_announcement(
        _delivery(),
        unsubscribe_url="https://canery.in/email/unsubscribe?token=abc",
        one_click_url="https://canery.in/api/email/unsubscribe?token=abc",
    )

    assert message.subject == "New on Canery: Proofs & Programs"
    assert "BLOG OF TODAY" in message.text
    assert "Research <without> shortcuts." in message.text
    assert "mathematics, technology" in message.text
    assert "research papers, mathematics, and technology" in message.text
    assert "https://canery.in/blogs/proofs-and-programs" in message.text
    assert message.html is not None
    assert "Research &lt;without&gt; shortcuts." in message.html
    assert 'alt="A proof &lt;tree&gt;"' in message.html


def test_announcement_has_one_click_unsubscribe_and_stable_idempotency() -> None:
    delivery = _delivery()
    first = render_announcement(
        delivery,
        unsubscribe_url="https://canery.in/email/unsubscribe?token=abc",
        one_click_url="https://canery.in/api/email/unsubscribe?token=abc",
    )
    second = render_announcement(
        delivery,
        unsubscribe_url="https://canery.in/email/unsubscribe?token=abc",
        one_click_url="https://canery.in/api/email/unsubscribe?token=abc",
    )

    assert first.headers == {
        "List-Unsubscribe": "<https://canery.in/api/email/unsubscribe?token=abc>",
        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
    }
    assert first.idempotency_key == second.idempotency_key
    assert delivery.campaign_id in (first.idempotency_key or "")
    assert delivery.user_id in (first.idempotency_key or "")


def test_missing_optional_metadata_is_omitted_cleanly() -> None:
    message = render_announcement(
        _delivery(
            summary=None,
            cover_image_url=None,
            cover_image_alt=None,
            tag_keys=(),
            tier=None,
            difficulty=None,
        ),
        unsubscribe_url="https://canery.in/email/unsubscribe?token=abc",
        one_click_url="https://canery.in/api/email/unsubscribe?token=abc",
    )
    assert "A new evidence-based article is ready to read." in message.text
    assert message.html is not None and "<img" not in message.html


def test_unsubscribe_token_is_signed_and_tamper_evident() -> None:
    service = AnnouncementService(
        uow=None,  # type: ignore[arg-type]  # token operations do not access storage
        clock=FrozenClock(datetime(2026, 8, 22, tzinfo=UTC)),
        ids=Uuid7Generator(),
        policy=DefaultAuthorizationPolicy(),
        public_site_url="https://canery.in",
        token_secret="test-secret-value-at-least-32-bytes",
    )
    user_id = "00000000-0000-7000-8000-000000000003"
    token = service._unsubscribe_token(user_id)

    assert service._verify_unsubscribe_token(token) == user_id
    with pytest.raises(BlogPlatformError):
        service._verify_unsubscribe_token(f"{token[:-1]}A")
