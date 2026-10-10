# Series context — Frontier Models

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** engineers and students who know the Transformer (from `foundational-architectures`
  or elsewhere) and want to read today's model releases and technical reports unaided.
- **Shape:** hybrid. Six family tracks, each a short ladder:
  - decision models, Laya then Jev (1–5) ← FA 12;
  - GPT (6, 7, 8, 12) ← FA 12;
  - the Llama block (9, 10, 11) ← Part 6;
  - DeepSeek (13, 14, 15, opt. 24) ← Part 9;
  - beyond attention (16, 17) ← FA 10;
  - JEPA/CLIP (18–22, opt. 23) ← FA 14.
- **Order is the user's:** the series opens on the System One decision models, Laya first and Jev
  second, then the other families.
- **Shared promise:** trace each mechanism on checkable numbers at tech-report depth, and place each
  model in its lineage, so the reader can find the new 10% in the *next* release themselves.
- **Only disclosed mechanisms are traced.** Jev is covered as a documented contract plus
  outside-measurable claims, never an inferred architecture. The same applies to GPT-4/5/6, Muse Spark
  and every other closed model.
- **Living list.** New parts need a mechanism no part owns, disclosed detail, and a second lab's
  adoption (or a plain one-source caveat). Every part's research opens with a currency check.
- **Category:** `machine-learning` for every part. Settled.

## Part status

`plan.md` holds what each part owns and hands off; this table holds only what has moved.

| # | Slug | Status | # | Slug | Status |
|---|---|---|---|---|---|
| 1 | laya-decision-model-explained | ready | 13 | deepseek-v3-mla-multi-token-prediction | planned |
| 2 | laya-latency-one-pass-no-output-tokens | planned | 14 | deepseek-sparse-attention-v3-2-v4 | planned |
| 3 | laya-calibration-proper-scoring-rules-rlcd | planned | 15 | deepseek-r1-grpo | planned |
| 4 | jev-typesafe-system-one-model | planned | 16 | mamba-selective-state-spaces | planned |
| 5 | decision-models-prompt-injection-escalation | planned | 17 | gated-deltanet-linear-attention-hybrids | planned |
| 6 | gpt-2-decoder-only-transformer-traced | planned | 18 | i-jepa-predicting-representations | planned |
| 7 | scaling-laws-6nd-chinchilla | planned | 19 | v-jepa-2-video-world-model | planned |
| 8 | rlhf-ppo-dpo-derived | planned | 20 | lejepa-sigreg-isotropic-gaussian | planned |
| 9 | llama-modern-transformer-block | planned | 21 | clip-contrastive-infonce | planned |
| 10 | rope-derived-context-extension | planned | 22 | vl-jepa-predicting-embeddings | planned |
| 11 | mixture-of-experts-routing-load-balancing | planned | 23 | vision-language-models-llava-to-native | optional |
| 12 | gpt-oss-architecture | planned | 24 | deepseek-mhc-muon | optional |

Status is `planned`, `researching`, `drafting`, `ready`, or `published`.

## Knowledge established

### Part 1 — laya-decision-model-explained (ready 2026-09-26, not published)

