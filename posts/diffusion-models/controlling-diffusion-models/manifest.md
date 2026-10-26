# Asset manifest — controlling-diffusion-models

Series `diffusion-models`, part 8. **Status: local draft assets ready for upload.** Upload the
PNGs and the six lab files to the public `media` bucket under the versioned object keys below,
write the resulting URLs to `urls.txt` in table order (images first, then `LAB_01`–`LAB_06`), then
run `fill_urls.py`. Upload the lab zip separately to the bucket root (see **Lab files**).

Nothing here has been published, so every object key stays at `v1`.

Thirteen figures and the cover are our own work; Figure 14 is the paper's own. The `source` route
was considered first for every paper-backed figure: of the five candidates in `research/ledger.md`
under **Figure candidates**, InstructPix2Pix's Figure 2 (F1) is CC BY 4.0 and is the method itself,
so it ships unchanged (copied byte for byte from arxiv.org/html/2211.09800v2/method.png); ControlNet's
and the guidance-interval paper's figures (F3, F4) carry only arXiv's non-exclusive licence, so the
post draws its own; DreamBooth's Figure 3 (F2) is CC BY 4.0 but the section's point is measured, not
drawn; Ho & Salimans' tables (F5) are numbers, charted as our own figure with credit.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | placed | template cover in the series house layout — the worked example's guided paths beside one exact-model sample at four guidance weights; a template build, not an external generator | — | — | blog/controlling-diffusion-models/cover-v1.png | Guided paths overshooting the strongest crescent beside one crescent sample that turns from faint to strong as the guidance weight grows |
| FIG_01 | assets/fig-01-guidance-moves-the-decision.png | plot | Q1/Q4 — closed-form paths of the one-number world at two guidance weights | — | — | blog/controlling-diffusion-models/fig-01-guidance-moves-the-decision-v1.png | Fifteen paths of the requested crescent's contrast: unguided they split between faint and strong; at w = 3 all but one end strong |
| FIG_02 | assets/fig-02-three-places-to-add-a-condition.png | mermaid | Q3 — 13 nodes in three parallel branches, every edge labelled with the condition it carries | — | — | blog/controlling-diffusion-models/fig-02-three-places-to-add-a-condition-v1.png | Map of control methods in three places: the sampler's arithmetic, new inputs to a frozen network, and changed weights, each with its cost |
| FIG_03 | assets/fig-03-guided-samples.png | placed | Q4 — real 8×8 samples from the exact model, the same noises at four weights | — | — | blog/controlling-diffusion-models/fig-03-guided-samples-v1.png | Ten 8x8 crescent samples at guidance weights 1, 2, 3 and 5: faint crescents turn strong and the strong ones brighten past the data |
| FIG_04 | assets/fig-04-what-guidance-costs.png | chart | Q1 — lab measurements: faint share, blends and over-saturation against w for three models | — | — | blog/controlling-diffusion-models/fig-04-what-guidance-costs-v1.png | Faint share, blends and over-saturated share against guidance weight for the exact model, a trained network and a weaker network |
| FIG_05 | assets/fig-05-published-guidance-curves.png | chart | Q1 — quoted table numbers with their setup (ledger F5) | data from Ho & Salimans, Classifier-Free Diffusion Guidance, arXiv:2207.12598, Tables 1–2 (L08, L09) | redrawn from published numbers | blog/controlling-diffusion-models/fig-05-published-guidance-curves-v1.png | Quoted FID and Inception Score against guidance strength on ImageNet 64 and 128: FID is lowest at a little guidance, IS keeps rising |
| FIG_06 | assets/fig-06-where-guidance-decides.png | chart | Q1 — lab measurements: faint share with guidance on only above or only below a noise level | — | — | blog/controlling-diffusion-models/fig-06-where-guidance-decides-v1.png | Faint share with guidance only above, or only below, a noise level: the faint/strong decision happens between sigma 2 and 20 |
| FIG_07 | assets/fig-07-fixes-compared.png | chart | Q1 — lab measurements: every guidance variant in one plane on the trained network | — | — | blog/controlling-diffusion-models/fig-07-fixes-compared-v1.png | Blends against faint share for CFG, autoguidance, guidance intervals, CFG-rescale and APG on the trained network |
| FIG_08 | assets/fig-08-controlnet-on-sd15.png | mermaid | Q3 — the post's one architecture view: 16 nodes, skips and zero convolutions crossing into the decoder | — | — | blog/controlling-diffusion-models/fig-08-controlnet-on-sd15-v1.png | Stable Diffusion 1.5 with a ControlNet: frozen U-Net, a trainable copy of its encoder, and 13 zero convolutions feeding its skip connections |
| FIG_09 | assets/fig-09-zero-init-vs-gaussian.png | chart | Q1 — lab measurements: control error and sample distance over ControlNet training, two inits × two seeds | — | — | blog/controlling-diffusion-models/fig-09-zero-init-vs-gaussian-v1.png | ControlNet training: zero-initialised connectors start as the frozen model and learn the layout; Gaussian ones start damaged |
| FIG_10 | assets/fig-10-what-each-method-trains.png | chart | Q1 — computed parameter counts (census) with two quoted adapter sizes (L40, L41) | adapter sizes as quoted by Mou et al. (T2I-Adapter) and Ye et al. (IP-Adapter) | redrawn from published numbers | blog/controlling-diffusion-models/fig-10-what-each-method-trains-v1.png | Trainable parameters per control method on SD 1.5, log scale, from 859.5 million for the full U-Net down to 768 for textual inversion |
| FIG_11 | assets/fig-11-personalisation-costs.png | chart | Q1 — lab measurements: five personalisation recipes, two seeds | — | — | blog/controlling-diffusion-models/fig-11-personalisation-costs-v1.png | Subject share, drift of the plain class, other classes' sample distance and the subject's brightness spread for each personalisation method |
| FIG_12 | assets/fig-12-inpainting-coherence.png | placed | Q4 — real 8×8 completions from the lab beside measured coherence bars | — | — | blog/controlling-diffusion-models/fig-12-inpainting-coherence-v1.png | Right-half completions of four crescents by replacement, resampling, a network with mask inputs and the exact posterior, with coherence |
| FIG_13 | assets/fig-13-sdedit-vs-inversion.png | chart | Q1 — lab measurements against the closed form τ/√(τ²+σ₀²) | — | — | blog/controlling-diffusion-models/fig-13-sdedit-vs-inversion-v1.png | SDEdit's ghost of the old crescent and its kept detail fall together with starting noise; DDIM inversion keeps the detail, no ghost |
| FIG_14 | assets/fig-14-instructpix2pix-pipeline.png | source | source check — the paper's own Figure 2 is the method this paragraph describes, and its arXiv record is CC BY 4.0 (ledger F1) | Brooks, Holynski & Efros, InstructPix2Pix: Learning to Follow Image Editing Instructions, CVPR 2023, Figure 2, https://arxiv.org/abs/2211.09800 | CC BY 4.0 (arXiv record); reproduced unchanged, credited in the caption | blog/controlling-diffusion-models/fig-14-instructpix2pix-pipeline-v1.png | InstructPix2Pix's pipeline: GPT-3 writes edits, Stable Diffusion with Prompt-to-Prompt renders image pairs, a diffusion model learns to edit |

