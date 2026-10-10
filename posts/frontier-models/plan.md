# Series plan — Frontier Models

**Slug:** frontier-models · **Shape:** hybrid (six family tracks, each a short ladder, each rooted
in one Foundational Architectures part) · **Parts:** 24 (22 committed, 2 optional) · **Category:**
`machine-learning` for every part

## Why this is a series and not one post

"How today's models work" is not one subject. It is six families, and each has its own prerequisite
seam:

- **Decision models** (Laya, Jev) need the encoder-only Transformer.
- The **GPT line** needs the decoder-only Transformer.
- The **Llama block** needs GPT-2's block to be the thing it changes.
- **DeepSeek's** attention needs grouped-query attention to be the thing it compresses.
- **Mamba and DeltaNet** need recurrence.
- **JEPA and CLIP** need the Vision Transformer.

Inside a family, one model can outgrow a post. Laya has three posts, Jev two, GPT four, JEPA four,
and DeepSeek three plus one optional. Budgeted as one article, the twenty-two committed parts come
to about 178,000 words and 278 figures.

**Shape: hybrid.** Six tracks, each a short ladder. Each track's entry part assumes one part of
`foundational-architectures` (or an earlier entry of this series), never a different track's middle.
A reader who only wants JEPA starts at Part 18 and needs ViT, not GPT.

| Track | Parts | Entry assumes |
|---|---|---|
| Decision models (System One): Laya, then Jev | 1, 2, 3, 4, 5 | Foundational Architectures Part 12 (Transformer, Part 1) |
| GPT line | 6, 7, 8, 12 | Foundational Architectures Part 12 |
| The Llama block and its successors | 9, 10, 11 | Part 6 |
| DeepSeek | 13, 14, 15 (+ optional 24) | Part 9 (GQA); Part 15 assumes Part 8 (PPO) |
| Beyond attention | 16, 17 | Foundational Architectures Part 10 (LSTM) |
| Representation learning: JEPA and CLIP | 18, 19, 20, 21, 22 (+ optional 23) | Foundational Architectures Part 14 (ViT) |

## Why the series opens on decision models

The user asked for this order: Laya first, then Jev, then everything else. The order is also right
on its merits:

- **Decision models are this month's new shape of model.** TypeSafe AI launched Jev, a hosted
  "System One" model, on 2026-09-15. Three days later, on 2026-09-18, Convai Innovations answered
  with Laya: the same category, open weights under Apache-2.0. Search interest is live now and will
  not wait for the rest of the series.
- **Laya first, because Laya is traceable.** It is open and small (421M parameters, ModernBERT-large
  plus a decision head), so the whole mechanism can be traced on a laptop CPU, number by number.
  That is this series' standard.
- **Jev second, because Jev is not traceable.** Its architecture, size and training objective are
  undisclosed. A reader who has seen Laya's internals can read Jev's contract and claims precisely —
  knowing which parts are the category, and which are TypeSafe's secret. Starting with Jev would mean
  teaching the category from a black box.
- **The rest follows.** GPT, Llama, DeepSeek, Mamba/DeltaNet, JEPA and CLIP come after, as planned.

## Why this is a separate series from Foundational Architectures

The seam is stability. The foundational series can be finished and stay true. This one goes stale
in months — the scope checks on 2026-09-26 found all of the following:

- **Decision models** arrived in one week in September 2026: Jev on 09-15 and Laya on 09-18.
- Meta **retired the open Llama line**. Muse Spark (April 2026) is proprietary, and Muse Glimmer
  (August 2026, 30B, Apache-2.0) is distilled from it.
- DeepSeek shipped **V3.2** (DeepSeek Sparse Attention) and **V4** (compressed sparse attention,
  manifold-constrained hyper-connections and the Muon optimiser, 1M context).
- **Qwen 3.5 and 3.6** made hybrid Gated-DeltaNet stacks mainstream.
- The JEPA line added **LeJEPA** (November 2025), **VL-JEPA** (December 2025) and **V-JEPA 2.1**
  (March 2026).
- **gpt-oss** (August 2025) is still OpenAI's only open-weight model since GPT-2.

Laya's model card and TypeSafe's launch post were read directly. Everything else came from secondary
coverage and set scope only. Every fact is re-verified against the primary source when its part is
researched.

## The angle

The saturated ground is the release-week post. "What's new in model X" is written within days of a
launch from the press release and a benchmark table. It rarely touches the mechanism with numbers,
and it cannot place the model in a lineage, because it covers one model. The decision-model launch
is already drawing exactly these posts: explainers built from TypeSafe's announcement, most calling
Jev "unable to hallucinate" without saying what that guarantee does and does not cover.

This series owns the reverse. **Every part traces the mechanism on numbers the reader can check,
at the depth of the technical report, reconciled against the published configuration.** Examples:
the option-marker softmax inside Laya, the proper scoring rule behind its calibration, per-token
cache arithmetic, routing on real gate values, RoPE wavelengths against a context window, GRPO
advantages on a real group of answers. Every part also places its model in the lineage — what it
inherits, and which 10% is new — so the reader can open the *next* tech report and find the new 10%
themselves. That second capability is the series' real promise, because the model list will keep
changing.

**Only disclosed mechanisms are traced.** GPT-4, GPT-5, Muse Spark and other closed models publish no
architecture, and this series does not infer one. **Jev is the one deliberate exception to the
model list, and not to the rule:** it has two parts because the user asked for it and the category
needs it. Those parts cover Jev's documented contract, its disclosed and vendor-reported claims, and
what can be measured from outside. They never contain an inferred architecture, and never the
sentence "Jev works like Laya".

## How this series grows

The model list is a living one. A new family gets a part only when all three hold:

1. It introduces a **mechanism no existing part owns**. A new model that reuses MLA and MoE is an
   instance inside Parts 11 and 13, not a new part.
2. Its architecture and training are **disclosed well enough to trace with numbers**: a technical
   report plus a configuration, or open weights. (Jev fails this and is covered as a contract; see
   above.)
3. The mechanism has been **reproduced or adopted by a second lab** — or the part says plainly that
   it has one source behind it, as the ML playbook requires. The decision-model category passes:
   two labs in one week, plus community reproductions.

Each part's research opens with a **currency check**: is there a newer version of this family, and
has anything superseded the mechanism? For the decision models that check is urgent, since the
category is days old and Laya's card itself says its act/escalate head "carries no usable signal
yet". Versions and dates are pinned per part at research time, never in this plan.

Candidates at the 2026-09-26 check, none yet a part:

- Muse Glimmer (architecture disclosure unknown).
- Qwen 3.5/3.6 (an instance in Part 17 unless they add a mechanism).
- Kimi, GLM and Ling (adopters of MLA, MoE and linear attention — instances).
- Further open System One reproductions (instances inside Parts 1–5 unless they add a mechanism).

## Naming: "Part 1" belongs to the model family

The same rule as Foundational Architectures. `series_position` is the reading order and never
appears in a title. "Part N" appears only when one family spans several posts, and it counts within
that family:

- *Laya, Part 1–3*
- *Jev, Part 1–2*
- *GPT, Part 1–4*
- *Llama, Part 1–2*
- *DeepSeek, Part 1–3*
- *JEPA, Part 1–4*

Single-post models (Mixture of Experts, Mamba, Gated DeltaNet, CLIP) carry no part label. Slugs never
carry a part number.

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | say what a decision model returns that an LLM in JSON mode and a fine-tuned classifier do not | 1 |
| 2 | trace a state and three typed questions through Laya to per-option probabilities | 1 |
| 3 | reconcile Laya's 421M parameters as backbone plus decision head | 1 |
| 4 | estimate from arithmetic why one encoder pass answers in tens of milliseconds, and where batching stops helping | 2 |
| 5 | say what the multilingual checkpoint's vocabulary costs in parameters | 2 |
| 6 | compute ECE and a Brier score by hand and fit a temperature | 3 |
| 7 | explain why rewarding a strictly proper scoring rule makes honest probabilities the optimal policy | 3 |
| 8 | say what TypeSafe discloses about Jev, what it does not, and which of its claims can be checked from outside | 4 |
| 9 | explain why a typed output can still be steered by text injected into the state, and what mitigates it | 5 |
| 10 | choose an act-vs-escalate confidence threshold from a risk–coverage curve | 5 |
| 11 | decide between a decision model, an LLM and a trained classifier for a given task | 5 |
| 12 | trace a string through GPT-2 to a next-token distribution and name every tensor | 6 |
| 13 | account for GPT-2's 124M parameters and say why a third are one table | 6 |
| 14 | predict what temperature, top-k and top-p do to one real distribution | 6 |
| 15 | derive C ≈ 6ND and say what it leaves out | 7 |
| 16 | allocate a compute budget between parameters and tokens from a fitted scaling law | 7 |
| 17 | explain why Kaplan and Chinchilla disagreed | 7 |
| 18 | derive the DPO loss from the KL-regularised RLHF objective | 8 |
| 19 | say what each stage of InstructGPT contributes and what it costs in memory | 8 |
| 20 | list every change from GPT-2's block to Llama's and say what each buys | 9 |
| 21 | compute a GQA model's per-token cache from its configuration | 9 |
| 22 | prove RoPE's relative-position property | 10 |
| 23 | explain PI, NTK-aware scaling, YaRN and Llama 3.1's scaling as re-mappings of one spectrum | 10 |
| 24 | compute routing, load and auxiliary loss for a toy MoE by hand | 11 |
| 25 | tell active from total parameters for any MoE configuration | 11 |
| 26 | explain attention sinks and banded attention in gpt-oss | 12 |
| 27 | encode and decode one MXFP4 block | 12 |
| 28 | derive MLA's cache saving and why RoPE needs a decoupled key | 13 |
| 29 | say what multi-token prediction adds to training | 13 |
| 30 | compare dense, sliding, NSA, DSA and V4 attention on one mask grid and one cost model | 14 |
| 31 | compute GRPO advantages and loss for a group of answers | 15 |
| 32 | say which GRPO normalisations were shown to bias it | 15 |
| 33 | discretise an SSM and show its recurrence and convolution forms agree | 16 |
| 34 | say why selectivity breaks the convolution form and how the scan restores parallelism | 16 |
| 35 | show why the delta rule retrieves an overwritten value where linear attention cannot | 17 |
| 36 | explain why hybrid stacks keep a few full-attention layers | 17 |
| 37 | place any self-supervised method in the contrastive / generative / joint-embedding taxonomy | 18 |
| 38 | say what collapse is and how I-JEPA's asymmetry avoids it | 18 |
| 39 | tokenise a video into tubelets and plan in latent space with CEM | 19 |
| 40 | explain why an isotropic Gaussian is LeJEPA's target and compute an Epps–Pulley statistic | 20 |
| 41 | compute CLIP's symmetric InfoNCE loss on a small batch by hand | 21 |
| 42 | say what changes when a VLM predicts an embedding instead of tokens | 22 |