- **Mechanism, from laya 0.3.20's source:** one sequence per question, `[CLS] <type> question:
  <ins> [SEP] ([MASK] opt)×k [SEP] state [SEP]`. The state is tokenized once and copied into every
  row; the rows run as one batch. `usage.input_tokens` counts every copy, and `output_tokens` is 0.
  **"One pass" ≠ "state read once".**
- **Shared ticket traced** (our run, CPU FP32, commit 55cf4c4e): the batch is `[3, 141]`, 399
  input tokens, 264 of them the 88-token ticket. Route: billing logit 4.196, T 1.760 → 0.847.
  Urgency: score 3.331, top level 4 at 0.530. Refund noul: 0.859. The act probability is 1.0 on
  every row. Numbers live in the part's `lab/trace.json`.
- **Head:** type embedding (3×d) added to every position → 2 × `nn.TransformerEncoderLayer`
  (pre-norm, 16 heads, ReLU 4d, no final norm) → gather at markers → scorer LN→Linear→GELU→Linear(d,1)
  → unused slots −1e4 → ÷T by (type, option-count) bucket, clamped 0.5–5 → softmax per question.
- **Parameters:** 394,781,696 backbone (ModernBERT-large; no MLM head in the checkpoint) +
  26,512,131 head = 421,293,827, FP16 on disk. Multilingual: 306,939,648 + 14,969,347 = 321,908,995.
- **Two confidence fields:** `confidence` = 1 − H/ln k for choice and score, max p for noul;
  `answer_confidence` = max p. Route: 0.577 vs 0.847.
- **Act head saturates** (issue #185, reproduced): the `[CLS]` norm goes 35.7 → 10,377.6, with act
  logits about +4,356 / −3,561.
- **Layout budget:** English 512/192. Options shrink from k = 13 and reach 4 tokens (marker + 3) at
  k = 36; the state room is 0 at k = 125 and laya still answers; it raises at 127. 1,024/256: room
  704 at k = 77.
- **Lineage:** UniMC (EMNLP 2022) already used `[O-MASK]` per option in one sequence, followed by
  GLiNER, GLiClass and GLiGuard. Laya's new 10% is the typed contract, the per-question rows, the
  head and RLCD.

## Decisions to preserve

- **Naming.** "Part N" counts within a family (*Laya, Part 1–3*; *Jev, Part 1–2*; *GPT, Part 1–4*;
  *Llama, Part 1–2*; *DeepSeek, Part 1–3*; *JEPA, Part 1–4*). Single-post models carry no part label.
  Slugs never carry a part number. JEPA and Jev are unrelated names; never conflate them.
- **Conventions** inherited from `foundational-architectures/context.md`: MACs with FLOPs = 2 × MACs,
  B × T × d, row vectors, three-way provenance in every caption, and the fixed colour maps. Added
  here:
  - parameters say total vs active, and with or without embeddings;
  - tokens name their tokenizer;
  - context says trained, extended or effective;
  - RoPE names its pairing;
  - benchmarks carry shots, temperature, pass@k and harness;
  - decision-model numbers say *vendor-reported*, *third-party measured* or *our local run*, and
    latency names its hardware and whether the network is included;
  - calibration names its metric, bin count, and raw vs post-temperature.
- **Visual system.** V1–V10 are inherited; V13–V27 are this series' own (see `plan.md`). V16 draws
  per-token architecture arithmetic only, and capacity belongs to nvidia-stack Part 11.
- **Shared examples.** The shared decision example (one support ticket plus three typed questions —
  choice, score, noul — chosen at Part 1) runs through Parts 1–5. One sentence (chosen at Part 6) is
  used for every tokenizer and LLM trace. The foundational Part 12 four-token, d = 8 attention toy is
  reused for GQA, MLA and RoPE.
- **Decision-model facts read from primary sources on 2026-09-26** (re-verify at research):
  - **Jev:** TypeSafe AI, launched 2026-09-15. Hosted only, early access. The architecture, size and
    RLCD objective are undisclosed. Priced at $0.042/MTok input with output free; latency 70–500 ms.
  - **Laya:** Convai Innovations, launched 2026-09-18, Apache-2.0. ModernBERT-large 395M + a 2-layer
    decision head, an option-marker scorer (one `[MASK]` per option, softmax within the question) and
    an act/escalate head (per its own card, "no usable signal yet"), 421M in total.
  - **Laya's three checkpoints:** `laya` (512 ctx), `laya-typed-decisions` (1,024 ctx), and
    `laya-multilingual` (mmBERT-base, 322M, 8,192 ctx).
  - **Laya's RLCD, per its card:** a reported distribution, Gaussian noise on the logits, a reward
    from proper scoring rules (log + spherical, plus RPS for ordinal questions), and REINFORCE with a
    group-mean baseline, using TD(λ = 1) for multi-turn conversations. No training code, data or
    paper.
  - **Laya's calibration and latency, per its card:** ECE 0.213 raw → 0.081 after temperature
    (English). On a T4, one question takes 39.5 ms and ten take 158.6 ms. It exposes the same
    `POST /v1/systemone` shape as Jev.
- **Other scope facts** (secondary; verify per part): Meta retired open Llama for Muse. DeepSeek
  V3.2 = DSA; V4 = CSA/HCA + mHC + Muon (arXiv 2606.19348). Qwen 3.5/3.6 are hybrid Gated
  DeltaNet + MoE. LeJEPA is arXiv 2511.08544; VL-JEPA dates from December 2025 and V-JEPA 2.1 from
  March 2026. gpt-oss is still OpenAI's only open model.

- **Set at Part 1, reuse in Parts 2, 3 and 5:**
  - The **shared ticket and three questions** are fixed in the part's `lab/trace_laya.py` (STATE,
    QUESTIONS): the route choice has billing / technical / account / sales; urgency is a 5-level
    score (0–4); refund is a noul.
  - **Tier B env:** `~/.cache/frontier-models-lab/.venv`, built from the part's
    `lab/requirements.txt`: laya 0.3.20, torch 2.14.0+cpu via `--index-strategy unsafe-best-match`.
    Plain `laya` pulls the CUDA build (+4.5 GB). laya 0.3.20's `load()` cannot pin a revision, so use
    `snapshot_download(revision=55cf4c4e…)` and pass a local path.
  - **Hooks must return None**, or they replace the module's output.
  - **V13 segment colours:** question #5e7a9b, option #b8915a, marker #eb6c36, state #7c8f6f,
    special tokens #2d3142.
  - **Toolchain:** copy the part's `assets/_build.py`, `_figs.py`, `_fig08.py` (Mermaid),
    `_cover.py` and `_social.py`. Figures and cards read `lab/trace.json` directly. Legends use a
    local `key()` with the marks' real opacity.
- **Currency facts at 2026-09-26:**
  - The card was updated 2026-09-24. The multilingual default context is **1,024** (8,192 only
    with `max_len`), not 8,192.
  - A fine-tuning notebook exists, but no RLCD pre-training code and no paper.
  - The card's ECE numbers are inconsistent across sections (0.213/0.144/0.466→0.081). Part 3
    must pin which table and which bin count.

## Open threads

- **Awaiting Checkpoint S** on the revised order: Jev API access (yes/no); promoting FA 18 (BERT) to
  committed; keeping the Llama and JEPA tracks; Tier B labs.
- **Security boundary for Part 5.** Injection demonstrations run on local Laya only, never against
  TypeSafe's service, and show mechanism and mitigation with no operational recipe.
- **Licences.** Laya is Apache-2.0 and clear. JEPA checkpoint licences and the canery.in
  commercial-use question are unresolved.
- **Muse Glimmer.** A candidate part if Meta discloses its architecture.
- **The shared sentence** (Part 6) is not chosen. The shared ticket is fixed; see Decisions.
- **Every hook number** in `plan.md` is unverified until its part's research.
- **`plan.md` corrections Part 1 found, not yet applied (the user's call):**
  - Part 2's hook ("the state is read once, and each extra question adds about 13 ms") is wrong
    about mechanism; each question re-reads the state.
  - Open decision 2 says Laya uses "BERT's masked-token head"; it does not. `[MASK]` is a read-out
    slot for a new scorer.
  - Part 1's "contexts (512, 1,024, 8,192)": the multilingual default is 1,024.
- **Tier B was built for Part 1** on the strength of "create the blog". Checkpoint S never
  formally approved it.
- **Part 1 was built end to end without stopping at Checkpoints A and B.** The user asked for the
  finished post.

## Next part brief

- **Part:** 2 — Laya, Part 2: Why It Answers in Milliseconds (`laya-latency-one-pass-no-output-tokens`).
- **Can assume:** Part 1's `#option-marker-scoring` and `#what-a-decision-model-is`; the per-question
  row layout; the 399-token accounting (link, don't re-derive).
- **Must teach:** the cost model with the **copied state**: N = ΣP_q + n(|s| + 1) tokens, not one
  shared read. Re-fit the card's T4 points (39.5 ms at 1 question, 158.6 at 10, 771 at 50) against
  that model. Cover CPU timing of the shared ticket at 1, 3 and 10 questions; batching limits; the
  context across checkpoints; the multilingual vocabulary share (196,608,000 of 306,939,648 backbone
  parameters are embeddings — verify); and pricing "output is free".
- **Must not repeat:** the head anatomy, the parameter table or the lineage (Part 1); calibration
  (Part 3).
- **Evidence still needed:** the card's latency tables and whether `predict_batch` or the TileLang
  fast path changes per-question cost; the repo's `research/results/latency_cpu_*.json` and
  `length_batching_cpu_*.json` (dated 2026-09-24); mmBERT's efficiency numbers; whether unpadding
  applies on CPU in transformers 5.17 (it does not; Part 1 checked).
- **Handoff:** a `#cost-per-question` anchor for Parts 4 and 5.
