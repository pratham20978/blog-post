# Asset manifest — few-step-diffusion-distillation

Series `diffusion-models`, part 7. **Status: local draft assets ready for upload.** Upload the
PNGs and the six lab files to the public `media` bucket under the versioned object keys below,
write the resulting URLs to `urls.txt` in table order (images first, then `LAB_01`–`LAB_06`), then
run `fill_urls.py`. Upload the lab zip separately to the bucket root (see **Lab files**).

Nothing here has been published, so every object key stays at `v1`.

All ten figures and the cover are our own work. The `source` route was considered first for every
paper-backed figure: of the three candidates recorded in `research/ledger.md` under **Figure
candidates**, CTM's Figure 2 and DMD2's Figure 8 carry only arXiv's non-exclusive licence (F1, F3),
so the post measures its own versions instead, and the shortcut paper's Table 1 is numbers, charted
as our own figure with credit (F2). Two figures chart quoted table numbers, each credited in its
caption.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | placed | template cover in the series house layout — the worked example's exact step against a fitted student's ramp, beside lab samples from the exact path, one DDIM call and a one-call student; a template build, not an external generator | — | — | blog/few-step-diffusion-distillation/cover-v1.png | The exact endpoint of the path as a step against a student's ramp, beside crescent samples from the exact path, DDIM and a student |
| FIG_01 | assets/fig-01-the-cliff.png | plot | Q1/Q4 — closed-form exact endpoints, DDIM's one- and two-call maps and a least-squares fit on the worked example's one number | — | — | blog/few-step-diffusion-distillation/fig-01-the-cliff-v1.png | Endpoint against starting noise between two crescents: the exact map jumps at zero, DDIM and a fitted network make ramps across it |
| FIG_02 | assets/fig-02-where-each-target-comes-from.png | mermaid | Q3 — 13 nodes in two families joined at the teacher, sorted by where each method's training target comes from | — | — | blog/few-step-diffusion-distillation/fig-02-where-each-target-comes-from-v1.png | Method family tree: path-followers take targets from teacher steps or their own jumps; distribution matchers from scores and real images |
| FIG_03 | assets/fig-03-students-against-solvers.png | chart | Q1 — lab measurements: sample distance and blends against calls for the students and two exact-denoiser solvers | — | — | blog/few-step-diffusion-distillation/fig-03-students-against-solvers-v1.png | Sample distance and blends against calls: progressive distillation's students beat DDIM and DPM-Solver++ with the exact denoiser |
| FIG_04 | assets/fig-04-one-call-samples.png | placed | Q4 — real 8×8 samples from the lab, near and far from a decision boundary | — | — | blog/few-step-diffusion-distillation/fig-04-one-call-samples-v1.png | Eight-by-eight samples from six noises: exact endpoints, DDIM and one-call students; near a decision boundary some blend or switch crescent |
| FIG_05 | assets/fig-05-errors-live-at-decisions.png | chart | Q1 — lab measurements: flips and blends by margin bin, with the share of noises per bin | — | — | blog/few-step-diffusion-distillation/fig-05-errors-live-at-decisions-v1.png | Flip and blend shares of one-call students by distance from a decision boundary: errors concentrate in the 13% of noises nearest one |
| FIG_06 | assets/fig-06-the-dmd-update.png | placed | Q5 — seven nodes with labelled edges, and the fake denoiser's own training loop beside the generator's update | — | — | blog/few-step-diffusion-distillation/fig-06-the-dmd-update-v1.png | DMD's update: a generated sample is noised and read by the frozen teacher and a fake denoiser; their difference moves the generator |
| FIG_07 | assets/fig-07-coverage-during-training.png | chart | Q1 — lab measurements: crescent coverage and mean brightness over DMD training; DMD2's own brightness plot is not reusable (ledger F3) | — | — | blog/few-step-diffusion-distillation/fig-07-coverage-during-training-v1.png | Crescent coverage during DMD training: every run collapses onto one crescent by update 100, then recovers; brightness drifts less at 5:1 |
| FIG_08 | assets/fig-08-one-network-any-step-count.png | chart | Q1 — lab measurements: sample distance and flips against calls for the shortcut, consistency and progressive students | — | — | blog/few-step-diffusion-distillation/fig-08-one-network-any-step-count-v1.png | Sample distance and flip share against calls: a shortcut model improves and stays paired; a consistency model's flips rise to 75% |
| FIG_09 | assets/fig-09-one-codebase-three-budgets.png | chart | Q1 — quoted table numbers with their setup (ledger F2) | data from Frans, Hafner, Levine & Abbeel, One Step Diffusion via Shortcut Models, ICLR 2025, Table 1 (L42) | redrawn from published numbers | blog/few-step-diffusion-distillation/fig-09-one-codebase-three-budgets-v1.png | Quoted FIDs at 128, 4 and 1 steps for six training objectives on CelebA-HQ and ImageNet 256: the shortcut model stays low at every budget |
| FIG_10 | assets/fig-10-precision-against-recall.png | chart | Q1 — quoted table numbers with their setup | data from Song & Dhariwal, Improved Techniques for Training Consistency Models, ICLR 2024, Table 3 (L57) | redrawn from published numbers | blog/few-step-diffusion-distillation/fig-10-precision-against-recall-v1.png | Quoted precision against recall on ImageNet 64: one-step PD loses precision, consistency training and a GAN lose recall |

