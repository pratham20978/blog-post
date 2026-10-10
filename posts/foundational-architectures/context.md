# Series context — Foundational Architectures

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** CS students and working engineers who know Python, matrix multiplication and the
  chain rule, and want to understand the canonical models *exactly* — every shape, count and
  derivation — not by analogy.
- **Shape:** hybrid. A toolkit root (1), a vision track (2–9) and a sequence track (10–13) that
  converge at ViT (14), with four two-part models: LeNet-5 1–2, Inception 5–6, ResNet 7–8,
  Transformer 12–13. Optional 15–18.
- **Shared promise:** read any architecture paper and reconcile its numbers yourself — shapes,
  parameters, MACs, receptive field — and say *why* the design trains, on numbers you can check.
- **The angle every part must obey:** reconcile, derive on checkable numbers, measure at toy scale,
  draw to scale. Introductory restatement of the block diagram is out of scope.
- **Sibling series:** `frontier-models` assumes Parts 10, 12 and 14. Nothing here depends on it.
- **Category:** `machine-learning` for every part. Settled.

## Part status

`plan.md` holds what each part owns and hands off; this table holds only what has moved.

| # | Slug | Status | # | Slug | Status |
|---|---|---|---|---|---|
| 1 | lenet-5-every-number-by-hand | planned | 10 | lstm-vanishing-gradients-cell-state | planned |
| 2 | backpropagation-through-a-cnn-by-hand | planned | 11 | seq2seq-bahdanau-attention | planned |
| 3 | alexnet-by-the-numbers | planned | 12 | transformer-shape-by-shape | planned |
| 4 | vgg-3x3-convolutions-138-million-parameters | planned | 13 | transformer-math-derived | planned |
| 5 | googlenet-inception-module-1x1-convolutions | planned | 14 | vision-transformer-vit | planned |
| 6 | batch-normalization-derived-inception-v3 | planned | 15 | resnext-densenet-senet | optional |
| 7 | resnet-residual-block-shape-by-shape | planned | 16 | efficientnet-compound-scaling | optional |
| 8 | why-residual-networks-train | planned | 17 | convnext-resnet-modernised | optional |
| 9 | mobilenet-depthwise-separable-inverted-residuals | planned | 18 | bert-encoder-only-transformer | optional |

Status is `planned`, `researching`, `drafting`, `ready`, or `published`.

## Knowledge established

None yet. After each completed part, add its heading and no more than eight durable bullets.

## Decisions to preserve

- **Naming.** "Part N" in a title counts within one model (*ResNet, Part 1*), never across the
  series. `series_position` is reading order and never appears in a title. Slugs never carry a part
  number.
- **Counting convention.** Count MACs and write FLOPs = 2 × MACs. When a paper says "FLOPs", state
  whether it means multiply-adds. Parameter totals say whether biases and BN affine terms are in;
  running statistics are buffers, not parameters.
- **Notation.** N × C × H × W for images, B × T × d for sequences, row vectors (y = xW).
- **Provenance.** Every figure number is *computed* (lab script from the published config),
  *measured* (our run, with a setup line) or *reported* (ledger row, with its protocol), and the
  caption says which. Toy runs are never presented as the paper's experiment.
- **Visual system V1–V12.** Shared generators copied into each part's `assets/`. Colour maps (one
  sequential, one diverging at zero) are fixed at Part 1 and never changed. Equations stay in KaTeX.
- **Shared examples.** The hand-worked conv patch is image-processing's 5×5 (rows
  `40 40 40 200 200`, r2 `40 255 40 200 200`), scaled to [0, 1] — never a second patch. One shared
  real image is used for every pretrained forward pass (chosen at Part 1's research, recorded here).
  Part 12's four-token, d = 8, two-head attention toy is the shared attention example; the frontier
  series reuses it.
- **Toolchain.** Copy the newest toolchain (image-processing Part 4's `assets/_build.py`, `_figs.py`,
  `_cover.py`, `_social.py`) and bump `ROOT = HERE.parents[3]` for series depth. Keep units out of
  uppercased labels (the µ → "M" bug). Rasterise with absolute paths.

## Open threads

- **Awaiting Checkpoint S.** The user must choose between two series and one, confirm the name, and
  approve Tier B.
- **Tier B lab environment.** It is not built. If approved, Part 1 or the first Tier B part creates
  the pinned `uv` environment (numpy, torch CPU, torchvision; transformers only when needed) and
  documents it in its lab README.
- **The shared image.** Not chosen. It needs a clear licence (CC0 or public domain) and must be
  recognisable to ImageNet classifiers.
- **Every hook number** in `plan.md` is unverified until its part's research.

## Next part brief

- **Part:** 1 — LeNet-5, Part 1: How to Read a CNN (`lenet-5-every-number-by-hand`).
- **Can assume:** Python, matrix multiplication, what a layer is. Link image-processing Part 1 for
  convolution as filtering.
- **Must teach:** output size, parameters, MACs, receptive field and activation memory, each
  reconciled against LeCun et al. 1998's own totals — including C3's partial connection table
  (1,516 parameters, to verify) and the trainable subsampling layers.
- **Must not repeat:** convolution-as-filtering from image-processing; any gradient (that is
  Part 2).
- **Evidence still needed:** the 1998 paper's layer-by-layer parameter and connection counts; the
  convolution-arithmetic guide's formulas; Luo et al. 2016 on effective receptive fields; a
  saturation check on "cnn parameter calculation" and "receptive field calculation" results.
- **Build duties this part carries for the series:** the V1 shape-strip and V2 params/MACs
  generators, the Tier A counting script every later part copies, the fixed colour maps and the
  choice of shared image.
- **Handoff:** the counting rules (`#the-counting-rules`) and receptive field (`#receptive-field`)
  anchors that Parts 2, 3, 4, 5 and 7 link to.
