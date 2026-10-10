# Asset manifest — diffusion-samplers-and-solvers

Series `diffusion-models`, part 6. **Status: local draft assets ready for upload.** Upload the
PNGs and the five lab files to the public `media` bucket under the versioned object keys below,
write the resulting URLs to `urls.txt` in table order (images first, then the lab files), then run
`fill_urls.py`. Upload the lab zip separately to the bucket root (see **Lab files**).

Nothing here has been published, so every object key stays at `v1`.

All twelve figures and the cover are our own work. The `source` route was considered first for
every paper-backed figure: of the five candidates recorded in `research/ledger.md` under **Figure
candidates**, only Restart's carry a reuse licence (CC BY 4.0), and neither serves: Figure 1(b) is a
schematic of regimes the post measures itself, and Figure 3 has no extractable image, so its table
numbers are charted instead. EDM's and DPM-Solver's figures carry only arXiv's non-exclusive
licence. Three figures chart quoted table numbers, each credited in its caption.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | placed | template cover in the series house layout — measured error against calls for DDIM and a third-order solver beside the toy's exact paths and DDIM's chords; a template build, not an external generator | — | — | blog/diffusion-samplers-and-solvers/cover-v1.png | Error against network calls for DDIM and a third-order solver, beside exact sampling paths that bend once and end on crescents |
| FIG_01 | assets/fig-01-where-ddim-loses-the-spread.png | plot | Q1/Q4 — closed-form per-step factors on part 5's grid, the worked example's table drawn | — | — | blog/diffusion-samplers-and-solvers/fig-01-where-ddim-loses-the-spread-v1.png | DDIM's share of the exact path after each of 50 steps, falling to 0.860 by σ = 14.5; log-SNR steps end at 0.941, DPM-Solver++ at 1.004 |
| FIG_02 | assets/fig-02-same-nfe-forty-fold.png | chart | Q1 — computed convergence curves for three solvers on two grids | — | — | blog/diffusion-samplers-and-solvers/fig-02-same-nfe-forty-fold-v1.png | Error in brightness spread against network calls on two grids: DDIM reaches 1% at 778 calls, DPM-Solver++(2M) on log-SNR steps at 30 |
| FIG_03 | assets/fig-03-straight-lines-and-one-bend.png | plot | Q4 — real trajectories of the exact denoiser's ODE against σ, with DDIM's chords; EDM's 1-D sketch is not reusable (ledger F3) | — | — | blog/diffusion-samplers-and-solvers/fig-03-straight-lines-and-one-bend-v1.png | Exact ODE paths of six crescent samples, straight above σ = 20 and below σ = 5, with DDIM's six-step chords cutting across the bend |
| FIG_04 | assets/fig-04-one-family-of-samplers.png | mermaid | Q3 — 11 nodes; equivalence edges join the stochastic and deterministic families | — | — | blog/diffusion-samplers-and-solvers/fig-04-one-family-of-samplers-v1.png | Sampler family tree: DDPM ancestral is DDIM at η = 1; DDIM at η = 0 is Euler and DPM-Solver-1; higher-order solvers build on it |
| FIG_05 | assets/fig-05-what-each-solver-evaluates.png | placed | Q4 — each solver's evaluation points to scale on one log-SNR step | — | — | blog/diffusion-samplers-and-solvers/fig-05-what-each-solver-evaluates-v1.png | One step on a log-SNR axis with a dot per denoiser call: one for DDIM, two for Heun, three for DPM-Solver-3, one reused for 2M |
| FIG_06 | assets/fig-06-error-against-nfe.png | chart | Q1 — lab measurements against an RK4 reference, with the one-grey-level line | — | — | blog/diffusion-samplers-and-solvers/fig-06-error-against-nfe-v1.png | Log-log error against network calls for five solvers, slopes near 1, 2 and 3; one grey level at 100, 49, 41, 25 and 16 calls |
| FIG_07 | assets/fig-07-dpm-solver-tables.png | chart | Q1 — quoted table numbers with their setup; DPM-Solver's Figure 2 carries no reuse licence (ledger F5) | data from Lu, Zhou, Bao, Chen, Li & Zhu, DPM-Solver, NeurIPS 2022, Tables 1 and 4 (L16, L18) | redrawn from published numbers | blog/diffusion-samplers-and-solvers/fig-07-dpm-solver-tables-v1.png | Quoted DPM-Solver FIDs on CIFAR-10: Runge–Kutta in t or λ against DPM-Solver, and five samplers on DDPM's model, 10 to 1,000 calls |
| FIG_08 | assets/fig-08-samples-at-low-nfe.png | placed | Q4 — real sample images from the lab at matched calls | — | — | blog/diffusion-samplers-and-solvers/fig-08-samples-at-low-nfe-v1.png | Crescent samples from four samplers at about 5, 10 and 20 network calls beside the exact endpoints of the same three noises |
| FIG_09 | assets/fig-09-local-error-per-noise-level.png | chart | Q1 — measured one-step error per noise level, repeating EDM's Appendix D.1 on the toy; EDM's own plot is not reusable (ledger F4) | — | — | blog/diffusion-samplers-and-solvers/fig-09-local-error-per-noise-level-v1.png | One-step error against noise level for DDIM and Heun under four 32-step schedules, peaking where structure and detail are decided |
| FIG_10 | assets/fig-10-schedules-at-matched-nfe.png | chart | Q1 — measured thresholds beside a quoted table | right panel: data from Sabour, Fidler & Kreis, Align Your Steps, ICML 2024, Table 5 (L38) | redrawn from published numbers | blog/diffusion-samplers-and-solvers/fig-10-schedules-at-matched-nfe-v1.png | Network calls each solver needs under five step schedules, beside quoted CIFAR-10 FIDs for log-SNR and optimised steps |
| FIG_11 | assets/fig-11-noise-costs-and-buys.png | chart | Q1 — lab measurements and the two closed-form limits | — | — | blog/diffusion-samplers-and-solvers/fig-11-noise-costs-and-buys-v1.png | Sample detail against calls for deterministic and stochastic samplers; spread on part 5's flawed schedule: 0.357 by ODE, 0.487 by SDE |
| FIG_12 | assets/fig-12-published-ode-vs-sde.png | chart | Q1 — quoted numbers with setup; Restart's CC BY 4.0 Figure 1(b) is a schematic, not data, and its Figure 3 has no extractable image (ledger F1, F2) | data from Xu et al., Restart Sampling, NeurIPS 2023, Tables 4 and 5 (L36), and Song, Meng & Ermon, DDIM, ICLR 2021, Table 1 (L06) | redrawn from published numbers | blog/diffusion-samplers-and-solvers/fig-12-published-ode-vs-sde-v1.png | Quoted FIDs: Heun, EDM's stochastic sampler, Euler–Maruyama and Restart on ImageNet-64; DDIM at three η values on CIFAR-10 |

