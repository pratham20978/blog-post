# Asset manifest — discrete-diffusion-language-models

Series `diffusion-models`, part 11. **Status: local draft assets ready for upload.** Upload the PNGs
and the six lab files to the public `media` bucket under the versioned object keys below, write the
resulting URLs to `urls.txt` in table order (images first, then `LAB_01`–`LAB_06`), then run
`fill_urls.py`. Upload the lab zip separately to the bucket root (see **Lab files**).

Nothing here has been published, so every object key stays at `v1`.

Nine figures and the cover are our own work; Figure 6 is the survey's own. The `source` route was
considered first for every paper-backed figure (ledger, **Figure candidates**): the survey's Figure 7 (F1)
is CC BY 4.0 and shows parallel decoding failing on a real 8B model, so it ships unchanged, rendered from
the arXiv v3 PDF (page 20) at 400 dpi and cropped to the figure and its panel labels, caption excluded,
nothing inside it altered (sha1 fb21d2ee03a6…). MDLM's Figure 1 is CC BY 4.0 but is a graphical abstract
whose right half is a word cloud and whose transparent background loses its text on dark pages (F2);
SEDD's Figure 1 shows the generative-perplexity curve that Zheng et al. attribute to the precision fault
(F3); D3PM's figures carry CC BY-NC-SA 4.0 and LLaDA's and Zheng et al.'s only arXiv's non-exclusive
licence (F4), so the post draws its own figures from its lab and from the papers' tables.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | placed | template cover in the series house layout: one crescent image written in random order, 16, 32, 48 and 64 of its 64 tokens; a template build, not an external generator | — | — | blog/discrete-diffusion-language-models/cover-v1.png | Four 8 by 8 token grids unmasking a crescent in random order: 16, 32, 48 and all 64 tokens written, masked cells hatched |
| FIG_01 | assets/fig-01-tokens-forward-step.png | placed | Q4 — grids of real values (the patch, its tokens, Part 1's ε and the mask it decides) side by side, plus one token's transition odds | — | — | blog/discrete-diffusion-language-models/fig-01-tokens-forward-step-v1.png | Part 1's patch as 16 grey-level tokens, Part 1's noise draw marking 7 of them masked at abar 0.64, and uniform replacement's odds |
| FIG_02 | assets/fig-02-four-turn-world-decoding.png | placed | Q4 — small multiples of real token grids and per-position probabilities, with a three-step decoding trace | — | — | blog/discrete-diffusion-language-models/fig-02-four-turn-world-decoding-v1.png | Four quarter turns of the patch, per-position probabilities with all 16 masked, decoding one token at a time, and one all-at-once draw |
| FIG_03 | assets/fig-03-absorbing-beats-uniform.png | chart | Q1 — quoted numbers from one table (ledger L13), five models on five datasets, one lane per model | — | — | blog/discrete-diffusion-language-models/fig-03-absorbing-beats-uniform-v1.png | Zero-shot perplexity of GPT-2 small, SEDD absorbing, SEDD uniform, D3PM and Plaid on five datasets; absorbing beats uniform on all five |
| FIG_04 | assets/fig-04-llada-training-step.png | placed | Q5 — 6 stages in one path, no crossings; a shape or a formula on every edge (LLaDA's configuration, ledger L09, L44) | — | — | blog/discrete-diffusion-language-models/fig-04-llada-training-step-v1.png | One LLaDA training step: draw t, mask 4,096 tokens, a transformer without a causal mask, cross-entropy on masked tokens times 1/t |
| FIG_05 | assets/fig-05-valid-share-against-calls.png | chart | Q1 — lab measurements, 4,096 images per sampler, with each sampler's first samples as tiles | — | — | blog/discrete-diffusion-language-models/fig-05-valid-share-against-calls-v1.png | Share of valid images against network calls: one token per call is exact; 2, 4 and 8 per call fail; ancestral steps; a threshold |
| FIG_06 | assets/fig-06-llada-answers-by-step-count.png | source | source check — the survey's own Figure 7 is the failure on a real model that the section describes, and its arXiv record is CC BY 4.0 (ledger F1) | Li, Chen, Guo & Shen, A Survey on Diffusion Language Models, arXiv:2508.10875 (v3), Figure 7, https://arxiv.org/abs/2508.10875 (file: arXiv v3 PDF, page 20) | CC BY 4.0 (arXiv record); reproduced unchanged, cropped to the figure, credited in the caption | blog/discrete-diffusion-language-models/fig-06-llada-answers-by-step-count-v1.png | LLaDA and MMaDA answers to one prompt at several step counts: correct with 1 or 2 tokens per step, wrong or garbled with more |
| FIG_07 | assets/fig-07-llada-against-llama3.png | chart | Q1 — quoted numbers from one table under one protocol (ledger L45) | — | — | blog/discrete-diffusion-language-models/fig-07-llada-against-llama3-v1.png | LLaDA 8B Base against LLaMA 3 8B Base on 15 benchmarks: ahead on math and Chinese, behind on BBH, HellaSwag, PIQA and MBPP |
| FIG_08 | assets/fig-08-llada-remasking-ablation.png | chart | Q1 — quoted numbers from one table (ledger L37) | — | — | blog/discrete-diffusion-language-models/fig-08-llada-remasking-ablation-v1.png | LLaDA 8B Base with random against low-confidence remasking: BBH, GSM8K, Math, HumanEval and MBPP all rise with low confidence |
| FIG_09 | assets/fig-09-decoders-that-do-not-sample.png | chart | Q1 — lab measurements, 4,096 images per decoder, with each decoder's first samples as tiles | — | — | blog/discrete-diffusion-language-models/fig-09-decoders-that-do-not-sample-v1.png | Images found of 72 and brightness spread for five one-token-per-step decoders with sample tiles; ranking by the drawn token collapses |
| FIG_10 | assets/fig-10-float32-race.png | chart | Q1 — lab measurements of the race in two precisions against the closed form, beside quoted numbers from one table (ledger L02) | — | — | blog/discrete-diffusion-language-models/fig-10-float32-race-v1.png | Share of its fair chance a token wins MDLM's race against the mask, float32 against float64, with the closed form and Zheng's ablation |

## Lab files

**Lab grade:** G1 · runs anywhere (numpy only; the full run takes about two minutes on one core).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/discrete-diffusion-language-models/README-v1.md` | grade, provenance, run order, the E1–E4 exercise ladder, cleanup |
| LAB_02 | `lab/tokens.py` | `labs/discrete-diffusion-language-models/tokens-v1.py` | crescent world as tokens with its exact denoiser, the worked example, every sampler in the article and the float32 race, in numpy |
| LAB_03 | `lab/requirements.txt` | `labs/discrete-diffusion-language-models/requirements-v1.txt` | the pinned numpy version |
| LAB_04 | `lab/captures.json` | `labs/discrete-diffusion-language-models/captures-v1.json` | the author's run, machine-readable; every measured figure reads it |
| LAB_05 | `lab/expected-output.txt` | `labs/discrete-diffusion-language-models/expected-output-v1.txt` | the author's run as printed |
| LAB_06 | `lab/notebook.ipynb` | `labs/discrete-diffusion-language-models/notebook-v1.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-discrete-diffusion-language-models.zip` | `lab-discrete-diffusion-language-models.zip` (bucket root) | every lab file in one zip; its final URL is already written in `blog.md` |

Upload with accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

## Series links to add

The owner adds these links; the post names them in plain text only. On 2026-10-09 the owner asked for
earlier parts to be named by title whether or not they are live yet.

| Post | Status on 2026-10-22 | Where it is named |
|---|---|---|
| Part 1 — What a Diffusion Model Actually Does | published | the "You need" line; frontmatter `prerequisites` ("Part 1 of this series"); later mentions ("Part 1's forward step", "Part 1's 4×4 patch", "Part 1's own noise draw") need no link |
| Part 3 — Where the Diffusion MSE Loss Comes From | not published | *What does a masked diffusion model learn?*, second paragraph ("the variational bound that Part 3 of this series, Where the Diffusion MSE Loss Comes From, derives for Gaussian diffusion") |
| Part 6 — Diffusion Samplers and Solvers: 1,000 Steps Into 20 | not published | *How does it write, and why does parallel decoding break?*, first paragraph ("the NFE of Part 6 of this series, Diffusion Samplers and Solvers: 1,000 Steps Into 20") |
| Part 9 — Evaluating Generative Models: What FID Measures and Hides | not published | *Why is sampler correctness contested?*, last subsection ("Part 9 of this series, Evaluating Generative Models: What FID Measures and Hides, makes the same point about images") |
| Part 10 — Diffusion Beyond Images: Video, Audio, 3-D and Molecules | not published | *The problem*, first paragraph ("Part 10 of this series, Diffusion Beyond Images: Video, Audio, 3-D and Molecules, met the same wall with atom types") |

Parts 2, 4, 5, 7 and 8 are not named; the post does not depend on them. Later parts are not named.

## Editable sources kept

| Route | File kept | Rebuild with |
|---|---|---|
| `placed`, `chart` | `assets/_figures.py` (shared helpers in `assets/_build.py`) plus each figure's exported `.html` and `.svg` | `python3 assets/_figures.py` (needs numpy, for the validity marks) |
| `source` | `assets/fig-06-llada-answers-by-step-count.png`, the survey's figure as cropped; the render and crop are in `fig06()`'s docstring | `python3 assets/_figures.py 6` checks it is in place |
| cover | `assets/cover.html` and `assets/cover-prompt.md` | `python3 assets/_figures.py cover` |
| social | `assets/_social.py` plus each card's `.html` and `.svg` under `assets/social/` | `python3 assets/_social.py`, then `render_social.py` |

`_figures.py` and `_social.py` read every measured and computed number from `lab/captures.json`, the
capture the article's lab download ships, and `_figures.py` checks every alt text against `blog.md`, so
prose, figures and lab cannot drift apart. The quoted tables (SEDD's Table 1, LLaDA's Tables 1 and 9,
Zheng et al.'s Table 2) are each typed once, beside their ledger keys. `lint_visuals.py` reports four
arrows as touching no node: they end exactly on 30–34 px token cells, below its 60 × 40 node size.
`_overlap.py`'s remaining reports are its known false positives (rotated axis titles; on the cards, the
serif title lines and the lockup's `.in`).

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-models/discrete-diffusion-language-models/ urls.txt
```

Do not overwrite a published object. Nothing in this manifest is published yet; once it is, a
re-rendered asset keeps its object key and the Cloudflare cache for that key is purged after upload.
