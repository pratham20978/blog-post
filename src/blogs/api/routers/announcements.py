"""Reader blog-email preferences and one-click unsubscribe."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from blogs.api.deps import Assembled, CurrentUser
from blogs.api.envelope import success
from blogs.contracts.announcement import BlogEmailPreference
from blogs.contracts.common import APIResponse, ContractModel

router = APIRouter(tags=["email preferences"])


class BlogEmailPreferenceBody(ContractModel):
    blog_announcements_enabled: bool


@router.get("/me/email-preferences")
async def get_email_preferences(
    user: CurrentUser, assembled: Assembled
) -> APIResponse[BlogEmailPreference]:
    preference = await assembled.announcement_service.get_preference(user)
    return success(preference)


@router.put("/me/email-preferences")
async def update_email_preferences(
    body: BlogEmailPreferenceBody,
    user: CurrentUser,
    assembled: Assembled,
) -> APIResponse[BlogEmailPreference]:
    preference = await assembled.announcement_service.set_preference(
        principal=user, enabled=body.blog_announcements_enabled
    )
    return success(preference, message="Email preference updated.")


@router.post("/email/preferences/unsubscribe")
async def unsubscribe(
    assembled: Assembled,
    token: Annotated[str, Query(min_length=20, max_length=1000)],
) -> APIResponse[BlogEmailPreference]:
    preference = await assembled.announcement_service.unsubscribe(token)
    return success(preference, message="You are unsubscribed from new-blog emails.")


__all__ = ["router"]