## Parts

Every "Hook" number is from memory, from Laya's model card, from TypeSafe's launch post, or from the
2026-09-26 scope check, and **must be verified against the primary source at research time**. A hook
whose number fails verification is rewritten, never bent. Primary sources for Parts 1–5 are the
vendors' own documents: every claim in them is labelled *vendor-reported* unless our local Laya run
reproduces it.

### 1 · Laya, Part 1 — What a Decision Model Is, Traced Through Laya

- **Slug:** laya-decision-model-explained
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 8,500 · **Figures:** 14
- **Hook:** Laya answers "which team should handle this ticket?" without writing a single word. Every
  option gets its own `[MASK]` token, and the answer is a softmax over those tokens.
- **Answers:** what is a "System One" decision model, how does Laya turn a piece of state and a list
  of typed questions into calibrated option probabilities in one forward pass, and how is that
  different from an LLM in JSON mode or a fine-tuned classifier?
- **Assumes:** Foundational Architectures Part 12's encoder block (`#the-encoder-block`). BERT's
  masked-token prediction is restated in three sentences, because Foundational Architectures Part 18
  is still optional — see *Open decisions*.
- **Owns (math):** the decision-model contract (state + typed questions → a distribution over
  pre-declared options); the three question types (choice, score, noul/boolean); option-marker
  scoring, where each option is scored at its own `[MASK]` and softmaxed within its question; the
  2-layer decision head and the act/escalate head; the ModernBERT backbone's changes from BERT
  (RoPE, GeGLU, alternating local/global attention, unpadding) as *use only*, with derivations left to
  Parts 9, 10 and 12; 421M reconciled as 395M backbone + head; the three checkpoints and their
  contexts (512, 1,024, 8,192).
- **Hands off:** latency and deployment to Part 2; calibration and RLCD training to Part 3; Jev to
  Part 4; failure modes to Part 5.
- **Worked example:** **the series' shared decision example** — one support ticket as state, with
  three typed questions: a choice among four routes, a 1–5 urgency score, and a true/false "asks for
  a refund". It is traced through the open `laya` checkpoint on CPU: the token count, the `[MASK]`
  position of every option, the backbone and head output shapes, every option's logit, each
  question's softmax, and the returned JSON.
- **Signature figures:** V13-variant token strip with state, question and option-marker segments
  coloured and each `[MASK]` flagged; V10 Laya's anatomy (backbone → decision head → option scorer →
  per-question softmax) with shapes on every edge; V25 decision readout (per-question option
  probabilities, measured); V14 parameter accounting, backbone vs head; V10 decision model vs LLM
  JSON mode vs classifier, side by side.
- **Traps:**
  - The three checkpoints differ in backbone and context length.
  - Laya's own card says the act/escalate head "carries no usable signal yet".
  - "Jev-compatible" means the same `POST /v1/systemone` request and response shape — not the same
    model or weights.
  - Laya is Convai's model, not TypeSafe's.
- **Key sources:** Convai Innovations 2026, Laya model card and checkpoints (Hugging Face
  `convaiinnovations/laya`, `laya-multilingual`, `laya-typed-decisions`); the author's write-up
  linked from the card; Warner et al. 2024 (ModernBERT, arXiv 2412.13663); Devlin et al. 2019
  (NAACL, BERT).
- **Search intent:** "laya decision model", "what is a decision model ai", "system one model", "laya
  vs jev", "decision model vs llm"

### 2 · Laya, Part 2 — Why It Answers in Milliseconds: One Pass, No Output Tokens

- **Slug:** laya-latency-one-pass-no-output-tokens
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Hook:** on a T4, one question costs Laya 39.5 ms and ten questions cost 158.6 ms, not 395. The
  state is read once, and each extra question adds about 13 ms.
- **Answers:** where does a decision model's speed come from, what does each extra question cost, and
  what does a laptop CPU actually do with it?
- **Assumes:** Part 1's option-marker scoring (`#option-marker-scoring`).
- **Owns (math):**
  - the cost model of one encoder pass over state + questions, against an LLM that decodes k answer
    tokens sequentially;
  - the fixed-plus-per-question latency fit from the card's own two points (39.5 = a + b and
    158.6 = a + 10b give a ≈ 26.3 ms and b ≈ 13.2 ms — verify);
  - where batching stops helping;
  - context length against cost across the three checkpoints;
  - the multilingual checkpoint's vocabulary share of its 322M parameters (mmBERT, 256k vocabulary —
    computed at research);
  - pricing arithmetic for "output tokens are free".
- **Hands off:** calibration to Part 3; KV caching and decoder serving to nvidia-stack Parts 11–12.
- **Worked example:** the shared ticket timed on this machine's CPU at 1, 3 and 10 questions, with the
  measured fixed and per-question costs set beside the card's T4 numbers. The CPU run is measured and
  labelled, and the T4 numbers are reported, never mixed.
- **Signature figures:** latency decomposition bars (reported T4 vs our measured CPU); cost against
  output length k for encoder vs decoder (exact, labelled as a model); V14 multilingual parameter
  accounting with the embedding share highlighted.
- **Traps:**
  - The "33 ms" headline is the multilingual checkpoint (32.8 ms); English is 39.5 ms.
  - Convai's "Jev 236–276 ms p50" is a hosted, over-the-network figure set against local inference,
    so it is not like-for-like.
  - The MLX and ONNX ports are community projects, not Convai releases.
  - T4 ≠ our CPU.
- **Key sources:** Laya model card (latency table); Warner et al. 2024 (ModernBERT efficiency:
  unpadding, local/global attention); the mmBERT paper (pinned at research); community ports
  `laya-onnx`, `laya-mlx` and `receptron/laya`, labelled as independent.
- **Search intent:** "laya latency", "run laya locally", "laya multilingual", "encoder vs decoder
  inference latency"

### 3 · Laya, Part 3 — Calibrated by Construction: Proper Scoring Rules and RLCD, Derived

- **Slug:** laya-calibration-proper-scoring-rules-rlcd
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Hook:** before temperature scaling, Laya's expected calibration error is 0.213. After one learned
  scalar it is 0.081. The training objective behind it rewards the model for reporting exactly what
  it believes.
- **Answers:** what does "calibrated" mean as a number, why does rewarding a strictly proper scoring
  rule make honest probabilities the best policy, and what exactly is RLCD as Convai describes it?
- **Assumes:** Part 1's per-question softmax (`#option-marker-scoring`).
- **Owns (math):**
  - calibration and reliability diagrams; ECE and its binning dependence;
  - the Brier score and its decomposition; negative log-likelihood;
  - temperature scaling as a one-parameter fit;
  - strictly proper scoring rules — log, spherical, and the ranked probability score for ordinal
    questions — with the proof that the expected score is maximised by the true distribution;
  - RLCD as Laya's card discloses it: the policy reports a distribution, exploration adds zero-mean
    Gaussian noise to the logits, and the reward is a proper scoring rule, updated by REINFORCE with a
    group-mean baseline and TD(λ = 1.0) for multi-turn conversations;
  - why "cannot hallucinate" is a *format* guarantee, not a correctness guarantee.
- **Hands off:** PPO to Part 8 and GRPO's clipped, standardised objective to Part 15, both of which
  link back here for REINFORCE with a group baseline; selective prediction and escalation thresholds
  to Part 5.
- **Worked example:** ten decisions with confidences and true outcomes, binned by hand into a
  reliability table, with ECE and Brier computed and a temperature fitted by grid search on NLL. Then
  one RLCD step: four noisy reports for one question, each scored by the log rule, with the group-mean
  baseline, the advantages and the direction of the REINFORCE gradient printed.
