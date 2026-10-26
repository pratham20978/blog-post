# Asset manifest — evaluating-generative-models

Series `diffusion-models`, part 9. **Status: local draft assets ready for upload.** Upload the
PNGs and the six lab files to the public `media` bucket under the versioned object keys below,
write the resulting URLs to `urls.txt` in table order (images first, then `LAB_01`–`LAB_06`), then
run `fill_urls.py`. Upload the lab zip separately to the bucket root (see **Lab files**).

Nothing here has been published, so every object key stays at `v1`.

Six figures and the cover are our own work; Figure 7 is the paper's own. The `source` route was
considered first for every paper-backed figure: of the six candidates in `research/ledger.md` under
**Figure candidates**, Stein et al.'s Figure 2 (F1) is CC BY 4.0 and is the evidence the section
argues from, so it ships unchanged (`assets/fig-07-human-error-vs-fid.svg` is the published SVG byte
for byte, sha1 a63ebdf1…; the PNG is that SVG rasterised at 2× in headless Chrome). Kynkäänniemi et
al.'s, Naeem et al.'s, Parmar et al.'s and Heusel et al.'s figures (F2, F3, F4, F6) carry only arXiv's
non-exclusive licence, so the post quotes their numbers and draws its own figures from its own lab;
SDXL's Figure 12 (F5) is CC BY 4.0 but would repeat Figure 7's point.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | placed | template cover in the series house layout: the worked example's real and moment-matched number lines beside the tied pair's samples; a template build, not an external generator | — | — | blog/evaluating-generative-models/cover-v1.png | Real and moment-matched crescent contrasts on number lines beside two crescent sample sets that share the same FD of 3.6221 |
| FIG_01 | assets/fig-01-fd-on-one-number.png | plot | Q4 — real values on number lines per generator, with the two FD terms printed beside each | — | — | blog/evaluating-generative-models/fig-01-fd-on-one-number-v1.png | Number lines of eight real crescent contrasts and three generators, with each generator's mean, spread and Fréchet distance |
| FIG_02 | assets/fig-02-how-fid-is-computed.png | placed | Q5 — 9 nodes in two parallel chains, no crossings; a shape on every edge and five protocol tags need hand placement | — | — | blog/evaluating-generative-models/fig-02-how-fid-is-computed-v1.png | FID pipeline: real and generated images resized to 299 px, Inception-v3 pool3 features, means and covariances, one Fréchet distance |
| FIG_03 | assets/fig-03-same-fd-different-failures.png | placed | Q4 — real 8×8 samples from the lab beside measured FD, precision, recall and coverage | — | — | blog/evaluating-generative-models/fig-03-same-fd-different-failures-v1.png | 8x8 samples from five generators with FD, precision, recall and coverage: drops-faint and grainy tie at FD 3.6221 |
| FIG_04 | assets/fig-04-one-stray-sample-buys-recall.png | plot | Q4 — k-NN balls drawn as intervals on a number line, computed by the lab | — | — | blog/evaluating-generative-models/fig-04-one-stray-sample-buys-recall-v1.png | Number line of real and generated contrasts with k-NN balls: one stray generated sample's wide ball lifts recall to 100% |
| FIG_05 | assets/fig-05-guidance-through-the-metrics.png | chart | Q1 — lab measurements: five metrics and the faint share across seven guidance weights | — | — | blog/evaluating-generative-models/fig-05-guidance-through-the-metrics-v1.png | FD, precision, recall, density and coverage against guidance weight: recall falls then rebounds at w = 7.5, coverage keeps falling |
| FIG_06 | assets/fig-06-fd-depends-on-n.png | chart | Q1 — lab measurements, 24 repeats per point, with the fitted lines in 1/N | — | — | blog/evaluating-generative-models/fig-06-fd-depends-on-n-v1.png | FD against 1/N for a perfect and a slightly grainy generator: straight lines whose intercepts are 0.0007 and 0.0291 |
| FIG_07 | assets/fig-07-human-error-vs-fid.png | source | source check — the paper's own Figure 2 is the evidence the section argues from, and its arXiv record is CC BY 4.0 (ledger F1) | Stein, Cresswell, Hosseinzadeh, Sui, Ross, Villecroze, Liu, Caterini, Taylor & Loaiza-Ganem, Exposing flaws of generative model evaluation metrics and their unfair treatment of diffusion models, NeurIPS 2023, Figure 2, https://arxiv.org/abs/2306.04675 (file: https://arxiv.org/html/2306.04675v2/summary.svg) | CC BY 4.0 (arXiv record); reproduced unchanged, the SVG rasterised at 2× without edits, credited in the caption | blog/evaluating-generative-models/fig-07-human-error-vs-fid-v1.png | Stein et al.'s human error rate for 41 models ordered by FID on four datasets: error rate does not rise as FID improves |

