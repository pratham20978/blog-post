# 02 — Admin Overlap Detection & Tag Vocabulary (your Feature 4) — PLANNING PROMPT

> Load `00_foundation_and_shared_contracts.md` with this file. **Plan only; write no code.**
> This context owns the canonical vocabulary and every write to tags-on-blog. It is the *emitter* of the propagation invariant (foundation §6); it does **not** compute user affinity (that is F1's job, triggered by the events this context emits).

## Objective
Plan two tightly related admin capabilities:
1. **Pre-publish overlap / duplication detection** — before the admin posts a new blog, show existing blogs that overlap (by tags and by text) and which categories are already well-covered, so the admin can avoid duplicating content and instead link/merge.
2. **Canonical tag vocabulary** — the controlled tag set with synonyms, hierarchy, status; **occasional** LLM-assisted re-ranking of the vocabulary (via the admin's API key); and **blog-tag reconciliation** that emits the events F1 uses to recompute user affinity.

All matching is **lexical + set-based only** — no embeddings, no vectors (foundation §3).

## Scope

**In scope**
- **Overlap detection service** for a draft blog (title, body text, proposed tag keys). Returns, without embeddings:
  - **Tag overlap**: existing blogs sharing tags with the draft, scored by set similarity over `tag_keys` — Jaccard and overlap-coefficient (choose per the ranking below), using the `GIN` index on `blogs.tag_keys`.
  - **Lexical overlap**: existing blogs whose text is similar to the draft — `ts_rank_cd` of the draft's key terms against `blogs.search_vector`, plus `pg_trgm` similarity on titles/summaries as a cheap near-duplicate title catch.
  - **Category coverage**: for the draft's mapped categories, how many existing blogs already cover them (a "you already have N here" signal).
  - **Section-level references**: surface relevant reference-pin targets so the admin can point at an exact section instead of rewriting it.
  - A combined **duplication-risk indicator** and a ranked list of the most-similar existing blogs.
- **Canonical vocabulary management**: CRUD on tag keys; **synonyms** (`alias → canonical`, applied on write, silent-remap style); **hierarchy** (parent/child; model with adjacency-list `parent_tag` or `ltree` — decide in plan); **status** (`active|deprecated`); usage counts and co-occurrence stats (materialized, refreshed on a schedule).
- **LLM-assisted vocabulary re-ranking** (occasional, admin-triggered, gated by the admin API key via `AiTextPort`): prompt the model with the **current allowed vocabulary + corpus tag stats** (usage counts, co-occurrence) and ask for a **constrained-JSON proposal** of changes: merges, renames, new canonical tags, deprecations, and re-assignments of tags on existing blogs. **Closed-set validation**: every referenced tag must exist in (or be a proposed addition to) the vocabulary; any hallucinated tag is snapped to the nearest allowed tag by **`pg_trgm` + `levenshtein`**, never by embedding. Admin reviews and approves before anything applies.
- **Blog-tag reconciliation (the only write path to tags-on-blog)**: on approval, apply the vocabulary changes and reassign tags on affected blogs, then **emit `TagVocabularyChanged` and `BlogTagsReassigned`** (foundation §7) so F1 recomputes affinity. This is the mechanism behind foundation §6.
- **Deprecation & culling**: merge near-duplicate tags (retag to canonical, deprecate alias) and flag stale single-use tags for culling.

**Out of scope (owned elsewhere)**
- Computing/updating **user tag-affinity** → **F1** (this context only emits the trigger events).
- Search ranking and query→tag mapping → **F1** (though this context and F1 both rely on the same `search_vector`/`GIN`/`pg_trgm` primitives — define the `search_vector` generated column here or in F1, but define it **once**; note where).
- Publishing blogs, comments, auth → **F3**.
- Email → **F2**.

## Domain model & invariants
- **Tag**: tag_key (PK), label, canonical_tag (self or another), parent_tag?, status(active|deprecated), usage_count.
- **TagSynonym**: alias (PK) → canonical_tag.
- **TagCooccurrence** (materialized): (t1, t2, co_count, ...). Refresh on schedule via `SchedulerPort`.
- **VocabularyChangeSet**: an admin-approved batch of proposed changes (create/rename/merge/split/deprecate + blog reassignments), with `proposed_json`, `validation_status`, `approved_by`, `approved_at`.
- **Invariants**:
  - Every tag reference in the system resolves to an **active canonical** tag (aliases silently remap).
  - **Tags-on-blog change only through an approved VocabularyChangeSet applied here.** No other context writes tags-on-blog (foundation §6.1).
  - Applying a change set **must** emit `BlogTagsReassigned` for each affected blog and a `TagVocabularyChanged` summarizing the operation (foundation §6.3). A change set that mutates tags without emitting these events is invalid.

## Driving ports (use cases)
- `DetectOverlapForDraft(draft{title, body, proposed_tags}) -> { similar_blogs[], category_coverage[], duplication_risk, suggested_pins[] }`.
- `SuggestTagsForDraft(draft) -> proposed_tag_keys[]` — optional, constrained to the allowed vocabulary (LLM via `AiTextPort` **or** a non-LLM keyword method; embeddings not allowed).
- `ProposeVocabularyReranking(admin) -> VocabularyChangeSet` (LLM, constrained JSON, closed-set validated).
- `ReviewChangeSet`, `ApproveChangeSet(admin, change_set_id)`, `RejectChangeSet`.
- `ApplyChangeSet(change_set_id)` — performs reassignment; emits `TagVocabularyChanged` + `BlogTagsReassigned`.
- Vocabulary CRUD: `CreateTag`, `RenameTag`, `MergeTags`, `DeprecateTag`, `AddSynonym`, `SetParent`.
- `RefreshCooccurrence()` (scheduled).

## Driven ports
- `VocabularyRepository`, `SynonymRepository`, `CooccurrenceRepository`, `ChangeSetRepository` (raw SQL).
- `BlogTagWritePort` — the guarded write to `blogs.tag_keys` (only this context holds it).
- `BlogReadPort` (from F3) — read blog title/body/tags for overlap detection.
- `AiTextPort` (foundation §8) — constrained JSON only; no embeddings.
- Foundation shared ports: `EventBusPort`, `SchedulerPort`, `ClockPort`, `IdGeneratorPort`.
- **Provide** `VocabularyReadPort` consumed by F3 (`is_valid_tag`, `canonical_of`) and by F1.

## Matching & scoring (no embeddings)
Plan the exact formulas:
- **Tag similarity**: overlap-coefficient `|Q∩D| / min(|Q|,|D|)` (robust to blogs with many tags) as primary; Jaccard as secondary. Weight rare tags higher via IDF `ln(1 + N/df(t))`.
- **Lexical similarity**: `ts_rank_cd(blogs.search_vector, tsquery(draft_key_terms))`, plus `similarity(title_a, title_b)` (`pg_trgm`) with a conservative threshold for near-duplicate titles.
- **Duplication risk**: a transparent weighted blend of tag-overlap + lexical-similarity + category-coverage, normalized to [0,1]. State the weights as tunable starting points.
- **Hallucination snapping** for LLM output: nearest allowed tag by `pg_trgm.similarity` then `levenshtein` tiebreak; reject if below threshold.

## Data model (raw SQL DDL sketch)
Plan: `tags`, `tag_synonyms`, `tag_cooccurrence` (materialized), `vocabulary_change_sets`, and the guarded update path to `blogs.tag_keys`. State the `GIN` index on `blogs.tag_keys` and the generated `blogs.search_vector` (`setweight` A=title, B=tags, D=body) **if defined here** — otherwise reference F1 as the single definition site. Include indexes for synonym lookup and co-occurrence refresh.

## Events consumed / emitted
- Consumes: `BlogPublished` (to keep usage counts and co-occurrence current).
- Emits: `TagVocabularyChanged`, `BlogTagsReassigned` (foundation §7) — the propagation trigger for F1.

## Acceptance criteria / test scenarios
- For a draft, overlap detection returns the correct most-similar existing blogs and category-coverage counts using only tag set-math + FTS/trigram — verified against seed data; no vector/embedding code exists.
- The LLM vocabulary proposal is closed-set validated; an injected hallucinated tag is either snapped to the nearest allowed tag or rejected, and never persisted as-is.
- Applying an approved change set reassigns tags on exactly the affected blogs and emits one `BlogTagsReassigned` per blog plus a `TagVocabularyChanged` — confirmed by a test that asserts F1's affinity-recompute handler would be triggered.
- No path outside this context can mutate `blogs.tag_keys`.
- Synonyms silently remap on read/write; deprecated tags never surface as active.

## Open questions to resolve in the plan
1. Hierarchy representation: adjacency-list `parent_tag` (recursive CTEs) vs. `ltree`.
2. Where the `search_vector` generated column is defined (here vs. F1) — pick one site and reference it.
3. Whether `SuggestTagsForDraft` uses the LLM or a non-LLM keyword method for v1 (both must stay embedding-free).
4. Overlap-detection thresholds and the duplication-risk weights (starting values + how the admin tunes them).
5. Batch size / safety limits when a single change set reassigns tags across many blogs (to bound the affinity recompute F1 must run).
