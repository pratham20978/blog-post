# Asset manifest — diffusion-backbones-unet-to-dit

Series `diffusion-models`, part 4. **Status: local draft assets ready for upload.** Upload the
PNGs and the five lab files to the public `media` bucket under the versioned object keys below,
write the resulting URLs to `urls.txt` in table order (images first, then the lab files), then run
`fill_urls.py`. Upload the lab zip separately to the bucket root (see **Lab files**).

Nothing here has been published, so every object key stays at `v1`.

Every figure is our own work. The route gate was run per figure against its real content, and the
`source` route was considered first for every paper-backed figure: four candidates (DiT Fig. 2 and
Fig. 3, SD3 Fig. 2, U-Net Fig. 1) are recorded in `research/ledger.md` under **Figure candidates**,
and none has verified reuse rights. Each figure here carries measured shapes or numbers that those
paper figures do not.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | placed | template cover in the series house layout — the U-Net and the patchified crescent motif; a diagram-design build, not an external generator | — | — | blog/diffusion-backbones-unet-to-dit/cover-v1.png | A U-shaped stack of shrinking and growing feature maps beside the noisy crescent patch cut into 2×2 patches and laid out as a strip of tokens |
| FIG_01 | assets/fig-01-one-contract-three-backbones.png | placed | Q4 — three small multiples, each drawn with its real grid or token strip; under nine nodes, no crossings | — | — | blog/diffusion-backbones-unet-to-dit/fig-01-one-contract-three-backbones-v1.png | Three panels mapping a C×64×64 latent to a same-shaped prediction: a U-Net pyramid down to 8×8, a DiT strip of 1,024 tokens, and an MM-DiT with image and text strips |
| FIG_02 | assets/fig-02-two-ways-to-shrink-a-patch.png | placed | Q4 — a grid of real values, pooled values and token strips; the values are the figure | — | — | blog/diffusion-backbones-unet-to-dit/fig-02-two-ways-to-shrink-a-patch-v1.png | Part 1's 4×4 noisy patch pooled into a 2×2 grid of means beside the same patch cut into four 4-value tokens, with 256, 16 and 16 attention pairs marked |
| FIG_03 | assets/fig-03-sd15-unet-shape-trace.png | plot | Q1 — every shape and parameter count is the lab's forward-hook capture, drawn to scale (height ∝ grid side, width ∝ channels) | — | — | blog/diffusion-backbones-unet-to-dit/fig-03-sd15-unet-shape-trace-v1.png | SD 1.5's U-Net drawn to scale, block width by channels and height by resolution, from 320×64×64 down to 1280×8×8 and back, with all 12 skips and their shapes |
| FIG_04 | assets/fig-04-inside-one-sd15-stage.png | mermaid | Q3 — 14 nodes, and two side inputs (timestep, prompt) cross into the main path | — | — | blog/diffusion-backbones-unet-to-dit/fig-04-inside-one-sd15-stage-v1.png | Flowchart of one SD 1.5 level: a ResNet block with group norm, SiLU, 3×3 convolutions and an added time bias, then a transformer block with self-attention, cross-attention to 77 text tokens and a gated feed-forward |
| FIG_05 | assets/fig-05-unet-params-vs-flops-by-level.png | chart | Q1 — measured parameter and FLOP counts per level, zero baseline | — | — | blog/diffusion-backbones-unet-to-dit/fig-05-unet-params-vs-flops-by-level-v1.png | Paired bars per U-Net level: the 64×64 level holds 3.4% of parameters and 38.2% of FLOPs, while the 16×16 level holds 46.3% of parameters and 26.8% of FLOPs |
| FIG_06 | assets/fig-06-dit-two-patch-sizes.png | placed | Q4 — two patch lattices and token sequences drawn to scale side by side, with lab and ledger numbers | — | — | blog/diffusion-backbones-unet-to-dit/fig-06-dit-two-patch-sizes-v1.png | DiT-XL/4 and DiT-XL/2 on the same 32×32 latent: an 8×8 lattice of 64 tokens against a 16×16 lattice of 256, each labelled with parameters, compute and FID |
| FIG_07 | assets/fig-07-dit-adaln-zero-block.png | mermaid | Q3 — 10 nodes; the condition path feeds four points on the main path, so edges cross | — | — | blog/diffusion-backbones-unet-to-dit/fig-07-dit-adaln-zero-block-v1.png | Flowchart of a DiT block with adaLN-Zero: the timestep and class embedding produce six 1152-wide vectors that shift, scale and gate the attention and MLP sublayers of 256 tokens |
| FIG_08 | assets/fig-08-mmdit-dual-stream-block.png | mermaid | Q3 — two parallel paths that merge in joint attention and split again, 13 nodes | — | — | blog/diffusion-backbones-unet-to-dit/fig-08-mmdit-dual-stream-block-v1.png | Flowchart of one SD3 MM-DiT block: 4,096 image tokens and 154 text tokens each pass their own modulation and QKV projections, meet in one joint attention over 4,250 tokens, then split into their own output projections and MLPs |
| FIG_09 | assets/fig-09-mmdit-params-vs-flops-by-stream.png | chart | Q1 — measured per-stream parameter and FLOP counts, part of whole | — | — | blog/diffusion-backbones-unet-to-dit/fig-09-mmdit-params-vs-flops-by-stream-v1.png | Two stacked bars for SD3's 2B MM-DiT: parameters split about evenly between image and text streams, while FLOPs are 66% image stream, 31.6% joint attention and 2.4% text stream |
| FIG_10 | assets/fig-10-attention-share-of-a-block.png | plot | Q1/Q4 — the closed-form curve on a log axis with six measured points from the lab | — | — | blog/diffusion-backbones-unet-to-dit/fig-10-attention-share-of-a-block-v1.png | Curve of attention's share of a transformer block's FLOPs against tokens per unit width, rising through 1/3 at N = 3D and 1/2 at N = 6D, with DiT-XL/2 at 256 and 512 pixels and SD3-2B at 1024 pixels on it |
| FIG_11 | assets/fig-11-naive-vs-fused-attention-cpu.png | chart | Q1 — times and allocations measured on the build machine, log scales labelled | — | — | blog/diffusion-backbones-unet-to-dit/fig-11-naive-vs-fused-attention-cpu-v1.png | Two log-scale panels, naive against fused attention on a laptop CPU from 256 to 4,096 tokens: time grows to 864 ms against 169 ms, and the largest allocation to 1,093 MB against 19 MB |
| FIG_12 | assets/fig-12-the-memory-bill.png | chart | Q1 — arithmetic on measured parameter counts with ledger formulas (L37, L38) and SD3's measured encoder sizes (L29), labelled as computed | — | — | blog/diffusion-backbones-unet-to-dit/fig-12-the-memory-bill-v1.png | Stacked bars on one gigabyte scale: what SD 1.5, DiT-XL/2 and SD3-2B with its encoders must load for inference, and per-image training memory split into state, activations and attention scores |
| FIG_13 | assets/fig-13-when-to-swap-the-backbone.png | placed | Q5 — a two-axis trade-off map with six placed models, no crossings | — | — | blog/diffusion-backbones-unet-to-dit/fig-13-when-to-swap-the-backbone-v1.png | Decision map with attention tokens on a log axis and conditioning type on the other, placing SD 1.5, SDXL, DiT-XL/2 at two sizes and SD3-2B either side of the N = 6D line |

