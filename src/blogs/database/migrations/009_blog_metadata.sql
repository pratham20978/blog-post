-- 009 — typed editorial metadata carried by the canonical Markdown source.
--
-- This is deliberately additive. Existing operational timestamps keep their
-- meaning; published_on/content_updated_on are the dates chosen by the author.

CREATE FUNCTION valid_blog_tag_keys(keys text[])
RETURNS boolean
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT
        COALESCE(bool_and(key ~ '^[a-z0-9]+(-[a-z0-9]+)*$'), true)
        AND count(*) = count(DISTINCT key)
    FROM unnest(keys) AS key
$$;

CREATE FUNCTION valid_blog_prerequisites(items text[])
RETURNS boolean
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT COALESCE(bool_and(item IS NOT NULL AND length(btrim(item)) > 0), true)
    FROM unnest(items) AS item
$$;

ALTER TABLE blogs
    ADD COLUMN cover_image_url text,
    ADD COLUMN cover_image_alt text,
    ADD COLUMN tag_keys text[] NOT NULL DEFAULT ARRAY[]::text[],
    ADD COLUMN tier text,
    ADD COLUMN difficulty text,
    ADD COLUMN prerequisites text[] NOT NULL DEFAULT ARRAY[]::text[],
    ADD COLUMN canonical_url text,
    ADD COLUMN published_on date,
    ADD COLUMN content_updated_on date,

    ADD CONSTRAINT blogs_cover_is_complete CHECK (
        (cover_image_url IS NULL AND cover_image_alt IS NULL)
        OR (
            cover_image_url ~ '^https?://[^[:space:]/<>{}]+($|/)'
            AND length(btrim(cover_image_alt)) > 0
        )
    ),
    ADD CONSTRAINT blogs_tag_keys_are_valid CHECK (valid_blog_tag_keys(tag_keys)),
    ADD CONSTRAINT blogs_tier_is_valid CHECK (
        tier IS NULL OR tier IN ('L1', 'L2', 'L3', 'L4')
    ),
    ADD CONSTRAINT blogs_difficulty_is_valid CHECK (
        difficulty IS NULL OR difficulty IN ('beginner', 'intermediate', 'advanced')
    ),
    ADD CONSTRAINT blogs_prerequisites_are_nonempty CHECK (
        valid_blog_prerequisites(prerequisites)
    ),
    ADD CONSTRAINT blogs_canonical_url_is_http CHECK (
        canonical_url IS NULL
        OR canonical_url ~ '^https?://[^[:space:]/<>{}]+($|/)'
    );

CREATE INDEX blogs_tag_keys_gin ON blogs USING gin (tag_keys);

CREATE UNIQUE INDEX blogs_canonical_url_unique
    ON blogs (canonical_url)
    WHERE canonical_url IS NOT NULL;
