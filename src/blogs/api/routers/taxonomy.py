"""Categories and series — public reads.

Split out of the analytics router deliberately. That one is mounted behind the
secret admin prefix, and these two endpoints are for readers: filtering the feed
by category needs the list of categories, so hiding them would break the public
site to protect nothing.
"""

from __future__ import annotations

from fastapi import APIRouter

from blogs.api.deps import Assembled
from blogs.api.envelope import success
from blogs.contracts.blog import Category, Series
from blogs.contracts.common import APIResponse

router = APIRouter(tags=["taxonomy"])


@router.get("/categories")
async def list_categories(assembled: Assembled) -> APIResponse[tuple[Category, ...]]:
    async with assembled.uow.read() as uow:
        return success(await uow.taxonomy.list_categories())


@router.get("/series")
async def list_series(assembled: Assembled) -> APIResponse[tuple[Series, ...]]:
    async with assembled.uow.read() as uow:
        return success(await uow.taxonomy.list_series())
