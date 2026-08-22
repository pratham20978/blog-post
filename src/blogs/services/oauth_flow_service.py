"""The OAuth handshake, without server-side flow state.

The problem: the authorization-code flow needs two things to survive the round
trip to the provider — a CSRF ``state`` and the PKCE ``code_verifier``. The
obvious solution is a ``pending_oauth_flows`` table, and foundation §3 rules
that out.

So the state *is* the storage: a short-lived signed JWT carrying the verifier,
the provider and the return path. The provider hands it back untouched, the
signature proves this server minted it, and the five-minute expiry bounds
replay. Nothing is written, nothing needs cleaning up, and a second API replica
can complete a flow the first one started.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import jwt

from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import OAuthProfile, OAuthProviderName
from blogs.core.clock import Clock
from blogs.core.errors import BlogPlatformError, raise_error
from blogs.core.registry import Registry

logger = logging.getLogger(__name__)

_ALGORITHM = "HS256"
_AUDIENCE = "oauth-state"

#: Long enough for a human to complete a provider's consent screen, short
#: enough that a leaked callback URL is not useful later.
_STATE_TTL = timedelta(minutes=5)


class OAuthFlowService:
    def __init__(
        self,
        *,
        providers: Registry[str, Any],
        clock: Clock,
        state_secret: str,
        issuer: str,
        redirect_base_url: str,
    ) -> None:
        self._providers = providers
        self._clock = clock
        self._secret = state_secret
        self._issuer = issuer
        self._redirect_base = redirect_base_url.rstrip("/")

    def _redirect_uri(self, provider: OAuthProviderName) -> str:
        return f"{self._redirect_base}/api/v1/auth/oauth/{provider.value}/callback"

    def _resolve(self, provider: OAuthProviderName, correlation_id: str | None) -> Any:
        adapter = self._providers.resolve(provider.value)
        if adapter is None:
            # Unconfigured providers are absent rather than broken, so this
            # fails at the start of the flow instead of after the user has
            # already been bounced to a login screen.
            raise_error(
                ErrorCategory.OAUTH_PROVIDER_UNKNOWN,
                correlation_id=correlation_id,
                safe_details={"provider": provider.value},
            )
        return adapter

    async def start(
        self,
        *,
        provider: OAuthProviderName,
        redirect_path: str = "/",
        correlation_id: str | None = None,
    ) -> tuple[str, str]:
        from blogs.adapters.oauth.providers import new_pkce_pair

        adapter = self._resolve(provider, correlation_id)
        verifier, _ = new_pkce_pair()
        now = self._clock.now()

        state = jwt.encode(
            {
                "iss": self._issuer,
                "aud": _AUDIENCE,
                "prv": provider.value,
                "vfy": verifier,
                # Only a path is carried, never a full URL: echoing back an
                # absolute URL would make this an open redirect.
                "rdr": redirect_path if redirect_path.startswith("/") else "/",
                "iat": int(now.timestamp()),
                "exp": int((now + _STATE_TTL).timestamp()),
            },
            self._secret,
            algorithm=_ALGORITHM,
        )
        url = adapter.authorization_url(
            state=state,
            code_verifier=verifier,
            redirect_uri=self._redirect_uri(provider),
        )
        return url, state

    async def complete(
        self,
        *,
        provider: OAuthProviderName,
        code: str,
        state: str,
        correlation_id: str | None = None,
    ) -> OAuthProfile:
        adapter = self._resolve(provider, correlation_id)
        try:
            claims = jwt.decode(
                state,
                self._secret,
                algorithms=[_ALGORITHM],
                audience=_AUDIENCE,
                issuer=self._issuer,
                options={"require": ["exp", "prv", "vfy"]},
            )
        except jwt.InvalidTokenError as exc:
            # An explicit raise rather than `raise_error`, so the original JWT
            # failure stays chained as __cause__ for the log.
            raise BlogPlatformError(
                ErrorCategory.OAUTH_STATE_INVALID, correlation_id=correlation_id
            ) from exc

        # The state names the provider it was minted for. Without this check a
        # state issued for one provider could be replayed against another.
        if claims["prv"] != provider.value:
            raise_error(ErrorCategory.OAUTH_STATE_INVALID, correlation_id=correlation_id)

        profile: OAuthProfile = await adapter.exchange(
            code=code,
            code_verifier=claims["vfy"],
            redirect_uri=self._redirect_uri(provider),
        )
        return profile

    def redirect_path_of(self, state: str) -> str:
        """Where to send the browser once sign-in completes. Never trusted as
        a full URL — see ``start``."""
        try:
            claims = jwt.decode(
                state,
                self._secret,
                algorithms=[_ALGORITHM],
                audience=_AUDIENCE,
                issuer=self._issuer,
                options={"verify_exp": False},
            )
        except jwt.InvalidTokenError:
            return "/"
        path = claims.get("rdr", "/")
        return path if isinstance(path, str) and path.startswith("/") else "/"