- **Signature figures:**
  - V26 reliability diagrams, raw vs temperature-scaled: reported ECE plus our own measured diagram
    on a small labelled set.
  - V20 scoring-rule geometry: expected log, spherical and Brier scores against the reported
    probability, when the true probability is 0.7, each peaking at 0.7 (exact).
  - V20 the RLCD group of four noisy reports with rewards and baseline, as small multiples.
- **Traps:**
  - ECE changes with the number of bins.
  - Raw and post-temperature numbers are different claims.
  - This RLCD is **Convai's description of its own training**. TypeSafe's RLCD is undisclosed, and
    the two may differ.
  - No training code or data is released, so the derivation is of the objective as described, not
    of verified code.
- **Key sources:** Laya model card (RLCD description, calibration table); Guo et al. 2017 (ICML, on
  calibration of modern networks); Naeini, Cooper & Hauskrecht 2015 (AAAI, ECE); Brier 1950 (Monthly
  Weather Review); Gneiting & Raftery 2007 (JASA, strictly proper scoring rules); Epstein 1969 (ranked
  probability score); Williams 1992 (Machine Learning, REINFORCE).
- **Search intent:** "rlcd reinforcement learning calibrated decisions", "expected calibration
  error", "proper scoring rule", "temperature scaling calibration"

### 4 · Jev, Part 1 — The Closed Original: What TypeSafe Discloses, and What It Doesn't

- **Slug:** jev-typesafe-system-one-model
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,500 · **Figures:** 7
- **Hook:** Jev charges $0.042 per million input tokens and nothing for output, because it produces
  no output tokens at all.
- **Answers:** what is Jev, what exactly does TypeSafe promise about it, and which of those promises
  can a reader check from outside?
- **Assumes:** Part 1's decision-model contract (`#what-a-decision-model-is`).
- **Owns:**
  - the "System One" naming and what the Kahneman analogy does and does not claim;
  - Jev's typed primitives (Choice, Score, Noul) and request shape as TypeSafe's docs define them;
  - "questions evaluated in isolation against shared state, in one pass";
  - RLCD as TypeSafe names it (the objective is undisclosed);
  - the pricing and latency claims (70–500 ms) worked through the contract that produces them;
  - the vendor's workflow benchmarks and their stated caveats;
  - the third-party comparisons in Laya's card (Jev ahead on soft accuracy and high-cardinality
    options; Laya faster).
  This is a map of disclosed vs undisclosed, not an architecture.
- **Hands off:** failure modes and the decision guide to Part 5.
- **Worked example:** the shared ticket written as a Jev request in TypeSafe's documented schema, with
  the response shape it promises and the request's price computed from published rates beside an
  LLM's input-plus-output price. If the user provides early-access API credentials, the real response
  is captured and labelled; otherwise the example is the documented shape only.
- **Signature figures:** a containment figure of the contract — documented inputs and outputs outside
  the box, "undisclosed" inside it (placed); latency ranges with provenance — TypeSafe-reported,
  Convai-measured, and Laya on T4 (chart); per-request cost against output length (computed from
  published prices).
- **Traps:**
  - The architecture, size, training data and RLCD objective are undisclosed. Say so, and infer
    nothing.
  - Benchmarks run on TypeSafe's own workflows against GPT-6 Astra and Fable 5.1 are self-reported,
    with the vendor's own bias caveat.
  - Early access only.
- **Key sources:** TypeSafe AI 2026, "Introducing System One Models & Jev" and `docs.typesafe.ai`;
  the Laya model card's comparison table (third-party measured); Willison 2026 (commentary tier);
  Kahneman 2011 (*Thinking, Fast and Slow*, for the naming only).
- **Search intent:** "what is jev ai", "typesafe jev", "jev system one model", "jev pricing"

### 5 · Jev, Part 2 — Where Decision Models Break, and When to Use One Instead of an LLM

- **Slug:** decision-models-prompt-injection-escalation
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,000 · **Figures:** 12
- **Hook:** a decision model can only answer from the options you list. Text hidden in the state can
  still choose which one it picks.
- **Answers:** how do typed decision models fail — injected instructions, distribution shift,
  confidently wrong answers — how do you set the threshold where a decision is escalated to a human,
  and when is a decision model the wrong tool?
- **Assumes:** Part 3's calibration (`#calibration`).
- **Owns (math):**
  - prompt injection against a typed model, explained as mechanism and defence (Check Point's findings
    on Jev, reproduced on a local Laya only);
  - the trust boundary between instructions and state;
  - calibration under distribution shift;
  - selective prediction — risk–coverage curves and choosing a confidence threshold for act vs
    escalate;
  - the decision guide: decision model vs LLM vs a classifier trained for a fixed label set.
- **Hands off:** nothing downstream in this track. GPT (Part 6) begins the next.
- **Worked example:** one injected sentence appended to the shared ticket flips Laya's route
  decision, with the probabilities before and after printed. A mitigation is applied and re-measured.
  Then a small labelled set gives a risk–coverage curve, and a threshold is chosen from it.
- **Signature figures:** V25 decision readouts before and after injection (measured, local Laya); a
  trust-boundary containment figure (placed); V27 risk–coverage curve with the chosen threshold
  (measured); a decision-guide quadrant (placed).
- **Traps:**
  - Every demonstration runs against the local open model, **never against TypeSafe's hosted
    service**.
  - Mechanism and mitigation only — no operational attack recipe (the security playbook).
  - Calibration is not robustness.
- **Key sources:** Check Point Research 2026 (prompt injection against Jev); Greshake et al. 2023
  (AISec, indirect prompt injection); Geifman & El-Yaniv 2017 (NeurIPS, selective classification);
  Ovadia et al. 2019 (NeurIPS, calibration under shift); OWASP Top 10 for LLM Applications (prompt
  injection).
- **Search intent:** "decision model prompt injection", "when to use a decision model vs llm",
  "confidence threshold escalation", "jev security"

### 6 · GPT, Part 1 — The Decoder-Only Transformer, Traced Through GPT-2

- **Slug:** gpt-2-decoder-only-transformer-traced
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 8,500 · **Figures:** 14
- **Hook:** GPT-2 small has 124 million parameters, and almost a third of them are one lookup table:
  the token embedding, which the model reuses as its output layer.
- **Answers:** what happens, tensor by tensor, between a string entering GPT-2 and the next token
  leaving it — and what changed from GPT-1 to GPT-3?
- **Assumes:** Foundational Architectures Part 12 (`#multi-head-attention`), restated in four
  sentences. Contrasts with Part 1's encoder-only decision model by link.
- **Owns (math):** byte-level BPE merges; token and learned position embeddings; the causal mask;
  GPT-2's Pre-LN block with a final LayerNorm; weight tying; next-token cross-entropy and perplexity;
  temperature, top-k and top-p as operations on one logit vector; the GPT-1 → 2 → 3 changes (context
  512/1024/2048, GPT-3's alternating dense and banded sparse layers); the 124M count reconciled.
- **Hands off:** scaling to Part 7; post-training to Part 8; the modern block to Part 9; KV-cache
  memory to nvidia-stack Part 11.
- **Worked example:** **the series' shared sentence** (chosen at this part's research), tokenised by
  GPT-2's BPE and pushed through real GPT-2 small on CPU. The logits, the top-10 next tokens, and one
  distribution under temperature 0.7/1.0/1.5 and top-p 0.9 are all printed.
- **Signature figures:** V13 tokenizer strip; V14 parameter accounting; V8 real causal attention
  heatmaps for selected heads (measured); one next-token distribution under each sampler as small
  multiples (measured).
- **Traps:** the paper reports the small model as 117M while the released checkpoint is 124M.
  Hugging Face stores GPT-2's projections as transposed `Conv1D`. Tokens are not words.
- **Key sources:** Radford et al. 2018 (GPT); Radford et al. 2019 (GPT-2); Brown et al. 2020
  (NeurIPS, GPT-3); Sennrich, Haddow & Birch 2016 (ACL, BPE); Holtzman et al. 2020 (ICLR, nucleus
  sampling); Press & Wolf 2017 (EACL, weight tying).
- **Search intent:** "gpt architecture explained", "how does gpt-2 work", "decoder only
  transformer", "top-p vs temperature"

### 7 · GPT, Part 2 — Scaling Laws: C ≈ 6ND and the Chinchilla Correction

- **Slug:** scaling-laws-6nd-chinchilla
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,000 · **Figures:** 12
- **Hook:** GPT-3's training used 3.14 × 10²³ floating-point operations. Six times its parameters
  times its training tokens gives the same number.
- **Answers:** where does C ≈ 6ND come from, what do scaling laws actually claim, and why did
  Chinchilla overturn Kaplan's advice?
- **Assumes:** Part 6's parameter accounting (`#counting-gpt-2`).
- **Owns (math):** 2N forward + 4N backward FLOPs per token, and the attention term that formula
  omits; Kaplan's power laws and what his N excludes; compute-optimal allocation by Lagrangian on
  L = E + A/N^α + B/D^β; the ~20 tokens-per-parameter rule; the Kaplan–Chinchilla discrepancy and its
  reconciliation; inference-aware over-training.
