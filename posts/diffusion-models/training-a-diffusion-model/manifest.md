# Asset manifest — training-a-diffusion-model

Series `diffusion-models`, part 5. **Status: local draft assets ready for upload.** Upload the
PNGs and the five lab files to the public `media` bucket under the versioned object keys below,
write the resulting URLs to `urls.txt` in table order (images first, then the lab files), then run
`fill_urls.py`. Upload the lab zip separately to the bucket root (see **Lab files**).

Nothing here has been published, so every object key stays at `v1`.

Thirteen figures and the cover are our own work. Figure 8 is the one reused figure: the `source`
route was considered first for every paper-backed figure, and of the four candidates recorded in
`research/ledger.md` under **Figure candidates**, only Lin et al.'s Figure 3 has a reuse licence.
It is reproduced unchanged, cut from page 5 of the arXiv PDF with its own sub-captions, and its
caption in `blog.md` carries the credit and the licence link that CC BY-SA 4.0 requires.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | placed | template cover in the series house layout — Stable Diffusion's log-SNR schedule beside the lab's paired crescent rows; a diagram-design build, not an external generator | — | — | blog/training-a-diffusion-model/cover-v1.png | Stable Diffusion's schedule ending at log-SNR −5.4, not minus infinity, beside crescents sampled with and without a pure-noise last step |
| FIG_01 | assets/fig-01-one-training-step.png | mermaid | Q3 — 15 nodes (ten steps, five decisions); the decisions feed six points on the path, so edges cross | — | — | blog/training-a-diffusion-model/fig-01-one-training-step-v1.png | Flowchart of one training step from data, timestep and noise to network, weighted loss, optimiser and EMA, with five decisions marked |
| FIG_02 | assets/fig-02-what-survives-the-last-step.png | placed | Q4 — the series' 4×4 patch as real values beside a bar of computed leak sizes; the values are the figure | — | — | blog/training-a-diffusion-model/fig-02-what-survives-the-last-step-v1.png | Part 1's 4×4 patch at Stable Diffusion's last step, beside the mean's leak rising from 0.04 to 1.42 noise s.d. as values grow to 16,384 |
| FIG_03 | assets/fig-03-four-schedules-in-log-snr.png | plot | Q1/Q4 — closed-form schedule curves from the lab's float64 computation | — | — | blog/training-a-diffusion-model/fig-03-four-schedules-in-log-snr-v1.png | Log-SNR against training progress for the linear, cosine and Stable Diffusion schedules and the zero-terminal-SNR rescale |
| FIG_04 | assets/fig-04-where-training-spends-its-samples.png | plot | Q1/Q4 — densities computed from the published definitions (L22, L23, L27) | — | — | blog/training-a-diffusion-model/fig-04-where-training-spends-its-samples-v1.png | Densities of training log-SNR under the linear, cosine and SD schedules, EDM's log-normal at 2.4, and SD3's logit-normal at 0 and −2.2 |
| FIG_05 | assets/fig-05-resolution-shifts-the-schedule.png | plot | Q4 — the cosine schedule under the s² pooling rule (L28), computed | — | — | blog/training-a-diffusion-model/fig-05-resolution-shifts-the-schedule-v1.png | The cosine schedule's log-SNR per pixel and for 4×4 and 16×16 block means, 2.8 and 5.5 higher, beside the schedule shifted down by 2.8 |
| FIG_06 | assets/fig-06-the-leak-in-samples.png | placed | Q4 — real samples from the exact denoiser and measured brightness histograms | — | — | blog/training-a-diffusion-model/fig-06-the-leak-in-samples-v1.png | Crescent samples from the data, Stable Diffusion's schedule and the rescaled one at 16,384 pixels, with brightness histograms |
| FIG_07 | assets/fig-07-leak-vs-pixels-and-steps.png | chart | Q1 — lab measurements with the closed form drawn through them | — | — | blog/training-a-diffusion-model/fig-07-leak-vs-pixels-and-steps-v1.png | Brightness spread kept against pixel count and against sampling steps: the flawed schedule stays near 0.36, the rescaled one nears 1 |
| FIG_08 | assets/fig-08-lin-et-al-flawed-vs-fixed.png | source | source check passed: the flaw and the fix on the real model, which the toy cannot show; the only candidate with a reuse licence (ledger F1) | Lin, Liu, Li & Yang, "Common Diffusion Noise Schedules and Sample Steps are Flawed", WACV 2024, Figure 3 (arXiv:2305.08891v4, p. 5) | CC BY-SA 4.0 — reproduced unchanged, credit and licence link in the caption | blog/training-a-diffusion-model/fig-08-lin-et-al-flawed-vs-fixed-v1.png | Lin et al.'s Figure 3: eight prompt pairs from reference Stable Diffusion and the fixed model, including a solid black background |
| FIG_09 | assets/fig-09-error-amplification-by-target.png | plot | Q4 — closed-form amplification curves | — | — | blog/training-a-diffusion-model/fig-09-error-amplification-by-target-v1.png | Error amplification against log-SNR for ε, x0 and v outputs: ε explodes at high noise, x0 at low noise, and v stays at or below one |
| FIG_10 | assets/fig-10-targets-at-two-widths.png | chart | Q1 — measured per-level error and sample distances, three seeds per target | — | — | blog/training-a-diffusion-model/fig-10-targets-at-two-widths-v1.png | Measured excess error over the exact denoiser against log-SNR for ε, x0 and v prediction, at network width 256 and at width 32 |
| FIG_11 | assets/fig-11-where-each-weighting-puts-the-error.png | chart | Q1 — measured per-level error for four weightings, three seeds each | — | — | blog/training-a-diffusion-model/fig-11-where-each-weighting-puts-the-error-v1.png | Measured excess error by log-SNR for constant, SNR, truncated-SNR and Min-SNR-5 weighting of an x0-predicting network |
| FIG_12 | assets/fig-12-reweight-or-resample.png | chart | Q1 — quoted table numbers with their setup; the paper's own figures carry no reuse licence (ledger F2–F4) | data from Hang, Gu, Geng & Guo, ICCV 2025, Table 3 (L46) | redrawn from published numbers | blog/training-a-diffusion-model/fig-12-reweight-or-resample-v1.png | FID-10K bars for DiT-B/2 on ImageNet 256: cosine, EDM, flow matching, Min-SNR, Soft-Min-SNR, Laplace, Cauchy, scaled and shifted cosine |
| FIG_13 | assets/fig-13-ema-profiles-and-lengths.png | chart | Q1 — closed-form EMA profiles beside measured sample distances | — | — | blog/training-a-diffusion-model/fig-13-ema-profiles-and-lengths-v1.png | EMA weight over past steps for decays 0.999 and 0.9999 and power averages, beside measured sample distance for raw weights and six EMAs |
| FIG_14 | assets/fig-14-scaling-model-size.png | chart | Q1 — EDM2's size ladder beside the lab's width sweep | left panel: data from Karras et al., EDM2, CVPR 2024, Table 2 (L52) | redrawn from published numbers | blog/training-a-diffusion-model/fig-14-scaling-model-size-v1.png | EDM2's ImageNet-512 FID falling with parameters from 125M to 1.5B, beside the lab's excess error against width for two weightings |

