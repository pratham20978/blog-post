# 03 — Search / Ranking / Re-ranking (your Feature 1) — PLANNING PROMPT

> Load `00_foundation_and_shared_contracts.md` with this file. **Plan only; write no code.**
> This context owns user tag-affinity and ranking. It is **lexical + set-based only — no vectors, no embeddings, no pgvector** (foundation §3). It is the *consumer* of the propagation invariant: it recomputes affinity when F4 emits tag/vocabulary changes (foundation §6).

## Objective

Plan a two-stage "retrieve-then-rerank" search that (a) returns relevant blogs for a query, (b) personalizes for Audience A via a **derived** tag-affinity profile that updates over time, and (c) degrades cleanly to non-personalized ranking for Audience B. Also plan the **highlight-to-search** entry point. Output must match foundation §10.

## Scope

**In scope**

- **Query understanding**: normalize (lowercase/trim); map query terms → known tag keys via **exact match → `pg_trgm` fuzzy → synonym table** (all read through `VocabularyReadPort`). **No embedding fallback** (foundation §3).
- **Candidate generation (recall)**: `WHERE blogs.search_vector @@ websearch_to_tsquery('english', q) OR blogs.tag_keys && mapped_query_tags`, `LIMIT ~500`. Uses the `GIN` indexes on `search_vector` and `tag_keys`.
- **Linear reranker (precision)** — transparent, hand-tuned, all terms normalized to [0,1]:
  `score = w_tag·TagMatch + w_pers·Personalization + w_lex·LexicalRank + w_fresh·Freshness + w_qual·Quality`
  Starting weights `w_tag=0.35, w_lex=0.25, w_pers=0.20, w_fresh=0.10, w_qual=0.10`.
  - `TagMatch` = IDF-weighted overlap of query∩blog tags, `idf(t)=ln(1+N/df(t))`.
  - `Personalization` = Σ over blog tags of `affinity(user, tag)` (0 for Audience B → non-personalized).
  - `LexicalRank` = normalized `ts_rank_cd(search_vector, tsquery)`.
  - `Freshness` = `1 / (age_hours + 2)^1.8`.
  - `Quality` = Bayesian-smoothed engagement rate `(positives + C·m)/(impressions + C)` from the engagement log.
- **Diversity + exploration**: MMR re-order of the top ~50 (`λ≈0.7`, similarity = tag-Jaccard — **not** embeddings) + **ε-greedy** exploration (`ε≈0.1`) injecting an adjacent-tag blog.
- **User tag-affinity (derived, the core)** — owned here:
  - Definition (foundation §6.3): over the set of blogs a user engaged with, `affinity(u,t) = normalize( Σ_{b∈Engaged(u), t∈tags(b)} signal(type_b)·decay(age_b) )`. Expressed as the **share/percentage** of the user's engaged blogs carrying `t`, weighted by engagement signal and recency — i.e. the union/intersection/percent model you described.
  - Signals (starting values, tunable): impression −0.1, click +1.0, valid dwell +2.0, complete +3.0, save/share +5.0, quick-bounce −0.5. Dwell normalized by length: `min(1, dwell / (word_count/238·60s))`; define a "valid read" threshold.
  - Time decay: half-life `H≈45 days`, `decay=0.5^(Δt/H)`. Cap weights; keep top ~50 tags per user; prune the tail.
  - **Two update paths (must converge to the same definition):**
    1. **Incremental** — on each engagement event from the log, update the affected tags.
    2. **Full recompute** — on `BlogTagsReassigned`/`TagVocabularyChanged` from F4, recompute affinity for affected users from their engaged blogs' **current** tags. This is the propagation (foundation §6.3/§6.4).
  - Optional **short-term interest** (unrelated to auth sessions): a recent-engagement view derived from the log, blended as `w_long·long + w_short·session` (start 0.7/0.3). **Decision point** — may be Postgres-backed or omitted for v1 (no Redis; foundation §3).
- **Highlight-to-search entry point**: user highlights/hovers a sentence → API searches **our blogs first** (reusing everything above), then optionally external results via `ExternalSearchPort` (Google). Return a reference panel: internal matches first, external second.
- **Impression logging**: emit `SearchImpressionLogged` and write impressions (with position) to the engagement log so ranking can be evaluated and debiased later.
- **Evaluation hooks**: log everything with position now; plan offline NDCG@k / MAP / MRR / Recall@k on the logged clicks, and the personalization check (personalized vs. non-personalized on the same users).

**Out of scope (owned elsewhere)**

