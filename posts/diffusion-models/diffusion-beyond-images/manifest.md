# Asset manifest — diffusion-beyond-images

Series `diffusion-models`, part 10. **Status: local draft assets ready for upload.** Upload the PNGs
and the six lab files to the public `media` bucket under the versioned object keys below, write the
resulting URLs to `urls.txt` in table order (images first, then `LAB_01`–`LAB_06`), then run
`fill_urls.py`. Upload the lab zip separately to the bucket root (see **Lab files**).

Nothing here has been published, so every object key stays at `v1`.

Ten figures and the cover are our own work; Figure 10 is the paper's own. The `source` route was
considered first for every paper-backed figure (ledger, **Figure candidates**): MVDream's Figure 1 (F1)
is CC BY 4.0 and shows the Janus problem itself, so it ships unchanged, cropped from the arXiv v4 PDF
(page 2) at 400 dpi to the figure and its panel labels, caption excluded, nothing inside it altered
(sha1 aa583ebc5595…). PYoCo's Figure 2, MCF's Figure 5 and GeoDiff's Figure 1 are CC BY 4.0 but would
repeat a point the prose or another figure already carries (F2–F4); the VDM, Align your Latents,
DreamFusion and ProlificDreamer figures carry only arXiv's non-exclusive licence (F5), so the post draws
its own figures from its lab and from the papers' stated shapes.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | placed | template cover in the series house layout: the joint model's turning clip above a per-frame clip that flickers; a template build, not an external generator | — | — | blog/diffusion-beyond-images/cover-v1.png | Four frames of a crescent turning a quarter turn each, above four frames sampled one at a time that flicker and jump |
| FIG_01 | assets/fig-01-numbers-per-sample.png | chart | Q1 — counts computed from the papers' stated configurations (lab `census`), one bar per sample type on a log axis | — | — | blog/diffusion-beyond-images/fig-01-numbers-per-sample-v1.png | Log-scale bars of numbers per sample, from 7.9 torsion angles and a 261-number molecule to 24.8 million for 14 video frames |
| FIG_02 | assets/fig-02-one-step-four-readings.png | placed | Q4 — a grid of real values laid out four ways, side by side | — | — | blog/diffusion-beyond-images/fig-02-one-step-four-readings-v1.png | One forward step on Part 1's 16 numbers, and the clean values as a 4x4 image, a 16-sample waveform, four 1x4 frames and eight 2-D points |
| FIG_03 | assets/fig-03-frame-by-frame-vs-joint.png | chart | Q1 — lab measurements, 4,096 clips per scheme, with each scheme's first clip as tiles | — | — | blog/diffusion-beyond-images/fig-03-frame-by-frame-vs-joint-v1.png | Bars for 4,096 clips per noise scheme: independent noise flickers, correlated noise freezes, warped noise and the joint model move |
| FIG_04 | assets/fig-04-video-denoiser-block.png | placed | Q5 — 5 nodes in one path, no crossings; a tensor shape on every edge and a computed cost box need hand placement | — | — | blog/diffusion-beyond-images/fig-04-video-denoiser-block-v1.png | Video denoiser block: latent clip 14x4x72x128, spatial layers per frame, temporal layers per pixel across frames, shapes on edges |
| FIG_05 | assets/fig-05-audio-to-scale.png | placed | Q4 — the three representations' lengths and DiffWave's reach must be drawn to scale | — | — | blog/diffusion-beyond-images/fig-05-audio-to-scale-v1.png | One 10-second clip drawn to scale as 160,000 waveform samples, 64,000 mel values and 32,000 latent values, with a 0.38 s reach |
| FIG_06 | assets/fig-06-equivariance-on-qm9.png | chart | Q1 — quoted numbers from one table (ledger L44), the gap to the data computed from them | — | — | blog/diffusion-beyond-images/fig-06-equivariance-on-qm9-v1.png | Bars of QM9 molecule stability: non-equivariant 63.2%, rotation-augmented 71.6%, equivariant EDM 82.0%, training data 95.2% |
| FIG_07 | assets/fig-07-noise-on-a-circle.png | plot | Q4 — densities computed on the circle (lab `census`), curves against a uniform reference | — | — | blog/diffusion-beyond-images/fig-07-noise-on-a-circle-v1.png | Wrapped normal densities on a circle at three noise levels flattening toward uniform, beside line Gaussians that spread past one turn |
| FIG_08 | assets/fig-08-score-distillation-loop.png | placed | Q5 — 6 nodes and 2 inputs in one loop, no crossings; a quantity on every edge | — | — | blog/diffusion-beyond-images/fig-08-score-distillation-loop-v1.png | Score distillation loop: NeRF parameters, render at a random camera, add noise, frozen 2-D denoiser with guidance, residual back |
| FIG_09 | assets/fig-09-sds-on-crescent-world.png | chart | Q1 — lab measurements: every SDS run's final contrast, ancestral ranges, and three spreads | — | — | blog/diffusion-beyond-images/fig-09-sds-on-crescent-world-v1.png | SDS on crescent world: contrast and spread of 256 runs per guidance weight against ancestral samples; SDS collapses and saturates |
| FIG_10 | assets/fig-10-janus-and-content-drift.png | source | source check — the paper's own Figure 1 is the failure the section describes, and its arXiv record is CC BY 4.0 (ledger F1) | Shi, Wang, Ye, Long, Li & Yang, MVDream: Multi-view Diffusion for 3D Generation, ICLR 2024, Figure 1, https://arxiv.org/abs/2308.16512 (file: arXiv v4 PDF, page 2) | CC BY 4.0 (arXiv record); reproduced unchanged, cropped to the figure, credited in the caption | blog/diffusion-beyond-images/fig-10-janus-and-content-drift-v1.png | MVDream's Figure 1: a generated horse with two faces across four views, and fried chicken that turns into waffles across views |
| FIG_11 | assets/fig-11-forecasting-by-replacement.png | chart | Q1 — lab measurements, 4,096 clips per setting, with one stored forecast as tiles | — | — | blog/diffusion-beyond-images/fig-11-forecasting-by-replacement-v1.png | Coherent forecasts from 1, 2 or 3 observed frames: replacement 17%, 63%, 96% against exact conditioning 99% at every count |

