"""Public traffic must not manufacture database identities."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from blogs.api.middleware import ACTOR_HEADER, IdentityMiddleware
from blogs.core.clock import FrozenClock
from blogs.services.actor_service import ActorService


@pytest.mark.asyncio
async def test_public_and_unmatched_routes_do_not_issue_actors() -> None:
    app = FastAPI()
    app.add_middleware(IdentityMiddleware)

    @app.get("/public")
    async def public() -> dict[str, bool]:
        return {"ok": True}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        public_response = await client.get("/public")
        missing_response = await client.get("/scanner-probe")

    assert public_response.status_code == 200
    assert ACTOR_HEADER not in public_response.headers
    assert missing_response.status_code == 404
    assert ACTOR_HEADER not in missing_response.headers


@pytest.mark.asyncio
async def test_existing_actor_token_is_verified_without_a_database_touch() -> None:
    actor_id = "00000000-0000-7000-8000-000000000001"
    actor_tokens = Mock()
    actor_tokens.verify.return_value = actor_id
    uow = Mock()
    service = ActorService(
        uow=uow,
        clock=FrozenClock(datetime(2026, 9, 17, tzinfo=UTC)),
        ids=Mock(),
        access_tokens=Mock(),
        actor_tokens=actor_tokens,
    )

    resolved = await service.resolve(authorization=None, actor_token="signed-token")

    assert resolved.principal.actor_id == actor_id
    assert resolved.issued_actor_token is None
    uow.begin.assert_not_called()