- Vocabulary CRUD, synonyms, hierarchy, blog-tag reassignment → **F4** (this context only *reads* the vocabulary and *reacts* to its change events).
- Blog CRUD, comments, auth, the engagement log's write path from reading → **F3** (this context reads the log and adds search impressions).
- Email → **F2**.
- **Anything vector/embedding/pgvector — explicitly forbidden here.**

## Domain model & invariants

- **UserTagAffinity**: (user_id, tag_key, weight, last_updated). Invariant: **derived only** — no use case sets it from outside; it is always a function of engagement × current tags (foundation §6.2). Invariant: bounded (capped) and top-N pruned.
- **Query**: normalized text + mapped tag keys + audience (A/B).
- **RankedResult**: blog_id, score, component breakdown (keep the breakdown for debuggability).
- Invariant: Audience B never contributes a nonzero personalization term.

## Driving ports (use cases)

- `Search(query, viewer?) -> ranked_results` (candidate-gen → rerank → MMR/ε-greedy → log impressions).
- `HighlightSearch(selection_text, viewer?) -> reference_panel` (internal first, external optional).
- `RecomputeAffinityForUsers(user_ids)` — invoked by the F4 event handler.
- `ApplyEngagement(event)` — incremental affinity update (subscribes to the engagement log / engagement events).
- `GetAffinityProfile(user_id)` (debug/inspection).

## Driven ports

- `BlogSearchRepository` (raw SQL: candidate gen + `ts_rank_cd`), `AffinityRepository` (raw SQL upsert/recompute).
- `VocabularyReadPort` (from F4) — exact/synonym/`pg_trgm` tag mapping and IDF/`df` lookups.
- `EngagementLogPort` (foundation §8) — read engaged blogs, aggregates for Quality and affinity.
- `ExternalSearchPort` (foundation §8, deferred) — Google web/scholar (scholar/PDF out of scope v1).
- Foundation shared ports: `EventBusPort` (subscribe to F4 events; publish `SearchImpressionLogged`), `ClockPort`.

## Algorithms — state them explicitly in the plan

- The candidate SQL and the reranker SQL (single round-trip where possible), with the normalized component terms and starting weights above.
- The affinity definition, both update paths, decay, caps, top-N pruning, and the proof that incremental and full-recompute converge.
- MMR (`λ`) and ε-greedy (`ε`) as a post-scoring application-layer pass over the top ~50.
- Cold start: new blog is immediately retrievable by its tags (advantage of tag-based); new user → Audience B ranking; optional "follow a few tags" bootstrap (coordinate with F3's follow primitive if present).

## Data model (raw SQL DDL sketch)

- `user_tag_affinity(user_id, tag_key, weight real, last_updated timestamptz, PRIMARY KEY(user_id, tag_key))`, index `(user_id, weight DESC)`.
- The generated `blogs.search_vector` (`setweight` A=title, B=tags, D=body) + `GIN` — **defined once** (here or F4; state which; foundation-consistent).
- Impression rows in the shared `engagement_events` log (position, query_id).
- Optional short-term-interest table if that decision is taken.

## Events consumed / emitted

- Consumes: `BlogTagsReassigned`, `TagVocabularyChanged` (→ `RecomputeAffinityForUsers`); engagement events / log appends (→ incremental affinity).
- Emits: `SearchImpressionLogged`.

## Acceptance criteria / test scenarios

- A query returns candidates via tag-overlap **and** FTS, reranked by the five-term linear score; results include a component breakdown; **no vector code path exists**.
- For a profiled user, personalized ranking differs from the non-personalized baseline and can be shown to help (higher rank for tags the user engages with); for Audience B the personalization term is exactly 0.
- Affinity updates incrementally on new engagement and **fully recomputes** on an F4 `BlogTagsReassigned` event; both yield the same weights for the same underlying data (convergence test).
- Query→tag mapping resolves exact, synonym, and fuzzy (`pg_trgm`) cases; unmapped conceptual queries fall back to FTS only (documented gap, since no embeddings).
- Highlight-to-search returns internal matches first; external adapter is optional and absent-safe.
- Impressions are logged with position for later evaluation.

## Open questions to resolve in the plan

1. Keep or drop the short-term/session interest blend for v1 (no Redis — if kept, Postgres-backed).
2. Exact "valid read" dwell threshold and words-per-minute constant for the audience.
3. Whether affinity recompute on large F4 change sets runs inline or via `JobQueuePort` (bounded fan-out).
4. Whether the external (Google) highlight-search adapter ships in v1 or is stubbed behind the port.
5. Single definition site for `search_vector` (coordinate with F4).
