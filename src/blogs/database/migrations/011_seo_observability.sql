-- 011 — SEO audit history, Search Console snapshots, and AI visibility.
--
-- Editorial source stays in Markdown and operational analytics stay in the
-- engagement log. These tables record external discoverability observations
-- and the decisions made from them; they do not alter ranking or publishing.

CREATE TABLE seo_sites (
    id                       uuid        PRIMARY KEY,
    base_url                 text        NOT NULL UNIQUE,
    brand_name               text        NOT NULL CHECK (length(btrim(brand_name)) > 0),
    search_console_property  text,
    timezone                 text        NOT NULL DEFAULT 'UTC'
                                         CHECK (length(btrim(timezone)) > 0),
    active                   boolean     NOT NULL DEFAULT true,
    created_at               timestamptz NOT NULL DEFAULT now(),
    updated_at               timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT seo_sites_base_url_http CHECK (
        base_url ~ '^https?://[^[:space:]/<>{}]+(:[0-9]+)?$'
    )
);

CREATE TRIGGER seo_sites_set_updated_at
    BEFORE UPDATE ON seo_sites
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


CREATE TABLE seo_pages (
    id                uuid        PRIMARY KEY,
    site_id           uuid        NOT NULL REFERENCES seo_sites (id) ON DELETE CASCADE,
    -- Passed by value rather than constrained: SEO history must survive an
    -- article archive, and this table also represents non-blog pages.
    blog_id           uuid,
    url               text        NOT NULL,
    canonical_url     text,
    page_type         text        NOT NULL DEFAULT 'other'
                                  CHECK (page_type IN (
                                      'home', 'article', 'series', 'category', 'other'
                                  )),
    indexable         boolean     NOT NULL DEFAULT true,
    content_sha256    bytea       CHECK (
                                  content_sha256 IS NULL OR octet_length(content_sha256) = 32
                              ),
    last_audited_at   timestamptz,
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),

    UNIQUE (site_id, url),
    CONSTRAINT seo_pages_url_http CHECK (
        url ~ '^https?://[^[:space:]<>{}]+$'
    ),
    CONSTRAINT seo_pages_canonical_http CHECK (
        canonical_url IS NULL OR canonical_url ~ '^https?://[^[:space:]<>{}]+$'
    )
);

CREATE UNIQUE INDEX seo_pages_blog
    ON seo_pages (site_id, blog_id)
    WHERE blog_id IS NOT NULL;

CREATE INDEX seo_pages_indexability
    ON seo_pages (site_id, indexable, page_type, updated_at DESC);

CREATE TRIGGER seo_pages_set_updated_at
    BEFORE UPDATE ON seo_pages
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


CREATE TABLE seo_audit_runs (
    id             uuid        PRIMARY KEY,
    site_id        uuid        NOT NULL REFERENCES seo_sites (id) ON DELETE CASCADE,
    kind           text        NOT NULL CHECK (kind IN (
                               'local', 'live', 'search_console', 'ai_visibility', 'full'
                           )),
    trigger        text        NOT NULL CHECK (trigger IN (
                               'manual', 'plugin', 'scheduled', 'ci'
                           )),
    status         text        NOT NULL DEFAULT 'running'
                               CHECK (status IN ('running', 'completed', 'failed')),
    started_at     timestamptz NOT NULL,
    completed_at   timestamptz,
    report         jsonb       NOT NULL DEFAULT '{}'::jsonb,
    error          text,
    created_at     timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT seo_audit_runs_completion CHECK (
        (status = 'running' AND completed_at IS NULL)
        OR (status IN ('completed', 'failed') AND completed_at IS NOT NULL)
    ),
    CONSTRAINT seo_audit_runs_error CHECK (
        status = 'failed' OR error IS NULL
    )
);

CREATE INDEX seo_audit_runs_recent
    ON seo_audit_runs (site_id, started_at DESC);


CREATE TABLE seo_findings (
    id            uuid        PRIMARY KEY,
    run_id        uuid        NOT NULL REFERENCES seo_audit_runs (id) ON DELETE CASCADE,
    page_id       uuid        REFERENCES seo_pages (id) ON DELETE SET NULL,
    rule_code     text        NOT NULL CHECK (rule_code ~ '^[A-Z][A-Z0-9_]{2,63}$'),
    severity      text        NOT NULL CHECK (severity IN ('error', 'warning', 'info')),
    message       text        NOT NULL CHECK (length(btrim(message)) > 0),
    evidence      jsonb       NOT NULL DEFAULT '{}'::jsonb,
    fingerprint   text        NOT NULL CHECK (fingerprint ~ '^[a-f0-9]{64}$'),
    status        text        NOT NULL DEFAULT 'open'
                              CHECK (status IN ('open', 'accepted', 'resolved', 'dismissed')),
    created_at    timestamptz NOT NULL DEFAULT now(),
    resolved_at   timestamptz,

    UNIQUE (run_id, fingerprint),
    CONSTRAINT seo_findings_resolution CHECK (
        (status = 'resolved' AND resolved_at IS NOT NULL)
        OR (status <> 'resolved' AND resolved_at IS NULL)
    )
);

CREATE INDEX seo_findings_open
    ON seo_findings (severity, created_at DESC)
    WHERE status = 'open';