## Lab files

**Lab grade:** G1 · runs anywhere (CPU PyTorch and numpy; diffusers only for the optional census).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/controlling-diffusion-models/README-v1.md` | grade, provenance, run order, the E1–E5 exercise ladder, cleanup |
| LAB_02 | `lab/control.py` | `labs/controlling-diffusion-models/control-v1.py` | crescent world's exact denoisers, the trained networks, every control method and experiment |
| LAB_03 | `lab/requirements.txt` | `labs/controlling-diffusion-models/requirements-v1.txt` | the pinned numpy and CPU PyTorch versions, and the optional diffusers |
| LAB_04 | `lab/captures.json` | `labs/controlling-diffusion-models/captures-v1.json` | the author's run, machine-readable; every measured figure reads it |
| LAB_05 | `lab/expected-output.txt` | `labs/controlling-diffusion-models/expected-output-v1.txt` | the author's run as printed |
| LAB_06 | `lab/notebook.ipynb` | `labs/controlling-diffusion-models/notebook-v1.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-controlling-diffusion-models.zip` | `lab-controlling-diffusion-models.zip` (bucket root) | every lab file in one zip; its final URL is already written in `blog.md` |

Upload with accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`,
`application/json`, `application/x-ipynb+json`) and, where the upload path supports object
metadata, `Content-Disposition: attachment; filename="<name>"`.

