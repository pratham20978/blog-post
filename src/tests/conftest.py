"""Test fixtures.

Integration tests run against a **real PostgreSQL**, in a database created and
dropped per run. Not a mock and not SQLite: most of the interesting behaviour in
this system lives in the schema — a partial unique index for one root comment
per user, a composite foreign key for single-level threads, a deferrable
constraint for the refresh chain — and none of it is exercised by a fake.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import psycopg
import pytest
import pytest_asyncio

from blogs.adapters.objectstore.memory_store import InMemoryObjectStore
from blogs.adapters.tokens.codecs import (
    JwtAccessTokenCodec,
    JwtActorTokenCodec,
    Sha256SecretHasher,
)
from blogs.adapters.tokens.passwords import ScryptPasswordHasher
from blogs.core.clock import FrozenClock
from blogs.core.ids import Uuid7Generator
from blogs.database.migrator import upgrade
from blogs.database.session import Database
from blogs.repository.uow import SqlUnitOfWorkFactory

ADMIN_DSN = os.environ.get(
    "BLOGS_TEST_ADMIN_DSN", "postgresql://lucifer:password123@127.0.0.1:5432/postgres"
)
TEST_DB = f"blogs_test_{os.getpid()}"


def _dsn_for(database: str) -> str:
    base, _, _ = ADMIN_DSN.rpartition("/")
    return f"{base}/{database}"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def database() -> AsyncIterator[Database]:
    """A disposable database with every migration applied.

    Created per test run rather than reused so a failed run cannot leave state
    that makes the next one pass — the failure mode that turns a suite into
    decoration.
    """
    async with await psycopg.AsyncConnection.connect(ADMIN_DSN, autocommit=True) as conn:
        await conn.execute(f'DROP DATABASE IF EXISTS "{TEST_DB}" WITH (FORCE)')
        await conn.execute(f'CREATE DATABASE "{TEST_DB}"')

    db = Database(_dsn_for(TEST_DB), min_size=1, max_size=5)
    await db.open()
    await upgrade(db)
    try:
        yield db
    finally:
        await db.close()
        async with await psycopg.AsyncConnection.connect(
            ADMIN_DSN, autocommit=True
        ) as conn:
            await conn.execute(f'DROP DATABASE IF EXISTS "{TEST_DB}" WITH (FORCE)')


@pytest_asyncio.fixture
async def uow(database: Database) -> AsyncIterator[SqlUnitOfWorkFactory]:
    """A clean slate for each test.

    Truncating between tests rather than wrapping each in a rolled-back
    transaction: the code under test opens its own transactions, and several
    behaviours here (reuse detection committing in a second transaction,
    deferred constraint checks firing at COMMIT) only happen for real when the
    commits are real.
    """
    async with database.connection() as conn:
        await conn.execute(
            """
            TRUNCATE
                users, oauth_identities, otp_challenges, refresh_tokens,
                anonymous_actors, admin_login_attempts,
                series, categories, blogs, blog_categories, blog_sections,
                reference_pins, comments, markers, catalogs, catalog_items,
                engagement_events, engagement_dedupe, recent_views,
                outbox_events, consumed_events
            RESTART IDENTITY CASCADE
            """
        )
    yield SqlUnitOfWorkFactory(database)


@pytest.fixture
def clock() -> FrozenClock:
    """Time only moves when a test moves it."""
    return FrozenClock(datetime(2026, 8, 22, 12, 0, 0, tzinfo=UTC))


@pytest.fixture
def ids() -> Uuid7Generator:
    return Uuid7Generator()


@pytest.fixture
def object_store() -> InMemoryObjectStore:
    return InMemoryObjectStore()


@pytest.fixture
def hasher() -> Sha256SecretHasher:
    return Sha256SecretHasher(otp_pepper="test-pepper")


@pytest.fixture
def passwords() -> ScryptPasswordHasher:
    return ScryptPasswordHasher()


@pytest.fixture
def access_tokens() -> JwtAccessTokenCodec:
    return JwtAccessTokenCodec(
        secret="test-secret-value-at-least-32-bytes-long",
        issuer="blogs-test",
        ttl_seconds=900,
    )


@pytest.fixture
def actor_tokens() -> JwtActorTokenCodec:
    return JwtActorTokenCodec(
        secret="test-actor-secret-at-least-32-bytes-long",
        issuer="blogs-test",
        ttl_seconds=86400,
    )
