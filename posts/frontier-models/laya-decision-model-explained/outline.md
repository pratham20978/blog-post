# Outline — laya-decision-model-explained

**Title:** Laya, Part 1: What a Decision Model Is, Traced Through Laya (59 chars)
**Series:** frontier-models, `series_position: 1` · **Tier:** L4 · **Difficulty:** intermediate
**Category:** machine-learning · **Target:** ~8,800 words · **Figures:** 13 + cover

## Brief (Phase 0)

- **Tier L4.** The reader must learn a contract, a sequence format, a scoring rule, an architecture,
  a parameter account and a lineage. The honest worked example needs three sequences of 122–141
  tokens, so it cannot fit on one screen. The adjacent option is L3, which would move the lineage
  and the three-checkpoint comparison out.
- **Difficulty intermediate.** It assumes the Transformer encoder (attention, residual stream,
  LayerNorm) and softmax, and restates BERT's `[MASK]` in three sentences. The adjacent option,
  advanced, would drop those restatements.
- **Angle** (from the saturation check): release-week explainers repeat the card. None shows the
  token sequence, the per-question rows, shapes, logits, the parameter reconciliation, or the
  lineage. This part owns all six.

## Research findings that change the plan

1. **One forward pass is one batch of per-question sequences.** Each question gets its own row
   holding a full copy of the state (`_encode_state`). The ticket's 88 tokens appear 3 times, so
   264 of the 399 input tokens are the same ticket. This is not "the state is read once". Part 2's
   hook in `plan.md` ("the state is read once") must change; record this in `context.md`.
2. **`[MASK]` is a read-out slot, not BERT's masked-token head.** The MLM vocabulary head is not in
   the checkpoint. A new scorer reads the hidden state at each `[MASK]`. `plan.md`'s Open decision 2
   overstates this ("BERT's masked-token head put to a new use").
3. **The format is inherited.** UniMC (EMNLP 2022) already put `[O-MASK] option` pairs in one
   sequence and softmaxed across options; GLiNER, GLiClass and GLiGuard continued the idea. What is
   new in Laya is the typed contract, the per-question rows, the RLCD training and the shipped
   temperatures.
4. **The multilingual checkpoint ships 1,024 context (8,192 opt-in) and no fitted temperatures.** On
   our ticket its route answer is 1.0000.
5. **The act head's constant 1.0 has a mechanism** (issue #185), reproduced on our input:
   `[CLS]` norm 35.7 → 10,377.6 after the head.
6. **Budget rule consequence:** at 125 options the English checkpoint gives the state 0 tokens and
   still answers.

## Section plan and word budget

| # | Section | Target | Job (what the reader can do after it) | Figures |
|---|---|---|---|---|
| — | Insights + level line + jump list | 250 | state the contract and the one-number trace | — |
| 1 | Why this matters | 300 | see why misreading "one pass" and `act_probability` costs money and safety | — |
| 2 | The problem | 650 | state the task (three typed answers from one ticket) and why a classifier and an LLM in JSON mode each fall short | — |
| 3 | Worked example | 1,300 | follow the ticket from JSON to 399 tokens to three softmaxes and the returned JSON, with every number | FIG_01, FIG_02, FIG_03 |
| 4 | Intuition | 550 | explain why a `[MASK]` per option works, and where the ballot analogy breaks | — |
| 5 | What is a decision model? `#what-a-decision-model-is` | 750 | define the contract, the three types, "System One", "Jev-compatible", and compare it with JSON mode and a classifier | FIG_04 |
| 6 | How does Laya lay out a question? | 550 | predict any request's sequence, rows and budgets, and when options starve the state | FIG_05 |
| 7 | Option-marker scoring `#option-marker-scoring` | 700 | compute any answer from logits: gather, score, mask, temperature, softmax, readouts, the two confidence fields | FIG_06, FIG_13 |
| 8 | What is inside Laya? | 800 | name every module, its shape and job; give ModernBERT's four changes in one line each; explain why the act head reads 1.0 | FIG_07, FIG_08, FIG_12 |
| 9 | Where do the 421 million parameters live? | 650 | reconcile 421,293,827 by hand and know the three checkpoints are different models | FIG_09, FIG_10 |
| 10 | Where did option markers come from? | 650 | place Laya in the lineage and name its new 10% | FIG_11 |
| 11 | The math | 850 | the contract as equations, collapsed back onto the ticket's numbers; parameter formulas | — |
| 12 | Implementation | 350 | run the trace; reproduce probabilities from logits | — |
| 13 | Limitations and common mistakes | 650 | avoid the eight traps; know which later part owns each | — |
| 14 | Key takeaways | 150 | — | — |
| 15 | Try it yourself | 250 | three exercises with answers | — |
| 16 | References | — | Lab downloads + sources | — |

Total ≈ 9,350 including references and captions; body prose ≈ 8,700.

## Figure plan (route gate run per figure; final numbering, as built)