## Lab files

**Lab grade:** G1 · runs anywhere (CPU PyTorch 2.14 and diffusers 0.40 in a pinned environment).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/diffusion-backbones-unet-to-dit/README-v1.md` | grade, provenance, run order, the E1–E5 exercise ladder, cleanup |
| LAB_02 | `lab/census.py` | `labs/diffusion-backbones-unet-to-dit/census-v1.py` | builds the three backbones on the meta device and measures every count in the post |
| LAB_03 | `lab/requirements.txt` | `labs/diffusion-backbones-unet-to-dit/requirements-v1.txt` | the pinned CPU PyTorch and diffusers versions |
| LAB_04 | `lab/captures.json` | `labs/diffusion-backbones-unet-to-dit/captures-v1.json` | the author's run, machine-readable; every figure reads it |
| LAB_05 | `lab/expected-output.txt` | `labs/diffusion-backbones-unet-to-dit/expected-output-v1.txt` | the author's run as printed |
| ARCHIVE | `lab-diffusion-backbones-unet-to-dit.zip` | `lab-diffusion-backbones-unet-to-dit.zip` (bucket root) | every lab file in one zip; its final URL is already written in `blog.md` |

Upload with accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`,
`application/json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

## Series links to add

The owner adds these links; the post names them in plain text only.

| Post | Status on 2026-10-03 | Where it is named |
|---|---|---|
| Part 1 — What a Diffusion Model Actually Does | published | the "You need" line; *The problem*, second paragraph ("Part 1 of this series, What a Diffusion Model Actually Does, explains why…"); *Worked example*, first paragraph; frontmatter `prerequisites` |
| Part 2 — Diffusion Model Architecture: The Complete Guide | not published | not named. If it goes live first, *The problem*'s first paragraph is the natural place for "the full system map is Part 2". |
| Part 3 — Where the Diffusion MSE Loss Comes From | not published | not named; nothing in this post depends on it. |

## Editable sources kept

| Route | File kept | Rebuild with |
|---|---|---|
| `placed`, `plot`, `chart` | `assets/_figures.py` plus each figure's exported `.html` and `.svg` | `python3 assets/_figures.py` |
| `mermaid` | `assets/fig-04-inside-one-sd15-stage.mmd`, `fig-07-dit-adaln-zero-block.mmd`, `fig-08-mmdit-dual-stream-block.mmd` | `python3 assets/_mermaid.py` |
| cover | `assets/cover.html` and `assets/cover-prompt.md` | `python3 assets/_figures.py cover` |

`_figures.py` reads every measured number from `lab/captures.json`, the capture the article's lab
download ships, so prose, figures and lab cannot drift apart. The two quoted tables (DiT's Table 4
and SD3's encoder sizes) are typed once at the top of `_figures.py`, next to their ledger keys.

Apply URLs after upload:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/diffusion-models/diffusion-backbones-unet-to-dit/ urls.txt
```

Do not overwrite a published object. Increment the version suffix when an asset changes so
long-lived caches cannot serve an older image under the same URL.