## Lab files

**Lab grade:** G1 · runs anywhere (numpy only, on a CPU).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/diffusion-samplers-and-solvers/README-v1.md` | grade, provenance, run order, the E1–E5 exercise ladder, cleanup |
| LAB_02 | `lab/samplers.py` | `labs/diffusion-samplers-and-solvers/samplers-v1.py` | the exact crescent-world denoiser, eight samplers, five schedules and every experiment |
| LAB_03 | `lab/requirements.txt` | `labs/diffusion-samplers-and-solvers/requirements-v1.txt` | the pinned numpy version |
| LAB_04 | `lab/captures.json` | `labs/diffusion-samplers-and-solvers/captures-v1.json` | the author's run, machine-readable; every measured and computed figure reads it |
| LAB_05 | `lab/expected-output.txt` | `labs/diffusion-samplers-and-solvers/expected-output-v1.txt` | the author's run as printed |
| ARCHIVE | `lab-diffusion-samplers-and-solvers.zip` | `lab-diffusion-samplers-and-solvers.zip` (bucket root) | every lab file in one zip; its final URL is already written in `blog.md` |

Upload with accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`,
`application/json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

## Series links to add

The owner adds these links; the post names them in plain text only. On 2026-10-09 the owner asked
for earlier parts to be named by title whether or not they are live yet.

| Post | Status on 2026-10-09 | Where it is named |
|---|---|---|
| Part 1 — What a Diffusion Model Actually Does | published | the "You need" line; *The problem*, first paragraph ("Part 1 of this series, What a Diffusion Model Actually Does, explained why…"); frontmatter `prerequisites` |
| Part 2 — Diffusion Model Architecture: The Complete Guide | not published | not named; the post does not depend on it |
| Part 3 — Where the Diffusion MSE Loss Comes From | not published | *The problem*, second paragraph ("Part 3 of this series, Where the Diffusion MSE Loss Comes From, showed that dividing a noisy sample…") |
| Part 4 — Diffusion Backbones: U-Net to DiT, Block by Block | not published | not named; the post does not depend on it |
| Part 5 — Training a Diffusion Model: The Decisions Before Step One | not published | *The problem*, last paragraph ("the toy from Part 5 of this series, Training a Diffusion Model: The Decisions Before Step One"); later mentions say "part 5" and need no link |

## Editable sources kept

| Route | File kept | Rebuild with |
|---|---|---|
| `placed`, `plot`, `chart` | `assets/_figures.py` (shared helpers in `assets/_build.py`) plus each figure's exported `.html` and `.svg` | `python3 assets/_figures.py` |
| `mermaid` | `assets/fig-04-one-family-of-samplers.mmd` | `python3 assets/_mermaid.py` |
| cover | `assets/cover.html` and `assets/cover-prompt.md` | `python3 assets/_figures.py cover` |
| social | `assets/_social.py` plus each card's `.html` and `.svg` under `assets/social/` | `python3 assets/_social.py`, then `render_social.py` |

`_figures.py` and `_social.py` read every measured and computed number from `lab/captures.json`,
the capture the article's lab download ships, so prose, figures and lab cannot drift apart. The
quoted tables (DPM-Solver's Tables 1 and 4, DDIM's Table 1, Restart's Tables 4 and 5, and Align
Your Steps' Table 5) are typed once at the top of `_figures.py`, next to their ledger keys.

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-models/diffusion-samplers-and-solvers/ urls.txt
```

Do not overwrite a published object. Nothing in this manifest is published yet; once it is, a
re-rendered asset keeps its object key and the Cloudflare cache for that key is purged after upload.
