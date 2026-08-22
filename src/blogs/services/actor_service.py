"""Resolving who is calling — including when nobody is signed in.

This is the front door for every request. It returns a ``Principal``, and the
important property is that it always returns one: an unauthenticated visitor
gets a real, server-issued actor rather than ``None``. Downstream code therefore
never branches on "is there a caller"; engagement, recent views and reads take
one path whether or not an account exists.

The actor token is signed by us. A client-chosen device id would be trivially
forgeable, and forging one means writing engagement as someone else — corrupting
the log that F1's affinity and F2's segmentation are computed from.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from blogs.contracts.identity import (
    AnonymousPrincipal,
    Principal,
    UserPrincipal,
)
from blogs.core.clock import Clock
from blogs.core.errors import BlogPlatformError
from blogs.core.ids import IdGenerator
from blogs.ports.services import AccessTokenCodec, ActorTokenCodec
from blogs.ports.uow import UnitOfWorkFactory

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ResolvedCaller:
    principal: Principal
    #: Set when a new actor was minted, so the transport can hand it back. The
    #: client stores it and presents it from then on.
    issued_actor_token: str | None = None


class ActorService:
    def __init__(
        self,
        *,
        uow: UnitOfWorkFactory,
        clock: Clock,
        ids: IdGenerator,
        access_tokens: AccessTokenCodec,
        actor_tokens: ActorTokenCodec,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._ids = ids
        self._access = access_tokens
        self._actor = actor_tokens

    async def resolve(
        self, *, authorization: str | None, actor_token: str | None
    ) -> ResolvedCaller:
        """Identify the caller from whatever credentials arrived.

        An access token wins when present and valid. Note what happens when it
        is *invalid*: this raises rather than quietly degrading to anonymous.
        Silently downgrading would turn an expired session into a confusing
        "why am I logged out but the page still works" state, and would hide
        a real authentication failure from the client.
        """
        now = self._clock.now()

        if authorization:
            claims = self._access.verify(self._bearer(authorization), now=now)
            return ResolvedCaller(
                principal=UserPrincipal(
                    actor_id=claims.actor_id,
                    user_id=claims.user_id,
                    is_admin=claims.is_admin,
                )
            )

        if actor_token:
            try:
                actor_id = self._actor.verify(actor_token, now=now)
            except BlogPlatformError:
                # A tampered or long-expired actor token is not worth an error
                # page for a reader who is just browsing. Issue a fresh actor
                # and carry on; the cost is a lost anonymous history, not a
                # failed request.
                logger.info("actor token rejected; minting a replacement")
                return await self._mint()
            await self._touch(actor_id)
            return ResolvedCaller(principal=AnonymousPrincipal(actor_id=actor_id))

        return await self._mint()

    @staticmethod
    def _bearer(header: str) -> str:
        scheme, _, token = header.partition(" ")
        return token.strip() if scheme.lower() == "bearer" else header.strip()

    async def _mint(
        self, *, user_agent: str | None = None, ip: str | None = None
    ) -> ResolvedCaller:
        actor_id = self._ids.new_id()
        async with self._uow.begin() as uow:
            await uow.actors.create(actor_id=actor_id, user_agent=user_agent, client_ip=ip)
        return ResolvedCaller(
            principal=AnonymousPrincipal(actor_id=actor_id),
            issued_actor_token=self._actor.issue(actor_id, now=self._clock.now()),
        )

    async def _touch(self, actor_id: str) -> None:
        """Move ``last_seen_at``. Best-effort — a lost touch costs nothing, and
        it must never be the reason a page fails to render."""
        try:
            async with self._uow.begin() as uow:
                await uow.actors.touch(actor_id, self._clock.now())
        except BlogPlatformError:
            logger.debug("actor touch failed", exc_info=True)
