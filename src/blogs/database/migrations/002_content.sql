-- 002 — articles, their structure, and the groupings they hang off.
--
-- There is no tag column here, and that is deliberate rather than pending.
-- F4 owns the canonical vocabulary and the weighting model behind it; adding
-- the column now would mean guessing at both. When F4 lands it adds
-- blogs.tag_keys, its GIN index and the tag_keys[] field on BlogPublished —
-- all additive, so nothing written against this schema breaks.
--
-- There is also no search_vector. Foundation §3 wants it defined exactly once,
-- and that site is F1 or F4, not here.

CREATE TABLE series (
    id           uuid        PRIMARY KEY,
    key          text        NOT NULL UNIQUE
                             CHECK (key ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
    title        text        NOT NULL CHECK (length(btrim(title)) > 0),
    description  text,
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER series_set_updated_at
    BEFORE UPDATE ON series
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- Non-hierarchical, per doc 01. Tag hierarchy is F4's problem; a category is
-- a flat label and modelling it as a tree here would invite the two concepts
-- to blur.
CREATE TABLE categories (
    key          text        PRIMARY KEY
                             CHECK (key ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
    label        text        NOT NULL CHECK (length(btrim(label)) > 0),
    description  text,
    created_at   timestamptz NOT NULL DEFAULT now()
);


CREATE TABLE blogs (
    id               uuid        PRIMARY KEY,
    slug             text        NOT NULL UNIQUE
                                 CHECK (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
    title            text        NOT NULL CHECK (length(btrim(title)) > 0),
    summary          text,
    -- Always the single admin. The application enforces which account that is;
    -- the FK enforces that it is a real one.
    author_id        uuid        NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
    series_id        uuid        REFERENCES series (id) ON DELETE SET NULL,
    series_position  integer     CHECK (series_position IS NULL OR series_position >= 0),

    -- Where the raw .md lives in the object store. Content-addressed, so
    -- re-publishing identical bytes is idempotent.
    markdown_uri     text        NOT NULL,
    content_sha256   bytea       NOT NULL CHECK (octet_length(content_sha256) = 32),

    word_count       integer     NOT NULL DEFAULT 0 CHECK (word_count >= 0),
    -- Ceiling division by the validated 238 wpm silent reading rate for English
    -- non-fiction (Brysbaert 2019). Generated, so it cannot drift from the word
    -- count it is derived from.
    reading_minutes  integer     GENERATED ALWAYS AS
                                 (GREATEST(1, (word_count + 237) / 238)) STORED,

    status           text        NOT NULL DEFAULT 'draft'
                                 CHECK (status IN ('draft', 'published', 'archived')),
    published_at     timestamptz,
    archived_at      timestamptz,
    created_at       timestamptz NOT NULL DEFAULT now(),
    updated_at       timestamptz NOT NULL DEFAULT now(),

    -- A published article without a publication time would sort arbitrarily in
    -- every feed and break every window query silently.
    CONSTRAINT blogs_published_has_timestamp
        CHECK (status <> 'published' OR published_at IS NOT NULL),
    CONSTRAINT blogs_archived_has_timestamp
        CHECK (status <> 'archived' OR archived_at IS NOT NULL),
    CONSTRAINT blogs_series_position_needs_series
        CHECK (series_position IS NULL OR series_id IS NOT NULL)
);

-- The feed query: published articles, newest first, keyset-paginated on
-- (published_at, id). Partial, because drafts and archives never appear in it.
CREATE INDEX blogs_feed
    ON blogs (published_at DESC, id DESC)
    WHERE status = 'published';

CREATE INDEX blogs_series_order
    ON blogs (series_id, series_position)
    WHERE series_id IS NOT NULL;

-- Admin listings filter by status; the feed index above cannot serve those.
CREATE INDEX blogs_status ON blogs (status, updated_at DESC);

CREATE TRIGGER blogs_set_updated_at
    BEFORE UPDATE ON blogs
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


CREATE TABLE blog_categories (
    blog_id       uuid NOT NULL REFERENCES blogs (id) ON DELETE CASCADE,
    -- RESTRICT, not CASCADE: deleting a category should fail loudly rather than
    -- quietly unfile every article in it.
    category_key  text NOT NULL REFERENCES categories (key) ON DELETE RESTRICT,

    PRIMARY KEY (blog_id, category_key)
);

-- The reverse direction — "articles in this category" — which the primary key
-- cannot serve.
CREATE INDEX blog_categories_by_category ON blog_categories (category_key, blog_id);


-- Headings extracted from the Markdown at publish time.
--
-- This is what makes an anchor checkable. Without it a reference pin's target
-- and a marker's section are free strings that may point nowhere, and nothing
-- would notice until a reader followed one. F1 later hangs passage-level
-- retrieval off these same rows.
CREATE TABLE blog_sections (
    blog_id     uuid     NOT NULL REFERENCES blogs (id) ON DELETE CASCADE,
    anchor      text     NOT NULL CHECK (anchor ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
    ordinal     integer  NOT NULL CHECK (ordinal >= 0),
    level       smallint NOT NULL CHECK (level BETWEEN 1 AND 6),
    title       text     NOT NULL,
    -- Offsets into the stored Markdown body.
    char_start  integer  NOT NULL CHECK (char_start >= 0),
    char_end    integer  NOT NULL CHECK (char_end >= char_start),

    PRIMARY KEY (blog_id, anchor)
);

CREATE INDEX blog_sections_order ON blog_sections (blog_id, ordinal);


-- An admin's pointer from one article to an exact section of another. Doc 01
-- surfaces these to F4's overlap detection.
CREATE TABLE reference_pins (
    id              uuid        PRIMARY KEY,
    source_blog_id  uuid        NOT NULL REFERENCES blogs (id) ON DELETE CASCADE,
    -- RESTRICT: an article that others point into cannot vanish out from under
    -- them. Archiving is how it is retired.
    target_blog_id  uuid        NOT NULL REFERENCES blogs (id) ON DELETE RESTRICT,
    target_anchor   text        NOT NULL,
    note            text,
    created_by      uuid        NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
    created_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT reference_pins_not_self CHECK (source_blog_id <> target_blog_id),
    UNIQUE (source_blog_id, target_blog_id, target_anchor),

    -- The anchor must be a real section of the target article, enforced by the
    -- database rather than by whoever remembers to look it up.
    FOREIGN KEY (target_blog_id, target_anchor)
        REFERENCES blog_sections (blog_id, anchor) ON DELETE RESTRICT
);

CREATE INDEX reference_pins_source ON reference_pins (source_blog_id);
CREATE INDEX reference_pins_target ON reference_pins (target_blog_id, target_anchor);