## Lab files

**Lab grade:** G1 · runs anywhere (numpy and CPU PyTorch 2.14 in a pinned environment).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/training-a-diffusion-model/README-v1.md` | grade, provenance, run order, the E1–E5 exercise ladder, cleanup |
| LAB_02 | `lab/training_decisions.py` | `labs/training-a-diffusion-model/training_decisions-v1.py` | computes the schedules, measures the leak with the exact denoiser, trains the 50 small denoisers |
| LAB_03 | `lab/requirements.txt` | `labs/training-a-diffusion-model/requirements-v1.txt` | the pinned numpy and CPU PyTorch versions |
| LAB_04 | `lab/captures.json` | `labs/training-a-diffusion-model/captures-v1.json` | the author's run, machine-readable; every measured figure reads it |
| LAB_05 | `lab/expected-output.txt` | `labs/training-a-diffusion-model/expected-output-v1.txt` | the author's run as printed |
| ARCHIVE | `lab-training-a-diffusion-model.zip` | `lab-training-a-diffusion-model.zip` (bucket root) | every lab file in one zip; its final URL is already written in `blog.md` |

Upload with accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`,
`application/json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

## Series links to add

The owner adds these links; the post names them in plain text only.

| Post | Status on 2026-10-08 | Where it is named |
|---|---|---|
| Part 1 — What a Diffusion Model Actually Does | published | the "You need" line; *The problem*, first paragraph ("Part 1 of this series, What a Diffusion Model Actually Does, walks one forward and one reverse step…"); *Worked example*, "Sixteen values" ("part 1's 4×4 crescent patch"); Figure 2's alt text; frontmatter `prerequisites` |
| Part 2 — Diffusion Model Architecture: The Complete Guide | not published | not named. If it goes live first, *The problem*'s paragraph after Figure 1, beside the review that "organises the whole design space", is the natural place for "the full system map is Part 2". |
| Part 3 — Where the Diffusion MSE Loss Comes From | not published | not named. The weighting section's opening ("every common loss can be written as one weighted error over λ") is where a link would go once it is live. |
| Part 4 — Diffusion Backbones: U-Net to DiT, Block by Block | not published | not named; *How does training scale?* uses DiT-XL/2's FLOP count, which Part 4 measures, and is the natural place for a link once it is live. |

## Editable sources kept

| Route | File kept | Rebuild with |
|---|---|---|
| `placed`, `plot`, `chart` | `assets/_figures.py` (shared helpers in `assets/_build.py`) plus each figure's exported `.html` and `.svg` | `python3 assets/_figures.py` |
| `mermaid` | `assets/fig-01-one-training-step.mmd` | `python3 assets/_mermaid.py` |
| `source` | `assets/fig-08-lin-et-al-flawed-vs-fixed.png` | re-extract from arXiv:2305.08891v4, page 5, rendered at 200 dpi and cropped to the box (126, 188, 1524, 1808) |
| cover | `assets/cover.html` and `assets/cover-prompt.md` | `python3 assets/_figures.py cover` |
| social | `assets/_social.py` plus each card's `.html` and `.svg` under `assets/social/` | `python3 assets/_social.py`, then `render_social.py` |

`_figures.py` reads every measured number from `lab/captures.json`, the capture the article's lab
download ships, so prose, figures and lab cannot drift apart. The two quoted tables (Hang et al.'s
Table 3 and EDM2's Table 2) are typed once at the top of `_figures.py`, next to their ledger keys,
and so is the series' 4×4 running example.

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-models/training-a-diffusion-model/ urls.txt
```

Do not overwrite a published object. Increment the version suffix when an asset changes so
long-lived caches cannot serve an older image under the same URL.
