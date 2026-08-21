from __future__ import annotations

import logging
from dataclasses import dataclass

from ai_auditor.adapters.mail.noop import NoOpMailer
from ai_auditor.adapters.mail.smtp import SmtpMailer
from ai_auditor.adapters.postgres.pool import PostgresPool
from ai_auditor.core.logging import configure_logging
from ai_auditor.core.settings import Settings
from ai_auditor.ports.obs import Mailer, Tracer
from ai_auditor.ports.storage import ObjectStore


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Container:
    settings: Settings
    
    # Infrastructure lifecycles
    postgres: PostgresPool
    object_store: ObjectStore
    tracer: Tracer
    mailer: Mailer


async def build_container(settings: Settings) -> Container:
    """Open every connection, verify the world, and wire it up."""
    configure_logging(level=logging.DEBUG if settings.debug else logging.INFO)

    postgres = PostgresPool(
        settings.database_url,
        min_size=settings.db_min_pool_size,
        max_size=settings.db_max_pool_size,
    )
    await postgres.open()
    await postgres.verify_extensions()

    object_store = MinioObjectStore(
        endpoint_url=settings.object_store_endpoint,
        bucket=settings.object_store_bucket,
        access_key=settings.object_store_access_key,
        secret_key=settings.object_store_secret_key,
    )
    await object_store.ensure_bucket()

    # NoOp when unconfigured — never None, so no call site carries an `if`.
    mailer: Mailer = (
        SmtpMailer(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            sender=settings.smtp_from,
        )
        if settings.mail_enabled
        else NoOpMailer()
    )
    tracer: Tracer = NoOpTracer()



    logger.info(
        "application assembled",
        extra={
            "environment": settings.environment,
            "mail": "smtp" if settings.mail_enabled else "noop",
            "tracing": "langfuse" if settings.tracing_enabled else "noop",
        },
    )

    return Container(
        settings=settings,
        postgres=postgres,
        object_store=object_store,
        tracer=tracer,
        mailer=mailer,
    )


async def close_container(container: Container) -> None:
    """Release everything, in reverse order of acquisition."""
    await container.redis_static_client.aclose()
    await container.redis_hot_client.aclose()
    await container.postgres.close()
    logger.info("application shut down")
