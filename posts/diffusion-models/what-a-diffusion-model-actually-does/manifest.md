# Asset manifest — what-a-diffusion-model-actually-does

Series `diffusion-models`, part 1. **Status: local draft assets ready for upload.** Upload the
PNGs to the public `media` bucket under the versioned object keys below, write the resulting URLs
to `urls.txt` in table order, then run `fill_urls.py`.

Nothing here has been published, so every object key stays at `v1`.

Every figure is our own work. The route gate was run per figure against its real content; the
`source` route was considered and rejected for all six — five candidate paper figures are
recorded in `research/ledger.md` under **Figure candidates**, and none has verified reuse rights.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | placed | template cover in the series house layout; a diagram-design build, not an external generator | — | — | blog/what-a-diffusion-model-actually-does/cover-v1.png | A twelve-by-twelve patch of pure noise resolving through six stages into a bright crescent, under the line 'Trained only to undo noise' |
| FIG_01 | assets/fig-01-forward-is-a-formula.png | placed | Q4 — the five states must be drawn as real patches at real signal levels; a box labelled "noising" carries none of the decay | — | — | blog/what-a-diffusion-model-actually-does/fig-01-forward-is-a-formula-v1.png | A crescent-shaped patch shown at five rising noise levels; the left-to-right arrow carries a closed-form equation with no parameters, the right-to-left arrow carries the learned network |
| FIG_02 | assets/fig-02-one-forward-step.png | placed | Q4 — a grid of sixteen real values where the reader checks 0.48 + 0.84 = 1.32 by eye | — | — | blog/what-a-diffusion-model-actually-does/fig-02-one-forward-step-v1.png | Three four-by-four grids of printed values, shaded by brightness: the scaled clean patch, the scaled noise, and their sum, with two cells traced through the addition |
| FIG_03 | assets/fig-03-noise-schedule.png | plot | Q1/Q4 — two continuous curves evaluated from the published schedule definitions, with axes and marked crossings; source is `_figures.py` | — | — | blog/what-a-diffusion-model-actually-does/fig-03-noise-schedule-v1.png | Two curves of the signal coefficient against normalised timestep: the linear schedule loses half its signal far earlier than the cosine one and flattens near zero for the last third, with the worked example's value of 0.80 marked |
| FIG_04 | assets/fig-04-the-average-is-the-blur.png | placed | Q4 — the point only lands if the four candidates and their mean are drawn as patches; boxes cannot show an average | — | — | blog/what-a-diffusion-model-actually-does/fig-04-the-average-is-the-blur-v1.png | A noisy patch on the left fans out to four different clean patches, each needing an equally ordinary noise draw, and those four average on the right into a smeared grey patch |
| FIG_05 | assets/fig-05-one-jump-versus-eight-steps.png | placed | Q4 — small multiples of one tensor at successive noise levels; the side-by-side comparison is the figure | — | — | blog/what-a-diffusion-model-actually-does/fig-05-one-jump-versus-eight-steps-v1.png | Top lane: one arrow from pure noise to a blurred patch, beside a table of error multipliers. Bottom lane: the same noise through eight small steps to a sharp crescent |
| FIG_06 | assets/fig-06-the-four-moving-parts.png | mermaid | Q3 — the post's one end-to-end view: 13 nodes, two loops that cross at the shared denoiser | — | — | blog/what-a-diffusion-model-actually-does/fig-06-the-four-moving-parts-v1.png | An end-to-end graph placing the training loop and the sampling loop around one shared denoiser, with the fixed schedule feeding both |

## Editable sources kept

| Route | File kept | Rebuild with |
|---|---|---|
| `placed`, `plot` | `assets/_figures.py` plus the exported `.html` and `.svg` per figure | `python3 assets/_figures.py` |
| `mermaid` | `assets/fig-06-the-four-moving-parts.mmd` | `python3 assets/_mermaid.py fig-06-the-four-moving-parts` |
| cover | `assets/cover.html` and `assets/cover-prompt.md` | `python3 assets/_figures.py cover` |

`_figures.py` computes every number it draws from the same `X0`, `EPS` and `ᾱ = 0.64` the post
uses, so a change to the worked example changes the figures with it. The schedule curves in
FIG_03 are evaluated from the two published schedule definitions inside the script; the
crossing values printed on it are computed, not quoted.

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-models/what-a-diffusion-model-actually-does/ urls.txt
```

Do not overwrite a published object. Increment the version suffix when an asset changes so
long-lived caches cannot serve an older image under the same URL.
