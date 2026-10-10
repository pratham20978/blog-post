# Asset manifest — laya-decision-model-explained

Series `frontier-models`, part 1 (Laya, Part 1). **Status: local draft assets ready for upload.**
Upload each PNG below to the public `media` bucket under the object key shown (the store is flat,
so every key carries the post slug), then each lab file under `labs/laya-decision-model-explained/`. Write the resulting
URLs to `urls.txt` in table order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/frontier-models/laya-decision-model-explained/ posts/frontier-models/laya-decision-model-explained/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/frontier-models/laya-decision-model-explained/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract
rejects a non-URL there, so it must be resolved before upload.

Every figure is our own work. Figures 1–7 and 9–13 are built by `assets/_figs.py` on top of
`assets/_build.py`; figure 8 is rendered from `fig-08-laya-end-to-end-laya-decision-model-explained.mmd` by `assets/_fig08.py`
(mermaid-cli with `_mermaid-config.json` and `_puppeteer.json`, then the same headless-Chrome shim,
with absolute paths); the cover is built by `assets/_cover.py`. Each exports `.html` (or `.mmd`),
`.svg` and a 2× `.png`.

**Every Laya number drawn is read from `lab/trace.json`**, the captured output of
`lab/trace_laya.py --all` (laya 0.3.20, torch 2.14.0+cpu, FP32, checkpoint commit 55cf4c4e). A
figure cannot disagree with the lab or the prose: change the lab, re-run it, and re-run the
figure scripts. Figures 7 and 9 add exact computations (entropy bands; the |i − j| ≤ 64 mask rule).

## Route gate

Figure 8 is the post's one end-to-end view of the model, so Q3 sends it to `mermaid`: nine nodes,
the act/escalate branch off the head and the merge into the output. The other twelve stop at Q1
(measured or counted data: figures 3, 5, 10, 11, 12) or Q4 (value from positions, grids, counts
or exact curves Mermaid cannot draw: 1, 2, 4, 6, 7, 9, 13). Figure 4 has three parallel columns,
but they are a comparison table drawn to count, not a graph whose takeaway is a connected path.

No paper figure is reused. The one candidate, UniMC's Figure 3 (ACL Anthology, CC BY 4.0), is
set aside in the ledger because Figure 13 compares eight formats on our own ticket, which the
source figure cannot do. Laya's own benchmark images are vendor comparisons and belong to Jev's
part. Source credit and Rights are therefore `—` throughout.

Every PNG was opened and checked by eye after its last render: arithmetic against `trace.json`,
arrow ownership on figure 8, label plates over curves (figures 5, 7, 9 were fixed for this),
legend swatches drawn at the opacity of the marks they name, and dead bands.

