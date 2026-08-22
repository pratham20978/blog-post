"""Driven ports that are not repositories: storage, tokens, providers, policy.

Each is the seam where a technology would otherwise appear in the application
layer. The domain names the capability; an adapter supplies it.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from blogs.contracts.blog import MarkdownDocument
from blogs.contracts.identity import (
    AccessTokenClaims,
    OAuthProfile,
    OAuthProviderName,
    Principal,
)


class ObjectStore(Protocol):
    """Foundation §8. The adapter is MinIO; nothing above this knows that."""

    async def put(
        self, *, key: str, data: bytes, content_type: str
    ) -> str:
        """Store bytes, returning a URI. Idempotent for a content-addressed key."""
        ...

    async def get(self, uri: str) -> bytes:
        """Raises ``ObjectNotFound`` when the key is absent."""
        ...

    async def exists(self, uri: str) -> bool: ...

    async def delete(self, uri: str) -> None: ...

    async def presign_get(self, uri: str, ttl_seconds: int) -> str: ...

    async def ensure_bucket(self) -> None: ...

    async def healthcheck(self) -> bool: ...


class AccessTokenCodec(Protocol):
    """Mints and verifies the short-lived access token.

    ``verify`` must not touch the database. The moment it does, every
    authenticated request costs a round trip and the "stateless" claim in
    foundation §3 stops being true.
    """

    def issue(
        self, *, user_id: str, actor_id: str, is_admin: bool, now: datetime
    ) -> tuple[str, AccessTokenClaims]: ...

    def verify(self, token: str, *, now: datetime) -> AccessTokenClaims:
        """Raises ``TokenInvalid`` or ``TokenExpired``."""
        ...


class ActorTokenCodec(Protocol):
    """Mints and verifies the long-lived anonymous actor token.

    Server-signed, so an actor id cannot be forged or borrowed. A client-chosen
    id would let anyone write engagement as anyone else and poison the log F1
    and F2 read.
    """

    def issue(self, actor_id: str, *, now: datetime) -> str: ...

    def verify(self, token: str, *, now: datetime) -> str: ...


class SecretHasher(Protocol):
    """One-way hashing for stored credentials, with constant-time comparison."""

    def hash_otp(self, code: str) -> bytes: ...

    def hash_token(self, secret: str) -> bytes: ...

    def new_token_secret(self) -> str: ...

    def new_otp_code(self, length: int) -> str: ...

    def compare(self, left: bytes, right: bytes) -> bool: ...


class PasswordHasher(Protocol):
    """Admin password hashing.

    Separate from ``SecretHasher`` because the threat is different. A refresh
    token is 256 random bits and an OTP code lives ten minutes; a password is
    low-entropy and long-lived, so it is the one credential here that can
    genuinely be brute-forced offline from a stolen database. That calls for a
    memory-hard function, not a fast digest — which is why these are two ports
    and not two methods on one.
    """

    def hash(self, password: str) -> bytes: ...

    def verify(self, password: str, stored: bytes | None) -> bool:
        """Must take the same time whether or not ``stored`` is present, or the
        response becomes an oracle for which accounts have credentials."""
        ...


class OAuthProvider(Protocol):
    name: OAuthProviderName

    def authorization_url(self, *, state: str, code_verifier: str, redirect_uri: str) -> str: ...

    async def exchange(
        self, *, code: str, code_verifier: str, redirect_uri: str
    ) -> OAuthProfile:
        """Raises ``OAuthExchangeFailed``."""
        ...


class MarkdownParser(Protocol):
    """Parses, never renders.

    Doc 00 §30 stops this work at the HTTP port, so choosing an output format
    would be deciding a presentation question for a client that does not exist.
    What is extracted is what the domain needs: frontmatter metadata, heading
    anchors, and a word count.
    """

    def parse(self, source: bytes) -> MarkdownDocument:
        """Raises ``MarkdownInvalid`` for undecodable input."""
        ...


class AuthorizationPolicy(Protocol):
    """The single place a permission question is answered.

    Doc 01 puts authorization in the application layer behind a policy port, so
    every write use case asks here first and no route re-derives the rule.
    """

    def can_publish(self, principal: Principal) -> bool: ...

    def can_edit_blog(self, principal: Principal) -> bool: ...

    def can_archive_blog(self, principal: Principal) -> bool: ...

    def can_manage_pins(self, principal: Principal) -> bool: ...

    def can_manage_taxonomy(self, principal: Principal) -> bool: ...

    def can_read_analytics(self, principal: Principal) -> bool: ...

    def can_moderate(self, principal: Principal) -> bool: ...

    def can_comment(self, principal: Principal) -> bool: ...

    def can_mark(self, principal: Principal) -> bool: ...

    def can_save(self, principal: Principal) -> bool: ...

    def can_record_engagement(self, principal: Principal) -> bool:
        """True for anonymous visitors too — that is the point of the actor id."""
        ...