| Fig | Section | One thing it communicates | Route | Why (the clause that settled it) | Provenance |
|---|---|---|---|---|---|
| FIG_01 | Worked example | the route row's 141 tokens by segment, each `[MASK]` flagged | placed | Q4 — a grid of the real tokens at their positions | our run |
| FIG_02 | Worked example | 3 rows of 141/136/122 padded to 141; the 88-token ticket in every row; 264 of 399 | placed | Q4 — drawn to scale | our run |
| FIG_03 | Worked example | returned distributions with the T = 1 softmax beside them | plot | Q1 — measured (V25) | our run |
| FIG_04 | What a decision model is | classifier vs JSON-mode LLM vs Laya, passes and tokens drawn to count | placed | Q4 — a comparison drawn to count, not a graph | our run + ledger |
| FIG_05 | Layout | tokens per option and state room against option count, both budgets | plot | Q1/Q4 — exact output of `build_sequence` (V7) | computed (lab sweep) |
| FIG_06 | Option-marker scoring | logits → mask → ÷T → softmax per row | placed | Q4 — grid of real values (V3) | our run |
| FIG_07 | Option-marker scoring | entropy-based confidence as a band against max p, with our answers | plot | Q4 — exact curves (V7) | computed + our run |
| FIG_08 | Inside Laya | the whole model, shape on every edge, parameters on every node | mermaid | Q3 — the post's one end-to-end view (V9) | computed from weights |
| FIG_09 | Inside Laya | local vs global masks on the route row, billing marker highlighted | plot | Q4 — two masks on one T × T grid (V18) | computed |
| FIG_10 | Inside Laya | `[CLS]` norm through the head and the act logits | plot | Q1 — measured | our run |
| FIG_11 | Parameters | 421,293,827 to scale, head zoomed | chart | Q1 — counted (V14) | computed |
| FIG_12 | Parameters | the ticket through three checkpoints | plot | Q1 — measured small multiples (V25) | our run |
| FIG_13 | Lineage | eight input formats, BERT 2019 to Laya 2026 | placed | Q4/Q5 — a timeline of format strings | ledger |

Cover: template cover (`placed`) built by `_cover.py`; `cover-prompt.md` holds the generated alternative.

## Term map

| Term | First section | What | Why here | When it matters |
|---|---|---|---|---|
| decision model | Insights | a model that maps a state and typed questions to distributions over declared options | the category the post defines | choosing it over an LLM for routing/triage |
| state | Insights / Problem | the input being judged (text or JSON) | one of the two inputs | truncation, cost |
| typed question: choice / score / noul | Problem | a question with a declared answer type and options | defines the answer space | picking the type; noul's label trap |
| option / option marker | Worked example | a declared answer; the `[MASK]` placed in front of it | the unit that gets scored | option counts, order |
| token, tokenizer (BPE) | Worked example | the text units the model reads; ModernBERT's byte-pair encoder | all counts are in tokens | budgets, cost |
| `[CLS]`, `[SEP]`, `[MASK]` | Worked example | special tokens: sequence start, separator, masked-slot | the layout | reading the strip |
| batch, padding, attention mask | Worked example | rows stacked into one tensor; filler tokens; which positions are real | the "one pass" | input_tokens accounting |
| hidden state | Worked example | the 1,024-number vector at each position | what gets gathered | shapes |
| logit | Worked example | an unnormalised score | scorer output | temperature |
| softmax, temperature | Worked example | normalise logits into probabilities; divide logits first to soften or sharpen | the returned numbers | calibration (Part 3) |
| expected level (score) | Worked example | Σ i·pᵢ | score readout | 3.33 is not a level |
| confidence vs answer_confidence | Option-marker scoring | 1 − normalised entropy vs max p | two different JSON fields | gating |
| act/escalate head | Worked example | a small head meant to say act or hand off | it reads 1.0 | never gate on it |
| encoder, bidirectional | Intuition | every token sees every other token | why a `[MASK]` can summarise | vs decoder |
| JSON mode, constrained decoding | Problem | an LLM whose next-token choices are masked to a schema | the main alternative | format vs correctness |
| fine-tuned classifier | Problem | an encoder plus a fixed K-way output layer | the other alternative | fixed label sets |
| System One | What is a decision model? | TypeSafe's name for the category (after Kahneman) | naming | reading vendor claims |
| Jev-compatible | What is a decision model? | the same `POST /v1/systemone` request and response shape | the Laya server's promise | not the same model |
| ModernBERT, RoPE, GeGLU, local/global attention, unpadding | Inside Laya | the backbone and its four changes from BERT | use only; derived in Parts 9, 10, 12 | long inputs, speed |
| pre-norm (Pre-LN), residual stream, LayerNorm | Inside Laya | norm before each sublayer; the running sum of sublayer outputs | explains #185 | the act head |
| question-type embedding | Inside Laya | a learned vector per type added to every position | how the head knows the type | — |
| GELU, ReLU | Inside Laya | activation functions | scorer vs head FFN | — |
| FP16 | Parameters | 16-bit floating point storage | file size | memory |
| cloze, verbalizer, NLI/entailment | Lineage | earlier ways to classify with a masked LM or an inference model | lineage | — |
| RLCD, proper scoring rule | Worked example (one line) | Convai's training objective | named, derived in Part 3 | — |
| calibration | Worked example (one line) | probabilities that match frequencies | named, derived in Part 3 | — |

## Hand-offs (no forward links — these parts are unpublished)

Latency and cost of the copied state → Part 2. Calibration, temperature fitting and RLCD → Part 3.
Jev's contract → Part 4. Injection, option-name attacks and thresholds → Part 5. Say "a later part"
without linking.
