"""Automatic new-blog campaigns, reader preferences, and email rendering."""

from __future__ import annotations

import base64
import hashlib
import hmac
from html import escape
from urllib.parse import quote

from blogs.contracts.announcement import (
    AnnouncementCampaignSummary,
    AnnouncementDelivery,
    BlogEmailPreference,
)
from blogs.contracts.common import ErrorCategory
from blogs.contracts.events import BlogPublished
from blogs.contracts.identity import Principal, UserPrincipal, UserStatus
from blogs.core.clock import Clock
from blogs.core.errors import raise_error
from blogs.core.ids import IdGenerator
from blogs.ports.services import AuthorizationPolicy, EmailMessage
from blogs.ports.uow import UnitOfWorkFactory
from blogs.services.policy import require

_TOKEN_DOMAIN = b"canery:blog-announcement-unsubscribe:v1:"
_MISSION = (
    "At Canery, we help the world learn from research papers, mathematics, "
    "and technology through careful, evidence-based writing."
)


class AnnouncementService:
    def __init__(
        self,
        *,
        uow: UnitOfWorkFactory,
        clock: Clock,
        ids: IdGenerator,
        policy: AuthorizationPolicy,
        public_site_url: str,
        token_secret: str,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._ids = ids
        self._policy = policy
        self._site_url = public_site_url.rstrip("/")
        self._token_secret = token_secret.encode("utf-8")

    async def stage_published(self, event: BlogPublished) -> bool:
        now = self._clock.now()
        async with self._uow.begin() as uow:
            return await uow.announcements.create_for_published(
                campaign_id=self._ids.new_id(),
                event=event,
                article_url=f"{self._site_url}/blogs/{event.slug}",
                now=now,
            )

    async def get_preference(self, principal: Principal) -> BlogEmailPreference:
        if not isinstance(principal, UserPrincipal):
            raise_error(ErrorCategory.AUTH_REQUIRED)
        async with self._uow.read() as uow:
            preference = await uow.users.get_blog_email_preference(principal.user_id)
        if preference is None:
            raise_error(ErrorCategory.USER_NOT_FOUND)
        return preference

    async def set_preference(
        self, *, principal: Principal, enabled: bool
    ) -> BlogEmailPreference:
        if not isinstance(principal, UserPrincipal):
            raise_error(ErrorCategory.AUTH_REQUIRED)
        return await self._set_preference(user_id=principal.user_id, enabled=enabled)

    async def unsubscribe(self, token: str) -> BlogEmailPreference:
        return await self._set_preference(
            user_id=self._verify_unsubscribe_token(token), enabled=False
        )

    async def _set_preference(
        self, *, user_id: str, enabled: bool
    ) -> BlogEmailPreference:
        now = self._clock.now()
        async with self._uow.begin() as uow:
            user = await uow.users.get(user_id)
            if user is None:
                raise_error(ErrorCategory.USER_NOT_FOUND)
            if user.status is not UserStatus.ACTIVE:
                raise_error(ErrorCategory.USER_INACTIVE)
            preference = await uow.users.set_blog_email_preference(
                user_id=user_id, enabled=enabled, at=now
            )
            if not enabled:
                await uow.announcements.cancel_pending_for_user(
                    user_id=user_id, now=now
                )
                await uow.announcements.settle_campaigns(now=now)
        assert preference is not None
        return preference

    async def campaign(
        self, *, principal: Principal, blog_id: str, correlation_id: str | None = None
    ) -> AnnouncementCampaignSummary:
        require(
            self._policy.can_publish(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        async with self._uow.read() as uow:
            campaign = await uow.announcements.get_by_blog(blog_id)
        if campaign is None:
            raise_error(ErrorCategory.BLOG_NOT_FOUND, correlation_id=correlation_id)
        return campaign

    async def retry_campaign(
        self, *, principal: Principal, blog_id: str, correlation_id: str | None = None
    ) -> int:
        require(
            self._policy.can_publish(principal),
            principal=principal,
            correlation_id=correlation_id,
        )
        async with self._uow.begin() as uow:
            campaign = await uow.announcements.get_by_blog(blog_id)
            if campaign is None:
                raise_error(ErrorCategory.BLOG_NOT_FOUND, correlation_id=correlation_id)
            return await uow.announcements.retry_dead(
                blog_id=blog_id, now=self._clock.now()
            )

    def message_for(self, delivery: AnnouncementDelivery) -> EmailMessage:
        token = self._unsubscribe_token(delivery.user_id)
        landing_url = f"{self._site_url}/email/unsubscribe?token={quote(token)}"
        one_click_url = f"{self._site_url}/api/email/unsubscribe?token={quote(token)}"
        return render_announcement(
            delivery,
            unsubscribe_url=landing_url,
            one_click_url=one_click_url,
        )

    def _unsubscribe_token(self, user_id: str) -> str:
        payload = base64.urlsafe_b64encode(user_id.encode("utf-8")).rstrip(b"=")
        signature = hmac.new(
            self._token_secret, _TOKEN_DOMAIN + payload, hashlib.sha256
        ).digest()
        encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=")
        return f"{payload.decode()}.{encoded_signature.decode()}"

    def _verify_unsubscribe_token(self, token: str) -> str:
        payload_text, separator, signature_text = token.partition(".")
        if not separator or not payload_text or not signature_text:
            raise_error(
                ErrorCategory.REQUEST_INVALID,
                safe_message="That unsubscribe link is invalid.",
            )
        try:
            payload = payload_text.encode("ascii")
            signature = _decode_urlsafe(signature_text)
            expected = hmac.new(
                self._token_secret, _TOKEN_DOMAIN + payload, hashlib.sha256
            ).digest()
            user_id = _decode_urlsafe(payload_text).decode("utf-8")
        except (UnicodeError, ValueError):
            raise_error(
                ErrorCategory.REQUEST_INVALID,
                safe_message="That unsubscribe link is invalid.",
            )
        if not hmac.compare_digest(signature, expected):
            raise_error(
                ErrorCategory.REQUEST_INVALID,
                safe_message="That unsubscribe link is invalid.",
            )
        return user_id


def _decode_urlsafe(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.b64decode(value + padding, altchars=b"-_", validate=True)


def render_announcement(
    delivery: AnnouncementDelivery,
    *,
    unsubscribe_url: str,
    one_click_url: str,
) -> EmailMessage:
    """Render one provider-independent multipart announcement."""
    details = [value for value in (delivery.tier, delivery.difficulty) if value]
    tags = ", ".join(delivery.tag_keys)
    text_parts = [
        "BLOG OF TODAY",
        "",
        delivery.title,
        "",
        delivery.summary or "A new evidence-based article is ready to read.",
    ]
    if details:
        text_parts.extend(("", " · ".join(details)))
    if tags:
        text_parts.extend(("", f"Topics: {tags}"))
    text_parts.extend(
        (
            "",
            _MISSION,
            "",
            f"Read the full article: {delivery.article_url}",
            "",
            f"Unsubscribe from new-blog emails: {unsubscribe_url}",
        )
    )

    cover = ""
    if delivery.cover_image_url and delivery.cover_image_alt:
        cover = (
            f'<img src="{escape(delivery.cover_image_url, quote=True)}" '
            f'alt="{escape(delivery.cover_image_alt, quote=True)}" width="640" '
            'style="display:block;width:100%;height:auto;margin:0 0 24px">'
        )
    detail_html = (
        f'<p style="font-size:13px;color:#606060;margin:0 0 12px">'
        f"{escape(' · '.join(details))}</p>"
        if details
        else ""
    )
    tags_html = (
        f'<p style="font-size:13px;color:#606060;margin:0 0 20px">'
        f"Topics: {escape(tags)}</p>"
        if tags
        else ""
    )
    summary = escape(
        delivery.summary or "A new evidence-based article is ready to read."
    )
    html = f"""\
<!doctype html>
<html lang="en">
  <body style="margin:0;background:#f5f5f3;color:#111">
    <div style="display:none;max-height:0;overflow:hidden">A new article from Canery.</div>
    <main style="max-width:640px;margin:0 auto;padding:36px 24px;background:#fff;
                 font-family:system-ui,-apple-system,sans-serif;line-height:1.6">
      <p style="font-size:12px;letter-spacing:.14em;margin:0 0 18px">BLOG OF TODAY</p>
      {cover}
      <h1 style="font-size:30px;line-height:1.2;margin:0 0 16px">{escape(delivery.title)}</h1>
      <p style="font-size:17px;color:#454545;margin:0 0 16px">{summary}</p>
      {detail_html}{tags_html}
      <p style="margin:0 0 24px">{escape(_MISSION)}</p>
      <p style="margin:0 0 30px">
        <a href="{escape(delivery.article_url, quote=True)}"
           style="display:inline-block;background:#111;color:#fff;padding:12px 18px;
                  text-decoration:none">Read the full article</a>
      </p>
      <p style="font-size:12px;color:#707070;margin:0">
        You receive this because you have a Canery account.
        <a href="{escape(unsubscribe_url, quote=True)}" style="color:#505050">Unsubscribe</a>.
      </p>
    </main>
  </body>
</html>"""
    return EmailMessage(
        to=delivery.recipient_email,
        subject=f"New on Canery: {delivery.title}",
        text="\n".join(text_parts),
        html=html,
        headers={
            "List-Unsubscribe": f"<{one_click_url}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        },
        idempotency_key=f"blog-announcement-{delivery.campaign_id}-{delivery.user_id}",
    )


__all__ = ["AnnouncementService", "render_announcement"]
