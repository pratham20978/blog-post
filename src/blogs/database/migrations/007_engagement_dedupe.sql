-- 007 — make beacon deduplication actually work.
--
-- 004 tried to enforce it with UNIQUE (dedupe_key, occurred_at) on
-- engagement_events. That cannot work, and the reason is structural: PostgreSQL
-- requires every unique index on a partitioned table to contain the partition
-- key, so occurred_at had to be in it. But occurred_at is assigned by the
-- server at insert time, so a beacon retried thirty seconds later carries the
-- same dedupe_key with a *different* timestamp — the pair is unique, the row
-- goes in, and the duplicate this was meant to stop is recorded twice.
--
-- Verified against the running system: three beacons plus one deliberate replay
-- produced four rows and a view count of 4.
--
-- The fix is a small un-partitioned table whose primary key is the dedupe key
-- alone. `INSERT ... ON CONFLICT DO NOTHING` there is race-free — two
-- simultaneous retries contend on one primary key and exactly one wins — and it
-- is checked before the event is written.

CREATE TABLE engagement_dedupe (
    dedupe_key     text        PRIMARY KEY,
    first_seen_at  timestamptz NOT NULL DEFAULT now()
);

-- For the retention sweep. Keys only need to outlive the window in which a
-- client might still retry; they are not history, and the log is.
CREATE INDEX engagement_dedupe_age ON engagement_dedupe (first_seen_at);

-- Backfill so keys already in the log keep suppressing their own retries.
INSERT INTO engagement_dedupe (dedupe_key, first_seen_at)
SELECT dedupe_key, min(occurred_at) FROM engagement_events GROUP BY dedupe_key
ON CONFLICT DO NOTHING;

-- Dropped rather than left in place. It never prevented a duplicate, and an
-- index that looks like a uniqueness guarantee while providing none is worse
-- than no index: the next person to read the schema would trust it.
DROP INDEX IF EXISTS engagement_events_dedupe;
