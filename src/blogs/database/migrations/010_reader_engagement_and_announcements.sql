-- 010 — qualified article views, member likes, and durable blog announcements.
--
-- Historical clicks/dwell/completions are deliberately not rewritten as reads.
-- They did not share the qualification rule introduced with this migration, so
-- presenting them as comparable data would manufacture a misleading baseline.

-- Whether the caller was signed in when the event happened is immutable. The
-- existing anonymous-history merge may later fill user_id, but a guest view must
-- remain a guest view in public/member analytics.
ALTER TABLE engagement_events
    ADD COLUMN authenticated_at_event boolean;

UPDATE engagement_events
SET authenticated_at_event = (user_id IS NOT NULL);

ALTER TABLE engagement_events
    ALTER COLUMN authenticated_at_event SET DEFAULT false,
    ALTER COLUMN authenticated_at_event SET NOT NULL;

ALTER TABLE engagement_events
    DROP CONSTRAINT engagement_events_kind_check;

ALTER TABLE engagement_events
    ADD CONSTRAINT engagement_events_kind_check CHECK (kind IN (
        'impression', 'click', 'read', 'dwell', 'complete',
        'save', 'share', 'comment', 'search_impression'
    ));

CREATE INDEX engagement_member_reads_by_blog
    ON engagement_events (blog_id, occurred_at DESC, user_id, actor_id)
    WHERE kind = 'read' AND authenticated_at_event;

CREATE INDEX engagement_guest_reads_by_blog
    ON engagement_events (blog_id, occurred_at DESC, actor_id)
    WHERE kind = 'read' AND NOT authenticated_at_event;


-- A like is current user state, not an append-only telemetry event. The primary
-- key makes PUT idempotent and makes two concurrent likes settle in the database.
CREATE TABLE blog_likes (
    blog_id    uuid        NOT NULL REFERENCES blogs (id) ON DELETE CASCADE,
    user_id    uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (blog_id, user_id)
);

CREATE INDEX blog_likes_by_user ON blog_likes (user_id, created_at DESC);


-- Public feed/detail reads must not aggregate the partitioned engagement log for
-- every card. This projection is updated in the same transaction as the event or
-- like row that supports it.
CREATE TABLE blog_engagement_stats (
    blog_id           uuid        PRIMARY KEY REFERENCES blogs (id) ON DELETE CASCADE,
    member_view_count bigint      NOT NULL DEFAULT 0 CHECK (member_view_count >= 0),
    guest_view_count  bigint      NOT NULL DEFAULT 0 CHECK (guest_view_count >= 0),
    like_count        bigint      NOT NULL DEFAULT 0 CHECK (like_count >= 0),
    updated_at        timestamptz NOT NULL DEFAULT now()
);

INSERT INTO blog_engagement_stats (blog_id)
SELECT id FROM blogs
ON CONFLICT DO NOTHING;


-- Blog mail is default-on by the product decision. Suspended/deleted/admin users
-- are still excluded by the recipient query.
ALTER TABLE users
    ADD COLUMN blog_announcements_enabled boolean NOT NULL DEFAULT true,
    ADD COLUMN blog_announcements_updated_at timestamptz NOT NULL DEFAULT now();


-- One immutable campaign snapshot per article. event_id protects the consumer
-- from at-least-once outbox delivery; blog_id enforces the "first publish only"
-- product rule independently of application code.
CREATE TABLE blog_announcement_campaigns (
    id              uuid        PRIMARY KEY,
    event_id        uuid        NOT NULL UNIQUE,
    blog_id         uuid        NOT NULL UNIQUE REFERENCES blogs (id) ON DELETE CASCADE,
    slug            text        NOT NULL,
    title           text        NOT NULL,
    summary         text,
    cover_image_url text,
    cover_image_alt text,
    tag_keys        text[]      NOT NULL DEFAULT '{}',
    tier            text,
    difficulty      text,
    article_url     text        NOT NULL,
    status          text        NOT NULL DEFAULT 'queued'
                                CHECK (status IN ('queued', 'sending', 'completed', 'partial')),
    created_at      timestamptz NOT NULL DEFAULT now(),
    completed_at    timestamptz,

    CONSTRAINT blog_announcement_cover_pair
        CHECK ((cover_image_url IS NULL) = (cover_image_alt IS NULL)),
    CONSTRAINT blog_announcement_completion_pair
        CHECK ((status IN ('completed', 'partial')) = (completed_at IS NOT NULL))
);

CREATE TABLE blog_announcement_deliveries (
    id                  uuid        PRIMARY KEY,
    campaign_id         uuid        NOT NULL REFERENCES blog_announcement_campaigns (id)
                                    ON DELETE CASCADE,
    user_id             uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    recipient_email     text        NOT NULL,
    status              text        NOT NULL DEFAULT 'pending'
                                    CHECK (status IN (
                                        'pending', 'sending', 'sent', 'cancelled', 'dead'
                                    )),
    attempts            smallint    NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    next_attempt_at     timestamptz NOT NULL DEFAULT now(),
    locked_at           timestamptz,
    provider_message_id text,
    last_error          text,
    sent_at             timestamptz,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),

    UNIQUE (campaign_id, user_id),
    CONSTRAINT blog_announcement_delivery_sent_pair
        CHECK ((status = 'sent') = (sent_at IS NOT NULL))
);

CREATE INDEX blog_announcement_deliveries_claimable
    ON blog_announcement_deliveries (next_attempt_at, id)
    WHERE status IN ('pending', 'sending');

CREATE INDEX blog_announcement_deliveries_campaign
    ON blog_announcement_deliveries (campaign_id, status);

CREATE INDEX blog_announcement_deliveries_user_pending
    ON blog_announcement_deliveries (user_id)
    WHERE status IN ('pending', 'sending');

CREATE TRIGGER blog_announcement_deliveries_set_updated_at
    BEFORE UPDATE ON blog_announcement_deliveries
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
