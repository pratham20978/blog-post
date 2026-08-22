"""SQL adapters for accounts and credentials."""

from __future__ import annotations

from datetime import datetime

from psycopg import errors
from psycopg.rows import DictRow

from blogs.contracts.identity import (
    AnonymousActor,
    AuthPurpose,
    OAuthProviderName,
    OtpChallenge,
    RefreshTokenRecord,
    User,
    UserStatus,
)
from blogs.repository.base import SqlRepository, as_utc, translate_integrity_error

_USER_COLUMNS = """
    id, email, display_name, is_admin, status,
    email_verified_at, created_at, updated_at
"""


def _to_user(row: DictRow) -> User:
    return User(
        id=str(row["id"]),
        email=row["email"],
        display_name=row["display_name"],
        is_admin=row["is_admin"],
        status=UserStatus(row["status"]),
        email_verified_at=row["email_verified_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class SqlUserRepository(SqlRepository):
    async def get(self, user_id: str) -> User | None:
        row = await self._fetch_one(
            f"SELECT {_USER_COLUMNS} FROM users WHERE id = %(id)s", {"id": user_id}
        )
        return _to_user(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        # Compares against the generated column, so the match is exactly what
        # the unique index enforces rather than whatever this call remembered
        # to normalise.
        row = await self._fetch_one(
            f"SELECT {_USER_COLUMNS} FROM users WHERE email_normalized = lower(btrim(%(e)s))",
            {"e": email},
        )
        return _to_user(row) if row else None

    async def create(
        self,
        *,
        user_id: str,
        email: str,
        display_name: str | None,
        is_admin: bool,
        email_verified_at: datetime | None,
    ) -> User:
        try:
            row = await self._fetch_one(
                f"""
                INSERT INTO users (id, email, display_name, is_admin, email_verified_at)
                VALUES (%(id)s, %(email)s, %(name)s, %(admin)s, %(verified)s)
                RETURNING {_USER_COLUMNS}
                """,
                {
                    "id": user_id,
                    "email": email,
                    "name": display_name,
                    "admin": is_admin,
                    "verified": as_utc(email_verified_at) if email_verified_at else None,
                },
            )
        except errors.IntegrityError as exc:
            raise translate_integrity_error(exc) from exc
        assert row is not None
        return _to_user(row)

    async def set_status(self, user_id: str, status: UserStatus) -> None:
        await self._execute(
            "UPDATE users SET status = %(s)s WHERE id = %(id)s",
            {"s": status.value, "id": user_id},
        )

    async def mark_email_verified(self, user_id: str, at: datetime) -> None:
        # COALESCE: the first verification is the one that counts, so a later
        # sign-in does not keep moving the date forward.
        await self._execute(
            "UPDATE users SET email_verified_at = COALESCE(email_verified_at, %(at)s) "
            "WHERE id = %(id)s",
            {"at": as_utc(at), "id": user_id},
        )

    async def get_admin(self) -> User | None:
        row = await self._fetch_one(
            f"SELECT {_USER_COLUMNS} FROM users WHERE is_admin LIMIT 1"
        )
        return _to_user(row) if row else None

    async def get_password_hash(self, user_id: str) -> bytes | None:
        """Read the stored hash.

        Deliberately not part of ``User``: the hash has exactly one caller and
        keeping it off the contract means it cannot be serialised into a
        response by accident.
        """
        row = await self._fetch_one(
            "SELECT password_hash FROM users WHERE id = %(id)s", {"id": user_id}
        )
        if row is None or row["password_hash"] is None:
            return None
        return bytes(row["password_hash"])

    async def set_password(self, *, user_id: str, password_hash: bytes, at: datetime) -> None:
        """Set or rotate the admin's password.

        The ``is_admin`` predicate mirrors the CHECK constraint: a reader can
        never acquire a password, whichever path calls this.
        """
        try:
            await self._execute(
                """
                UPDATE users
                SET password_hash = %(hash)s, password_updated_at = %(at)s
                WHERE id = %(id)s AND is_admin
                """,
                {"hash": password_hash, "at": as_utc(at), "id": user_id},
            )
        except errors.IntegrityError as exc:
            raise translate_integrity_error(exc) from exc


class SqlAdminLoginAttemptRepository(SqlRepository):
    """The admin sign-in audit log, and the lockout that reads it."""

    async def record(
        self,
        *,
        attempt_id: str,
        email: str,
        succeeded: bool,
        at: datetime,
        client_ip: str | None,
        user_agent: str | None,
    ) -> None:
        """Log one attempt.

        ``attempted_at`` is stamped from the caller's clock rather than left to
        the column default. The lockout window is computed from that same
        injected clock, and two different time sources cannot be compared: with
        the DB default, every attempt landed outside the window whenever the
        two disagreed, and the lockout silently never triggered.
        """
        await self._execute(
            """
            INSERT INTO admin_login_attempts
                (id, email_normalized, succeeded, attempted_at, client_ip, user_agent)
            VALUES (%(id)s, lower(btrim(%(e)s)), %(ok)s, %(at)s, %(ip)s, %(ua)s)
            """,
            {
                "id": attempt_id,
                "e": email,
                "ok": succeeded,
                "at": as_utc(at),
                "ip": client_ip,
                "ua": user_agent,
            },
        )

    async def recent_failures(self, *, email: str, since: datetime) -> int:
        """Failures since a cutoff.

        Counted only since the last *success*: a correct password clears the
        slate, so an admin who mistypes four times, succeeds, then mistypes
        again is not one attempt from being locked out.
        """
        row = await self._fetch_one(
            """
            SELECT count(*) AS n FROM admin_login_attempts
            WHERE email_normalized = lower(btrim(%(e)s))
              AND attempted_at >= %(since)s
              AND NOT succeeded
              AND attempted_at > COALESCE((
                  SELECT max(attempted_at) FROM admin_login_attempts
                  WHERE email_normalized = lower(btrim(%(e)s)) AND succeeded
              ), '-infinity'::timestamptz)
            """,
            {"e": email, "since": as_utc(since)},
        )
        return int(row["n"]) if row else 0

    async def delete_older_than(self, before: datetime) -> int:
        return await self._execute(
            "DELETE FROM admin_login_attempts WHERE attempted_at < %(before)s",
            {"before": as_utc(before)},
        )


class SqlOAuthIdentityRepository(SqlRepository):
    async def find_user_id(
        self, provider: OAuthProviderName, provider_subject: str
    ) -> str | None:
        row = await self._fetch_one(
            "SELECT user_id FROM oauth_identities "
            "WHERE provider = %(p)s AND provider_subject = %(s)s",
            {"p": provider.value, "s": provider_subject},
        )
        return str(row["user_id"]) if row else None

    async def link(
        self,
        *,
        identity_id: str,
        user_id: str,
        provider: OAuthProviderName,
        provider_subject: str,
        email_at_provider: str | None,
    ) -> None:
        # Idempotent: signing in again with a provider already linked updates
        # the recorded address rather than failing.
        await self._execute(
            """
            INSERT INTO oauth_identities
                (id, user_id, provider, provider_subject, email_at_provider)
            VALUES (%(id)s, %(uid)s, %(p)s, %(s)s, %(email)s)
            ON CONFLICT (provider, provider_subject)
            DO UPDATE SET email_at_provider = EXCLUDED.email_at_provider
            """,
            {
                "id": identity_id,
                "uid": user_id,
                "p": provider.value,
                "s": provider_subject,
                "email": email_at_provider,
            },
        )


_OTP_COLUMNS = """
    id, email_normalized, purpose, expires_at, attempts,
    max_attempts, consumed_at, created_at
"""


def _to_challenge(row: DictRow) -> OtpChallenge:
    return OtpChallenge(
        id=str(row["id"]),
        email=row["email_normalized"],
        purpose=AuthPurpose(row["purpose"]),
        expires_at=row["expires_at"],
        attempts=row["attempts"],
        max_attempts=row["max_attempts"],
        consumed_at=row["consumed_at"],
        created_at=row["created_at"],
    )


class SqlOtpChallengeRepository(SqlRepository):
    async def create(
        self,
        *,
        challenge_id: str,
        email: str,
        purpose: AuthPurpose,
        code_hash: bytes,
        expires_at: datetime,
        max_attempts: int,
        client_ip: str | None,
    ) -> OtpChallenge:
        row = await self._fetch_one(
            f"""
            INSERT INTO otp_challenges
                (id, email_normalized, purpose, code_hash,
                 expires_at, max_attempts, requested_ip)
            VALUES (%(id)s, lower(btrim(%(e)s)), %(p)s, %(hash)s,
                    %(exp)s, %(max)s, %(ip)s)
            RETURNING {_OTP_COLUMNS}
            """,
            {
                "id": challenge_id,
                "e": email,
                "p": purpose.value,
                "hash": code_hash,
                "exp": as_utc(expires_at),
                "max": max_attempts,
                "ip": client_ip,
            },
        )
        assert row is not None
        return _to_challenge(row)

    async def latest_live(self, email: str, purpose: AuthPurpose) -> OtpChallenge | None:
        row = await self._fetch_one(
            f"""
            SELECT {_OTP_COLUMNS} FROM otp_challenges
            WHERE email_normalized = lower(btrim(%(e)s))
              AND purpose = %(p)s
              AND consumed_at IS NULL
            ORDER BY created_at DESC
            LIMIT 1
            """,
            {"e": email, "p": purpose.value},
        )
        return _to_challenge(row) if row else None

    async def consume_if_matching(
        self, *, email: str, purpose: AuthPurpose, code_hash: bytes, now: datetime
    ) -> tuple[OtpChallenge | None, str]:
        """Verify and burn in one statement.

        The whole check is a single UPDATE against the newest live challenge.
        Incrementing ``attempts`` in the same statement that tests the hash is
        what makes the limit hold under concurrency: a read-then-write would let
        N parallel guesses all observe the same count and collectively spend far
        more than ``max_attempts``.

        ``consumed_at`` is set only on a match, so a wrong guess costs an
        attempt but does not destroy a code the legitimate user is still typing.
        """
        row = await self._fetch_one(
            """
            WITH target AS (
                SELECT id FROM otp_challenges
                WHERE email_normalized = lower(btrim(%(e)s))
                  AND purpose = %(p)s
                  AND consumed_at IS NULL
                ORDER BY created_at DESC
                LIMIT 1
                FOR UPDATE
            ),
            updated AS (
                UPDATE otp_challenges c
                SET attempts    = c.attempts + 1,
                    consumed_at = CASE
                        WHEN c.code_hash = %(hash)s
                         AND c.expires_at > %(now)s
                         AND c.attempts < c.max_attempts
                        THEN %(now)s ELSE NULL END
                FROM target
                WHERE c.id = target.id
                RETURNING c.id, c.email_normalized, c.purpose, c.expires_at,
                          c.attempts, c.max_attempts, c.consumed_at, c.created_at,
                          (c.code_hash = %(hash)s) AS hash_ok
            )
            SELECT * FROM updated
            """,
            {"e": email, "p": purpose.value, "hash": code_hash, "now": as_utc(now)},
        )
        if row is None:
            return None, "missing"

        challenge = _to_challenge(row)
        # attempts was incremented above, so the pre-attempt count is one less.
        if challenge.attempts > challenge.max_attempts:
            return challenge, "exhausted"
        if challenge.expires_at <= now:
            return challenge, "expired"
        if not row["hash_ok"]:
            return challenge, "mismatch"
        return challenge, "matched"

    async def delete_expired(self, before: datetime) -> int:
        return await self._execute(
            "DELETE FROM otp_challenges WHERE expires_at < %(before)s",
            {"before": as_utc(before)},
        )


_REFRESH_COLUMNS = """
    id, user_id, family_id, issued_at, expires_at,
    consumed_at, replaced_by_id, revoked_at, revoked_reason
"""


def _to_refresh(row: DictRow) -> RefreshTokenRecord:
    return RefreshTokenRecord(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        family_id=str(row["family_id"]),
        issued_at=row["issued_at"],
        expires_at=row["expires_at"],
        consumed_at=row["consumed_at"],
        replaced_by_id=str(row["replaced_by_id"]) if row["replaced_by_id"] else None,
        revoked_at=row["revoked_at"],
        revoked_reason=row["revoked_reason"],
    )


class SqlRefreshTokenRepository(SqlRepository):
    async def create(
        self,
        *,
        token_id: str,
        user_id: str,
        family_id: str,
        token_hash: bytes,
        expires_at: datetime,
        user_agent: str | None,
        client_ip: str | None,
    ) -> RefreshTokenRecord:
        row = await self._fetch_one(
            f"""
            INSERT INTO refresh_tokens
                (id, user_id, family_id, token_hash, expires_at, user_agent, client_ip)
            VALUES (%(id)s, %(uid)s, %(fid)s, %(hash)s, %(exp)s, %(ua)s, %(ip)s)
            RETURNING {_REFRESH_COLUMNS}
            """,
            {
                "id": token_id,
                "uid": user_id,
                "fid": family_id,
                "hash": token_hash,
                "exp": as_utc(expires_at),
                "ua": user_agent,
                "ip": client_ip,
            },
        )
        assert row is not None
        return _to_refresh(row)

    async def find_by_hash(self, token_hash: bytes) -> RefreshTokenRecord | None:
        row = await self._fetch_one(
            f"SELECT {_REFRESH_COLUMNS} FROM refresh_tokens WHERE token_hash = %(h)s",
            {"h": token_hash},
        )
        return _to_refresh(row) if row else None

    async def consume(self, *, token_id: str, replaced_by_id: str, now: datetime) -> bool:
        """Rotate a token, once.

        The ``consumed_at IS NULL`` predicate is the race winner: exactly one of
        N concurrent refreshes updates a row, and every loser gets False. That
        False is precisely the reuse signal — a second presentation of a token
        the honest client has already traded in.
        """
        affected = await self._execute(
            """
            UPDATE refresh_tokens
            SET consumed_at = %(now)s, replaced_by_id = %(new)s
            WHERE id = %(id)s AND consumed_at IS NULL AND revoked_at IS NULL
            """,
            {"now": as_utc(now), "new": replaced_by_id, "id": token_id},
        )
        return affected == 1

    async def revoke_family(self, family_id: str, *, reason: str, now: datetime) -> int:
        return await self._execute(
            """
            UPDATE refresh_tokens
            SET revoked_at = %(now)s, revoked_reason = %(reason)s
            WHERE family_id = %(fid)s AND revoked_at IS NULL
            """,
            {"now": as_utc(now), "reason": reason, "fid": family_id},
        )

    async def revoke_all_for_user(self, user_id: str, *, reason: str, now: datetime) -> int:
        return await self._execute(
            """
            UPDATE refresh_tokens
            SET revoked_at = %(now)s, revoked_reason = %(reason)s
            WHERE user_id = %(uid)s AND revoked_at IS NULL
            """,
            {"now": as_utc(now), "reason": reason, "uid": user_id},
        )

    async def delete_expired(self, before: datetime) -> int:
        return await self._execute(
            "DELETE FROM refresh_tokens WHERE expires_at < %(before)s",
            {"before": as_utc(before)},
        )


def _to_actor(row: DictRow) -> AnonymousActor:
    return AnonymousActor(
        id=str(row["id"]),
        created_at=row["created_at"],
        last_seen_at=row["last_seen_at"],
        merged_into_user_id=(
            str(row["merged_into_user_id"]) if row["merged_into_user_id"] else None
        ),
        merged_at=row["merged_at"],
    )


_ACTOR_COLUMNS = "id, created_at, last_seen_at, merged_into_user_id, merged_at"


class SqlAnonymousActorRepository(SqlRepository):
    async def create(
        self, *, actor_id: str, user_agent: str | None, client_ip: str | None
    ) -> AnonymousActor:
        row = await self._fetch_one(
            f"""
            INSERT INTO anonymous_actors (id, first_user_agent, first_client_ip)
            VALUES (%(id)s, %(ua)s, %(ip)s)
            RETURNING {_ACTOR_COLUMNS}
            """,
            {"id": actor_id, "ua": user_agent, "ip": client_ip},
        )
        assert row is not None
        return _to_actor(row)

    async def get(self, actor_id: str) -> AnonymousActor | None:
        row = await self._fetch_one(
            f"SELECT {_ACTOR_COLUMNS} FROM anonymous_actors WHERE id = %(id)s",
            {"id": actor_id},
        )
        return _to_actor(row) if row else None

    async def touch(self, actor_id: str, at: datetime) -> None:
        await self._execute(
            "UPDATE anonymous_actors SET last_seen_at = %(at)s WHERE id = %(id)s",
            {"at": as_utc(at), "id": actor_id},
        )

    async def mark_merged(self, *, actor_id: str, user_id: str, at: datetime) -> None:
        # First merge wins: an actor token replayed after sign-in must not
        # re-point an established history at a different account.
        await self._execute(
            """
            UPDATE anonymous_actors
            SET merged_into_user_id = %(uid)s, merged_at = %(at)s
            WHERE id = %(id)s AND merged_into_user_id IS NULL
            """,
            {"uid": user_id, "at": as_utc(at), "id": actor_id},
        )


__all__ = [
    "SqlAdminLoginAttemptRepository",
    "SqlAnonymousActorRepository",
    "SqlOAuthIdentityRepository",
    "SqlOtpChallengeRepository",
    "SqlRefreshTokenRepository",
    "SqlUserRepository",
]
