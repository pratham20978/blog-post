# Asset manifest — diffusion-math-derived

Series `diffusion-models`, part 3. **Status: local draft assets ready for upload.** Upload the
PNGs and the lab file to the public `media` bucket under the versioned object keys below, write
the resulting URLs to `urls.txt` in table order (images first, then the lab file), then run
`fill_urls.py`.

Nothing here has been published, so every object key stays at `v1`.

Every figure is our own work. The route gate was run per figure against its real content; the
`source` route was considered and rejected for all twelve — four candidate paper figures are
recorded in `research/ledger.md` under **Figure candidates**, and none has verified reuse rights.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | placed | template cover in the series house layout — the teacher/student curves from Figure 1 plus the crescent motif; a diagram-design build, not an external generator | — | — | blog/diffusion-math-derived/cover-v1.png | Two overlapping bell curves, the teacher's solid and the network's dashed, with the gap between their centres marked, beside the crescent patch clean and noised |
| FIG_01 | assets/fig-01-teacher-and-student.png | plot | Q4 — four densities over a real axis at the worked values; the precision sum 5 + 4 = 9 cannot be shown as boxes | — | — | blog/diffusion-math-derived/fig-01-teacher-and-student-v1.png | Four bell curves over the previous pixel value: evidence from the clean pixel centred at 0.85, evidence from the noisy pixel at 0.48, their product the teacher at 0.69, and the student at 0.61 |
| FIG_02 | assets/fig-02-one-error-five-prices.png | placed | Q4/Q5 — a five-row ledger of real values with bars proportional to each squared error; under nine elements, no crossings | — | — | blog/diffusion-math-derived/fig-02-one-error-five-prices-v1.png | Five rows pricing one prediction error: noise, clean pixel, score, velocity and the ELBO step, each with its squared error as a bar and the constant that converts it back to 0.04 |
| FIG_03 | assets/fig-03-diffusion-is-a-fixed-encoder-vae.png | placed | Q4 — three small multiples compared side by side; each panel has at most three nodes | — | — | blog/diffusion-math-derived/fig-03-diffusion-is-a-fixed-encoder-vae-v1.png | Three small graphical models side by side: a VAE with a learned encoder, a hierarchical VAE with a chain of learned encoders, and a diffusion model whose encoder chain is fixed and whose latents have the image's size |
| FIG_04 | assets/fig-04-where-each-elbo-term-lives.png | placed | Q5 — five chain nodes and three brackets, no crossings; the term formulas must sit on the chain they describe | — | — | blog/diffusion-math-derived/fig-04-where-each-elbo-term-lives-v1.png | The chain from x-zero to x-T with three brackets: the prior term at the noise end, one denoising-matching term per intermediate step, and the reconstruction term at the image end, each marked with whether it touches the network |
| FIG_05 | assets/fig-05-the-weight-ddpm-dropped.png | plot | Q4 — a curve computed from DDPM's published schedule on a log axis, with its extremes marked | — | — | blog/diffusion-math-derived/fig-05-the-weight-ddpm-dropped-v1.png | Log-scale curve of the per-step ELBO weight across 1,000 DDPM steps: 0.27 at the second step, falling to a minimum of 0.005 near step 349, rising to 0.010 at the last step, beside a flat line at 1 for the simple loss |
| FIG_06 | assets/fig-06-bound-versus-samples.png | chart | Q1 — measured NLL and FID from ledger rows L10 and L42, zero baseline | — | — | blog/diffusion-math-derived/fig-06-bound-versus-samples-v1.png | Two bar panels of CIFAR-10 results: negative log-likelihood in bits per dimension and FID for the true bound, the hybrid loss and the simple loss, from the DDPM and Improved DDPM papers with their setups labelled |
| FIG_07 | assets/fig-07-one-loss-many-weightings.png | plot | Q4 — curves evaluated from the published w(λ) formulas, with the worked noise level added | — | — | blog/diffusion-math-derived/fig-07-one-loss-many-weightings-v1.png | Weighting curves over log signal-to-noise ratio for the ELBO, epsilon and velocity prediction with the cosine schedule, EDM and Min-SNR, with the worked example's noise level and DDPM's range marked |
| FIG_08 | assets/fig-08-the-ideal-denoiser-is-an-average.png | plot | Q4 — exact posterior weights and the score field of a three-value dataset on real axes | — | — | blog/diffusion-math-derived/fig-08-the-ideal-denoiser-is-an-average-v1.png | Three data values with bars for their posterior weights and the weighted average between them; below, the noisy value 0.43 with an arrow to the scaled average, and the score curve marked at that value |
| FIG_09 | assets/fig-09-noisy-targets-average-to-the-score.png | plot | Q1/Q4 — a deterministic simulation from the lab plotted against the exact score curve | — | — | blog/diffusion-math-derived/fig-09-noisy-targets-average-to-the-score-v1.png | Scatter of six hundred per-sample targets falling on three straight lines, one per clean value, with binned averages of those targets lying on the exact score curve between them |
| FIG_10 | assets/fig-10-three-formulations-one-object.png | mermaid | Q3 — 12 nodes with crossing edges between the discrete and continuous groups; the post's one end-to-end view | — | — | blog/diffusion-math-derived/fig-10-three-formulations-one-object-v1.png | A graph of the discrete DDPM and NCSN chains and the continuous VP and VE SDEs, joined by rescaling and limit edges, all feeding one shared network whose loss splits into ELBO, simple-loss and DSM weightings |
| FIG_11 | assets/fig-11-vp-and-ve-are-one-path.png | plot | Q4 — trajectories of the worked pixel over log-SNR, computed | — | — | blog/diffusion-math-derived/fig-11-vp-and-ve-are-one-path-v1.png | Two trajectories of the top-left pixel against log signal-to-noise ratio: the VE value explodes past minus three as noise grows while the VP value stays within one, and the rescaled VE curve lies exactly on the VP curve |
| FIG_12 | assets/fig-12-more-steps-tighter-bound.png | chart | Q1 — measured bits per dimension from ledger row L22, zero baseline | — | — | blog/diffusion-math-derived/fig-12-more-steps-tighter-bound-v1.png | Bits per dimension on the CIFAR-10 test set falling as the number of diffusion steps grows from 10 to 10,000, levelling toward the continuous-time value of 2.65 |

## Lab files

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/loss_identities.py` | `labs/diffusion-math-derived/loss_identities-v1.py` | standard-library script that recomputes and asserts every identity in the post |

Upload with `Content-Type: text/x-python` and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="loss_identities.py"`.

## Editable sources kept

| Route | File kept | Rebuild with |
|---|---|---|
| `placed`, `plot`, `chart` | `assets/_figures.py` plus the exported `.html` and `.svg` per figure | `python3 assets/_figures.py` |
| `mermaid` | `assets/fig-10-three-formulations-one-object.mmd` | `python3 assets/_mermaid.py fig-10-three-formulations-one-object` |
| cover | `assets/cover.html` and `assets/cover-prompt.md` | `python3 assets/_figures.py cover` |

`_figures.py` imports every computed number from `lab/loss_identities.py` — the same module the
article's lab download ships — so prose, figures and lab cannot drift apart. The two measured
figures (6 and 12) type their numbers once, in `_figures.py`, next to the ledger keys they quote.

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-models/diffusion-math-derived/ urls.txt
```

Do not overwrite a published object. Increment the version suffix when an asset changes so
long-lived caches cannot serve an older image under the same URL.
