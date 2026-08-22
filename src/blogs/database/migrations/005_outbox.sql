-- 005 — the transactional outbox.
--
-- Foundation §8 models the event bus as a port with a Postgres adapter, and
-- this is that adapter's storage. The point of the pattern: the event row is
-- written in the same transaction as the business change, so the event exists
-- if and only if the change committed. No dual write, no "the blog published
-- but nobody was told".

CREATE TABLE outbox_events (
    id              uuid        PRIMARY KEY,
    event_name      text        NOT NULL,
    event_version   smallint    NOT NULL DEFAULT 1,
    aggregate_type  text        NOT NULL,
    aggregate_id    uuid        NOT NULL,
    payload         jsonb       NOT NULL,
    -- When the thing happened, versus when we recorded it. They differ under
    -- retry and backdating, and consumers order by the former.
    occurred_at     timestamptz NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),

    status          text        NOT NULL DEFAULT 'pending'
                                CHECK (status IN ('pending', 'published', 'dead')),
    attempts        smallint    NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    next_attempt_at timestamptz NOT NULL DEFAULT now(),
    last_error      text,
    published_at    timestamptz
)
-- Rows are written once, then updated once or twice as they are claimed and
-- published. Leaving space on the page lets those updates stay HOT, so the
-- indexes below are not rewritten every time a row changes status.
WITH (fillfactor = 70,
      autovacuum_vacuum_scale_factor = 0.02,
      autovacuum_analyze_scale_factor = 0.02);

-- The claim query, and the only one that matters for throughput: the oldest
-- due pending rows. Partial, so the index holds the backlog rather than the
-- entire history — on a healthy system it stays nearly empty regardless of how
-- many events have been published.
CREATE INDEX outbox_events_claimable
    ON outbox_events (next_attempt_at, id)
    WHERE status = 'pending';

-- For the admin view of the dead-letter queue.
CREATE INDEX outbox_events_dead
    ON outbox_events (created_at DESC)
    WHERE status = 'dead';

-- Tracing what a given aggregate emitted.
CREATE INDEX outbox_events_aggregate
    ON outbox_events (aggregate_type, aggregate_id, occurred_at);


-- Notifies the worker that something is due, so the poll interval is a floor on
-- latency rather than the mechanism. The worker still polls as a fallback:
-- NOTIFY is not durable, and a listener that reconnects must not have missed
-- work permanently.
CREATE OR REPLACE FUNCTION notify_outbox() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    PERFORM pg_notify('outbox_events', '');
    RETURN NULL;
END;
$$;

-- Statement-level: one notification per INSERT statement rather than one per
-- row. A publish that writes five events should wake the worker once.
CREATE TRIGGER outbox_events_notify
    AFTER INSERT ON outbox_events
    FOR EACH STATEMENT EXECUTE FUNCTION notify_outbox();


-- Consumer-side idempotency, required of every consumer by foundation §7.
--
-- Delivery is at-least-once — exactly-once across a process boundary is not
-- achievable, and pretending otherwise is how duplicate emails get sent. A
-- consumer records what it has handled here and skips what it has seen.
--
-- F3 consumes nothing in v1. The table is created here because the contract is
-- shared, and F1, F2 and F4 all need it to exist.
CREATE TABLE consumed_events (
    consumer     text        NOT NULL,
    event_id     uuid        NOT NULL,
    consumed_at  timestamptz NOT NULL DEFAULT now(),

    PRIMARY KEY (consumer, event_id)
);
