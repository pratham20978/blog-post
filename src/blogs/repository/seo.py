"""PostgreSQL adapter for SEO audit observations."""

from __future__ import annotations

from datetime import datetime

from psycopg.types.json import Jsonb
from pydantic import JsonValue

from blogs.contracts.seo import SeoOverview
from blogs.repository.base import SqlRepository, as_utc


class SqlSeoRepository(SqlRepository):
    async def upsert_site(
        self,
        *,
        site_id: str,
        base_url: str,
        brand_name: str,
        search_console_property: str | None,
        timezone: str,
    ) -> str:
        row = await self._fetch_one(
            """
            INSERT INTO seo_sites
                (id, base_url, brand_name, search_console_property, timezone)
            VALUES
                (%(id)s, %(base_url)s, %(brand_name)s, %(property)s, %(timezone)s)
            ON CONFLICT (base_url) DO UPDATE
            SET brand_name = EXCLUDED.brand_name,
                search_console_property = EXCLUDED.search_console_property,
                timezone = EXCLUDED.timezone,
                active = true
            RETURNING id
            """,
            {
                "id": site_id,
                "base_url": base_url,
                "brand_name": brand_name,
                "property": search_console_property,
                "timezone": timezone,
            },
        )
        assert row is not None
        return str(row["id"])

    async def create_run(
        self,
        *,
        run_id: str,
        site_id: str,
        kind: str,
        trigger: str,
        started_at: datetime,
    ) -> None:
        await self._execute(
            """
            INSERT INTO seo_audit_runs (id, site_id, kind, trigger, started_at)
            VALUES (%(id)s, %(site)s, %(kind)s, %(trigger)s, %(started)s)
            """,
            {
                "id": run_id,
                "site": site_id,
                "kind": kind,
                "trigger": trigger,
                "started": as_utc(started_at),
            },
        )

    async def upsert_page(
        self,
        *,
        page_id: str,
        site_id: str,
        url: str,
        canonical_url: str | None,
        blog_id: str | None,
        page_type: str,
        indexable: bool,
        content_sha256: str | None,
        audited_at: datetime,
    ) -> str:
        row = await self._fetch_one(
            """
            INSERT INTO seo_pages
                (id, site_id, blog_id, url, canonical_url, page_type,
                 indexable, content_sha256, last_audited_at)
            VALUES
                (%(id)s, %(site)s, %(blog)s, %(url)s, %(canonical)s, %(type)s,
                 %(indexable)s, %(digest)s, %(audited)s)
            ON CONFLICT (site_id, url) DO UPDATE
            SET blog_id = COALESCE(EXCLUDED.blog_id, seo_pages.blog_id),
                canonical_url = EXCLUDED.canonical_url,
                page_type = EXCLUDED.page_type,
                indexable = EXCLUDED.indexable,
                content_sha256 = EXCLUDED.content_sha256,
                last_audited_at = EXCLUDED.last_audited_at
            RETURNING id
            """,
            {
                "id": page_id,
                "site": site_id,
                "blog": blog_id,
                "url": url,
                "canonical": canonical_url,
                "type": page_type,
                "indexable": indexable,
                "digest": bytes.fromhex(content_sha256) if content_sha256 else None,
                "audited": as_utc(audited_at),
            },
        )
        assert row is not None
        return str(row["id"])

    async def add_finding(
        self,
        *,
        finding_id: str,
        run_id: str,
        page_id: str | None,
        rule_code: str,
        severity: str,
        message: str,
        evidence: dict[str, JsonValue],
        fingerprint: str,
    ) -> bool:
        row = await self._fetch_one(
            """
            INSERT INTO seo_findings
                (id, run_id, page_id, rule_code, severity, message, evidence, fingerprint)
            VALUES
                (%(id)s, %(run)s, %(page)s, %(rule)s, %(severity)s,
                 %(message)s, %(evidence)s, %(fingerprint)s)
            ON CONFLICT (run_id, fingerprint) DO NOTHING
            RETURNING id
            """,
            {
                "id": finding_id,
                "run": run_id,
                "page": page_id,
                "rule": rule_code,
                "severity": severity,
                "message": message,
                "evidence": Jsonb(evidence),
                "fingerprint": fingerprint,
            },
        )
        return row is not None

    async def complete_run(
        self,
        *,
        run_id: str,
        completed_at: datetime,
        report: dict[str, JsonValue],
    ) -> None:
        await self._execute(
            """
            UPDATE seo_audit_runs
            SET status = 'completed', completed_at = %(completed)s,
                report = %(report)s, error = NULL
            WHERE id = %(id)s
            """,
            {
                "id": run_id,
                "completed": as_utc(completed_at),
                "report": Jsonb(report),
            },
        )

    async def overview(self, *, base_url: str) -> SeoOverview | None:
        row = await self._fetch_one(
            """
            WITH selected_site AS (
                SELECT id, base_url FROM seo_sites WHERE base_url = %(base_url)s
            ), latest AS (
                SELECT r.id, r.completed_at
                FROM seo_audit_runs r
                JOIN selected_site s ON s.id = r.site_id
                WHERE r.status = 'completed'
                ORDER BY r.completed_at DESC, r.id DESC
                LIMIT 1
            )
            SELECT s.id, s.base_url,
                   (SELECT completed_at FROM latest) AS last_run_at,
                   (SELECT count(*) FROM seo_audit_runs r
                    WHERE r.site_id = s.id AND r.status = 'completed') AS total_runs,
                   (SELECT count(*) FROM seo_findings f
                    WHERE f.run_id = (SELECT id FROM latest)
                      AND f.status = 'open' AND f.severity = 'error') AS open_errors,
                   (SELECT count(*) FROM seo_findings f
                    WHERE f.run_id = (SELECT id FROM latest)
                      AND f.status = 'open' AND f.severity = 'warning') AS open_warnings,
                   (SELECT count(*) FROM seo_pages p
                    WHERE p.site_id = s.id) AS tracked_pages
            FROM selected_site s
            """,
            {"base_url": base_url},
        )
        if row is None:
            return None
        return SeoOverview(
            site_id=str(row["id"]),
            site_url=row["base_url"],
            last_run_at=row["last_run_at"],
            total_runs=int(row["total_runs"]),
            open_errors=int(row["open_errors"]),
            open_warnings=int(row["open_warnings"]),
            tracked_pages=int(row["tracked_pages"]),
        )


__all__ = ["SqlSeoRepository"]
