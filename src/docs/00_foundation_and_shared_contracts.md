# 00 — Foundation & Shared Contracts (READ FIRST)

> This is the shared spine for all four feature-planning prompts. It is **not** a build task by itself.
> In each Claude Code planning session, load this file **plus one** feature file, and nothing else.
> Everything a feature plan needs to agree on with the others lives here so the four plans never overlap.

---

## 0. How to use these files with Claude Code

1. Drop all five files into your repo, e.g. `planning/`.
2. Plan **one feature per session**, in the recommended order (§4). In each session tell Claude Code:
   > "Read `planning/00_foundation_and_shared_contracts.md` and `planning/0X_<feature>.md`. Produce the implementation plan described in the 'Deliverables the plan must produce' section. **Do not write any code yet.**"
3. Review the plan, then start a fresh session to implement.
4. Because contracts (events, ports, the tag-propagation invariant) are fixed here, features stay independently plannable and buildable.

---

## 1. What we are building

A backend-only blog platform with a **single admin** author and many read-only registered users. Four features:

| # (your label) | Feature | One-line scope |
|---|---|---|
| **F3** | Core Blog Platform | Auth (OTP + OAuth, stateless), admin blog authoring from Markdown, comments, markers, catalogs/saves, recent views, engagement log, admin read models |
| **F4** | Admin Overlap + Tag Vocabulary | Pre-publish duplicate/overlap detection; the canonical tag vocabulary; occasional LLM-assisted vocabulary re-ranking; blog-tag reconciliation that **triggers** user-affinity recompute |
| **F1** | Search / Ranking / Re-ranking | Personalized tag+lexical retrieval and a transparent linear reranker; derived user tag-affinity that updates over time; highlight-to-search entry point |
| **F2** | Email Pipeline | Admin-controlled, event-driven email: transactional, personalized, daily digest, AI-generated blog notifications; segmentation, consent, deliverability |

**No UI in scope.** These plans stop at the driving (HTTP/API) port; the request/response contracts are defined, the UI is not.

---

## 2. Two audiences (this shapes F1 and F2)

- **Audience A — profiled users.** Authenticated users we track. They have a **derived tag-affinity profile** (F1) and can be targeted by behavior/interest in email (F2). They get personalized ranking.
- **Audience B — unprofiled recipients.** Anonymous readers and opted-in subscribers with no affinity profile. They get **non-personalized** ranking (freshness + quality + tag/lexical match) and **broadcast/segment** email only.

Every ranking and every email decision must state which audience it is serving and degrade cleanly from A to B (cold start).

---

## 3. Locked constraints (apply to ALL features)

- **Architecture: hexagonal (ports & adapters).** Domain and application layers hold all logic and depend only on ports (interfaces). Adapters are the only place technology appears.
- **Persistence: raw SQL on PostgreSQL. No ORM.** Repositories are ports; adapters issue hand-written SQL. DDL sketches in these files are contracts, not final migrations.
- **Object storage: MinIO** behind an `ObjectStorePort` (Markdown source files and images).
- **No other infrastructure is assumed.** No Redis, no external broker. Model the **event bus, job queue, and scheduler as ports**; the initial adapters are **Postgres-backed** (transactional outbox + poller; `FOR UPDATE SKIP LOCKED` work queue; a due-jobs table + poller). They can be swapped later without touching the domain.
- **No vector search, no embeddings anywhere in the running system.** Retrieval, matching, dedup, and query→tag mapping are **lexical + set-based only** (`tsvector`/`ts_rank_cd`, `pg_trgm`, `GIN`, `levenshtein`, set similarity). Embeddings, if ever used, are a one-off offline design aid and are **not** part of any adapter.
- **LLM usage is narrow and gated by an admin-supplied API key**, used in exactly two places:
  1. F4 — occasional tag-vocabulary re-ranking (constrained JSON proposal against the allowed vocabulary).
  2. F2 — blog-notification email content (constrained JSON into a locked template).
  Everything the LLM returns is closed-set validated; hallucinated tags are snapped to the nearest allowed tag by **string similarity, not embeddings**.
- **Authentication is token-based and stateless.** No server-side session store. ("Session" in the search sense, §6, is optional recent-interest state, unrelated to auth, and if kept is derived from the engagement log — see F1.)
- **Language: English only.** Postgres text search config `'english'`.
- **"Tech stack not named."** These plans describe the domain, ports, and adapter *roles*. Do **not** pin a language, web framework, queue library, or LLM vendor. PostgreSQL/MinIO and Postgres features (`tsvector`, `pg_trgm`, `GIN`, `ltree`) are named because they are the committed infrastructure. *(If this reading is wrong and you also want the language/framework fixed, say so before planning.)*

---