## Series links to add

The owner adds these links; the post names them in plain text only. On 2026-10-09 the owner asked
for earlier parts to be named by title whether or not they are live yet.

| Post | Status on 2026-10-18 | Where it is named |
|---|---|---|
| Part 1 — What a Diffusion Model Actually Does | published | not named; the post does not depend on it |
| Part 2 — Diffusion Model Architecture: The Complete Guide | not published | not named |
| Part 3 — Where the Diffusion MSE Loss Comes From | not published | not named |
| Part 4 — Diffusion Backbones: U-Net to DiT, Block by Block | not published | *How does ControlNet add a condition…*, first paragraph ("with the U-Net's skips from Part 4 of this series, Diffusion Backbones: U-Net to DiT, Block by Block") |
| Part 5 — Training a Diffusion Model: The Decisions Before Step One | not published | *The problem*, the lab paragraph ("Part 5 is Training a Diffusion Model: The Decisions Before Step One"); later mentions say "Part 5" and need no link |
| Part 6 — Diffusion Samplers and Solvers: 1,000 Steps Into 20 | not published | the "You need" line; frontmatter `prerequisites`; *The problem* opens with "Part 6 framed sampling…" |
| Part 7 — Few-Step Diffusion and Distillation: 20 Steps Into 1 | not published | *Which fixes keep guidance's benefit?*, last paragraph ("the progressive distillation of Part 7 of this series, Few-Step Diffusion and Distillation: 20 Steps Into 1") |

The post names no later part; it defers FID's limits by comparing scores only within one paper's table.

## Editable sources kept

| Route | File kept | Rebuild with |
|---|---|---|
| `placed`, `plot`, `chart` | `assets/_figures.py` (shared helpers in `assets/_build.py`) plus each figure's exported `.html` and `.svg` | `python3 assets/_figures.py` |
| `mermaid` | `assets/fig-02-three-places-to-add-a-condition.mmd`, `assets/fig-08-controlnet-on-sd15.mmd` | `python3 assets/_mermaid.py` |
| `source` | `assets/fig-14-instructpix2pix-pipeline.png`, the paper's file unchanged | — |
| cover | `assets/cover.html` and `assets/cover-prompt.md` | `python3 assets/_figures.py cover` |
| social | `assets/_social.py` plus each card's `.html` and `.svg` under `assets/social/` | `python3 assets/_social.py`, then `render_social.py` |

`_figures.py` and `_social.py` read every measured and computed number from `lab/captures.json`,
the capture the article's lab download ships, so prose, figures and lab cannot drift apart. The quoted
numbers (Ho & Salimans' Tables 1–2, the two adapter sizes) are typed once in `_figures.py`, next to
their ledger keys.

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-models/controlling-diffusion-models/ urls.txt
```

Do not overwrite a published object. Nothing in this manifest is published yet; once it is, a
re-rendered asset keeps its object key and the Cloudflare cache for that key is purged after upload.
