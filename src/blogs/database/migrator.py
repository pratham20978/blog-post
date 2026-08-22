"""Apply ordered ``NNN_name.sql`` files, exactly once, in order.

No ORM and no migration framework: foundation §3 commits to raw SQL, and a
migration tool whose only job is tracking a version number does not earn a
SQLAlchemy dependency.

Three properties are worth the code:

* **Serialised.** A session-level advisory lock is taken for the whole run, so
  two processes starting at once (two API replicas, a deploy racing a worker)
  cannot apply the same file twice.
* **Immutable once applied.** Each file's checksum is recorded. Editing an
  applied migration changes the checksum and the next run refuses to start —
  the alternative is a schema that differs between environments with nothing to
  show for it.
* **One transaction per file.** A failing migration leaves nothing behind.

Usage::

    python -m blogs.database.migrator up
    python -m blogs.database.migrator status
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import logging
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from psycopg import AsyncConnection
from psycopg.rows import DictRow

from blogs.core.logging import configure_logging
from blogs.core.settings import Settings
from blogs.database.session import Database

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_FILENAME = re.compile(r"^(\d{3,})_([a-z0-9_]+)\.sql$")

#: An arbitrary but fixed key. Any process migrating this schema must use the
#: same one, which is why it is a constant here and not a parameter.
_ADVISORY_LOCK_KEY = 0x1B10_6570

_BOOTSTRAP = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version       integer      PRIMARY KEY,
    name          text         NOT NULL,
    checksum      text         NOT NULL,
    applied_at    timestamptz  NOT NULL DEFAULT now(),
    execution_ms  integer      NOT NULL
);
"""


class MigrationError(RuntimeError):
    """A migration could not be applied, or the recorded history is wrong."""


@dataclass(frozen=True, slots=True)
class Migration:
    version: int
    name: str
    path: Path
    sql: str

    @property
    def checksum(self) -> str:
        return hashlib.sha256(self.sql.encode("utf-8")).hexdigest()


def discover(directory: Path = MIGRATIONS_DIR) -> tuple[Migration, ...]:
    """Read the migration files, ordered by version.

    A gap in the numbering is fine; a duplicate is not, because the order two
    migrations sharing a version apply in would depend on the filesystem.
    """
    if not directory.is_dir():
        raise MigrationError(f"migrations directory not found: {directory}")

    found: dict[int, Migration] = {}
    for path in sorted(directory.iterdir()):
        if path.suffix != ".sql":
            continue
        match = _FILENAME.match(path.name)
        if match is None:
            raise MigrationError(
                f"migration filename must look like 001_name.sql, got: {path.name}"
            )
        version = int(match.group(1))
        if version in found:
            raise MigrationError(
                f"duplicate migration version {version}: "
                f"{found[version].path.name} and {path.name}"
            )
        found[version] = Migration(
            version=version,
            name=match.group(2),
            path=path,
            sql=path.read_text(encoding="utf-8"),
        )
    return tuple(found[v] for v in sorted(found))


async def _applied(conn: AsyncConnection[DictRow]) -> dict[int, dict[str, object]]:
    cursor = await conn.execute(
        "SELECT version, name, checksum, applied_at FROM schema_migrations ORDER BY version"
    )
    return {int(row["version"]): dict(row) for row in await cursor.fetchall()}


def _verify_history(
    migrations: tuple[Migration, ...], applied: dict[int, dict[str, object]]
) -> None:
    """Refuse to run if an already-applied file has since been edited."""
    by_version = {m.version: m for m in migrations}
    for version, record in applied.items():
        migration = by_version.get(version)
        if migration is None:
            raise MigrationError(
                f"migration {version} ({record['name']}) is recorded as applied but its "
                f"file is missing — the database is ahead of this checkout"
            )
        if migration.checksum != record["checksum"]:
            raise MigrationError(
                f"migration {version} ({migration.name}) was modified after it was applied. "
                f"Migrations are immutable: add a new one instead."
            )


async def upgrade(database: Database) -> tuple[Migration, ...]:
    """Apply everything not yet applied. Returns what it applied."""
    migrations = discover()

    async with database.connection() as conn:
        # Session-level, so it is held across the separate per-file
        # transactions below and released when this connection returns to
        # the pool.
        await conn.execute("SELECT pg_advisory_lock(%s)", (_ADVISORY_LOCK_KEY,))
        try:
            await conn.execute(_BOOTSTRAP)
            applied = await _applied(conn)
            _verify_history(migrations, applied)

            pending = [m for m in migrations if m.version not in applied]
            if not pending:
                logger.info("schema up to date", extra={"applied_count": len(applied)})
                return ()

            for migration in pending:
                started = time.monotonic()
                async with conn.transaction():
                    await conn.execute(migration.sql)  # type: ignore[arg-type]
                    elapsed_ms = int((time.monotonic() - started) * 1000)
                    await conn.execute(
                        "INSERT INTO schema_migrations "
                        "(version, name, checksum, execution_ms) "
                        "VALUES (%(version)s, %(name)s, %(checksum)s, %(ms)s)",
                        {
                            "version": migration.version,
                            "name": migration.name,
                            "checksum": migration.checksum,
                            "ms": elapsed_ms,
                        },
                    )
                logger.info(
                    "migration applied",
                    # Not "name": logging reserves it on LogRecord and raises
                    # rather than shadowing. Same for "module", "filename",
                    # "levelname", "args" — prefix anything that might collide.
                    extra={
                        "migration_version": migration.version,
                        "migration_name": migration.name,
                        "execution_ms": elapsed_ms,
                    },
                )
            return tuple(pending)
        finally:
            await conn.execute("SELECT pg_advisory_unlock(%s)", (_ADVISORY_LOCK_KEY,))


async def status(database: Database) -> list[str]:
    migrations = discover()
    async with database.connection() as conn:
        await conn.execute(_BOOTSTRAP)
        applied = await _applied(conn)

    lines = []
    for migration in migrations:
        record = applied.get(migration.version)
        if record is None:
            mark = "PENDING"
        elif record["checksum"] != migration.checksum:
            mark = "MODIFIED (!)"
        else:
            mark = f"applied {record['applied_at']}"
        lines.append(f"  {migration.version:>3}  {migration.name:<28} {mark}")
    return lines


async def _run(command: str) -> int:
    settings = Settings()
    configure_logging(level=logging.INFO)
    database = Database(
        settings.database_url,
        min_size=1,
        max_size=2,
        statement_timeout_ms=300_000,  # DDL on a populated table can be slow
        idle_in_transaction_timeout_ms=300_000,
    )
    await database.open()
    try:
        if command == "up":
            applied = await upgrade(database)
            print(f"applied {len(applied)} migration(s)")
            for migration in applied:
                print(f"  {migration.version:>3}  {migration.name}")
        else:
            print("migrations:")
            for line in await status(database):
                print(line)
    except MigrationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        await database.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="blogs.database.migrator")
    parser.add_argument("command", choices=("up", "status"))
    return asyncio.run(_run(parser.parse_args().command))


if __name__ == "__main__":
    raise SystemExit(main())
