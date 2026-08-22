-- 001 — accounts, the credentials that create them, and anonymous visitors.
--
-- No extensions are enabled anywhere in this schema. gen_random_uuid() is
-- built into PostgreSQL 13+, ids are generated in the application via UUIDv7,
-- and F3 needs neither trigram nor full-text search — F1 and F4 enable what
-- their own features require.

-- Sets updated_at on any UPDATE. One function, reused by every table that has
-- the column, so "the timestamp did not move" cannot be a per-table bug.
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;


CREATE TABLE users (
    id                 uuid        PRIMARY KEY,
    email              text        NOT NULL CHECK (length(email) BETWEEN 3 AND 320),
    -- Generated rather than normalised in the application: uniqueness must hold
    -- against what is stored, not against what some caller remembered to lower.
    email_normalized   text        GENERATED ALWAYS AS (lower(btrim(email))) STORED,
    display_name       text        CHECK (display_name IS NULL OR length(display_name) <= 120),
    is_admin           boolean     NOT NULL DEFAULT false,
    status             text        NOT NULL DEFAULT 'active'
                                   CHECK (status IN ('active', 'suspended', 'deleted')),
    email_verified_at  timestamptz,
    created_at         timestamptz NOT NULL DEFAULT now(),
    updated_at         timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX users_email_normalized_key ON users (email_normalized);

-- The single-admin invariant, declared rather than checked.
--
-- Only rows with is_admin = true are indexed, and every one of them has the
-- same key, so a second admin collides. Doc 01 states "at most one is_admin =
-- true"; this is that sentence as a constraint the database enforces.
CREATE UNIQUE INDEX users_single_admin ON users ((is_admin)) WHERE is_admin;

CREATE TRIGGER users_set_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


CREATE TABLE oauth_identities (
    id                 uuid        PRIMARY KEY,
    user_id            uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    provider           text        NOT NULL CHECK (provider IN ('google', 'github')),
    provider_subject   text        NOT NULL,
    email_at_provider  text,
    linked_at          timestamptz NOT NULL DEFAULT now(),

    -- The provider's subject is the stable identity; an email at the provider
    -- can change and must never be the thing we key on.
    UNIQUE (provider, provider_subject)
);

CREATE INDEX oauth_identities_user ON oauth_identities (user_id);


-- A one-time code is a short-lived credential, not a session: foundation §3
-- forbids a server-side session store, and this is not one.
CREATE TABLE otp_challenges (
    id                uuid        PRIMARY KEY,
    email_normalized  text        NOT NULL,
    purpose           text        NOT NULL CHECK (purpose IN ('login', 'signup')),
    -- sha256(pepper || code). The code itself is never stored and never leaves
    -- the process that generated it.
    code_hash         bytea       NOT NULL,
    expires_at        timestamptz NOT NULL,
    attempts          smallint    NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    max_attempts      smallint    NOT NULL DEFAULT 5 CHECK (max_attempts > 0),
    consumed_at       timestamptz,
    created_at        timestamptz NOT NULL DEFAULT now(),
    requested_ip      inet
);

-- Verification looks up the newest live challenge for an address, and the
-- resend cooldown reads the same row. Partial, because a consumed challenge is
-- never a lookup target again.
CREATE INDEX otp_challenges_live
    ON otp_challenges (email_normalized, purpose, created_at DESC)
    WHERE consumed_at IS NULL;

-- Supports the sweep that deletes expired challenges.
CREATE INDEX otp_challenges_expiry ON otp_challenges (expires_at);


-- The refresh registry.
--
-- This is not a session store: no authenticated request reads it. An access
-- token verifies by signature alone, and only /auth/refresh and /auth/revoke
-- ever touch this table.
CREATE TABLE refresh_tokens (
    id              uuid        PRIMARY KEY,
    user_id         uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    -- Every token descended from one sign-in shares a family. Rotation issues
    -- a successor in the same family; detecting reuse kills all of them.
    family_id       uuid        NOT NULL,
    -- sha256 of the opaque secret. A database read alone does not yield a
    -- usable token.
    token_hash      bytea       NOT NULL UNIQUE,
    issued_at       timestamptz NOT NULL DEFAULT now(),
    expires_at      timestamptz NOT NULL,
    -- Set when rotated. A token presented after this is set is a leak: the
    -- honest client already moved on to its successor.
    consumed_at     timestamptz,
    replaced_by_id  uuid        REFERENCES refresh_tokens (id) ON DELETE SET NULL,
    revoked_at      timestamptz,
    revoked_reason  text,
    user_agent      text,
    client_ip       inet
);

CREATE INDEX refresh_tokens_live
    ON refresh_tokens (user_id)
    WHERE revoked_at IS NULL AND consumed_at IS NULL;

-- Revoking a family on reuse detection touches every member at once.
CREATE INDEX refresh_tokens_family ON refresh_tokens (family_id);

CREATE INDEX refresh_tokens_expiry ON refresh_tokens (expires_at);


-- A reader we have issued an actor token to but who has not signed in.
--
-- This is what makes unauthenticated action first-class: engagement has a
-- subject before there is an account, and on sign-in that history is merged
-- into the user rather than thrown away.
CREATE TABLE anonymous_actors (
    id                   uuid        PRIMARY KEY,
    created_at           timestamptz NOT NULL DEFAULT now(),
    last_seen_at         timestamptz NOT NULL DEFAULT now(),
    first_user_agent     text,
    first_client_ip      inet,
    merged_into_user_id  uuid        REFERENCES users (id) ON DELETE SET NULL,
    merged_at            timestamptz,

    CONSTRAINT anonymous_actors_merge_is_atomic
        CHECK ((merged_into_user_id IS NULL) = (merged_at IS NULL))
);

CREATE INDEX anonymous_actors_merged
    ON anonymous_actors (merged_into_user_id)
    WHERE merged_into_user_id IS NOT NULL;
