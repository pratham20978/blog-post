# 04 — Email Pipeline (your Feature 2) — PLANNING PROMPT

> Load `00_foundation_and_shared_contracts.md` with this file. **Plan only; write no code.**
> This is the most independent context. It consumes events from F3 and reads segmentation data; it emits nothing the others depend on. **No Redis/broker assumed** — queue, scheduler, and event bus are Postgres-backed ports (foundation §3/§8). The LLM is used **only** for blog-notification content, via `AiTextPort`, constrained JSON, **no embeddings** (foundation §3).

## Objective
Plan an admin-controlled, event-driven email subsystem with four first-class email types, AI-generated blog notifications inside locked templates, dynamic segmentation, consent/suppression/preferences, and deliverability by default. Output must match foundation §10.

## Scope

**In scope**
- **Event-driven pipeline**: domain events / scheduler triggers → **decision/rules engine** (resolve audience/segment, check consent + preferences + quiet hours, throttle/dedupe, aggregate digests) → **template + merge** → **delivery workers** (per-stream queues) → **providers** → **webhook ingest + analytics**. Keep decision and delivery split (deterministic, testable decisions; pluggable delivery).
- **Four email types**, each with its own consent basis, provider stream, and config:
  1. **Transactional** (login/signup): welcome, verification, password reset, **OTP**, magic link. Triggered by F3 auth events (`OtpRequested`, etc.). Latency-critical; no marketing unsubscribe; keep strictly transactional.
  2. **Personalized**: behavioral or admin-initiated campaigns to a segment; per-user merge data (tags, recent activity, follows).
  3. **Daily digest**: scheduled per user timezone; aggregates new relevant content since last send; skip if below a min-content threshold.
  4. **Blog notification** (new/latest posts): triggered by `BlogPublished` (real-time or batched) to **all users / a segment / the confirmed follow-updates list**; **AI-generated** summary inside a **locked** template.
- **AI content for blog emails only** (via `AiTextPort`): the model fills **schema-constrained JSON** (headline, intro, per-post blurb, CTA), **grounded strictly on real post metadata** (title, excerpt, author, topics, canonical URL), low temperature, links must equal input URLs, abstention allowed. **Validation**: JSON schema + grounding/link check; self-heal retry once; on repeated failure or outage **fall back to a deterministic template** (raw title + excerpt) so the pipeline never blocks. Optional human approval (ON initially, then sampled). Full audit in `ai_generations`. **No embeddings.**
- **Segmentation engine**: a segment = a boolean rule tree (JSONB) over user attributes, tags, follows, and **activity aggregates** (rolling 7/30/90-day counts precomputed from the engagement log). Operators: equals/in/not-in/contains/≥/≤/between/exists/within-last-N-days; nested AND/OR/NOT. **Dynamic** (re-evaluated at send) vs **static** (snapshot) segments. Live count + preview before send. Evaluate via raw SQL against Postgres.
- **Consent, suppression, preferences**: append-only immutable `consent_records`; a `suppression_list` checked before **every** send; a preference center (types/frequency/quiet hours); **double opt-in** for the follow-updates list.
- **Two provider streams behind one port**: `EmailProviderPort` with a **transactional** adapter and a **bulk/marketing** adapter (separate subdomains/IP pools conceptually). Provider-agnostic so streams can be swapped/failed over. (Do not name a specific vendor per foundation §3; the plan defines the port and two adapter roles.)
- **Delivery reliability**: per-stream queues via `JobQueuePort`; **idempotency key** per intended send (e.g. `campaign:{id}:user:{id}` / `otp:{user}:{request}`) checked against `send_events` before sending (at-least-once queues → dedupe mandatory); retries with exponential backoff + jitter; classify transient vs permanent; **dead-letter queue** that is monitored and replayable from the admin panel.
- **Webhook ingest + analytics**: verify signatures; return 200 fast, process async; idempotent on duplicate events; update `send_events`/`email_events`; sync suppression; power per-campaign / per-user / deliverability dashboards (delivered/open/click/bounce/complaint/unsubscribe). Treat open rate as directional.
- **Deliverability defaults**: SPF/DKIM/DMARC alignment guidance; RFC 8058 one-click unsubscribe on marketing mail; complaint-rate monitoring with alert/auto-pause thresholds; warm-up ramp steps built into the scheduler; list hygiene (validate at signup, suppress on hard bounce). *(These are requirements the plan must encode as config/checks, not code to write now.)*
- **Admin control surface (contracts only, no UI)**: providers/domains + per-type stream routing; templates (versioned, merge-field schema, preview/test-send); segments (rule builder inputs, live count); campaigns (type, template, audience, AI config, schedule, approval, start/pause/cancel); AI content studio (prompt version, guardrails, review/approve/reject); schedules; subscribers & consent; analytics; roles/audit.

