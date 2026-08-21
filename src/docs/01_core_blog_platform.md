# 01 — Core Blog Platform (your Feature 3) — PLANNING PROMPT

> Load `00_foundation_and_shared_contracts.md` with this file. **Plan only; write no code.**
> This context is the base everything else builds on. Keep it strictly self-contained: no ranking, no email, no vocabulary re-ranking logic here (those are F1/F2/F4). This context *produces the data* those features consume.

## Objective
Plan the base platform: stateless auth, single-admin authoring from Markdown, read-only user experience (view, comment, mark, save, recent), and the **engagement log** that F1/F2/F4 depend on. Output must match the "Deliverables the plan must produce" list in the foundation §10.

## Scope

**In scope**
- Authentication: sign up + log in via **OTP** (email code) and **OAuth**; **magic link** optional; **token-based, stateless** (no server-side sessions). Exactly **one admin** account; all other accounts are read-only users.
- Authorization: admin may create/update/delete blogs and reference pins; users may only read + comment + mark + save. Enforce at the application layer via a policy port.
- Blog authoring (admin): upload a **Markdown file** as the blog source → store the raw `.md` in MinIO (`ObjectStorePort`) → parse metadata (title, proposed tags, category, series) → persist blog metadata in Postgres → generate a unique `slug`. Tags provided at publish must be **validated against the canonical vocabulary** (owned by F4) via a read port; publishing with unknown tags either rejects or quarantines them (decide in plan).
- Blog reading: list blogs (paginated) and read a single blog by slug; serve rendered content from the stored Markdown.
- **Markers**: one per user per blog — a saved position/anchor so the user can resume. Create/update/delete.
- **Reference pins** (admin): pointer from one blog to an exact section of another blog; used while authoring and surfaced to F4's overlap detection.
- **Comments**: **one comment per user per blog**, editable and deletable by its author; **replies** allowed (threaded one level or arbitrary depth — decide in plan). Admin moderation (delete any).
- **Catalogs & saves**: a user can save a blog into a catalog; list a user's catalogs and saved blogs.
- **Recent views**: per user, the recently viewed blogs (derive from the engagement log or a small projection).
- **Engagement log**: append-only capture of impression / click / dwell / complete / save / share / comment via `EngagementLogPort` (foundation §8). This is the single source for KPIs, affinity, and segmentation.
- **Admin read models / KPIs**: read-only aggregates for the admin dashboard — most-viewed, trending, by-category, per-blog comment/engagement counts, engagement over time. (Just the data + query contracts; no UI, no charts.)
- Blog organization primitives: `series` and `category` as **non-hierarchical, professionally modeled** groupings (blogs may belong to a series and one or more categories). Tag *hierarchy* itself is F4's concern; here just store category/series membership.

**Out of scope (owned elsewhere — do not implement)**
- Ranking, personalization, query→tag mapping, affinity math → **F1**.
- Canonical vocabulary CRUD, synonyms, tag hierarchy, LLM re-ranking, blog-tag reassignment → **F4**. (This context only *reads* the vocabulary to validate publish-time tags and *emits* `BlogPublished`.)
- Any email sending, templates, consent → **F2**. (This context only *emits* `UserRegistered` and the auth events.)

## Domain model & invariants
- **Blog**: id, slug (unique), title, tag_keys[] (validated), category_keys[], series_id?, author_id (always the admin), markdown_uri (MinIO), status(draft|published), published_at, updated_at.
  - Invariant: `author_id` is always the single admin. Invariant: tag set stable after publish except via F4 (foundation §6) — this context has **no** post-publish tag-edit use case.
- **User**: id, email (unique), is_admin, auth identities (OAuth provider links), created_at. Invariant: at most one `is_admin = true`.
- **Comment**: id, blog_id, user_id, parent_comment_id?, body, created_at, updated_at, deleted_at?. Invariant: unique (blog_id, user_id) for top-level comments (one per user per blog); replies exempt or modeled distinctly — decide and state.
- **Marker**: (user_id, blog_id) unique, anchor/position payload, updated_at.
- **ReferencePin**: id, source_blog_id, target_blog_id, target_anchor, created_by(admin).
- **Catalog / CatalogItem**: catalog(id, user_id, name); item(catalog_id, blog_id, added_at).
- **EngagementEvent** (log): see foundation §8/§9.

