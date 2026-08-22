"""OAuth 2.0 providers, spoken to directly over HTTP.

No OAuth framework. The authorization-code flow with PKCE is three requests, and
a library that hides them would still leave every provider quirk to handle —
GitHub's separate email endpoint, Google's ``email_verified`` claim — while
making the port harder to fake in a test.

Two safety properties are non-negotiable and are enforced here rather than left
to the caller:

* **PKCE on every flow.** The ``code_verifier`` never leaves us, so a stolen
  authorization code cannot be redeemed by whoever stole it.
* **Verified email or nothing.** An unverified address from a provider is an
  account-takeover primitive: anyone able to claim ``victim@example.com`` at a
  sloppy provider would otherwise be handed the existing local account.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import secrets
from typing import Any
from urllib.parse import urlencode

import httpx

from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import OAuthProfile, OAuthProviderName
from blogs.core.errors import BlogPlatformError
from blogs.core.registry import Registry

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


def new_pkce_pair() -> tuple[str, str]:
    """Return ``(verifier, challenge)`` for the S256 method."""
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


class _HttpOAuthProvider:
    name: OAuthProviderName
    _authorize_url: str
    _token_url: str
    _scope: str

    def __init__(self, *, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    def authorization_url(self, *, state: str, code_verifier: str, redirect_uri: str) -> str:
        _, challenge = self._challenge_for(code_verifier)
        query = urlencode(
            {
                "client_id": self._client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": self._scope,
                "state": state,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            }
        )
        return f"{self._authorize_url}?{query}"

    @staticmethod
    def _challenge_for(verifier: str) -> tuple[str, str]:
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        return verifier, base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    async def _exchange_code(
        self, *, code: str, code_verifier: str, redirect_uri: str
    ) -> str:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            try:
                response = await client.post(
                    self._token_url,
                    data={
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "code": code,
                        "code_verifier": code_verifier,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri,
                    },
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                payload = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                # The provider's body can echo the code and the client secret,
                # so it is never logged or surfaced.
                logger.warning(
                    "oauth token exchange failed",
                    extra={"provider": self.name.value},
                    exc_info=True,
                )
                raise BlogPlatformError(ErrorCategory.OAUTH_EXCHANGE_FAILED) from exc

        access_token = payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise BlogPlatformError(ErrorCategory.OAUTH_EXCHANGE_FAILED)
        return access_token

    async def _get_json(self, url: str, access_token: str) -> Any:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            try:
                response = await client.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json",
                    },
                )
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError) as exc:
                raise BlogPlatformError(ErrorCategory.OAUTH_EXCHANGE_FAILED) from exc


class GoogleOAuthProvider(_HttpOAuthProvider):
    name = OAuthProviderName.GOOGLE
    _authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
    _token_url = "https://oauth2.googleapis.com/token"  # noqa: S105 — an endpoint
    _userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
    _scope = "openid email profile"

    async def exchange(
        self, *, code: str, code_verifier: str, redirect_uri: str
    ) -> OAuthProfile:
        access_token = await self._exchange_code(
            code=code, code_verifier=code_verifier, redirect_uri=redirect_uri
        )
        info = await self._get_json(self._userinfo_url, access_token)
        subject = info.get("sub")
        if not subject:
            raise BlogPlatformError(ErrorCategory.OAUTH_EXCHANGE_FAILED)

        return OAuthProfile(
            provider=self.name,
            subject=str(subject),
            email=info.get("email"),
            # Google sends this as a real bool; anything else is treated as
            # unverified rather than coerced.
            email_verified=info.get("email_verified") is True,
            display_name=info.get("name"),
        )


class GitHubOAuthProvider(_HttpOAuthProvider):
    name = OAuthProviderName.GITHUB
    _authorize_url = "https://github.com/login/oauth/authorize"
    _token_url = "https://github.com/login/oauth/access_token"  # noqa: S105 — an endpoint
    _user_url = "https://api.github.com/user"
    _emails_url = "https://api.github.com/user/emails"
    _scope = "read:user user:email"

    async def exchange(
        self, *, code: str, code_verifier: str, redirect_uri: str
    ) -> OAuthProfile:
        access_token = await self._exchange_code(
            code=code, code_verifier=code_verifier, redirect_uri=redirect_uri
        )
        user = await self._get_json(self._user_url, access_token)
        subject = user.get("id")
        if subject is None:
            raise BlogPlatformError(ErrorCategory.OAUTH_EXCHANGE_FAILED)

        # GitHub's /user omits the address when the profile hides it, and says
        # nothing about verification either way — so the addresses endpoint is
        # the only source that answers the question we actually care about.
        email, verified = None, False
        for entry in await self._get_json(self._emails_url, access_token):
            if entry.get("primary") and entry.get("verified"):
                email, verified = entry.get("email"), True
                break

        return OAuthProfile(
            provider=self.name,
            subject=str(subject),
            email=email,
            email_verified=verified,
            display_name=user.get("name") or user.get("login"),
        )


def build_provider_registry(
    *,
    google_client_id: str | None,
    google_client_secret: str | None,
    github_client_id: str | None,
    github_client_secret: str | None,
) -> Registry[str, Any]:
    """Register only the providers that are actually configured.

    An unconfigured provider is absent rather than present-and-broken, so the
    failure is ``OAUTH_PROVIDER_UNKNOWN`` at the start of the flow instead of an
    exchange failure after the user has already been bounced to a login screen.
    """
    registry: Registry[str, Any] = Registry("oauth_providers")
    if google_client_id and google_client_secret:
        registry.register(
            OAuthProviderName.GOOGLE.value,
            GoogleOAuthProvider(
                client_id=google_client_id, client_secret=google_client_secret
            ),
        )
    if github_client_id and github_client_secret:
        registry.register(
            OAuthProviderName.GITHUB.value,
            GitHubOAuthProvider(
                client_id=github_client_id, client_secret=github_client_secret
            ),
        )
    return registry
