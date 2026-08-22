-- 004 — the append-only engagement log, and the recent-views projection.
--
-- This is the single source doc 01 promises F1 (affinity), F2 (segmentation)
-- and F4 (KPIs). Everything about it is shaped by one fact: it is the highest
-- write volume table in the system and it only ever grows.

CREATE TABLE engagement_events (
    id            uuid        NOT NULL,
    occurred_at   timestamptz NOT NULL,

    -- Always present, logged in or not. This is what lets an anonymous reader
    -- generate engagement at all, and what makes merge-on-login a matter of
    -- filling in user_id rather than of reconstructing history.
    actor_id      uuid        NOT NULL,
    user_id       uuid,

    blog_id       uuid,
    kind          text        NOT NULL CHECK (kind IN (
                      'impression', 'click', 'dwell', 'complete',
                      'save', 'share', 'comment', 'search_impression')),
    position      integer     CHECK (position IS NULL OR position >= 0),
    query_id      uuid,
    dwell_ms      integer     CHECK (dwell_ms IS NULL OR dwell_ms >= 0),
    scroll_depth  real        CHECK (scroll_depth IS NULL
                                     OR scroll_depth BETWEEN 0 AND 1),
    source        text        CHECK (source IS NULL OR source IN (
                      'feed', 'search', 'series', 'catalog', 'direct')),
    client_ip     inet,

    -- Ingestion from a browser is at-least-once: a retried beacon must not
    -- become a second row. NOT NULL with an id-derived default because
    -- PostgreSQL forbids *partial* unique indexes on a partitioned table, so
    -- "unique when present" is not expressible — "always present" is.
    dedupe_key    text        NOT NULL,

    metadata      jsonb       NOT NULL DEFAULT '{}'::jsonb,

    -- The partition key must be part of every unique constraint, hence the
    -- composite primary key.
    PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

-- Deliberately no foreign keys.
--
-- Three reasons, all of them load-bearing. Foundation §9 passes cross-context
-- references by value rather than by FK. The log must survive a deleted blog or
-- account — history that disappears when its subject does is not an audit
-- trail. And an FK check on every insert into the busiest table in the system
-- is a cost paid forever for a guarantee this table does not need.

CREATE UNIQUE INDEX engagement_events_dedupe
    ON engagement_events (dedupe_key, occurred_at);

-- F1 reads a user's engaged set to compute affinity.
CREATE INDEX engagement_events_by_user
    ON engagement_events (user_id, occurred_at DESC)
    WHERE user_id IS NOT NULL;

-- Per-article KPIs and the trending window.
CREATE INDEX engagement_events_by_blog
    ON engagement_events (blog_id, occurred_at DESC)
    WHERE blog_id IS NOT NULL;

-- The anonymous path, and the merge that runs on sign-in.
CREATE INDEX engagement_events_by_actor
    ON engagement_events (actor_id, occurred_at DESC);

-- Append-only and time-ordered is the exact shape BRIN was built for: a few
-- kilobytes covering the whole table, versus a btree that grows with it. Serves
-- the wide window scans behind "engagement over time".
CREATE INDEX engagement_events_occurred_brin
    ON engagement_events USING BRIN (occurred_at) WITH (pages_per_range = 32);


-- Creates monthly partitions from the current month forward.
--
-- Idempotent, so bootstrap can call it on every start and a scheduled job can
-- call it again without coordination.
CREATE OR REPLACE FUNCTION ensure_engagement_partitions(months_ahead integer DEFAULT 3)
RETURNS integer
LANGUAGE plpgsql AS $$
DECLARE
    created    integer := 0;
    offset_m   integer;
    start_at   date;
    end_at     date;
    part_name  text;
BEGIN
    FOR offset_m IN 0..months_ahead LOOP
        start_at  := date_trunc('month', (now() AT TIME ZONE 'UTC'))::date
                     + (offset_m || ' months')::interval;
        end_at    := start_at + interval '1 month';
        part_name := format('engagement_events_%s', to_char(start_at, 'YYYY_MM'));

        IF to_regclass(format('public.%I', part_name)) IS NULL THEN
            EXECUTE format(
                'CREATE TABLE %I PARTITION OF engagement_events '
                'FOR VALUES FROM (%L) TO (%L)',
                part_name, start_at, end_at);
            created := created + 1;
        END IF;
    END LOOP;
    RETURN created;
END;
$$;

SELECT ensure_engagement_partitions(3);

-- A safety net so a clock-skewed or backdated insert never errors outright.
--
-- It is a net, not a plan: rows landing here block attaching a real partition
-- covering that range, so /readyz reports its row count and a non-zero value
-- means the partition job fell behind.
CREATE TABLE engagement_events_default PARTITION OF engagement_events DEFAULT;


-- Recent views, maintained beside the log rather than derived from it.
--
-- The derivation — DISTINCT ON (blog_id) over a partitioned, ever-growing log —
-- is correct but degrades without bound, and it runs on a page a reader looks
-- at constantly. This projection is upserted in the same transaction as the
-- engagement append, so it cannot drift from the log it summarises.
--
-- Keyed by actor, so an anonymous reader has recent views too.
CREATE TABLE recent_views (
    actor_id        uuid        NOT NULL,
    blog_id         uuid        NOT NULL REFERENCES blogs (id) ON DELETE CASCADE,
    user_id         uuid        REFERENCES users (id) ON DELETE SET NULL,
    first_viewed_at timestamptz NOT NULL DEFAULT now(),
    last_viewed_at  timestamptz NOT NULL DEFAULT now(),
    view_count      integer     NOT NULL DEFAULT 1 CHECK (view_count >= 1),

    PRIMARY KEY (actor_id, blog_id)
);

CREATE INDEX recent_views_by_actor ON recent_views (actor_id, last_viewed_at DESC);

CREATE INDEX recent_views_by_user
    ON recent_views (user_id, last_viewed_at DESC)
    WHERE user_id IS NOT NULL;
