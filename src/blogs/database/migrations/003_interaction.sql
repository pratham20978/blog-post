-- 003 — comments, markers, catalogs.
--
-- Doc 01 asks for two rules that application code is bad at keeping: one
-- comment per user per article, and replies only to top-level comments. Both
-- are declared here instead, so they hold no matter which code path writes.

CREATE TABLE comments (
    id                 uuid        PRIMARY KEY,
    blog_id            uuid        NOT NULL REFERENCES blogs (id) ON DELETE CASCADE,
    user_id            uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    parent_comment_id  uuid,
    depth              smallint    NOT NULL CHECK (depth IN (0, 1)),
    body               text        NOT NULL
                                   CHECK (length(btrim(body)) BETWEEN 1 AND 10000),
    created_at         timestamptz NOT NULL DEFAULT now(),
    updated_at         timestamptz NOT NULL DEFAULT now(),
    -- Soft delete: a removed comment leaves a tombstone so its replies keep
    -- their parent and the thread does not silently reshape.
    deleted_at         timestamptz,
    deleted_by         uuid        REFERENCES users (id) ON DELETE SET NULL,

    -- A root has no parent; a reply must have one. Neither state is reachable
    -- by mistake.
    CONSTRAINT comments_depth_matches_parent
        CHECK ((depth = 0 AND parent_comment_id IS NULL)
            OR (depth = 1 AND parent_comment_id IS NOT NULL)),

    -- Referenced by the composite foreign key below.
    CONSTRAINT comments_id_depth_blog_key UNIQUE (id, depth, blog_id)
);

-- Single-level threading, enforced by the schema rather than by a check the
-- application must remember.
--
-- parent_depth is generated as 0 for every reply and NULL for every root. The
-- foreign key then demands that the parent row have depth = 0 *and* the same
-- blog_id. Under the default MATCH SIMPLE the constraint is skipped whenever
-- any referencing column is NULL, so roots pass untouched while every reply
-- must resolve to a top-level comment on the same article.
--
-- The result: a reply to a reply is not merely refused, it is unrepresentable.
-- No recursive CTE, no materialised path, no cycle guard, no depth cap.
ALTER TABLE comments
    ADD COLUMN parent_depth smallint
        GENERATED ALWAYS AS (CASE WHEN parent_comment_id IS NULL THEN NULL ELSE 0 END) STORED;

ALTER TABLE comments
    ADD CONSTRAINT comments_parent_is_root
        FOREIGN KEY (parent_comment_id, parent_depth, blog_id)
        REFERENCES comments (id, depth, blog_id) ON DELETE CASCADE;

-- One comment per user per article — doc 01's rule, scoped to roots and
-- ignoring tombstones so deleting yours lets you write another.
CREATE UNIQUE INDEX comments_one_root_per_user_blog
    ON comments (blog_id, user_id)
    WHERE depth = 0 AND deleted_at IS NULL;

-- Listing a thread: roots for an article, newest first.
CREATE INDEX comments_roots
    ON comments (blog_id, created_at DESC)
    WHERE depth = 0 AND deleted_at IS NULL;

-- Attaching replies to the roots just listed.
CREATE INDEX comments_replies
    ON comments (parent_comment_id, created_at)
    WHERE parent_comment_id IS NOT NULL;

CREATE TRIGGER comments_set_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- One saved position per user per article. The primary key is the invariant:
-- placing a marker again moves it rather than adding a second.
CREATE TABLE markers (
    user_id         uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    blog_id         uuid        NOT NULL REFERENCES blogs (id) ON DELETE CASCADE,
    -- A discriminated union: section | offset | range. Validated by the
    -- contract on the way in; stored as jsonb because its shape is a domain
    -- concern rather than a relational one.
    anchor          jsonb       NOT NULL,
    -- Kept beside the anchor rather than derived from it, so a "continue
    -- reading" list never has to interpret the payload to sort.
    progress_ratio  real        CHECK (progress_ratio IS NULL
                                       OR progress_ratio BETWEEN 0 AND 1),
    updated_at      timestamptz NOT NULL DEFAULT now(),

    PRIMARY KEY (user_id, blog_id),
    CONSTRAINT markers_anchor_is_object CHECK (jsonb_typeof(anchor) = 'object')
);

-- "Where was I?" — the user's markers, most recently moved first.
CREATE INDEX markers_by_user ON markers (user_id, updated_at DESC);


CREATE TABLE catalogs (
    id          uuid        PRIMARY KEY,
    user_id     uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name        text        NOT NULL CHECK (length(btrim(name)) BETWEEN 1 AND 120),
    -- Saving without naming a catalog lands here.
    is_default  boolean     NOT NULL DEFAULT false,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

-- Case-insensitive: "Reading List" and "reading list" are the same collection
-- to the person who made them.
CREATE UNIQUE INDEX catalogs_name_per_user ON catalogs (user_id, lower(btrim(name)));

-- The lazily-created default catalog can never double up, even if two saves
-- race on a user who has none.
CREATE UNIQUE INDEX catalogs_one_default ON catalogs (user_id) WHERE is_default;

CREATE TRIGGER catalogs_set_updated_at
    BEFORE UPDATE ON catalogs
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


CREATE TABLE catalog_items (
    catalog_id  uuid        NOT NULL REFERENCES catalogs (id) ON DELETE CASCADE,
    blog_id     uuid        NOT NULL REFERENCES blogs (id) ON DELETE CASCADE,
    added_at    timestamptz NOT NULL DEFAULT now(),
    note        text,

    PRIMARY KEY (catalog_id, blog_id)
);

-- "Who saved this article" — for per-blog KPIs, and for F2's segmentation
-- later.
CREATE INDEX catalog_items_by_blog ON catalog_items (blog_id);

-- Listing a catalog in the order things were added.
CREATE INDEX catalog_items_recent ON catalog_items (catalog_id, added_at DESC);