- **Hands off:** MoE's active-vs-total accounting to Part 11.
- **Worked example:** GPT-3 175B's 6ND recomputed against the paper's table, and Chinchilla 70B on
  1.4T tokens. Then one budget allocated three ways — Kaplan, Chinchilla, over-trained — with the
  loss each predicts under the fitted law.
- **Signature figures:** V19 iso-FLOP curves and the compute-optimal frontier from the published
  constants (a fitted model, labelled), with reported points overlaid; V2 per-token FLOP budget
  split into matmuls and attention (exact); tokens-per-parameter for named models (reported).
- **Traps:** FLOPs vs FLOP/s. N with or without embeddings. Chinchilla's three approaches give
  different exponents, and an independent replication (Besiroglu et al. 2024) found its parametric
  fit inconsistent — the post says so.
- **Key sources:** Kaplan et al. 2020; Hoffmann et al. 2022 (NeurIPS); Besiroglu et al. 2024;
  Porian et al. 2024 (NeurIPS); Pearce & Song 2024.
- **Search intent:** "chinchilla scaling laws", "6nd flops formula", "compute optimal training",
  "kaplan vs chinchilla scaling"

### 8 · GPT, Part 3 — From GPT-3 to ChatGPT: RLHF, PPO and DPO, Derived

- **Slug:** rlhf-ppo-dpo-derived
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 13
- **Hook:** DPO trains on human preferences without ever building the reward model RLHF needs,
  because that reward model was hiding inside the policy all along.
- **Answers:** what three stages turned GPT-3 into an assistant, and how does DPO collapse two of
  them into one loss?
- **Assumes:** Part 6's next-token loss (`#the-training-loss`). Links Part 3 for REINFORCE with a
  group baseline, and does not re-derive it.
- **Owns (math):** SFT; the Bradley–Terry preference model and reward-model loss; the KL-regularised
  objective; PPO's clipped surrogate with a per-token KL penalty; the closed-form optimum
  π* ∝ π_ref · exp(r/β); the DPO loss derivation; what β means; the models each method holds in
  memory (four vs two).
- **Hands off:** critic-free group-relative RL (GRPO) to Part 15.
- **Worked example:** one prompt with a chosen and a rejected completion, using real log-probabilities
  from a small model on CPU. The Bradley–Terry probability, the DPO loss and its gradient weight are
  computed by hand.
- **Signature figures:** V20 DPO loss against implicit reward margin with the worked pair marked;
  V20 the PPO clip region; V9 the InstructGPT pipeline (Mermaid); models in memory per method.
- **Traps:** the direction of the KL. Per-token vs sequence-level KL. β means different things in
  PPO and DPO papers. InstructGPT's "1.3B preferred over 175B" is a human-preference result, not a
  benchmark.
- **Key sources:** Christiano et al. 2017 (NeurIPS); Stiennon et al. 2020 (NeurIPS); Ouyang et al.
  2022 (NeurIPS); Schulman et al. 2017 (PPO); Rafailov et al. 2023 (NeurIPS, DPO).
- **Search intent:** "rlhf explained", "dpo derivation", "ppo for llm", "dpo vs rlhf"

### 9 · Llama, Part 1 — The Modern Transformer Block: RMSNorm, SwiGLU, RoPE and GQA

- **Slug:** llama-modern-transformer-block
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 8,000 · **Figures:** 13
- **Hook:** Llama's feed-forward width is 11,008 in the 7B model and 14,336 in Llama 3 8B. Neither is
  4 × 4,096, and two different rounding rules explain both.
- **Answers:** what changed between GPT-2's block and the block nearly every open model now uses,
  and what does each change buy?