**Out of scope (owned elsewhere)**
- Generating OTP codes / auth tokens, blog CRUD, the engagement log's primary writes → **F3** (this context *consumes* `OtpRequested`/`BlogPublished`/`UserRegistered` and *reads* aggregates).
- Ranking/affinity → **F1** (email may *read* affinity/tags for targeting but does not compute them).
- Vocabulary → **F4**.

## Domain model & invariants
Plan entities: `email_templates` + `email_template_versions` (immutable versions, one active, merge-field schema), `segments` (+ `segment_members` for snapshots), `campaigns`, `scheduled_jobs`, `send_events` (idempotency anchor), `email_events` (append-only webhook log), `suppression_list`, `consent_records` (immutable), `preferences`, `ai_generations` (audit), `update_subscribers` (double-opt-in follow list).
- Invariant: **no send without** (a) a suppression check and (b) for marketing types, a valid consent/soft-opt-in record.
- Invariant: **every intended send has a unique idempotency key**; a retried job never double-sends.
- Invariant: transactional stream is never blocked behind a bulk campaign (separate queues).
- Invariant: AI output is schema-valid and grounded, or the deterministic fallback is used; raw HTML from the model is never sent.

## Driving ports (use cases)
- `HandleAuthEmail(event)` (transactional; immediate).
- `PublishBlogNotification(trigger, audience)` → per-recipient AI content → validate → render → enqueue.
- `RunDailyDigest(schedule_tick)` (aggregate → render → enqueue; skip empties).
- `RunPersonalizedCampaign(campaign_id)`.
- `EvaluateSegment(definition) -> { count, sample }` and `MaterializeSegment`.
- Template: `CreateTemplateVersion`, `PublishTemplateVersion`, `PreviewTemplate`, `TestSend`.
- AI: `GenerateBlogEmailContent(post_ids, recipient_ctx) -> validated_json`, `ReviewAiDraft`, `ApproveAiDraft/RejectAiDraft`.
- Consent/subs: `StartFollowOptIn`, `ConfirmFollowOptIn` (double opt-in), `RecordConsent`, `Unsubscribe`, `UpdatePreferences`.
- Ops: `ReplayDeadLetter`, `PauseCampaign`, `IngestWebhook(payload)`.

## Driven ports
- `EmailProviderPort` (two adapters: transactional, bulk). `TemplateRenderPort` (merge-field validated render → HTML + plaintext). `AiTextPort` (foundation §8; constrained JSON; no embeddings).
- `SegmentRepository`, `CampaignRepository`, `TemplateRepository`, `ConsentRepository`, `SuppressionRepository`, `PreferenceRepository`, `SubscriberRepository`, `SendEventRepository`, `EmailEventRepository`, `AiGenerationRepository` (raw SQL).
- `UserReadPort` / `AffinityReadPort` (from F3/F1) for targeting merge data. `BlogReadPort` (from F3) for grounding.
- Foundation shared ports: `EventBusPort` (subscribe to F3 events), `JobQueuePort`, `SchedulerPort`, `ClockPort`, `IdGeneratorPort`.

## Data model (raw SQL DDL sketch)
Plan the tables above with: unique `send_events.idempotency_key`, unique `suppression_list.email_normalized`, append-only `consent_records` and `email_events`, JSONB `segments.definition`, and indexes for segment evaluation over precomputed activity aggregates (rolling counts derived from `engagement_events`). Include the Postgres-backed queue/outbox/due-jobs tables (or reference the foundation adapters).

## Events consumed / emitted
- Consumes: `OtpRequested`, `MagicLinkRequested`, `PasswordResetRequested`, `UserRegistered`, `BlogPublished` (foundation §7); reads engagement aggregates for segmentation.
- Emits: none that other contexts depend on (internal delivery/analytics only).

## Acceptance criteria / test scenarios
- Auth email (OTP) sends within seconds on `OtpRequested`, on the transactional stream, never behind a bulk campaign.
- A blog notification generates AI content that is schema-valid and grounded (every link equals an input URL); an injected adversarial post body cannot change links or inject instructions; on repeated AI failure the deterministic fallback sends.
- No marketing send occurs to a suppressed address or without a consent/soft-opt-in record; double opt-in moves a follower to `confirmed`.
- A retried delivery job (simulated at-least-once) does not double-send (idempotency verified).
- Dead-lettered jobs are replayable from the admin contract; webhook ingestion is idempotent and updates suppression + analytics.
- Dynamic vs static segments evaluate correctly with a live count; a control/holdout option exists.
- No embeddings/vectors anywhere; no Redis dependency (queue/scheduler are Postgres-backed).

## Open questions to resolve in the plan
1. Human-approval default duration before switching to sampled review.
2. Digest min-content threshold and per-timezone scheduling granularity.
3. Blog-notification batching window (real-time per `BlogPublished` vs. batched roundup).
4. Whether the two provider adapters are two vendors or one vendor with two streams (kept behind the port either way).
5. Retention windows for `email_events`, `consent_records`, and raw activity used in segmentation.