CREATE INDEX seo_findings_page_history
    ON seo_findings (page_id, created_at DESC)
    WHERE page_id IS NOT NULL;


CREATE TABLE seo_search_metrics_daily (
    id            uuid        PRIMARY KEY,
    site_id       uuid        NOT NULL REFERENCES seo_sites (id) ON DELETE CASCADE,
    page_id       uuid        REFERENCES seo_pages (id) ON DELETE SET NULL,
    metric_date   date        NOT NULL,
    query         text,
    search_type   text        NOT NULL DEFAULT 'web'
                              CHECK (search_type IN (
                                  'web', 'image', 'video', 'news', 'discover', 'googleNews'
                              )),
    appearance    text,
    country       text,
    device        text        CHECK (
                              device IS NULL OR device IN ('desktop', 'mobile', 'tablet')
                          ),
    clicks        double precision NOT NULL DEFAULT 0 CHECK (clicks >= 0),
    impressions   double precision NOT NULL DEFAULT 0 CHECK (impressions >= 0),
    ctr           double precision NOT NULL DEFAULT 0 CHECK (ctr BETWEEN 0 AND 1),
    position      double precision CHECK (position IS NULL OR position >= 0),
    source        text        NOT NULL DEFAULT 'search_console'
                              CHECK (source IN (
                                  'search_console', 'search_console_ai', 'manual_import'
                              )),
    is_partial    boolean     NOT NULL DEFAULT false,
    imported_at   timestamptz NOT NULL DEFAULT now(),

    UNIQUE NULLS NOT DISTINCT (
        site_id, page_id, metric_date, query, search_type,
        appearance, country, device, source
    )
);

CREATE INDEX seo_search_metrics_page_date
    ON seo_search_metrics_daily (page_id, metric_date DESC)
    WHERE page_id IS NOT NULL;

CREATE INDEX seo_search_metrics_site_date
    ON seo_search_metrics_daily (site_id, metric_date DESC);


CREATE TABLE seo_ai_queries (
    id          uuid        PRIMARY KEY,
    site_id     uuid        NOT NULL REFERENCES seo_sites (id) ON DELETE CASCADE,
    prompt      text        NOT NULL CHECK (length(btrim(prompt)) > 0),
    intent      text        CHECK (intent IS NULL OR intent IN (
                                'informational', 'navigational', 'commercial', 'transactional'
                            )),
    locale      text        NOT NULL DEFAULT 'en-IN',
    active      boolean     NOT NULL DEFAULT true,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now(),

    UNIQUE (site_id, prompt, locale)
);

CREATE TRIGGER seo_ai_queries_set_updated_at
    BEFORE UPDATE ON seo_ai_queries
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


CREATE TABLE seo_ai_observations (
    id              uuid        PRIMARY KEY,
    query_id        uuid        NOT NULL REFERENCES seo_ai_queries (id) ON DELETE CASCADE,
    page_id         uuid        REFERENCES seo_pages (id) ON DELETE SET NULL,
    engine          text        NOT NULL CHECK (engine IN (
                                 'google_ai_overview', 'google_ai_mode',
                                 'chatgpt_search', 'perplexity', 'other'
                             )),
    observed_at     timestamptz NOT NULL,
    brand_mentioned boolean     NOT NULL DEFAULT false,
    page_cited      boolean     NOT NULL DEFAULT false,
    citation_url    text,
    evidence        jsonb       NOT NULL DEFAULT '{}'::jsonb,
    created_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT seo_ai_observations_citation CHECK (
        (page_cited AND citation_url IS NOT NULL)
        OR (NOT page_cited AND citation_url IS NULL)
    ),
    CONSTRAINT seo_ai_observations_citation_http CHECK (
        citation_url IS NULL OR citation_url ~ '^https?://[^[:space:]<>{}]+$'
    )
);

CREATE INDEX seo_ai_observations_history
    ON seo_ai_observations (query_id, engine, observed_at DESC);


CREATE TABLE seo_changes (
    id             uuid        PRIMARY KEY,
    finding_id     uuid        REFERENCES seo_findings (id) ON DELETE SET NULL,
    page_id        uuid        REFERENCES seo_pages (id) ON DELETE SET NULL,
    summary        text        NOT NULL CHECK (length(btrim(summary)) > 0),
    status         text        NOT NULL DEFAULT 'proposed'
                               CHECK (status IN (
                                   'proposed', 'approved', 'applied', 'rejected', 'reverted'
                               )),
    before_sha256  bytea       CHECK (
                               before_sha256 IS NULL OR octet_length(before_sha256) = 32
                           ),
    after_sha256   bytea       CHECK (
                               after_sha256 IS NULL OR octet_length(after_sha256) = 32
                           ),
    proposed_at    timestamptz NOT NULL DEFAULT now(),
    approved_at    timestamptz,
    applied_at     timestamptz,
    notes          text,

    CONSTRAINT seo_changes_approval CHECK (
        status IN ('proposed', 'rejected') OR approved_at IS NOT NULL
    ),
    CONSTRAINT seo_changes_application CHECK (
        status NOT IN ('applied', 'reverted') OR applied_at IS NOT NULL
    )
);

CREATE INDEX seo_changes_page_history
    ON seo_changes (page_id, proposed_at DESC)
    WHERE page_id IS NOT NULL;
