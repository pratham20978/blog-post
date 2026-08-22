"""Token minting and verification, and the hashing behind stored credentials.

The one rule that shapes this module: ``verify`` never touches the database.
Foundation §3 requires stateless authentication, and the moment a signature
check needs a row, every authenticated request costs a round trip and the claim
stops being true. The refresh registry exists precisely so that revocation does
not have to live on this path.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

import jwt

from blogs.contracts.common import ErrorCategory
from blogs.contracts.identity import AccessTokenClaims
from blogs.core.errors import BlogPlatformError
from blogs.core.ids import random_id

_ALGORITHM = "HS256"

#: Distinguishes an access token from an actor token even if the two ever shared
#: a key. Without it, a long-lived anonymous token could be presented where a
#: short-lived authenticated one is expected — the classic token-confusion bug.
_ACCESS_AUDIENCE = "access"
_ACTOR_AUDIENCE = "actor"


class JwtAccessTokenCodec:
    def __init__(self, *, secret: str, issuer: str, ttl_seconds: int) -> None:
        self._secret = secret
        self._issuer = issuer
        self._ttl = timedelta(seconds=ttl_seconds)

    def issue(
        self, *, user_id: str, actor_id: str, is_admin: bool, now: datetime
    ) -> tuple[str, AccessTokenClaims]:
        expires_at = now + self._ttl
        token_id = random_id()
        payload = {
            "iss": self._issuer,
            "aud": _ACCESS_AUDIENCE,
            "sub": user_id,
            "act": actor_id,
            "adm": is_admin,
            "jti": token_id,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
        }
        token = jwt.encode(payload, self._secret, algorithm=_ALGORITHM)
        return token, AccessTokenClaims(
            user_id=user_id,
            actor_id=actor_id,
            is_admin=is_admin,
            token_id=token_id,
            issued_at=now,
            expires_at=expires_at,
        )

    def verify(self, token: str, *, now: datetime) -> AccessTokenClaims:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                # A list of exactly one: passing the expected algorithm is what
                # prevents an attacker re-signing with "none" or downgrading to
                # a weaker one.
                algorithms=[_ALGORITHM],
                audience=_ACCESS_AUDIENCE,
                issuer=self._issuer,
                options={"require": ["exp", "iat", "sub", "jti"]},
            )
        except jwt.ExpiredSignatureError as exc:
            raise BlogPlatformError(ErrorCategory.AUTH_TOKEN_EXPIRED) from exc
        except jwt.InvalidTokenError as exc:
            raise BlogPlatformError(ErrorCategory.AUTH_TOKEN_INVALID) from exc

        return AccessTokenClaims(
            user_id=payload["sub"],
            actor_id=payload["act"],
            is_admin=bool(payload.get("adm", False)),
            token_id=payload["jti"],
            issued_at=datetime.fromtimestamp(payload["iat"], tz=now.tzinfo),
            expires_at=datetime.fromtimestamp(payload["exp"], tz=now.tzinfo),
        )


class JwtActorTokenCodec:
    """The anonymous visitor's identity.

    Server-signed rather than client-chosen. A client-supplied device id would
    be forgeable, and forging one means writing engagement as somebody else —
    poisoning the log that F1's affinity and F2's segmentation are built on.
    """

    def __init__(self, *, secret: str, issuer: str, ttl_seconds: int) -> None:
        self._secret = secret
        self._issuer = issuer
        self._ttl = timedelta(seconds=ttl_seconds)

    def issue(self, actor_id: str, *, now: datetime) -> str:
        payload = {
            "iss": self._issuer,
            "aud": _ACTOR_AUDIENCE,
            "sub": actor_id,
            "iat": int(now.timestamp()),
            "exp": int((now + self._ttl).timestamp()),
        }
        return jwt.encode(payload, self._secret, algorithm=_ALGORITHM)

    def verify(self, token: str, *, now: datetime) -> str:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[_ALGORITHM],
                audience=_ACTOR_AUDIENCE,
                issuer=self._issuer,
                options={"require": ["exp", "sub"]},
            )
        except jwt.InvalidTokenError as exc:
            raise BlogPlatformError(ErrorCategory.ACTOR_TOKEN_INVALID) from exc
        return str(payload["sub"])


class Sha256SecretHasher:
    """Hashing for the two stored credential types.

    Both are SHA-256 with a pepper rather than a slow KDF, and the reasoning
    differs for each:

    * **Refresh tokens** are 256 bits of CSPRNG output. There is no dictionary to
      attack, so key stretching buys nothing — the hash exists so that a leaked
      database does not hand over usable tokens.
    * **OTP codes** have only a million possibilities, so a stolen database
      *could* be brute-forced offline. What protects them is that they live for
      ten minutes, allow five attempts, and are single-use. The pepper is what
      makes precomputation useless, and it is held outside the database.

    If OTP codes ever became long-lived, this reasoning would stop holding and
    the algorithm would have to change with it.
    """

    def __init__(self, *, otp_pepper: str) -> None:
        self._otp_pepper = otp_pepper.encode("utf-8")

    def hash_otp(self, code: str) -> bytes:
        return hashlib.sha256(self._otp_pepper + code.encode("utf-8")).digest()

    def hash_token(self, secret: str) -> bytes:
        return hashlib.sha256(secret.encode("utf-8")).digest()

    def new_token_secret(self) -> str:
        return secrets.token_urlsafe(32)

    def new_otp_code(self, length: int) -> str:
        """A numeric code with no modulo bias.

        ``randbelow`` over the exact range, rather than ``randint`` on each digit
        or a modulo of a larger random — both of which skew the distribution and
        shrink the effective keyspace.
        """
        upper = 10**length
        return str(secrets.randbelow(upper)).zfill(length)

    def compare(self, left: bytes, right: bytes) -> bool:
        """Constant-time. A byte-wise ``==`` leaks the position of the first
        mismatch through timing, which is enough to recover a short code."""
        return hmac.compare_digest(left, right)
