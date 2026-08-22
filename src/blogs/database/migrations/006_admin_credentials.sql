-- 006 — a password for the admin, and the throttle that protects it.
--
-- Doc 01 specifies OTP and OAuth, and that stays the whole story for readers:
-- no reader account has or needs a password. The admin is different. Email
-- possession alone is a single factor that a compromised mailbox defeats
-- entirely, and the admin is the only account that can publish, edit, delete
-- and read every KPI on the platform.
--
-- So the admin gets a password *in addition*: reaching the console requires the
-- secret path, then the password, then the same signed token every other
-- request carries.

ALTER TABLE users
    -- scrypt output stored as salt(16) || derived key(32). One column rather
    -- than two, because the halves are meaningless apart and storing them
    -- together makes it impossible to read one without the other.
    ADD COLUMN password_hash       bytea,
    ADD COLUMN password_updated_at timestamptz;

ALTER TABLE users
    ADD CONSTRAINT users_password_hash_shape
        CHECK (password_hash IS NULL OR octet_length(password_hash) = 48);

-- Only the admin may hold a password. A reader row with one would mean a second
-- authentication path nobody designed, reviewed, or rate-limited.
ALTER TABLE users
    ADD CONSTRAINT users_password_is_admin_only
        CHECK (password_hash IS NULL OR is_admin);


-- Every admin sign-in attempt, successful or not.
--
-- Separate from the users row on purpose: a counter column would be updated on
-- each failure, and an attacker could then measure lock state through response
-- timing. A log also answers "when was this attacked" after the fact, which a
-- counter cannot.
CREATE TABLE admin_login_attempts (
    id                uuid        PRIMARY KEY,
    email_normalized  text        NOT NULL,
    attempted_at      timestamptz NOT NULL DEFAULT now(),
    succeeded         boolean     NOT NULL,
    client_ip         inet,
    user_agent        text
);

-- The lockout query: recent failures for this address. Partial, so the index
-- holds only what the check reads and successful history does not inflate it.
CREATE INDEX admin_login_attempts_recent_failures
    ON admin_login_attempts (email_normalized, attempted_at DESC)
    WHERE NOT succeeded;

-- For the retention sweep.
CREATE INDEX admin_login_attempts_age ON admin_login_attempts (attempted_at);
