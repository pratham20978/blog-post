"""Assembly. The only module that knows every concrete class.

This is where hexagonal architecture pays out: everything above depends on a
port, and the choice of adapter is made once, here. Swapping MinIO for S3 or the
Postgres outbox for a broker is an edit to this file and nothing else.

Wiring is explicit — no container library, no decorator scanning, no import-time
registration. The graph is a hundred lines of constructor calls that can be read
top to bottom, and a test builds its own with fakes by calling the same
functions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from blogs.adapters.email import ResendEmailSender, UnconfiguredEmailSender
from blogs.adapters.markdown.parser import MarkdownItParser
from blogs.adapters.oauth.providers import build_provider_registry
from blogs.adapters.objectstore.minio_store import MinioObjectStore
from blogs.adapters.tokens.codecs import (
    JwtAccessTokenCodec,
    JwtActorTokenCodec,
    Sha256SecretHasher,
)
from blogs.adapters.tokens.passwords import ScryptPasswordHasher
from blogs.core.clock import Clock, SystemClock
from blogs.core.ids import IdGenerator, Uuid7Generator
from blogs.core.logging import configure_logging
from blogs.core.settings import Settings
from blogs.database.session import Database
from blogs.ports.services import EmailSender, ObjectStore
from blogs.repository.uow import SqlUnitOfWorkFactory
from blogs.services.actor_service import ActorService
from blogs.services.admin_read_service import AdminReadService
from blogs.services.announce_service import AnnounceService
from blogs.services.auth_service import AuthService, OtpSettings
from blogs.services.blog_service import BlogService
from blogs.services.engagement_service import EngagementService
from blogs.services.interaction_service import InteractionService
from blogs.services.oauth_flow_service import OAuthFlowService
from blogs.services.policy import DefaultAuthorizationPolicy

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Container:
    """The assembled application.

    Frozen: assembly happens once, at startup. A container that could be mutated
    at request time would make the behaviour of the system depend on which
    request got there first.
    """

    settings: Settings

    # Infrastructure lifecycles
    database: Database
    object_store: ObjectStore
    email: EmailSender

    # Seams
    clock: Clock
    ids: IdGenerator
    uow: SqlUnitOfWorkFactory

    # Application services
    actor_service: ActorService
    auth_service: AuthService
    auth_service_oauth: OAuthFlowService
    blog_service: BlogService
    interaction_service: InteractionService
    engagement_service: EngagementService
    admin_read_service: AdminReadService
    announce_service: AnnounceService


async def build_container(settings: Settings) -> Container:
    """Open every connection, verify the world, and wire it up."""
    configure_logging(level=logging.DEBUG if settings.debug else logging.INFO)

    database = Database(
        settings.database_url,
        min_size=settings.db_min_pool_size,
        max_size=settings.db_max_pool_size,
        connect_timeout_s=settings.db_connect_timeout_s,
        pool_timeout_s=settings.db_pool_timeout_s,
        statement_timeout_ms=settings.db_statement_timeout_ms,
        idle_in_transaction_timeout_ms=settings.db_idle_in_transaction_timeout_ms,
        max_lifetime_s=settings.db_max_lifetime_s,
        max_idle_s=settings.db_max_idle_s,
    )
    await database.open()
    await _ensure_partitions(database, settings.engagement_partition_months_ahead)

    object_store: ObjectStore = MinioObjectStore(
        endpoint=settings.object_store_endpoint,
        access_key=settings.object_store_access_key.get_secret_value(),
        secret_key=settings.object_store_secret_key.get_secret_value(),
        bucket=settings.object_store_bucket,
        secure=settings.object_store_secure,
        region=settings.object_store_region,
    )
    await object_store.ensure_bucket()

    email = _build_email_sender(settings)

    clock: Clock = SystemClock()
    ids: IdGenerator = Uuid7Generator()
    uow = SqlUnitOfWorkFactory(database)

    hasher = Sha256SecretHasher(otp_pepper=settings.otp_pepper.get_secret_value())
    access_tokens = JwtAccessTokenCodec(
        secret=settings.jwt_secret.get_secret_value(),
        issuer=settings.jwt_issuer,
        ttl_seconds=settings.access_token_ttl_s,
    )
    actor_tokens = JwtActorTokenCodec(
        secret=settings.actor_token_secret.get_secret_value(),
        issuer=settings.jwt_issuer,
        ttl_seconds=settings.actor_token_ttl_s,
    )
    passwords = ScryptPasswordHasher()
    policy = DefaultAuthorizationPolicy()
    markdown = MarkdownItParser(max_bytes=settings.max_markdown_bytes)

    providers = build_provider_registry(
        google_client_id=settings.google_client_id,
        google_client_secret=_secret_or_none(settings.google_client_secret),
        github_client_id=settings.github_client_id,
        github_client_secret=_secret_or_none(settings.github_client_secret),
    )

    container = Container(
        settings=settings,
        database=database,
        object_store=object_store,
        email=email,
        clock=clock,
        ids=ids,
        uow=uow,
        actor_service=ActorService(
            uow=uow,
            clock=clock,
            ids=ids,
            access_tokens=access_tokens,
            actor_tokens=actor_tokens,
        ),
        auth_service=AuthService(
            uow=uow,
            email=email,
            clock=clock,
            ids=ids,
            hasher=hasher,
            access_tokens=access_tokens,
            actor_tokens=actor_tokens,
            passwords=passwords,
            otp_settings=OtpSettings(
                length=settings.otp_length,
                ttl_seconds=settings.otp_ttl_s,
                max_attempts=settings.otp_max_attempts,
                resend_cooldown_seconds=settings.otp_resend_cooldown_s,
                log_codes=settings.otp_log_codes,
                dev_bypass_code=_secret_or_none(settings.otp_dev_bypass_code),
            ),
            refresh_ttl_seconds=settings.refresh_token_ttl_s,
            access_ttl_seconds=settings.access_token_ttl_s,
            admin_max_failed_logins=settings.admin_max_failed_logins,
            admin_lockout_window_s=settings.admin_lockout_window_s,
        ),
        auth_service_oauth=OAuthFlowService(
            providers=providers,
            clock=clock,
            state_secret=settings.jwt_secret.get_secret_value(),
            issuer=settings.jwt_issuer,
            redirect_base_url=settings.oauth_redirect_base_url,
        ),
        blog_service=BlogService(
            uow=uow,
            clock=clock,
            ids=ids,
            object_store=object_store,
            markdown=markdown,
            policy=policy,
            default_page_size=settings.default_page_size,
            max_page_size=settings.max_page_size,
        ),
        interaction_service=InteractionService(
            uow=uow,
            clock=clock,
            ids=ids,
            policy=policy,
            default_page_size=settings.default_page_size,
        ),
        engagement_service=EngagementService(
            uow=uow, clock=clock, ids=ids, policy=policy
        ),
        admin_read_service=AdminReadService(uow=uow, clock=clock, policy=policy),
        announce_service=AnnounceService(
            uow=uow,
            email=email,
            policy=policy,
            # Recipients need an absolute URL; a relative one is unusable
            # in an email client.
            site_url=settings.public_site_url,
            max_recipients=settings.announce_max_recipients,
        ),
    )

    await _seed_admin(container)

    logger.info(
        "application assembled",
        extra={
            "environment": settings.environment.value,
            "oauth_providers": list(providers.registered_keys()),
            "object_store_bucket": settings.object_store_bucket,
        },
    )
    return container


async def close_container(container: Container) -> None:
    """Release everything, in reverse order of acquisition."""
    closer = getattr(container.email, "aclose", None)
    if closer is not None:
        await closer()
    await container.database.close()
    logger.info("application shut down")


def _build_email_sender(settings: Settings) -> EmailSender:
    """Pick the adapter, or the one that refuses.

    ``UnconfiguredEmailSender`` is not a null object — it raises. A deployment
    with no provider should fail at the moment something tries to send, not
    accept the message and drop it, which would make sign-in report success
    while no code was ever delivered.
    """
    if settings.email_provider == "resend":
        # Both are guaranteed present by `_email_provider_is_complete`.
        assert settings.resend_api_key is not None
        assert settings.email_from is not None
        return ResendEmailSender(
            api_key=settings.resend_api_key.get_secret_value(),
            sender=settings.email_from,
            reply_to=settings.email_reply_to,
            timeout_s=settings.email_timeout_s,
        )

    logger.warning(
        "no email provider configured; sign-in codes and announcements cannot "
        "be delivered. Set BLOGS_EMAIL_PROVIDER=resend to enable them."
    )
    return UnconfiguredEmailSender()


def _secret_or_none(value: Any) -> str | None:
    return value.get_secret_value() if value is not None else None


async def _ensure_partitions(database: Database, months_ahead: int) -> None:
    """Create engagement partitions for the months ahead.

    Called on every start and idempotent, so a long-running deployment keeps
    itself ahead of the calendar without a separate scheduled job. Rows landing
    in the default partition mean this fell behind, which is why ``/readyz``
    reports it.
    """
    async with database.connection() as conn:
        cursor = await conn.execute(
            "SELECT ensure_engagement_partitions(%s) AS created", (months_ahead,)
        )
        row = await cursor.fetchone()
    if row and row["created"]:
        logger.info("engagement partitions created", extra={"created": row["created"]})


async def _seed_admin(container: Container) -> None:
    """Create the single admin if configured and absent.

    Idempotent by check, safe by constraint: the ``users_single_admin`` partial
    unique index is what actually guarantees there is only ever one, so a race
    between two starting replicas ends with one insert failing rather than with
    two admins.
    """
    email = container.settings.admin_email
    if not email:
        return

    async with container.uow.begin() as uow:
        if await uow.users.get_admin() is not None:
            return
        existing = await uow.users.get_by_email(email)
        if existing is not None:
            logger.warning(
                "admin_email names an existing non-admin account; not promoting it",
                extra={"user_id": existing.id},
            )
            return
        admin = await uow.users.create(
            user_id=container.ids.new_id(),
            email=email,
            display_name="Administrator",
            is_admin=True,
            email_verified_at=container.clock.now(),
        )
    logger.info("admin account seeded", extra={"user_id": admin.id})
    await _seed_admin_password(container, admin.id)


async def _seed_admin_password(container: Container, user_id: str) -> None:
    """Set the admin's console password from configuration, once.

    Only ever runs for a freshly seeded admin, so restarting the process cannot
    silently reset a password the admin has since changed. The configured value
    is hashed immediately and never read back — rotating it afterwards is a call
    to the console's password endpoint, not an environment edit.
    """
    configured = container.settings.admin_initial_password
    if configured is None:
        logger.warning(
            "admin seeded without a password; console sign-in is unavailable "
            "until BLOGS_ADMIN_INITIAL_PASSWORD is set and the admin re-seeded"
        )
        return
    await container.auth_service.set_admin_password(
        user_id=user_id, password=configured.get_secret_value()
    )