- **Assumes:** Part 6's block (`#the-gpt-2-block`).
- **Owns (math):** RMSNorm vs LayerNorm; SwiGLU and the ⅔ hidden-size rule (`multiple_of`,
  `ffn_dim_multiplier`), with GeGLU (used by Laya's ModernBERT backbone) as a sibling; RoPE as a
  drop-in (use only); GQA and MQA parameter and per-token cache ratios; dropped biases; the 32K → 128K
  tokenizer and its effect on sequence length; the Llama 1 → 2 → 3 → 3.1 → 4 changes; Llama 3 8B's
  count reconciled; Meta's 2026 move to Muse in one dated paragraph.
- **Hands off:** RoPE's derivation and context extension to Part 10; Llama 4's MoE to Part 11; KV
  capacity to nvidia-stack Part 11.
- **Worked example:** the shared sentence through an **ungated** Llama-architecture model on CPU
  (TinyLlama or SmolLM2, pinned at research), with every tensor shape through one block. The 8B
  model's counts are computed from its published configuration, because Meta's weights are gated.
- **Signature figures:** V10 GPT-2's block beside Llama's, shapes on every edge; V16 per-token K/V
  elements for MHA, GQA and MQA at Llama 3 8B's dimensions (exact); V13 the same sentence under three
  tokenizers; V14 parameter accounting.
- **Traps:** Llama 2 7B uses MHA — GQA is only on 34B and 70B. Llama 3 8B has 8 KV heads.
  `rope_theta` went from 10,000 to 500,000.
- **Key sources:** Touvron et al. 2023a (LLaMA), 2023b (Llama 2); Grattafiori et al. 2024 (The Llama 3
  Herd of Models); Zhang & Sennrich 2019 (NeurIPS, RMSNorm); Shazeer 2020 (GLU variants); Ainslie et
  al. 2023 (EMNLP, GQA); Shazeer 2019 (MQA).
- **Search intent:** "llama architecture explained", "rmsnorm vs layernorm", "swiglu explained",
  "grouped query attention"

### 10 · Llama, Part 2 — RoPE, Derived, and How Context Windows Get Stretched

- **Slug:** rope-derived-context-extension
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 15
- **Hook:** RoPE turns position into rotation. Stretching an 8K model to 128K means choosing which
  of its 64 rotation speeds to slow down, and by how much.
- **Answers:** why does rotating queries and keys encode relative position, and what do position
  interpolation, NTK-aware scaling, YaRN and Llama 3.1's scaling each change?
- **Assumes:** Part 9's use of RoPE (`#rope-as-used`). Links Foundational Architectures Part 13 for
  the sinusoidal shift property.
- **Owns (math):** RoPE by complex multiplication; ⟨R_m q, R_n k⟩ = ⟨q, R_{n−m} k⟩; the wavelength of
  each dimension pair, 2π·θ^{2i/d}; the long-range decay claim and its limits; PI; NTK-aware base
  change; YaRN's ramp and temperature; Llama 3.1's frequency-dependent scaling; Llama 4's interleaved
  NoPE layers.
- **Hands off:** sparse and compressed long-context attention to Part 14; memory to nvidia-stack
  Part 11.
- **Worked example:** a query and key at d = 8 (four rotation pairs), placed at positions 3 and 7 and
  rotated by hand, with the dot product shown to depend only on the offset 4. Then Llama 3's 64 pairs'
  wavelengths at θ = 500,000, set against 8K and 128K windows.
- **Signature figures:** V15 rotation geometry, four planes as small multiples; V15 the wavelength
  spectrum against context length before and after PI, NTK, YaRN and Llama 3.1 scaling, all on one
  set of axes; V7 score against relative distance for random q and k, with its variance band (exact).
- **Traps:** interleaved-pair vs half-split implementations (GPT-J vs NeoX / Hugging Face Llama) —
  same math, different weight layout. Trained, extended and effective context are three numbers.
- **Key sources:** Su et al. 2024 (Neurocomputing, RoFormer); Chen et al. 2023 (position
  interpolation); Peng et al. 2024 (ICLR, YaRN); Kazemnejad et al. 2023 (NeurIPS, NoPE); Grattafiori
  et al. 2024; bloc97 2023 (NTK-aware scaling — a community post, tiered as such).
- **Search intent:** "rope explained", "rotary position embedding derivation", "yarn context
  extension", "how to extend context length llm"

### 11 · Mixture of Experts — Routing, Load Balancing, and Why Active Isn't Total

- **Slug:** mixture-of-experts-routing-load-balancing
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Hook:** Mixtral 8×7B has 46.7 billion parameters and uses 12.9 billion per token. It is not
  8 × 7 = 56, because the experts share everything except the feed-forward layer.
- **Answers:** how does a router pick experts, why do experts collapse onto a few favourites without
  help, and how did load balancing move from auxiliary losses to bias terms?
- **Assumes:** Part 9's SwiGLU FFN (`#swiglu`), which each expert is.
- **Owns (math):** top-k gating (softmax-then-top-k vs top-k-then-softmax; sigmoid routers); Switch's
  auxiliary loss N·Σ f_i·P_i and why it is minimised at uniform load; the capacity factor and token
  dropping; router z-loss; fine-grained and shared experts (DeepSeekMoE); auxiliary-loss-free
  balancing by per-expert bias (DeepSeek-V3); total vs active accounting; Llama 4 and Qwen MoE
  configurations as instances.
- **Hands off:** expert parallelism and all-to-all to nvidia-stack Part 15; gpt-oss's MoE to Part 12.
- **Worked example:** 8 tokens, 4 experts, top-2, with gate logits, probabilities, selections,
  per-expert load and the auxiliary loss computed by hand. The same batch then gets two steps of
  bias correction.
- **Signature figures:** V17 routing matrix (tokens × experts, top-k outlined); V17 load histogram
  against uniform from a toy run with and without balancing (measured); V14 total vs active for four
  or five named models (computed from configurations); V10 the MoE layer with shapes.
- **Traps:** "8×7B" is a name, not a product. Active parameters include attention and embeddings.
  Top-k renormalisation conventions differ.
- **Key sources:** Shazeer et al. 2017 (ICLR); Lepikhin et al. 2021 (ICLR, GShard); Fedus, Zoph &
  Shazeer 2022 (JMLR, Switch); Jiang et al. 2024 (Mixtral); Dai et al. 2024 (ACL, DeepSeekMoE); Wang et
  al. 2024 (auxiliary-loss-free balancing).
- **Search intent:** "mixture of experts explained", "moe load balancing loss", "active vs total
  parameters", "how does mixtral work"

### 12 · GPT, Part 4 — gpt-oss: Attention Sinks, Banded Attention and MXFP4 Experts

- **Slug:** gpt-oss-architecture
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 10
- **Hook:** OpenAI's first open weights since GPT-2 are 116.8 billion parameters, 5.1 billion of them
  active per token, with the experts stored at about four bits each.
- **Answers:** what does the one modern OpenAI model with published weights look like inside, and
  which of its choices are new?
- **Assumes:** Part 11's MoE layer (`#the-moe-layer`).
- **Owns (math):** alternating dense and banded (sliding-window) attention, of which Laya's ModernBERT
  local/global alternation is an encoder-side instance; learned attention sinks as an extra softmax
  logit per head; MXFP4 as a storage format (a shared scale per block); its GQA configuration; the
  o200k_harmony tokenizer and harmony format in brief; the 120b and 20b counts reconciled.
- **Hands off:** executing FP4 on tensor cores to nvidia-stack Part 10; serving to nvidia-stack
  Parts 11–12.
- **Worked example:** one softmax row with and without a sink logit, showing where the mass goes.
  Then one MXFP4 block encoded and decoded, with the error printed.
- **Signature figures:** V18 dense and banded masks on one T×T grid; V3 an MXFP4 block encode/decode
  grid; V14 total vs active for 120b and 20b.
- **Traps:** GPT-4, GPT-5 and GPT-6 architectures remain undisclosed, and this part infers nothing
  about them. MXFP4 covers the MoE weights only.
- **Key sources:** OpenAI 2025, gpt-oss model card (arXiv 2508.10925); Xiao et al. 2024 (ICLR,
  attention sinks); OCP Microscaling Formats (MX) specification v1.0 (2023); Rouhani et al. 2023 (MX
  formats).
- **Search intent:** "gpt-oss architecture", "attention sinks explained", "mxfp4 format"

### 13 · DeepSeek, Part 1 — V3: Multi-Head Latent Attention and Multi-Token Prediction

- **Slug:** deepseek-v3-mla-multi-token-prediction
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Hook:** standard multi-head attention at DeepSeek-V3's size would cache 32,768 numbers per token
  per layer. MLA caches 576.
- **Answers:** how does MLA compress the key–value cache into a latent vector without losing
  multi-head expressiveness, why does RoPE get in the way, and what does predicting more than one
  token add?
- **Assumes:** Part 9's GQA (`#grouped-query-attention`). Links Part 11 for V3's MoE and does not
  re-teach it.
- **Owns (math):** low-rank joint KV compression; the up-projections; matrix absorption at inference
  (W_UK into W_Q, W_UV into W_O); why RoPE is incompatible with absorption, and the decoupled RoPE key;
  per-token cache for MHA, GQA and MLA; multi-token prediction modules and loss; fine-grained FP8
  scaling in one section.
- **Hands off:** cache capacity to nvidia-stack Part 11; FP8 execution to nvidia-stack Part 10;
  sparse attention to Part 14.
- **Worked example:** MLA at toy dimensions (d = 8, latent 2, two heads) — compress, up-project,
  absorb, and show the attention scores are identical with and without absorption. Then V3's real
  dimensions for 576 vs 32,768.
- **Signature figures:** V16 per-token cache bars (exact, V3 dimensions); V10 MLA with the
  decoupled-RoPE path highlighted; V3 absorption as matrix products on numbers; V9 the V3 block with
  MoE and MTP (Mermaid).
- **Traps:** V2 and V3 dimensions differ. "Latent" is not a VAE latent. MTP's training benefit and
  its use for speculative decoding are two separate claims.
- **Key sources:** DeepSeek-AI 2024, DeepSeek-V2 (arXiv 2405.04434); DeepSeek-AI 2024, DeepSeek-V3
  technical report (arXiv 2412.19437); Gloeckle et al. 2024 (ICML, multi-token prediction).
- **Search intent:** "multi-head latent attention explained", "deepseek v3 architecture", "mla vs
  gqa", "multi-token prediction"

### 14 · DeepSeek, Part 2 — Sparse Attention to a Million Tokens: DSA to V4's Compressed Attention

- **Slug:** deepseek-sparse-attention-v3-2-v4
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Hook:** DeepSeek V4 reads a million-token context by compressing keys along the sequence and
  letting a cheap indexer choose which blocks each query may see.
- **Answers:** how do learned sparse-attention schemes decide what each query attends to, and what
  does that cost against dense attention?
- **Assumes:** Part 13's MLA (`#multi-head-latent-attention`).
- **Owns (math):** the attention cost model (dense O(T²) against top-k selection plus indexer cost);
  Native Sparse Attention's three branches as background; V3.2's lightning indexer and top-k
  selection; V4's compressed sparse attention (CSA) and heavily compressed attention (HCA) —
  compression ratio, indexer precision and selected-block count, all pinned from the V4 report; what
  is trained from scratch vs added in continued pre-training.
- **Hands off:** V4's mHC and Muon to optional Part 24; serving economics to nvidia-stack.
- **Worked example:** a 32-token toy with 4:1 compression — indexer scores, top-k block selection and
  the resulting mask, printed. Then the per-query cost at 128K and 1M tokens from V4's published
  parameters.
- **Signature figures:** V18 dense, sliding, NSA, DSA and CSA masks on one T×T grid, cell for cell;
  cost against T from the cost model (exact, labelled as a model); V9 V4's attention path (Mermaid).
- **Traps:** the numbers circulating in secondary coverage (4:1, top-512, FP4 indexer) come from the
  V4 report or not at all. "Supports 1M tokens" is not "uses 1M tokens well".
- **Key sources:** DeepSeek-AI 2025, DeepSeek-V3.2 (arXiv 2512.02556); DeepSeek-AI 2026, DeepSeek-V4
  (arXiv 2606.19348); Yuan et al. 2025 (ACL, Native Sparse Attention).
- **Search intent:** "deepseek sparse attention explained", "deepseek v4 architecture", "native
  sparse attention", "long context attention"

### 15 · DeepSeek, Part 3 — R1 and GRPO: Reasoning Learned by Reinforcement

- **Slug:** deepseek-r1-grpo
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 12
- **Hook:** GRPO drops PPO's value network. Each answer's advantage is just its reward, standardised
  against the other answers to the same question.
- **Answers:** how did R1-Zero learn to reason from reward alone, what exactly does GRPO optimise,
  and which of its choices were later shown to bias it?
- **Assumes:** Part 8's PPO objective (`#ppo-clipped-objective`). Links Part 3 for REINFORCE with a
  group-mean baseline — the simpler relative Laya's RLCD uses.
- **Owns (math):** the GRPO objective — group sampling, standardised advantages, the clipped ratio,
  and the KL term via the k3 estimator; rule-based rewards; the R1-Zero and R1 pipelines;
  distillation into small dense models; the length and standard-deviation normalisation biases
  (Dr. GRPO); what the "aha moment" claim rests on.
- **Hands off:** inference-time compute on hardware to nvidia-stack.
- **Worked example:** one question with a group of 8 sampled answers and their rewards. Advantages,
  ratios and the per-token loss are computed by hand, then recomputed under Dr. GRPO's normalisation
  to show the length bias change.
- **Signature figures:** V20 advantages as z-scores on a number line, as small multiples over reward
  mixes; V20 PPO vs GRPO clipping; V9 the R1 training pipeline (Mermaid); reported response length
  against RL steps, plotted as reported.
- **Traps:** R1-Zero is not R1. Reported pass@1 is sampled at a stated temperature. Emergent
  reflection is one lab's observation. Check each source's peer-review status.
- **Key sources:** Shao et al. 2024 (DeepSeekMath, GRPO); DeepSeek-AI 2025, DeepSeek-R1 (arXiv
  2501.12948); Liu et al. 2025 (Understanding R1-Zero-Like Training); Schulman 2020 (KL
  approximators, k3).
- **Search intent:** "grpo explained", "deepseek r1 explained", "grpo vs ppo", "how reasoning models
  are trained"

### 16 · Mamba — Selective State Spaces, Derived

- **Slug:** mamba-selective-state-spaces
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 15
- **Hook:** a state-space layer can run as a recurrence or as one long convolution, with identical
  outputs. Mamba's key idea breaks the convolution on purpose, then needs a parallel scan to stay
  fast.
- **Answers:** what is a state-space layer, why does making it input-dependent matter, and how does
  Mamba still train in parallel?
- **Assumes:** Foundational Architectures Part 10's recurrence and gating (`#the-cell-state`).
- **Owns (math):** x′ = Ax + Bu, y = Cx; zero-order-hold discretisation Ā = exp(ΔA),
  B̄ = (ΔA)⁻¹(exp(ΔA) − I)·ΔB; recurrence ↔ convolution kernel (CB̄, CĀB̄, …); selectivity (Δ, B and C
  from the input) and its link to RNN gating; the associative parallel scan; Mamba-2's state-space
  duality, where the SSM is a semiseparable masked attention matrix; cost against attention.
- **Hands off:** linear attention and the delta rule to Part 17; hardware kernels to nvidia-stack
  Part 9.
- **Worked example:** a length-4 input through a two-state diagonal SSM, with recurrence and
  convolution computed separately and shown equal. Then Δ is made input-dependent and the convolution
  fails, and one four-element scan is done by hand.
- **Signature figures:** V21 state evolution as small multiples; V21 recurrence beside convolution
  with identical outputs; V7 the SSD semiseparable matrix beside a causal attention matrix on one grid
  (exact); cost against T (exact).
- **Traps:** S4's HiPPO initialisation vs Mamba's diagonal A. Mamba-1 vs Mamba-2. Linear training
  time and constant inference memory are two different claims.
- **Key sources:** Gu, Goel & Ré 2022 (ICLR, S4); Gu & Dao 2023 (Mamba, arXiv 2312.00752); Dao & Gu
  2024 (ICML, Mamba-2); Blelloch 1990 (prefix sums).
- **Search intent:** "mamba explained", "state space model explained", "selective scan", "mamba vs
  transformer"

### 17 · Gated DeltaNet — Linear Attention as Online Regression, and the Hybrids Built on It

- **Slug:** gated-deltanet-linear-attention-hybrids
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Hook:** linear attention keeps a d×d memory and only ever adds to it. The delta rule lets it
  overwrite, and that one change is inside 2026's hybrid open models.
- **Answers:** how does linear attention become a recurrent memory, what does the delta rule fix,
  and why do current open models mix a few full-attention layers with many linear ones?
- **Assumes:** Part 16's recurrence/parallel duality (`#two-ways-to-compute-it`).
- **Owns (math):** linear attention as S_t = S_{t−1} + v_t k_tᵀ; the delta rule
  S_t = S_{t−1}(I − β_t k_t k_tᵀ) + β_t v_t k_tᵀ as one step of online least squares; gating decay;
  the chunkwise-parallel form (WY representation, briefly); hybrid layer ratios in named models,
  pinned at research; what recall tasks reveal about linear memories.
- **Hands off:** serving to nvidia-stack.
- **Worked example:** a 2×2 state updated by four key–value pairs under plain linear attention and
  under the delta rule. The delta rule retrieves an overwritten value exactly, while linear attention
  returns a blend.
- **Signature figures:** V21 state matrices over time for both rules (small multiples); V7 retrieval
  error against stored pairs for both rules (exact); a hybrid stack's layer pattern as a to-scale
  strip.
- **Traps:** DeltaNet, Gated DeltaNet and Gated DeltaProduct are three things. "Linear" means linear
  in sequence length. Hybrid ratios are per model.
- **Key sources:** Katharopoulos et al. 2020 (ICML); Schlag, Irie & Schmidhuber 2021 (ICML); Yang et
  al. 2024 (NeurIPS, parallel DeltaNet); Yang, Kautz & Hatamizadeh 2025 (ICLR, Gated DeltaNet); Qwen
  team technical reports (pinned at research).
- **Search intent:** "gated deltanet explained", "linear attention explained", "delta rule
  attention", "hybrid attention models"

### 18 · JEPA, Part 1 — I-JEPA: Predicting Representations Instead of Pixels

- **Slug:** i-jepa-predicting-representations
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 8,500 · **Figures:** 14
- **Hook:** a masked autoencoder spends its capacity redrawing every pixel of a leaf. I-JEPA predicts
  only what the hidden region *means* — and has to be stopped from predicting the same constant
  everywhere.
- **Answers:** what is a joint-embedding predictive architecture, how does I-JEPA train one on
  images, and what stops the representation from collapsing?
- **Assumes:** Foundational Architectures Part 14's ViT (`#patch-embedding`).
- **Owns (math):** the three families of self-supervised learning (contrastive, generative / masked
  reconstruction, joint-embedding predictive) in LeCun's energy-based framing; complete and
  dimensional collapse; the context encoder, EMA target encoder and narrow predictor; stop-gradient
  and asymmetry as collapse prevention; multi-block masking arithmetic; the L2 loss in representation
  space; linear-probe evaluation. InfoNCE is stated in one equation and linked to Part 21 once that
  is live.
- **Hands off:** video and planning to Part 19; the principled replacement for EMA and stop-gradient
  to Part 20; contrastive losses to Part 21.
- **Worked example:** one masking draw on ViT-H/14's 16×16 patch grid at 224 px — the context block
  and four target blocks at the paper's scale and aspect ranges, with patch counts printed — and the
  tensor shapes through the predictor.
- **Signature figures:** V23 masking grids from several seeded draws (small multiples); V22 healthy,
  complete and dimensional collapse in a toy run, with covariance spectra (measured); V9 the training
  graph with EMA and stop-gradient edges (Mermaid); V10 contrastive, MAE and JEPA side by side.
- **Traps:** linear-probe and low-shot protocols give different numbers. The EMA momentum schedule.
  The weight licence, checked before any forward-pass figure. JEPA is not Jev — the names are
  unrelated.
- **Key sources:** LeCun 2022 (A Path Towards Autonomous Machine Intelligence); Assran et al. 2023
  (CVPR, I-JEPA); He et al. 2022 (CVPR, MAE); Grill et al. 2020 (NeurIPS, BYOL); Bardes, Ponce & LeCun
  2022 (ICLR, VICReg); Jing et al. 2022 (ICLR, dimensional collapse).
- **Search intent:** "jepa explained", "i-jepa", "joint embedding predictive architecture", "jepa vs
  mae"

### 19 · JEPA, Part 2 — V-JEPA and V-JEPA 2: Video, Tubelets and Planning in Latent Space

- **Slug:** v-jepa-2-video-world-model
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Hook:** V-JEPA 2 plans robot-arm motions without generating a single frame. It searches for the
  actions whose predicted embedding lands nearest the goal's.
- **Answers:** how does the JEPA recipe extend from images to video, and how does an
  action-conditioned predictor turn a representation into a planner?
- **Assumes:** Part 18's training scheme (`#i-jepa-training`).
- **Owns (math):** tubelet tokenisation (2×16×16) and tokens per clip; spatiotemporal multi-block
  masking; L1 feature prediction; V-JEPA 2's scaling (pinned); the action-conditioned predictor, with
  energy as the distance between predicted and goal embeddings; cross-entropy-method planning over
  action sequences; V-JEPA 2.1's changes (pinned).
- **Hands off:** vision-language JEPA to Part 22.
- **Worked example:** one 16-frame 256×256 clip tokenised, with tubelet count and masked fraction.
  Then three CEM iterations in a two-dimensional toy action space, with the energy of every sample.
- **Signature figures:** V23 a video masking grid (time × height × width, small multiples by frame
  pair); CEM iterations as shrinking sample clouds on an energy contour (toy, computed); V9 the
  planning loop (Mermaid).
- **Traps:** V-JEPA (2024), V-JEPA 2 (2025) and 2.1 (2026) are three releases. Zero-shot robot
  claims are tied to specific setups. Frames are not tubelets.
- **Key sources:** Bardes et al. 2024 (V-JEPA, arXiv 2404.08471); Assran et al. 2025 (V-JEPA 2, arXiv
  2506.09985); V-JEPA 2.1 (Meta, March 2026 — pin); Rubinstein 1999 (cross-entropy method).
- **Search intent:** "v-jepa 2 explained", "video world model", "jepa robot planning"

### 20 · JEPA, Part 3 — LeJEPA: Isotropic Gaussians and SIGReg, Derived

- **Slug:** lejepa-sigreg-isotropic-gaussian
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 15
- **Hook:** LeJEPA throws out the teacher network, the stop-gradient and the momentum schedule, and
  replaces them with a statistical test that the embeddings look like a standard Gaussian.
- **Answers:** why is an isotropic Gaussian the embedding distribution to aim for, and how does
  SIGReg push a high-dimensional batch towards it in linear time?
- **Assumes:** Part 18's account of collapse (`#why-representations-collapse`).
- **Owns (math):** the downstream-risk argument for isotropy (probe bias and variance under
  anisotropic embeddings); Cramér–Wold, testing a distribution through its 1-D projections; the
  Epps–Pulley characteristic-function statistic; SIGReg's sketch over random directions and its
  cost; the full LeJEPA loss with its single trade-off λ; what the paper proves, under which
  assumptions, and what is still one paper.
- **Hands off:** nothing downstream. Part 22 is independent of this part.
- **Worked example:** six two-dimensional embeddings projected onto three random directions and
  standardised. The empirical characteristic function is compared with e^{−t²/2} at a few t, and the
  Epps–Pulley statistic is computed by hand. Then the same for a collapsed set.
- **Signature figures:** V22 collapsed, anisotropic and isotropic embeddings with 1-D projection
  histograms against N(0, 1); V7 empirical vs Gaussian characteristic functions with the weighted
  area shaded (exact); V5 a toy SIGReg run, covariance spectrum over training steps (measured).
- **Traps:** the paper is from November 2025, so check its peer-review status at research time.
  "Provable" refers to specific theorems with stated assumptions. The single-λ claim is set against
  the sensitivity the paper actually shows.
- **Key sources:** Balestriero & LeCun 2025 (LeJEPA, arXiv 2511.08544) and its code; Epps & Pulley
  1983 (Biometrika); Cramér & Wold 1936.
- **Search intent:** "lejepa explained", "sigreg", "isotropic gaussian embeddings", "self supervised
  learning without heuristics"

### 21 · CLIP — Contrastive Pretraining and the InfoNCE Loss, by Hand

- **Slug:** clip-contrastive-infonce
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Hook:** CLIP classifies ImageNet without training on ImageNet. It embeds the image, embeds
  "a photo of a {label}" for every class, and picks the nearest.
- **Answers:** what loss does CLIP optimise, what does its temperature do, and how does
  nearest-caption search become a classifier?
- **Assumes:** Foundational Architectures Part 14's ViT (`#the-class-token`).
- **Owns (math):** dual encoders projected to one space; the N×N similarity matrix and symmetric
  cross-entropy; the learned temperature, its initialisation and clamp; InfoNCE as a mutual-information
  lower bound capped at log N; zero-shot classification and prompt ensembling; SigLIP's sigmoid
  alternative in one section.
- **Hands off:** image embeddings inside an LLM to optional Part 23; approximate nearest-neighbour
  search to search-algorithms Parts 14–15, linked once live.
- **Worked example:** 4 images × 4 captions — embeddings, cosines, scaled logits, row and column
  softmaxes and the loss, by hand. Then a real CLIP ViT-B/32 forward on CPU for the shared image
  against five prompts.
- **Signature figures:** V24 the similarity matrix split into its row and column softmaxes; V7 loss
  against temperature for the worked batch (exact); V22 a small real batch of image and text
  embeddings on the sphere (measured).
- **Traps:** logit scale vs temperature. Batch size is a hyperparameter of the loss. Zero-shot
  accuracy depends on prompt templates.
- **Key sources:** Radford et al. 2021 (ICML); van den Oord, Li & Vinyals 2018 (CPC, InfoNCE); Poole
  et al. 2019 (ICML); Zhai et al. 2023 (ICCV, SigLIP).
- **Search intent:** "clip explained", "infonce loss", "contrastive learning explained", "clip zero
  shot"

### 22 · JEPA, Part 4 — VL-JEPA: Answering by Predicting Embeddings, Not Tokens

- **Slug:** vl-jepa-predicting-embeddings
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,000 · **Figures:** 11
- **Hook:** a standard vision-language model answers one token at a time. VL-JEPA predicts the
  answer's embedding in one shot and decodes it into words only when someone needs to read it.
- **Answers:** what changes when a vision-language model's target is a text embedding instead of a
  token sequence, and what does that buy in parameters and latency?
- **Assumes:** Part 18's JEPA framing (`#three-families`). Links Part 21 for contrastive alignment,
  and Part 2 for the same "no output tokens" latency argument made on decision models.
- **Owns (math):** the VL-JEPA objective and architecture (pinned from the paper); embedding
  prediction vs autoregressive decoding cost; selective decoding; the reported parameter and latency
  comparisons, each with its baseline.
- **Hands off:** standard VLM architecture to optional Part 23.
- **Worked example:** pinned at research — the smallest honest instance of a predicted and a target
  embedding and their loss.
- **Signature figures:** V10 a standard VLM beside VL-JEPA; decode cost from the paper's
  configuration (computed, labelled); V24 predicted-vs-target similarity.
- **Traps:** preprint status. "Half the trainable parameters" needs its baseline named.
- **Key sources:** VL-JEPA (Meta FAIR, December 2025 — authors and arXiv id pinned at research);
  Assran et al. 2023.
- **Search intent:** "vl-jepa explained", "jepa vision language model"

### 23 (optional) · Vision-Language Models — From LLaVA to Natively Multimodal

- **Slug:** vision-language-models-llava-to-native
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** how does an image become tokens an LLM can read, and what changes when a model is
  multimodal from the first layer?
- **Assumes:** Part 21 (`#dual-encoders`).
- **Owns (math):** the projector (linear → MLP); image-token arithmetic (336 px / 14 = 24² = 576
  tokens); AnyRes tiling; the Q-Former contrast; early fusion (Chameleon, Llama 4).
- **Key sources:** Liu et al. 2023 (NeurIPS, LLaVA); Liu et al. 2024 (CVPR, LLaVA-1.5); Li et al.
  2023 (ICML, BLIP-2); Chameleon Team 2024.
- **Search intent:** "how do vision language models work", "llava architecture"

### 24 (optional) · DeepSeek, Part 4 — mHC and Muon: Rebuilding the Residual Stream and the Optimiser

- **Slug:** deepseek-mhc-muon
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** what replaces the single residual stream in V4, why does it need a constraint, and
  what does Muon do to an update that Adam does not?
- **Assumes:** Foundational Architectures Part 8 (`#the-identity-gradient`) — this is that story ten
  years on.
- **Owns (math):** hyper-connections, with several residual streams mixed by learned matrices; the
  manifold constraint and why it restores the identity-mapping property (mechanism pinned from the mHC
  paper); Muon's orthogonalised update by Newton–Schulz iteration; MuonClip as a variant.
- **Key sources:** Zhu et al. 2025 (ICLR, Hyper-Connections); the DeepSeek mHC paper (pinned);
  DeepSeek-V4 report; Jordan et al. 2024 (Muon); Liu et al. 2025 (Muon is Scalable for LLM Training).
- **Search intent:** "deepseek mhc explained", "hyper-connections", "muon optimizer explained"

## Visual system

This series inherits Foundational Architectures' families V1–V10 and its seven figure rules
unchanged (provenance in every caption, printed scales, fixed colour maps, KaTeX never as an image,
figure scripts importing lab numbers, `source` only with a verified licence, every PNG read before
the gate). It adds the families these models need:

| Code | Family | What it must show | Route | Precision rule |
|---|---|---|---|---|
| V13 | Tokenizer strip | a text under one or more tokenizers, boundaries drawn over the same characters, id under each token, count at the end; the decision-model variant colours state, question and option-marker segments | `placed` (Q4) | computed by the real tokenizers; vocabulary size printed |
| V14 | Parameter accounting | embeddings / attention / FFN or experts / heads / norms to scale, total vs active with active highlighted inside total | `chart` | computed from the published configuration; reconciled to the stated total with the delta |
| V15 | Rotation geometry | RoPE pairs as vectors rotating in 2-D planes; the wavelength spectrum against context windows; each extension method as a re-mapping on the same axes | `plot` | exact; θ and d printed |
| V16 | Per-token memory bars | K/V elements per token per layer for MHA, GQA, MQA, MLA and compressed schemes, to scale | `chart` | exact from configurations; capacity (× tokens × layers × bytes) is nvidia-stack's, not ours |
| V17 | Routing matrix | tokens × experts gate probabilities with top-k outlined; per-expert load against uniform | `plot` | hand-worked or measured toy, labelled which |
| V18 | Mask grid | causal, banded, sink, NSA, DSA and compressed patterns on **one** T×T grid at **one** T | `plot` | cell-for-cell comparable; never different T in one comparison |
| V19 | Fitted-law plot | log-log iso-FLOP curves and frontiers from published constants, reported points overlaid | `plot` | caption says "fitted model, constants from …"; never presented as data |
| V20 | Objective geometry | expected score against reported probability (proper scoring rules), loss against margin (Bradley–Terry, DPO), clip regions (PPO, GRPO), advantages as z-scores, CEM clouds | `plot` | the worked example's point is marked on every curve |
| V21 | State evolution | SSM and DeltaNet state matrices over time, recurrence and parallel forms side by side with identical outputs | `placed` / `plot` | small multiples; the equality is printed, not asserted |
| V22 | Embedding geometry | collapsed / anisotropic / isotropic clouds, covariance eigenvalue spectra (log), 1-D projections against N(0, 1) | `plot` | toy runs labelled measured; the spectrum axis is log |
| V23 | Masking grid | patch or tubelet grids with context and target blocks from the real sampler, seed printed, counts printed | `placed` / `plot` | several draws as small multiples, never one lucky draw |
| V24 | Similarity matrix | N×N logits with the row-softmax and column-softmax halves of a symmetric loss | `plot` | the diagonal (positives) is marked |
| V25 | Decision readout | per question: every option's probability as a bar, the chosen option, the confidence, and the act/escalate threshold as a line; before/after pairs for perturbations | `plot` | measured on local Laya or reported by a vendor — never both in one panel without a legend |
| V26 | Reliability diagram | confidence bins against observed accuracy, bar width ∝ count, the calibration gap shaded, ECE and bin count printed | `plot` | the bin count is printed, since ECE depends on it |
| V27 | Risk–coverage curve | error rate among accepted decisions against the fraction accepted, the chosen threshold marked | `plot` | from a labelled set whose size is printed |

**Shared examples.**
- **The shared decision example** (one support ticket plus three typed questions, chosen at Part 1)
  is used in Parts 1–5.
- **One sentence** (chosen at Part 6) is used for every tokenizer and LLM trace.
- Foundational Architectures Part 12's four-token, d = 8 attention toy is reused for GQA, MLA and
  RoPE.
- The foundational series' shared image is used for every vision forward pass.

## Math ownership

| Derivation | Owner | Linked from |
|---|---|---|
| decision-model contract, option-marker scoring, typed heads, Laya's count | 1 | 2, 3, 4, 5 |
| encoder-pass vs decode cost model, per-question latency fit, vocabulary share | 2 | 4, 22 |
| calibration (ECE, Brier, reliability, temperature), proper scoring rules, RLCD, REINFORCE with group baseline | 3 | 5, 8, 15 |
| Jev's documented contract, primitives and pricing arithmetic | 4 | 5 |
| injection mechanism and mitigation, selective prediction, the decision-model/LLM/classifier guide | 5 | — |
| BPE, weight tying, causal LM loss, sampling operators, perplexity | 6 | 7, 8, 9, 12 |
| 6ND, fitted laws, compute-optimal allocation | 7 | 11 |
| Bradley–Terry, PPO, KL-regularised optimum, DPO | 8 | 15 |
| RMSNorm, SwiGLU/GeGLU sizing, GQA/MQA ratios | 9 | 1, 10, 11, 13 |
| RoPE, relative property, wavelength spectrum, PI / NTK / YaRN / Llama 3.1 scaling | 10 | 1, 13, 14 |
| gating, auxiliary and bias balancing, capacity, active parameters | 11 | 12, 13 |
| attention sinks, banded/local–global alternation, MXFP4 block format | 12 | 1, 14 |
| MLA compression and absorption, decoupled RoPE, MTP | 13 | 14 |
| sparse-attention cost model, DSA, CSA/HCA | 14 | — |
| GRPO, k3 KL estimator, normalisation biases | 15 | — |
| SSM discretisation, recurrence/convolution equivalence, scan, SSD | 16 | 17 |
| linear attention state, delta rule, chunkwise form | 17 | — |
| SSL taxonomy, collapse, EMA/stop-gradient asymmetry, multi-block masking | 18 | 19, 20, 22 |
| tubelets, latent energy, CEM planning | 19 | — |
| isotropy argument, Cramér–Wold, Epps–Pulley, SIGReg | 20 | — |
| InfoNCE, symmetric loss, temperature, MI bound | 21 | 18, 22, 23 |

Part 1 uses RoPE, GeGLU and local/global attention before Parts 9, 10 and 12 derive them. It defines
each in one line and adds no forward link. Those later parts link back to Part 1 as an encoder-side
instance.

## Conventions printed beside every number

- **Parameters** state whether embeddings are included (Kaplan's N excludes them) and whether a count
  is total or active.
- **Tokens** always name their tokenizer. The same text is a different number of tokens in each
  model.
- **Context** is trained, extended or effective — three numbers, never one.
- **FLOPs** follow the foundational series' MAC convention. 6ND omits the attention term; say so
  wherever it matters.
- **Layout** is B × T × d with the row-vector convention y = xW. Hugging Face's GPT-2 `Conv1D`
  transposes this, and the post says so where it matters.
- **RoPE** names its pairing (interleaved or half-split).
- **Every benchmark** carries its protocol: shots, sampling temperature, pass@k, and the evaluation
  harness.
- **Decision-model numbers** carry their provenance: *vendor-reported* (TypeSafe or Convai),
  *third-party measured* (with who and how), or *our local run*. Latency always names its hardware
  and whether it includes the network.
- **Calibration** numbers name the metric, the bin count, and raw vs post-temperature.

## Publication order and cadence

Reading order is the numbering, and the decision models come first by the user's instruction.

- **Wave 1 — decision models, in the user's order:** 1, 2, 3 (Laya), then 4, 5 (Jev). The series'
  entry is Part 1. It links Foundational Architectures Part 12 once that is live; until then it
  restates the encoder block and BERT's masked-token prediction in a few sentences. The decision
  models are trending *now*, so this wave should not wait for the foundational series.
- **Wave 2 — the rest of the families the user named:** 6 (GPT, Part 1), 9 and 10 (Llama), 18
  (JEPA, Part 1), 20 (LeJEPA).
- **Wave 3:** 11 (MoE), 13 (DeepSeek V3), 8 (RLHF/DPO), 15 (R1), 7 (scaling).
- **Wave 4:** 12, 14, 16, 17, 19, 21, 22, then the optional parts.

One part a week, alternating with Foundational Architectures once both are running. Before each part,
run the currency check in *How this series grows*. For Parts 1–5 it must also check whether Convai has
released training code or a paper, or TypeSafe any architecture detail, since either would change what
those parts can trace.

## Cross-links

- **foundational-architectures:** Part 1 links its Part 12 (and its Part 18, BERT, if that part is
  committed); Part 6 links its Part 12; Part 16 links its Part 10; Parts 18 and 21 link its Part 14;
  Part 10 links its Part 13 for the sinusoidal shift; optional Part 24 links its Part 8.
- **nvidia-stack:** Parts 9 and 13 link Part 11 (VRAM and KV-cache capacity) and never re-derive it;
  Part 2 links Parts 11–12 for decoder serving costs. Parts 12 and 13 link Part 10 (executed low
  precision). Part 11 links Part 15 (parallelism). Part 16 links Part 9 (kernels). This series owns
  per-token *architecture* arithmetic; nvidia-stack owns capacity, hardware and serving.
- **diffusion-models:** discrete diffusion language models belong to diffusion Part 11. This series
  does not cover them and links there when relevant.
- **search-algorithms:** Part 21 links Parts 14–15 (ANN indexes) for embedding retrieval, once live.

Within the series, each part links back to at most one prerequisite anchor. No forward links to
unpublished posts. All links take the form `https://canery.in/blogs/<slug>#<anchor>`.

## The lab policy

The Foundational Architectures policy applies: Tier A is stdlib-only, and Tier B is CPU PyTorch in
a pinned `uv` environment writing JSON that the stdlib figure builder reads. This series adds limits
that come from the machine (16 cores, 14 GB RAM, no NVIDIA GPU):

- **Real forward passes only on models that fit comfortably in CPU memory:** all three Laya
  checkpoints (421M and 322M, Apache-2.0), GPT-2 small/medium, a ≤ 1.1B ungated Llama-architecture
  model, a small Mamba checkpoint, CLIP ViT-B/32, and a small ViT where a JEPA licence allows.
  Everything larger (Llama 3 8B, gpt-oss, DeepSeek, Qwen) is **configuration arithmetic only**,
  computed from published configs and labelled computed.
- **Laya is the series' best lab subject:** open, small and CPU-runnable. Parts 1, 2, 3 and 5 all run
  it locally, and their lab is shared (one environment, one runner, several experiments).
- **Jev is never run without the user's credentials,** and never attacked. Jev measurements need
  TypeSafe early access, which costs per input token. Without it, Jev parts use only disclosed and
  third-party numbers. Security demonstrations run only on local Laya.
- **Gated weights are never needed.** Numbers for Meta's gated models come from papers and model
  cards; real runs use an ungated model of the same architecture.
- **Weight licences are checked before a forward pass reaches a figure.** Some JEPA checkpoints may be
  non-commercial, and canery.in is a company site. If the licence is NC or unclear, that part uses
  computed and toy figures only.

## Open decisions for the user

1. **Jev API access.** With early-access credentials, Jev Part 1 can capture a real response and
   measure calibration and latency from outside. Without them it stays on disclosed and third-party
   numbers. Either is honest; the first is stronger.
2. **Promote Foundational Architectures Part 18 (BERT) to committed?** Laya scores options at `[MASK]`
   tokens, which is BERT's masked-token head put to a new use, so BERT becomes Laya's natural
   prerequisite. Recommended. The adjacent option is for Laya Part 1 to restate it.
3. **Llama and JEPA stay.** I first read "leya" as Llama and "jev" as JEPA. Both tracks earn their
   place anyway: the Llama block underlies every open LLM, and the JEPA line runs into LeJEPA. Either
   drops in one word.
4. **Closed models.** GPT-4/5/6, Muse Spark and other undisclosed models stay out of scope for
   architecture. Jev is covered as a contract, not an architecture.
5. **Tier B labs** — the same decision as the foundational series, and more valuable here, because
   Laya runs locally.
6. **Optional parts 23–24**, and whether Muse Glimmer becomes a part if Meta discloses its
   architecture.

## What this series will not cover

Closed-model architectures; benchmark leaderboards and model-vs-model shopping; prompt engineering,
agents and tool use; operational attacks on hosted services; diffusion language models
(diffusion-models Part 11); serving, quantisation execution and hardware (nvidia-stack); safety and
policy; and training-infrastructure engineering. Each is its own subject, and several already have a
home in this blog.