## Driving ports (use cases) — signatures & pre/postconditions
Plan these (names indicative):
- `RequestOtp(email, purpose)`; `VerifyOtp(email, code) -> tokens`; `StartOAuth(provider) / CompleteOAuth(provider, code) -> tokens`; `RefreshTokens`, `RevokeTokens`.
- `PublishBlogFromMarkdown(admin, file, metadata) -> blog` — validates tags against vocabulary read port; stores md; emits `BlogPublished`.
- `UpdateBlog(admin, blog_id, patch)` — note: **cannot** change tags here; emits `BlogUpdated`.
- `ListBlogs(filter, page)`, `GetBlogBySlug(slug, viewer?)`.
- `PlaceMarker/UpdateMarker/DeleteMarker(user, blog_id, anchor)`.
- `CreatePin/DeletePin(admin, …)`.
- `CreateComment(user, blog_id, body)`, `UpdateComment`, `DeleteComment`, `ReplyToComment(user, parent_id, body)`.
- `SaveToCatalog(user, blog_id, catalog_id?)`, `ListCatalogs(user)`, `ListRecentViews(user)`.
- `RecordEngagement(...)` (thin wrapper over `EngagementLogPort` used by read/scroll endpoints).
- Admin read models: `TopViewed(window)`, `Trending(window)`, `ByCategory`, `PerBlogKpis(blog_id)`, `EngagementOverTime(window, bucket)`.

## Driven ports
- `BlogRepository`, `UserRepository`, `CommentRepository`, `MarkerRepository`, `PinRepository`, `CatalogRepository` (raw-SQL adapters).
- `VocabularyReadPort` (from F4) — `is_valid_tag(key) -> bool`, `canonical_of(key) -> key?`. Read-only.
- `AuthTokenPort` (issue/verify stateless tokens), `OAuthProviderPort`, `OtpDeliveryPort` (hands the code to F2 via `OtpRequested` — this context does not send email).
- Foundation shared ports: `ObjectStorePort`, `EngagementLogPort`, `EventBusPort`, `ClockPort`, `IdGeneratorPort`.

## Data model (raw SQL DDL sketch — contract, not final)
Plan tables for: `users`, `oauth_identities`, `blogs`, `blog_categories`, `series`, `comments`, `markers`, `reference_pins`, `catalogs`, `catalog_items`, and the shared `engagement_events` (partitioned monthly). Include: unique `blogs.slug`, unique `(comments.blog_id, comments.user_id)` for top-level, unique `(markers.user_id, markers.blog_id)`, partial unique index enforcing a single admin, `GIN` on `blogs.tag_keys` (also used by F1/F4). State every index and why.

## Events consumed / emitted
- Emits: `UserRegistered`, `OtpRequested`, `MagicLinkRequested`, `PasswordResetRequested`, `BlogPublished`, `BlogUpdated`, `ArticleSaved`, `ArticleCompleted` (foundation §7).
- Consumes: none required for v1.

## Acceptance criteria / test scenarios
- OTP and OAuth login both yield valid stateless tokens; no session row exists anywhere.
- Only the admin can publish/update/delete; a user attempting any write is denied by policy.
- Publishing a `.md` stores the raw file in MinIO, persists metadata, generates a unique slug, validates tags against the vocabulary, and emits `BlogPublished` exactly once.
- A user can hold exactly one comment per blog, edit and delete it, and reply to others; uniqueness is enforced at the DB.
- One marker per user per blog; updating moves it.
- Engagement events land in the append-only log with position/dwell where applicable; recent views and KPIs derive from it.
- Admin KPI queries return correct most-viewed / trending / by-category / over-time aggregates on seed data.

## Open questions to resolve in the plan
1. Reply depth: single-level threads vs. arbitrary depth.
2. Publish-time unknown tags: reject vs. quarantine-until-vocabulary-approves.
3. Marker anchor representation (character offset vs. heading/section id vs. serialized range).
4. Trending definition (reuse the freshness/decay shape F1 defines, or a simple velocity window) — pick one and keep it consistent with F1.