## Lab files

**Lab grade:** G1 · runs anywhere (numpy only; the full run takes about a minute on one core).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/diffusion-beyond-images/README-v1.md` | grade, provenance, run order, the E1–E4 exercise ladder, cleanup |
| LAB_02 | `lab/beyond.py` | `labs/diffusion-beyond-images/beyond-v1.py` | crescent world in motion, exact frame and clip denoisers, noise schemes, forecasting, SDS and the size census, in numpy |
| LAB_03 | `lab/requirements.txt` | `labs/diffusion-beyond-images/requirements-v1.txt` | the pinned numpy version |
| LAB_04 | `lab/captures.json` | `labs/diffusion-beyond-images/captures-v1.json` | the author's run, machine-readable; every measured figure reads it |
| LAB_05 | `lab/expected-output.txt` | `labs/diffusion-beyond-images/expected-output-v1.txt` | the author's run as printed |
| LAB_06 | `lab/notebook.ipynb` | `labs/diffusion-beyond-images/notebook-v1.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-diffusion-beyond-images.zip` | `lab-diffusion-beyond-images.zip` (bucket root) | every lab file in one zip; its final URL is already written in `blog.md` |

Upload with accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

## Series links to add

The owner adds these links; the post names them in plain text only. On 2026-10-09 the owner asked for
earlier parts to be named by title whether or not they are live yet.

| Post | Status on 2026-10-21 | Where it is named |
|---|---|---|
| Part 1 — What a Diffusion Model Actually Does | published | the "You need" line; frontmatter `prerequisites` ("Part 1 of this series"); later mentions ("Part 1's recipe", "Part 1's 4×4 patch", "Part 1's training loss") need no link |
| Part 2 — Diffusion Model Architecture: The Complete Guide | not published | *The problem*, the paragraph after Figure 1 ("introduced in Part 2 of this series, Diffusion Model Architecture: The Complete Guide") |
| Part 4 — Diffusion Backbones: U-Net to DiT, Block by Block | not published | *How do video models let frames see each other?*, first paragraph ("Part 4 of this series, Diffusion Backbones: U-Net to DiT, Block by Block, counts its cost") |
| Part 6 — Diffusion Samplers and Solvers: 1,000 Steps Into 20 | not published | *What can correlated noise buy?* ("DDIM, the one Part 6 of this series, Diffusion Samplers and Solvers: 1,000 Steps Into 20, analyses") |
| Part 8 — Controlling Diffusion Models: Guidance, ControlNet, LoRA | not published | *How do you make 3-D objects without 3-D data?*, second paragraph ("w = 101 in Part 8's convention (Controlling Diffusion Models: Guidance, ControlNet, LoRA)"); the later "Part 8's lesson" in the time-series section needs no link |
| Part 9 — Evaluating Generative Models: What FID Measures and Hides | not published | *Why this matters* ("Part 9 of this series, Evaluating Generative Models: What FID Measures and Hides, explains FID") |

Parts 3, 5 and 7 are not named; the post does not depend on them. Later parts are not named: denoising
categories directly "comes later in this series".

## Editable sources kept

| Route | File kept | Rebuild with |
|---|---|---|
| `placed`, `plot`, `chart` | `assets/_figures.py` (shared helpers in `assets/_build.py`) plus each figure's exported `.html` and `.svg` | `python3 assets/_figures.py` |
| `source` | `assets/fig-10-janus-and-content-drift.png`, the paper's figure as cropped; the crop command is in `fig10()`'s docstring | `python3 assets/_figures.py 10` checks it is in place |
| cover | `assets/cover.html` and `assets/cover-prompt.md` | `python3 assets/_figures.py cover` |
| social | `assets/_social.py` plus each card's `.html` and `.svg` under `assets/social/` | `python3 assets/_social.py`, then `render_social.py` |

`_figures.py` and `_social.py` read every measured and computed number from `lab/captures.json`, the
capture the article's lab download ships, and check every alt text against `blog.md`, so prose, figures
and lab cannot drift apart. Figure 6 draws EDM's quoted numbers from one dict, with its ledger key.

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-models/diffusion-beyond-images/ urls.txt
```

Do not overwrite a published object. Nothing in this manifest is published yet; once it is, a
re-rendered asset keeps its object key and the Cloudflare cache for that key is purged after upload.