## Lab files

**Lab grade:** G1 · runs anywhere (CPU PyTorch and numpy).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/few-step-diffusion-distillation/README-v1.md` | grade, provenance, run order, the E1–E4 exercise ladder, cleanup |
| LAB_02 | `lab/distill.py` | `labs/few-step-diffusion-distillation/distill-v1.py` | the exact crescent-world teacher, the solvers, every student and every experiment |
| LAB_03 | `lab/requirements.txt` | `labs/few-step-diffusion-distillation/requirements-v1.txt` | the pinned numpy and CPU PyTorch versions, with the install line |
| LAB_04 | `lab/captures.json` | `labs/few-step-diffusion-distillation/captures-v1.json` | the author's run, machine-readable; every measured figure reads it |
| LAB_05 | `lab/expected-output.txt` | `labs/few-step-diffusion-distillation/expected-output-v1.txt` | the author's run as printed |
| LAB_06 | `lab/notebook.ipynb` | `labs/few-step-diffusion-distillation/notebook-v1.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-few-step-diffusion-distillation.zip` | `lab-few-step-diffusion-distillation.zip` (bucket root) | every lab file in one zip; its final URL is already written in `blog.md` |

Upload with accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`,
`application/json`, `application/x-ipynb+json`) and, where the upload path supports object
metadata, `Content-Disposition: attachment; filename="<name>"`.

## Series links to add

The owner adds these links; the post names them in plain text only. On 2026-10-09 the owner asked
for earlier parts to be named by title whether or not they are live yet.

| Post | Status on 2026-10-16 | Where it is named |
|---|---|---|
| Part 1 — What a Diffusion Model Actually Does | published | *The problem*, second paragraph ("which Part 1 of this series, What a Diffusion Model Actually Does, called the averaging argument") |
| Part 2 — Diffusion Model Architecture: The Complete Guide | not published | not named; the post does not depend on it |
| Part 3 — Where the Diffusion MSE Loss Comes From | not published | not named; the post does not depend on it |
| Part 4 — Diffusion Backbones: U-Net to DiT, Block by Block | not published | not named; the post does not depend on it |
| Part 5 — Training a Diffusion Model: The Decisions Before Step One | not published | *The problem*, the bullet on the set ("the sliced Wasserstein distance of Part 5 of this series, Training a Diffusion Model: The Decisions Before Step One"); later mentions say "Part 5" and need no link |
| Part 6 — Diffusion Samplers and Solvers: 1,000 Steps Into 20 | not published | the "You need" line; *Why this matters* ("Part 6 of this series, Diffusion Samplers and Solvers: 1,000 Steps Into 20, took a trained model…"); frontmatter `prerequisites`; later mentions say "Part 6" and need no link |

The post points forward once, to "a later part of this series" on guidance (*Limitations*), without
a title; part 8 is not written.

## Editable sources kept

| Route | File kept | Rebuild with |
|---|---|---|
| `placed`, `plot`, `chart` | `assets/_figures.py` (shared helpers in `assets/_build.py`) plus each figure's exported `.html` and `.svg` | `python3 assets/_figures.py` |
| `mermaid` | `assets/fig-02-where-each-target-comes-from.mmd` | `python3 assets/_mermaid.py` |
| cover | `assets/cover.html` and `assets/cover-prompt.md` | `python3 assets/_figures.py cover` |
| social | `assets/_social.py` plus each card's `.html` and `.svg` under `assets/social/` | `python3 assets/_social.py`, then `render_social.py` |

`_figures.py` and `_social.py` read every measured and computed number from `lab/captures.json`,
the capture the article's lab download ships, so prose, figures and lab cannot drift apart. The
quoted tables (the shortcut paper's Table 1 and iCT's Table 3) are typed once in `_figures.py`,
next to their ledger keys.

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-models/few-step-diffusion-distillation/ urls.txt
```

Do not overwrite a published object. Nothing in this manifest is published yet; once it is, a
re-rendered asset keeps its object key and the Cloudflare cache for that key is purged after upload.