## Lab files

**Lab grade:** G1 · runs anywhere (numpy only; the full run takes about 45 s on one core).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/evaluating-generative-models/README-v1.md` | grade, provenance, run order, the E1–E3 exercise ladder, cleanup |
| LAB_02 | `lab/evaluate.py` | `labs/evaluating-generative-models/evaluate-v1.py` | crescent world, every generator and every metric in the post, in numpy |
| LAB_03 | `lab/requirements.txt` | `labs/evaluating-generative-models/requirements-v1.txt` | the pinned numpy version |
| LAB_04 | `lab/captures.json` | `labs/evaluating-generative-models/captures-v1.json` | the author's run, machine-readable; every measured figure reads it |
| LAB_05 | `lab/expected-output.txt` | `labs/evaluating-generative-models/expected-output-v1.txt` | the author's run as printed |
| LAB_06 | `lab/notebook.ipynb` | `labs/evaluating-generative-models/notebook-v1.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-evaluating-generative-models.zip` | `lab-evaluating-generative-models.zip` (bucket root) | every lab file in one zip; its final URL is already written in `blog.md` |

Upload with accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`,
`application/json`, `application/x-ipynb+json`) and, where the upload path supports object
metadata, `Content-Disposition: attachment; filename="<name>"`.

## Series links to add

The owner adds these links; the post names them in plain text only. On 2026-10-09 the owner asked
for earlier parts to be named by title whether or not they are live yet.

| Post | Status on 2026-10-21 | Where it is named |
|---|---|---|
| Part 1 — What a Diffusion Model Actually Does | published | the "You need" line; frontmatter `prerequisites` ("Part 1 of this series") |
| Part 7 — Few-Step Diffusion and Distillation: 20 Steps Into 1 | not published | *Turning a quality dial*, first paragraph ("the subject of Part 7 of this series, Few-Step Diffusion and Distillation: 20 Steps Into 1") |
| Part 8 — Controlling Diffusion Models: Guidance, ControlNet, LoRA | not published | *Turning a quality dial*, first paragraph ("Part 8, Controlling Diffusion Models: Guidance, ControlNet, LoRA, explains guidance"); later mentions say "Part 8" and need no link |

Parts 2–6 are not named; the post does not depend on them. Later parts are not named: the copier
paragraph says only that memorisation is "a question this series takes up later".

## Editable sources kept

| Route | File kept | Rebuild with |
|---|---|---|
| `placed`, `plot`, `chart` | `assets/_figures.py` (shared helpers in `assets/_build.py`) plus each figure's exported `.html` and `.svg` | `python3 assets/_figures.py` |
| `source` | `assets/fig-07-human-error-vs-fid.svg`, the paper's file unchanged; `.png` rasterised from it | `python3 assets/_figures.py 7` |
| cover | `assets/cover.html` and `assets/cover-prompt.md` | `python3 assets/_figures.py cover` |
| social | `assets/_social.py` plus each card's `.html` and `.svg` under `assets/social/` | `python3 assets/_social.py`, then `render_social.py` |

`_figures.py` and `_social.py` read every measured and computed number from `lab/captures.json`, the
capture the article's lab download ships, and check every alt text against `blog.md`, so prose,
figures and lab cannot drift apart. No quoted paper number is drawn on any figure.

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-models/evaluating-generative-models/ urls.txt
```

Do not overwrite a published object. Nothing in this manifest is published yet; once it is, a
re-rendered asset keeps its object key and the Cloudflare cache for that key is purged after upload.