Re-render: `cd assets && python3 _figs.py && python3 _fig08.py && python3 _cover.py`.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-laya-decision-model-explained.png | placed | template cover in the house layout, built by `_cover.py` from figure 1's motif — a diagram-design build, not an external generator | — | — | cover-laya-decision-model-explained.png | A row of token tiles in which four tiles glow as masked slots, each feeding one bar of a small probability chart |
| FIG_01 | assets/fig-01-route-token-strip-laya-decision-model-explained.png | placed | Q4 — a grid of the 141 real tokens at their positions, coloured by segment; Mermaid cannot draw it | — | — | fig-01-route-token-strip-laya-decision-model-explained.png | The route row's 141 tokens in a grid coloured as question, option, marker and state, with MASK markers at 13, 23, 34 and 43 |
| FIG_02 | assets/fig-02-one-batch-laya-decision-model-explained.png | placed | Q4 — three rows and the 399-token total drawn to scale; the repeated ticket band is the point | — | — | fig-02-one-batch-laya-decision-model-explained.png | Three token rows of 141, 136 and 122 real tokens padded to 141, with the same 88-token ticket band repeated in every row |
| FIG_03 | assets/fig-03-decision-readout-laya-decision-model-explained.png | plot | Q1 — measured probabilities per question, with the T = 1 softmax of the same logits (V25) | — | — | fig-03-decision-readout-laya-decision-model-explained.png | Bar charts of the returned probabilities for route, urgency and refund, each option's T equals 1 probability marked beside it |
| FIG_04 | assets/fig-04-three-ways-laya-decision-model-explained.png | placed | Q4 — decode steps and passes drawn to count in three columns; a comparison, not a graph | — | — | fig-04-three-ways-laya-decision-model-explained.png | Three columns comparing a classifier, an LLM in JSON mode and Laya by who declares options, passes, output tokens and probabilities |
| FIG_05 | assets/fig-05-option-budget-laya-decision-model-explained.png | plot | Q1/Q4 — exact output of laya's own build_sequence over 1–140 options (V7) | — | — | fig-05-option-budget-laya-decision-model-explained.png | Line charts of tokens per option, question tokens and state room against option count for the 512 and 1,024 token budgets |
| FIG_06 | assets/fig-06-scoring-grid-laya-decision-model-explained.png | placed | Q4 — a grid of real values in small multiples, one block per question (V3) | — | — | fig-06-scoring-grid-laya-decision-model-explained.png | Three small grids per question showing logits, masked slots, logits divided by temperature and the resulting probabilities |
| FIG_07 | assets/fig-07-two-confidences-laya-decision-model-explained.png | plot | Q4 — exact curves of 1 − H/ln k against the top probability, with measured points (V7) | — | — | fig-07-two-confidences-laya-decision-model-explained.png | Bands of entropy-based confidence against top probability for 4 and 5 options beside the identity line, with our three answers marked |
| FIG_08 | assets/fig-08-laya-end-to-end-laya-decision-model-explained.png | mermaid | Q3 — the post's one end-to-end architecture view: 9 nodes, a branch and a merge (V9) | — | — | fig-08-laya-end-to-end-laya-decision-model-explained.png | Laya end to end: token ids, ModernBERT-large, type embedding, two head layers, marker gather, scorer, softmax, and an act head off CLS |
| FIG_09 | assets/fig-09-local-global-attention-laya-decision-model-explained.png | plot | Q4 — two masks on one 141 × 141 grid, cell for cell (V18) | — | — | fig-09-local-global-attention-laya-decision-model-explained.png | Two 141 by 141 attention masks for the route row, a band of half-width 64 and a full block, with the billing marker's row highlighted |
| FIG_10 | assets/fig-10-act-head-saturation-laya-decision-model-explained.png | plot | Q1 — measured norms and logits; log scale for the norms | — | — | fig-10-act-head-saturation-laya-decision-model-explained.png | Log-scale bars of the CLS vector norm after the backbone and after the head for each question row, and the act and escalate logits |
| FIG_11 | assets/fig-11-parameter-accounting-laya-decision-model-explained.png | chart | Q1 — parameter counts from the loaded checkpoint, to scale (V14) | — | — | fig-11-parameter-accounting-laya-decision-model-explained.png | Horizontal bar of Laya's parameters by component, GeGLU MLP largest, then attention, embeddings and the decision head, totalling 421,293,827 |
| FIG_12 | assets/fig-12-three-checkpoints-laya-decision-model-explained.png | plot | Q1 — measured probabilities from three checkpoints as small multiples (V25) | — | — | fig-12-three-checkpoints-laya-decision-model-explained.png | Small multiples of route, urgency and refund probabilities for the laya, laya-multilingual and laya-typed-decisions checkpoints |
| FIG_13 | assets/fig-13-lineage-laya-decision-model-explained.png | placed | Q4/Q5 — a timeline whose value is the exact input format of each method | — | — | fig-13-lineage-laya-decision-model-explained.png | Timeline from BERT 2019 to Laya 2026 showing each method's input format for the route question, with marker tokens highlighted |

## Lab files

Upload each file under its key with an accurate `Content-Type` and, where the upload tool allows,
`Content-Disposition: attachment`. The lab is Tier B: CPU PyTorch in a pinned environment.

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/laya-decision-model-explained/README.md` | the environment, run order, expected output, download sizes and cleanup |
| LAB_02 | `lab/requirements.txt` | `labs/laya-decision-model-explained/requirements.txt` | pinned packages: laya 0.3.20, CPU PyTorch 2.14.0, transformers 5.17.0 |
| LAB_03 | `lab/trace_laya.py` | `labs/laya-decision-model-explained/trace_laya.py` | traces the ticket with forward hooks, checks probabilities, counts parameters, sweeps the budget, and traces all three checkpoints with --all |
| LAB_04 | `lab/trace.json` | `labs/laya-decision-model-explained/trace.json` | the captured output of trace_laya.py --all that every figure reads |
