"""Sign-in, sign-out, and the merge that makes a new account not-cold.

Two things here are worth reading closely.

**Refresh rotation with family reuse-detection.** Every sign-in starts a token
family. Refreshing consumes the presented token and issues a successor in the
same family. If a token that was already consumed is presented again, the honest
client would have moved on — so the presentation is a leak, and the entire
family is revoked. This is the OWASP-recommended shape and it is why the
registry exists at all; the access-token path still never reads the database.

**Merge on login.** An anonymous visitor's engagement is claimed by the account
the moment they sign in. This is the cold-start head start: instead of a brand
new profile with nothing in it, F1 gets a real engagement history to personalise
from on the very first page the user sees.
"""

from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from blogs.contracts.common import ErrorCategory
from blogs.contracts.events import (
    AnonymousActorMerged,
    OtpRequested,
    UserRegistered,
)
from blogs.contracts.identity import (
    AuthPurpose,
    OAuthProfile,
    OtpIssued,
    TokenPair,
    User,
    UserStatus,
)
from blogs.core.clock import Clock
from blogs.core.errors import BlogPlatformError, raise_error
from blogs.core.ids import IdGenerator
from blogs.ports.services import (
    AccessTokenCodec,
    ActorTokenCodec,
    EmailMessage,
    EmailSender,
    PasswordHasher,
    SecretHasher,
)
from blogs.ports.uow import UnitOfWorkFactory

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class OtpSettings:
    length: int
    ttl_seconds: int
    max_attempts: int
    resend_cooldown_seconds: int
    log_codes: bool
    #: Development only, and refused in production by ``Settings``. See
    #: ``verify_otp`` for what accepting it actually skips.
    dev_bypass_code: str | None = None


@dataclass(frozen=True, slots=True)
class SignInResult:
    tokens: TokenPair
    user: User
    created: bool
    merged_events: int


