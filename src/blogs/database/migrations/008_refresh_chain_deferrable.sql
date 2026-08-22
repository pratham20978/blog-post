-- 008 — let the refresh chain close within a transaction.
--
-- Rotation is one atomic step with two halves: mark the presented token
-- consumed and point it at its successor, then insert that successor. Whichever
-- order they are written in, there is a moment inside the transaction when
-- refresh_tokens.replaced_by_id names a row that does not exist yet — and an
-- immediate foreign key rejects it there.
--
-- Verified against the running system: POST /auth/refresh returned 500 with
-- "Key (replaced_by_id)=(...) is not present in table refresh_tokens".
--
-- Reordering the writes would work but makes the chain a two-statement dance
-- that a future edit can silently break. Deferring is the accurate statement of
-- intent instead: the constraint must hold when the transaction *commits*, not
-- at every instant within it. A rollback still discards both halves, so a
-- dangling pointer can never be observed or persisted.

ALTER TABLE refresh_tokens
    DROP CONSTRAINT refresh_tokens_replaced_by_id_fkey;

ALTER TABLE refresh_tokens
    ADD CONSTRAINT refresh_tokens_replaced_by_id_fkey
        FOREIGN KEY (replaced_by_id) REFERENCES refresh_tokens (id)
        ON DELETE SET NULL
        DEFERRABLE INITIALLY DEFERRED;
