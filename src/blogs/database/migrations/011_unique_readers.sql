-- 011 — public views are unique readers, while repeat reads stay in the log.
--
-- A browser may retry a beacon and a person may deliberately revisit an
-- article. Both are useful engagement facts, but neither should manufacture a
-- second person in the public counter. This claim table is the concurrency
-- boundary: its primary key decides whether a logical reader was counted.

CREATE TABLE blog_unique_readers (
    blog_id                     uuid        NOT NULL REFERENCES blogs (id)
                                            ON DELETE CASCADE,
    reader_kind                 text        NOT NULL
                                            CHECK (reader_kind IN ('actor', 'user')),
    reader_id                   uuid        NOT NULL,
    first_viewed_at             timestamptz NOT NULL,
    authenticated_at_first_read boolean     NOT NULL,

    PRIMARY KEY (blog_id, reader_kind, reader_id)
);

CREATE INDEX blog_unique_readers_by_identity
    ON blog_unique_readers (reader_kind, reader_id, blog_id);

-- Known users are canonical even when their first read happened anonymously:
-- the sign-in merge has already backfilled user_id on those events. This also
-- collapses the same account across devices. A truly anonymous reader can only
-- be identified by the signed actor id.
INSERT INTO blog_unique_readers
    (blog_id, reader_kind, reader_id, first_viewed_at,
     authenticated_at_first_read)
SELECT readers.blog_id,
       readers.reader_kind,
       readers.reader_id,
       readers.occurred_at,
       readers.authenticated_at_event
FROM (
    (
        SELECT DISTINCT ON (e.blog_id, e.user_id)
               e.blog_id,
               'user'::text AS reader_kind,
               e.user_id AS reader_id,
               e.occurred_at,
               e.authenticated_at_event
        FROM engagement_events e
        WHERE e.kind = 'read'
          AND e.blog_id IS NOT NULL
          AND e.user_id IS NOT NULL
        ORDER BY e.blog_id, e.user_id, e.occurred_at, e.id
    )
    UNION ALL
    (
        SELECT DISTINCT ON (e.blog_id, e.actor_id)
               e.blog_id,
               'actor'::text AS reader_kind,
               e.actor_id AS reader_id,
               e.occurred_at,
               e.authenticated_at_event
        FROM engagement_events e
        WHERE e.kind = 'read'
          AND e.blog_id IS NOT NULL
          AND e.user_id IS NULL
        ORDER BY e.blog_id, e.actor_id, e.occurred_at, e.id
    )
) readers
-- The append-only engagement log deliberately survives blog deletion and has
-- no foreign key to blogs. Claims are live per-blog state, so historical reads
-- for deleted blogs must not be copied into this FK-backed projection.
JOIN blogs b ON b.id = readers.blog_id;

ALTER TABLE blog_engagement_stats
    ADD COLUMN unique_reader_count bigint NOT NULL DEFAULT 0
        CHECK (unique_reader_count >= 0);

-- Migration 010 counted read sessions. Rebuild all three counters from the
-- claims so already-inflated production values are corrected on deployment.
UPDATE blog_engagement_stats
SET member_view_count = 0,
    guest_view_count = 0,
    unique_reader_count = 0,
    updated_at = now();

UPDATE blog_engagement_stats stats
SET member_view_count = counts.member_readers,
    guest_view_count = counts.guest_readers,
    unique_reader_count = counts.unique_readers,
    updated_at = now()
FROM (
    SELECT blog_id,
           count(*) FILTER (
               WHERE authenticated_at_first_read
           ) AS member_readers,
           count(*) FILTER (
               WHERE NOT authenticated_at_first_read
           ) AS guest_readers,
           count(*) AS unique_readers
    FROM blog_unique_readers
    GROUP BY blog_id
) counts
WHERE stats.blog_id = counts.blog_id;