class AuthService:
    def __init__(
        self,
        *,
        uow: UnitOfWorkFactory,
        email: EmailSender,
        clock: Clock,
        ids: IdGenerator,
        hasher: SecretHasher,
        access_tokens: AccessTokenCodec,
        actor_tokens: ActorTokenCodec,
        passwords: PasswordHasher,
        otp_settings: OtpSettings,
        refresh_ttl_seconds: int,
        access_ttl_seconds: int,
        admin_max_failed_logins: int = 5,
        admin_lockout_window_s: int = 900,
    ) -> None:
        self._uow = uow
        self._email = email
        self._clock = clock
        self._ids = ids
        self._hasher = hasher
        self._access = access_tokens
        self._actor = actor_tokens
        self._otp = otp_settings
        self._passwords = passwords
        self._refresh_ttl = timedelta(seconds=refresh_ttl_seconds)
        self._access_ttl_seconds = access_ttl_seconds
        self._admin_max_failed_logins = admin_max_failed_logins
        self._admin_lockout_window_s = admin_lockout_window_s

    # ── OTP ─────────────────────────────────────────────────────────────────

    async def request_otp(
        self,
        *,
        email: str,
        purpose: AuthPurpose,
        client_ip: str | None = None,
        correlation_id: str | None = None,
    ) -> OtpIssued:
        """Issue a one-time code and stage the email for F2.

        The code is generated, hashed and forgotten. What goes on the bus is a
        ``token_ref`` — an opaque handle — because foundation §7 forbids putting
        the credential itself on a queue other contexts read.
        """
        now = self._clock.now()

        async with self._uow.begin() as uow:
            existing = await uow.otp.latest_live(email, purpose)
            if existing is not None:
                cooldown_ends = existing.created_at + timedelta(
                    seconds=self._otp.resend_cooldown_seconds
                )
                if now < cooldown_ends:
                    raise_error(
                        ErrorCategory.OTP_THROTTLED,
                        correlation_id=correlation_id,
                        safe_details={"retry_after_s": int((cooldown_ends - now).total_seconds())},
                    )

            code = self._hasher.new_otp_code(self._otp.length)
            expires_at = now + timedelta(seconds=self._otp.ttl_seconds)
            challenge = await uow.otp.create(
                challenge_id=self._ids.new_id(),
                email=email,
                purpose=purpose,
                code_hash=self._hasher.hash_otp(code),
                expires_at=expires_at,
                max_attempts=self._otp.max_attempts,
                client_ip=client_ip,
            )
            existing_user = await uow.users.get_by_email(email)

            await uow.outbox.add(
                OtpRequested(
                    id=self._ids.new_id(),
                    occurred_at=now,
                    subject_user_id=existing_user.id if existing_user else None,
                    email=email,
                    purpose=purpose.value,  # type: ignore[arg-type]
                    token_ref=challenge.id,
                    expires_at=expires_at,
                    requested_at=now,
                ),
                aggregate_type="otp_challenge",
                aggregate_id=challenge.id,
            )

        # Delivery happens after the commit, deliberately. Holding a database
        # transaction open across an HTTP call to a mail provider would pin a
        # connection for the provider's latency and, on a timeout, roll back a
        # challenge whose email may already have gone out.
        await self._deliver_otp(
            email=email, code=code, correlation_id=correlation_id
        )

        return OtpIssued(
            token_ref=challenge.id,
            expires_at=expires_at,
            resend_after=now + timedelta(seconds=self._otp.resend_cooldown_seconds),
        )

    async def verify_otp(
        self,
        *,
        email: str,
        code: str,
        actor_id: str,
        user_agent: str | None = None,
        client_ip: str | None = None,
        correlation_id: str | None = None,
    ) -> SignInResult:
        now = self._clock.now()

        if self._is_dev_bypass(code):
            # Straight to the happy path: no challenge is looked up, none is
            # consumed, and the attempt counter is untouched. There may not be
            # a challenge at all — that is the point, since nothing can send
            # one until F2 lands.
            #
            # Everything downstream is the real flow, so the resulting session
            # is a genuine one: real tokens, real user row (created here if the
            # address is new), and the same actor merge a real code would do.
            logger.warning(
                "DEV ONLY - accepting the OTP bypass code for %s; no challenge was verified",
                email,
            )
            async with self._uow.begin() as uow:
                return await self._complete_otp_sign_in(
                    uow,
                    email=email,
                    actor_id=actor_id,
                    now=now,
                    user_agent=user_agent,
                    client_ip=client_ip,
                    correlation_id=correlation_id,
                )

        code_hash = self._hasher.hash_otp(code)

        async with self._uow.begin() as uow:
            challenge, outcome = await uow.otp.consume_if_matching(
                email=email, purpose=AuthPurpose.LOGIN, code_hash=code_hash, now=now
            )
            if outcome != "matched":
                # Leave the block WITHOUT raising, so the attempt counter that
                # `consume_if_matching` just incremented actually commits.
                #
                # Raising here instead would roll it back, and the limit would
                # never advance no matter how many codes were tried — unlimited
                # guesses against a six-digit space, with the rate limit that is
                # supposed to stop it silently doing nothing.
                failed_outcome = outcome
            else:
                assert challenge is not None
                return await self._complete_otp_sign_in(
                    uow,
                    email=email,
                    actor_id=actor_id,
                    now=now,
                    user_agent=user_agent,
                    client_ip=client_ip,
                    correlation_id=correlation_id,
                )

        # Mapped one-to-one rather than collapsed: the caller retypes on a
        # mismatch and requests a new code on the other two, and cannot tell
        # which without being told.
        raise_error(
            {
                "missing": ErrorCategory.OTP_INVALID,
                "mismatch": ErrorCategory.OTP_INVALID,
                "expired": ErrorCategory.OTP_EXPIRED,
                "exhausted": ErrorCategory.OTP_ATTEMPTS_EXCEEDED,
            }[failed_outcome],
            correlation_id=correlation_id,
        )

    async def _deliver_otp(
        self, *, email: str, code: str, correlation_id: str | None
    ) -> None:
        """Send the code, or explain why it could not be sent.

        The failure mode this exists to avoid: answering "a code is on its way"
        when nothing was sent. Someone then waits for an email that will never
        arrive, and the logs show a clean 200.
        """
        if self._otp.log_codes:
            # Development only; Settings refuses to start in production with
            # this on. The logging formatter redacts a key containing "otp", so
            # the value is placed in the message rather than in `extra`.
            logger.warning("DEV ONLY — OTP for %s is %s", email, code)

        minutes = max(1, round(self._otp.ttl_seconds / 60))

        try:
            result = await self._email.send(
                EmailMessage(
                    to=email,
                    subject=f"{code} is your sign-in code",
                    text=_OTP_TEXT.format(code=code, minutes=minutes),
                    html=_OTP_HTML.format(code=code, minutes=minutes),
                )
            )
        except BlogPlatformError as error:
            # No provider configured. In development the log line above *is*
            # the delivery channel, so the flow continues; anywhere else this
            # is a real misconfiguration and the caller must hear about it.
            unconfigured = error.category is ErrorCategory.EMAIL_NOT_CONFIGURED
            if unconfigured and self._otp.log_codes:
                return
            raise

        if not result.sent:
            logger.warning(
                "otp email refused by provider", extra={"detail": result.detail}
            )
            raise_error(
                ErrorCategory.EMAIL_SEND_FAILED, correlation_id=correlation_id
            )

    def _is_dev_bypass(self, code: str) -> bool:
        """Whether this is the configured development code.

        ``compare_digest`` rather than ``==``: the comparison is cheap either
        way, and a short-circuiting one on a value this guessable is the kind of
        detail that gets copied into a context where it does matter.
        """
        configured = self._otp.dev_bypass_code
        if not configured:
            return False
        return secrets.compare_digest(code, configured)

    async def _complete_otp_sign_in(  # type: ignore[no-untyped-def]
        self,
        uow,
        *,
        email: str,
        actor_id: str,
        now: datetime,
        user_agent: str | None,
        client_ip: str | None,
        correlation_id: str | None,
    ) -> SignInResult:
        """The happy path, once a code has been verified and burned."""
        user = await uow.users.get_by_email(email)
        created = user is None
        if user is None:
            user = await uow.users.create(
                user_id=self._ids.new_id(),
                email=email,
                display_name=None,
                is_admin=False,
                email_verified_at=now,
            )
            await uow.outbox.add(
                UserRegistered(
                    id=self._ids.new_id(),
                    occurred_at=now,
                    user_id=user.id,
                    email=user.email,
                    is_admin=user.is_admin,
                    registered_at=now,
                ),
                aggregate_type="user",
                aggregate_id=user.id,
            )
        else:
            # Possessing a code sent to that address proves control of it.
            await uow.users.mark_email_verified(user.id, now)

        self._assert_active(user, correlation_id=correlation_id)
        merged = await self._merge_actor(uow, actor_id=actor_id, user=user, now=now)
        tokens = await self._issue_pair(
            uow,
            user=user,
            actor_id=actor_id,
            now=now,
            user_agent=user_agent,
            client_ip=client_ip,
        )
        return SignInResult(
            tokens=tokens, user=user, created=created, merged_events=merged
        )

    # ── OAuth ───────────────────────────────────────────────────────────────

    async def complete_oauth(
        self,
        *,
        profile: OAuthProfile,
        actor_id: str,
        user_agent: str | None = None,
        client_ip: str | None = None,
        correlation_id: str | None = None,
    ) -> SignInResult:
        """Link or create an account from a verified provider profile.

        Resolution order — provider subject, then verified email, then create —
        and the middle step is the dangerous one. Linking by email is only safe
        because an unverified address is refused outright: otherwise anyone who
        could assert ``victim@example.com`` at any provider would be handed the
        existing account.
        """
        now = self._clock.now()

        async with self._uow.begin() as uow:
            user_id = await uow.oauth_identities.find_user_id(
                profile.provider, profile.subject
            )
            created = False
            user = await uow.users.get(user_id) if user_id else None

            if user is None:
                if not profile.email or not profile.email_verified:
                    raise_error(
                        ErrorCategory.OAUTH_EMAIL_UNVERIFIED, correlation_id=correlation_id
                    )
                user = await uow.users.get_by_email(profile.email)
                if user is None:
                    created = True
                    user = await uow.users.create(
                        user_id=self._ids.new_id(),
                        email=profile.email,
                        display_name=profile.display_name,
                        is_admin=False,
                        email_verified_at=now,
                    )
                    await uow.outbox.add(
                        UserRegistered(
                            id=self._ids.new_id(),
                            occurred_at=now,
                            user_id=user.id,
                            email=user.email,
                            is_admin=user.is_admin,
                            registered_at=now,
                        ),
                        aggregate_type="user",
                        aggregate_id=user.id,
                    )
                await uow.oauth_identities.link(
                    identity_id=self._ids.new_id(),
                    user_id=user.id,
                    provider=profile.provider,
                    provider_subject=profile.subject,
                    email_at_provider=profile.email,
                )

            self._assert_active(user, correlation_id=correlation_id)
            merged = await self._merge_actor(uow, actor_id=actor_id, user=user, now=now)
            tokens = await self._issue_pair(
                uow,
                user=user,
                actor_id=actor_id,
                now=now,
                user_agent=user_agent,
                client_ip=client_ip,
            )

        return SignInResult(tokens=tokens, user=user, created=created, merged_events=merged)

    # ── Admin console sign-in ───────────────────────────────────────────────

    async def admin_password_login(
        self,
        *,
        email: str,
        password: str,
        actor_id: str,
        user_agent: str | None = None,
        client_ip: str | None = None,
        correlation_id: str | None = None,
    ) -> SignInResult:
        """Sign the admin in with a password.

        Readers never reach this: it is mounted only under the secret console
        prefix, and the schema forbids a non-admin from holding a password at
        all. The admin gets this *in addition* to OTP because email possession
        is a single factor that a compromised mailbox defeats outright, and this
        account can publish, edit and delete everything on the platform.

        Three properties matter more than the happy path:

        * **One error for every failure.** Unknown address, no password set,
          wrong password — all report ``ADMIN_CREDENTIALS_INVALID``. Anything
          finer tells whoever found the console which half they got right.
        * **The hash is always computed.** Even for an address that does not
          exist, so a missing account and a wrong password take the same time
          and cannot be told apart by timing.
        * **Every attempt is logged before the answer is given**, so the lockout
          counts what actually happened rather than what the happy path
          remembered to record.
        """
        now = self._clock.now()
        window_start = now - timedelta(seconds=self._admin_lockout_window_s)

        # Both failure paths below leave the transaction WITHOUT raising, so the
        # attempt they recorded actually commits. Raising inside would roll the
        # record back and the lockout would never advance — the counter would
        # read zero however many passwords were tried.
        locked_out = False
        failed = False

        async with self._uow.begin() as uow:
            failures = await uow.admin_logins.recent_failures(
                email=email, since=window_start
            )
            if failures >= self._admin_max_failed_logins:
                await uow.admin_logins.record(
                    attempt_id=self._ids.new_id(),
                    email=email,
                    succeeded=False,
                    at=now,
                    client_ip=client_ip,
                    user_agent=user_agent,
                )
                locked_out = True
            else:
                user = await uow.users.get_by_email(email)
                # Only a real admin's stored hash is ever compared. For anything
                # else the verify still runs against None, which the hasher
                # answers with a full dummy derivation so the timing matches.
                stored = (
                    await uow.users.get_password_hash(user.id)
                    if user is not None and user.is_admin
                    else None
                )
                ok = self._passwords.verify(password, stored)

                await uow.admin_logins.record(
                    attempt_id=self._ids.new_id(),
                    email=email,
                    succeeded=ok,
                    at=now,
                    client_ip=client_ip,
                    user_agent=user_agent,
                )
                failed = not ok or user is None

            if locked_out or failed:
                pass
            else:
                return await self._complete_admin_login(
                    uow,
                    user=user,
                    actor_id=actor_id,
                    now=now,
                    user_agent=user_agent,
                    client_ip=client_ip,
                    correlation_id=correlation_id,
                )

        if locked_out:
            raise_error(
                ErrorCategory.ADMIN_LOCKED_OUT,
                correlation_id=correlation_id,
                safe_details={"retry_after_s": self._admin_lockout_window_s},
            )
        logger.warning(
            "admin sign-in refused",
            extra={"failures_in_window": failures + 1, "client_ip": client_ip},
        )
        raise_error(
            ErrorCategory.ADMIN_CREDENTIALS_INVALID, correlation_id=correlation_id
        )

    async def _complete_admin_login(  # type: ignore[no-untyped-def]
        self,
        uow,
        *,
        user: User,
        actor_id: str,
        now: datetime,
        user_agent: str | None,
        client_ip: str | None,
        correlation_id: str | None,
    ) -> SignInResult:
        """Issue tokens once the password has been verified."""
        self._assert_active(user, correlation_id=correlation_id)
        merged = await self._merge_actor(uow, actor_id=actor_id, user=user, now=now)
        tokens = await self._issue_pair(
            uow,
            user=user,
            actor_id=actor_id,
            now=now,
            user_agent=user_agent,
            client_ip=client_ip,
        )
        logger.info("admin signed in", extra={"user_id": user.id, "client_ip": client_ip})
        return SignInResult(
            tokens=tokens, user=user, created=False, merged_events=merged
        )

    async def set_admin_password(
        self, *, user_id: str, password: str, correlation_id: str | None = None
    ) -> None:
        """Set or rotate the admin's password, revoking every existing session.

        Revocation is the point of rotating: if the password is being changed
        because it leaked, leaving the tokens it minted alive would defeat the
        change entirely.
        """
        now = self._clock.now()
        async with self._uow.begin() as uow:
            user = await uow.users.get(user_id)
            if user is None or not user.is_admin:
                raise_error(ErrorCategory.ADMIN_REQUIRED, correlation_id=correlation_id)
            await uow.users.set_password(
                user_id=user_id, password_hash=self._passwords.hash(password), at=now
            )
            await uow.refresh_tokens.revoke_all_for_user(
                user_id, reason="password_changed", now=now
            )
        logger.info("admin password set", extra={"user_id": user_id})

    # ── Refresh and revoke ──────────────────────────────────────────────────

    async def refresh(
        self,
        *,
        refresh_token: str,
        user_agent: str | None = None,
        client_ip: str | None = None,
        correlation_id: str | None = None,
    ) -> TokenPair:
        now = self._clock.now()
        token_hash = self._hasher.hash_token(refresh_token)

        async with self._uow.begin() as uow:
            record = await uow.refresh_tokens.find_by_hash(token_hash)
            if record is None:
                raise_error(
                    ErrorCategory.REFRESH_TOKEN_INVALID, correlation_id=correlation_id
                )
            if record.revoked_at is not None:
                raise_error(
                    ErrorCategory.AUTH_TOKEN_REVOKED, correlation_id=correlation_id
                )
            if record.expires_at <= now:
                raise_error(
                    ErrorCategory.REFRESH_TOKEN_EXPIRED, correlation_id=correlation_id
                )

            successor_id = self._ids.new_id()
            if await uow.refresh_tokens.consume(
                token_id=record.id, replaced_by_id=successor_id, now=now
            ):
                user = await uow.users.get(record.user_id)
                if user is None:
                    raise_error(
                        ErrorCategory.USER_NOT_FOUND, correlation_id=correlation_id
                    )
                self._assert_active(user, correlation_id=correlation_id)

                actor_id = await self._actor_for_user(uow, user=user, now=now)
                return await self._issue_pair(
                    uow,
                    user=user,
                    actor_id=actor_id,
                    now=now,
                    user_agent=user_agent,
                    client_ip=client_ip,
                    token_id=successor_id,
                    family_id=record.family_id,
                )

            # The token was already spent. Either it leaked and the thief is
            # using it, or it leaked, the thief used it, and this is the real
            # user arriving second. Both readings mean the family is
            # compromised, so all of it dies and everyone signs in again.
            #
            # The revocation deliberately does NOT happen here. Raising inside
            # this block rolls the transaction back and takes the revocation
            # with it — the caller would be told the session was killed while
            # every token in the family stayed alive. So the block is left
            # normally, carrying only the family id out, and the revocation runs
            # in its own transaction below where it can actually commit.
            compromised_family = record.family_id

        async with self._uow.begin() as uow:
            revoked = await uow.refresh_tokens.revoke_family(
                compromised_family, reason="reuse_detected", now=now
            )
        logger.warning(
            "refresh token reuse detected; family revoked",
            extra={"family": compromised_family, "revoked_count": revoked},
        )
        raise_error(ErrorCategory.REFRESH_TOKEN_REUSED, correlation_id=correlation_id)

    async def revoke(
        self, *, refresh_token: str | None, user_id: str, all_devices: bool
    ) -> int:
        """Sign out. One device by default, everywhere on request."""
        now = self._clock.now()
        async with self._uow.begin() as uow:
            if all_devices or refresh_token is None:
                return await uow.refresh_tokens.revoke_all_for_user(
                    user_id, reason="user_revoked", now=now
                )
            record = await uow.refresh_tokens.find_by_hash(
                self._hasher.hash_token(refresh_token)
            )
            if record is None or record.user_id != user_id:
                # Not an error: signing out with a token that is already gone
                # has achieved what the caller wanted.
                return 0
            return await uow.refresh_tokens.revoke_family(
                record.family_id, reason="user_revoked", now=now
            )

    # ── Internals ───────────────────────────────────────────────────────────

    @staticmethod
    def _assert_active(user: User, *, correlation_id: str | None) -> None:
        if user.status is not UserStatus.ACTIVE:
            raise_error(ErrorCategory.USER_INACTIVE, correlation_id=correlation_id)

    async def _merge_actor(self, uow, *, actor_id: str, user: User, now: datetime) -> int:  # type: ignore[no-untyped-def]
        """Claim an anonymous actor's history for the account signing in.

        Best-effort by design. A failure here must not cost someone their login:
        the history is valuable, the sign-in is essential.
        """
        try:
            actor = await uow.actors.get(actor_id)
            if actor is None or actor.merged_into_user_id is not None:
                return 0

            merged = await uow.engagement.attribute_to_user(
                actor_id=actor_id, user_id=user.id
            )
            await uow.recent_views.attribute_to_user(actor_id=actor_id, user_id=user.id)
            await uow.actors.mark_merged(actor_id=actor_id, user_id=user.id, at=now)

            if merged:
                await uow.outbox.add(
                    AnonymousActorMerged(
                        id=self._ids.new_id(),
                        occurred_at=now,
                        actor_id=actor_id,
                        user_id=user.id,
                        events_merged=merged,
                        merged_at=now,
                    ),
                    aggregate_type="user",
                    aggregate_id=user.id,
                )
            return merged
        except BlogPlatformError:
            logger.warning("anonymous actor merge failed", exc_info=True)
            return 0

    async def _actor_for_user(self, uow, *, user: User, now: datetime) -> str:  # type: ignore[no-untyped-def]
        """Mint a fresh actor for a refresh that arrives without one."""
        actor_id = self._ids.new_id()
        await uow.actors.create(actor_id=actor_id, user_agent=None, client_ip=None)
        await uow.actors.mark_merged(actor_id=actor_id, user_id=user.id, at=now)
        return actor_id

    async def _issue_pair(  # type: ignore[no-untyped-def]
        self,
        uow,
        *,
        user: User,
        actor_id: str,
        now: datetime,
        user_agent: str | None,
        client_ip: str | None,
        token_id: str | None = None,
        family_id: str | None = None,
    ) -> TokenPair:
        access_token, _ = self._access.issue(
            user_id=user.id, actor_id=actor_id, is_admin=user.is_admin, now=now
        )
        secret = self._hasher.new_token_secret()
        resolved_id = token_id or self._ids.new_id()
        await uow.refresh_tokens.create(
            token_id=resolved_id,
            user_id=user.id,
            # A new sign-in starts a new family; a refresh stays in its own.
            family_id=family_id or resolved_id,
            token_hash=self._hasher.hash_token(secret),
            expires_at=now + self._refresh_ttl,
            user_agent=user_agent,
            client_ip=client_ip,
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=secret,
            expires_in=self._access_ttl_seconds,
            actor_token=self._actor.issue(actor_id, now=now),
        )


__all__ = ["AuthService", "OtpSettings", "SignInResult"]


_OTP_TEXT = """Your sign-in code is {code}

It expires in {minutes} minutes and can be used once.

If you did not ask to sign in, you can ignore this message \u2014 the code is
useless without access to this inbox, and nobody has been signed in.
"""

#: Inline styles only: every mail client strips <style> blocks, and about half
#: strip <head> entirely.
_OTP_HTML = """\
<div style="font-family:system-ui,-apple-system,sans-serif;font-size:15px;
            color:#0a0a0a;line-height:1.6">
  <p>Your sign-in code is</p>
  <p style="font-size:32px;font-weight:600;letter-spacing:0.15em;margin:24px 0">{code}</p>
  <p style="color:#6b6b6b">It expires in {minutes} minutes and can be used once.</p>
  <p style="color:#6b6b6b">If you did not ask to sign in, you can ignore this
  message &mdash; the code is useless without access to this inbox, and nobody
  has been signed in.</p>
</div>
"""