## 4. Bounded contexts, build order, dependency map

Recommended **sequential** build order (each is independently plannable because contracts below are fixed):

```
  F3 Core Blog ──▶ F4 Vocabulary/Overlap ──▶ F1 Search/Ranking ──▶ F2 Email
      (base)          (clean tags first)        (needs clean tags)     (most independent)
```

Dependencies (who reads/consumes what — all via events/ports, never direct calls):

- **F3** produces: users, blogs, tags-on-blogs, comments, and the **engagement log**. Emits blog/auth/engagement events.
- **F4** owns the **canonical vocabulary** and blog-tag assignments. Consumes `BlogPublished`. Emits `TagVocabularyChanged`, `BlogTagsReassigned`.
- **F1** owns **user tag-affinity** and ranking. Consumes engagement events (incremental affinity) and `BlogTagsReassigned`/`TagVocabularyChanged` (**recompute** affinity — the propagation invariant §6). Emits `SearchImpressionLogged`.
- **F2** consumes `BlogPublished`, `UserRegistered`, auth events, and reads segmentation data. Emits nothing other contexts depend on.

No context imports another context's internals. They meet only at the event catalog (§7) and shared ports (§8).

---

## 5. Ubiquitous language (glossary)

- **Blog / Article** — one published post. Markdown source in MinIO; metadata (title, slug, tags, series, category, timestamps) in Postgres.
- **Tag key** — the canonical, normalized identifier of a tag (lowercased, hyphenated, e.g. `machine-learning`). All references are by tag key.
- **Canonical vocabulary** — the controlled set of active tag keys plus synonyms, hierarchy, and status. Owned by F4.
- **Tags-on-blog** — the set of tag keys assigned to a blog. Changes only via F4 (vocabulary update / reassignment), never ad hoc after publish. *(Initial tags at publish come from the admin in F3 but must be validated against the vocabulary.)*
- **User tag-affinity** — a **derived** per-user, per-tag weight (Audience A only). Never hand-set. A projection over (that user's engagement × current tags-on-blog). Owned by F1.
- **Engagement event** — one row in the append-only engagement log: impression / click / dwell / complete / save / share / comment, with position, query id, dwell, timestamp.
- **Marker** — a user's personal position bookmark inside a specific blog ("where I stopped / want to resume"). One per user per blog.
- **Reference pin** — an admin's cross-blog pointer to an exact section of another blog (used while authoring and by overlap detection).
- **Catalog** — a user's saved collection of blogs (bookmarks grouped).
- **Segment** — a boolean rule tree over user attributes/tags/follows/activity, evaluated to a recipient set (F2).

---

## 6. THE core invariant: vocabulary → blog tags → user affinity

This is the rule the whole system pivots on. State it verbatim in every relevant plan.

1. **Blog tags change only when the vocabulary changes.** A blog's tag set is stable after publish except when F4 runs a vocabulary operation (create / rename / merge / split / deprecate) and reassigns tags. There is no other write path to tags-on-blog.
2. **User tags are never edited directly.** `user_tag_affinity` is a **derived projection**, a function of:
   - the set of blogs the user engaged with, and
   - the **current** tags-on-blog for those blogs,
   weighted by engagement type and time decay.
3. **Therefore, when blog tags change, user affinity must recompute.** F4 emits `BlogTagsReassigned` / `TagVocabularyChanged`; F1 consumes them and recomputes affinity for the affected users using set mathematics:
   - a user's **tag set** = union of current tags across their engaged blogs;
   - a tag's **strength** = weighted count / **share (percentage)** of that user's engaged blogs carrying it (this is the "union / intersection / percent" you described), scaled by engagement signal and recency, then normalized and capped.
4. **Incremental vs. full recompute.** On each new engagement event, F1 updates affinity incrementally. On a vocabulary/blog-tag change, F1 fully recomputes affinity for affected users so the projection stays consistent with reality. Both paths converge to the same definition.

If a plan proposes editing user tags directly, or editing blog tags outside F4, it is wrong — flag it.

---

## 7. Shared domain event catalog (the contract spine)

Events are the only cross-context contract. Each carries a stable name, a schema, and an `occurred_at`. Transport is the `EventBusPort` (Postgres outbox initially). Consumers are idempotent (dedupe on event id).

**Auth / user (emitted by F3, consumed by F2):**
- `UserRegistered { user_id, email, is_admin, registered_at }`
- `OtpRequested { subject_user_id?, email, purpose(login|signup), token_ref, expires_at, requested_at }`
- `MagicLinkRequested { email, token_ref, expires_at, requested_at }`
- `PasswordResetRequested { user_id, email, token_ref, expires_at, requested_at }`
  *(`token_ref` is an opaque handle; the code/link itself is never put on the bus.)*

**Content (emitted by F3, consumed by F4 and F2):**
- `BlogPublished { blog_id, slug, title, tag_keys[], category_keys[], series_id?, author_id, published_at }`
- `BlogUpdated { blog_id, changed_fields[], updated_at }`

**Engagement (written by whichever context observes it via `EngagementLogPort`; consumed by F1 for affinity, F2 for segmentation, F4/F3 for KPIs):**
- Engagement is primarily a **log**, not a fan-out event, but the following are also published for real-time consumers:
- `ArticleSaved { user_id, blog_id, catalog_id?, occurred_at }`
- `ArticleCompleted { user_id, blog_id, occurred_at }`
- *(impression/click/dwell/share/comment live in the log; publish more of them only if a real-time consumer needs them.)*

**Vocabulary (emitted by F4, consumed by F1):**
- `TagVocabularyChanged { change_type(create|rename|merge|split|deprecate), affected_tag_keys[], mapping{old→new}, changed_at }`
- `BlogTagsReassigned { blog_id, old_tag_keys[], new_tag_keys[], reassigned_at }`

**Search (emitted by F1; optional consumers):**
- `SearchImpressionLogged { user_id?, query_id, blog_ids[], positions[], shown_at }`

Any new cross-context need = a new event added **here first**, then referenced by the plans.

---

## 8. Shared ports (interfaces every context may depend on)

Signatures are language-neutral contracts (name → inputs → output). Adapters live outside the domain.

- **`EventBusPort`** — `publish(event)`, `subscribe(event_name, handler)`. *Adapter: Postgres transactional outbox + poller.*
- **`JobQueuePort`** — `enqueue(job, run_at?, dedup_key?)`, `claim(worker) -> job`, `ack(job)`, `dead_letter(job, reason)`. *Adapter: Postgres table + `FOR UPDATE SKIP LOCKED`.*
- **`SchedulerPort`** — `register(name, cron_or_interval, timezone)`, `due() -> jobs`. *Adapter: Postgres due-table + poller.*
- **`ObjectStorePort`** — `put(bucket, key, bytes, content_type) -> uri`, `get(uri) -> bytes`, `presign_get(uri, ttl) -> url`. *Adapter: MinIO.*
- **`EngagementLogPort`** — `append(event)`, `aggregate(user_id, window, group_by) -> rows`, `blogs_engaged_by(user_id) -> [{blog_id, type, occurred_at}]`. *Adapter: Postgres append-only table (partitioned by month).*
- **`ClockPort`** — `now()`. **`IdGeneratorPort`** — `new_id()`.
- **`AiTextPort`** — `complete_json(prompt, json_schema, config{model, temperature, api_key}) -> validated_json`. Closed-set validation and abstention handled by the caller. **No embedding method exists on this port.** *Adapter: an LLM HTTP client keyed by the admin API key.*
- **`ExternalSearchPort`** (F1, deferred) — `web_search(query) -> results`, `scholar_search(query) -> results`. *Adapter: Google APIs. PDF/scholar path is out of scope for v1.*

Each context additionally defines its **own** driving ports (use cases) and driven ports (its repositories) inside its file.

---

## 9. Shared data conventions

- IDs are opaque (ULID/UUID via `IdGeneratorPort`); do not leak sequence semantics across contexts.
- All timestamps `timestamptz`, UTC.
- Tag keys match `^[a-z0-9]+(-[a-z0-9]+)*$`; enforce at the boundary.
- The **engagement log** is append-only and partitioned by month; index `(user_id, occurred_at)` and `(blog_id, occurred_at)`.
- Cross-context reads go through a port, never a foreign key into another context's private tables. Shared reference data (blog id, tag key, user id) is passed by value.

---

## 10. Deliverables the plan must produce (applies to every feature session)

When planning a feature, Claude Code must output — **in prose and lists, no code**:

1. **Context map & module layout** — packages for domain / application / adapters; where each port lives.
2. **Port interfaces** — every driving and driven port with method signatures and pre/postconditions.
3. **Domain model & invariants** — entities, value objects, and the rules that must always hold (including §6 where relevant).
4. **SQL migration list** — ordered DDL sketch (tables, indexes, partitions) as raw SQL contracts.
5. **Use-case list** — each with trigger, inputs, steps, outputs, error cases.
6. **Events consumed / emitted** — referencing §7 exactly.
7. **Task breakdown** — ordered, dependency-annotated, each task independently verifiable.
8. **Acceptance criteria / test scenarios** — including cold-start and failure paths.
9. **Risks & open questions** — anything ambiguous, plus the open questions listed in the feature file.

Every plan ends by confirming it honored the §3 constraints and did not touch another context's scope.
