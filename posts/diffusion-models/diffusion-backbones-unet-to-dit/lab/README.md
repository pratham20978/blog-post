# Lab — Diffusion Backbones: U-Net to DiT, Block by Block

- **Grade:** G1 · runs anywhere (CPU PyTorch in a pinned environment; this series' "stdlib and CPU" lab letter)
- **Executed:** yes · 2026-10-03 · AMD Ryzen 7 5825U laptop, Ubuntu 26.04.1, no GPU
- **Provenance:** Linux 7.0.0-31-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs, PyTorch using 8 threads), 14 GB RAM; Python 3.12.13, torch 2.14.0+cpu, diffusers 0.40.0 (numpy 2.5.3, safetensors 0.8.0, huggingface-hub 1.33.0 as installed by diffusers)

This lab reproduces every measured number in the article. `census.py` builds Stable Diffusion
1.5's U-Net from its published config, DiT-XL at three patch sizes from a short implementation of
the official architecture, and Stable Diffusion 3's MM-DiT from its paper's sizing rule, all on
PyTorch's `meta` device: shapes, parameter counts and FLOP counts are exact there, and no weights
are downloaded or allocated. It then runs one real attention layer on your CPU, naive and fused,
and prints the memory arithmetic. The article's figures were drawn from the `captures.json` this
script wrote on the machine above.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `census.py` | G1 | yes | the entry point: six sections (`patch`, `unet`, `dit`, `mmdit`, `attention`, `memory`) |
| `requirements.txt` | — | — | the two pinned packages and where to get the CPU build of PyTorch |
| `captures.json` | — | — | the author's run, machine-readable; every figure in the article reads it |
| `expected-output.txt` | — | — | the same run as printed, to compare with yours |

## What you need

| | |
|---|---|
| Hardware | any laptop with about 3 GB of free RAM (the naive attention at 4,096 tokens allocates 1.1 GB); 6 GB for the optional `--execute` run |
| Software | Python 3.10 or newer; CPU PyTorch 2.14.0 (about 200 MB) and diffusers 0.40.0 |
| Privileges | none: no root, no Docker, no GPU, nothing outside this folder and its virtual environment |
| Disk, network, time | about 1 GB for the environment; no model download; about 20 seconds per run on the author's laptop, plus 5–10 seconds for `--execute` |

## Run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.0+cpu
pip install diffusers==0.40.0
python census.py               # all sections; writes captures.json
python census.py unet dit      # selected sections; prints only
python census.py --execute     # also runs the real fp32 U-Net once on the CPU (3.4 GB)
```

Running all sections overwrites `captures.json`. Copy the shipped one aside first if you want to
diff against it.

## What to expect

The first line is the provenance of your run. Then, section by section (excerpt):

```text
== unet: Stable Diffusion 1.5 U-Net, 512x512 image, batch 1 ==
  params 859,520,964   forward 803.27 GFLOP (conv 443.95, linear 233.28, attention core 126.05)
  skip stack: 12 tensors, 6,635,520 values = 13.3 MB in fp16 per image
  level 0       64px params   29.3M ( 3.4%)  GFLOP  307.12 (38.2%)  attn-core 109.39
== dit: DiT-XL at three patch sizes (batch 1) ==
  DiT-XL/2  256px latent [4, 32, 32] ->  256 tokens  params  675.1M (paper 675M)   118.62 GMAC (paper 118.64 'Gflops')
== mmdit: SD3 MM-DiT ==
  d=24: width 1536, 24 heads, params 2,028,328,000  (image stream 1020M, text stream 989M, outside blocks 19M)
```

**Exact:** every shape, parameter count and FLOP count, in every section. They depend only on the
architecture, so they must match `expected-output.txt` digit for digit on any machine.
**Close:** the `--execute` output shape must be `[1, 4, 64, 64]`; its time is your CPU's.
**Machine-dependent:** the attention timings and allocation sizes. Timings vary by CPU, thread
count and load, by a factor of two or more between runs on the same machine; the ratio between
naive and fused should stay above about 3× at 4,096 tokens. The largest naive allocation must be
at least the score matrix, $16 \times N^2 \times 4$ bytes (1,073.7 MB at 4,096 tokens); the fused
path's should stay in the tens of megabytes.

FLOPs count a multiply-add as 2. The DiT paper counts it as 1, so its "Gflops" equal this
script's GMAC.

## Exercises

Do them in order. Each has a self-check you can mark yourself against, with the answer from the
author's run hidden below it. This is an L4 post, so the lab ships E1 to E5.

### E1 — Reproduce: the three headline counts

Run `python census.py unet dit mmdit` and find SD 1.5's parameter count and forward FLOPs, DiT-XL/2's
GMAC at 256×256, and the d = 24 MM-DiT's parameter count.

**Self-check:** all four match `expected-output.txt` exactly, and your provenance line printed first.

<details><summary>Answer</summary>

859,520,964 parameters and 803.27 GFLOP; 118.62 GMAC; 2,028,328,000 parameters. A mismatch in any of
them means a different diffusers or torch version changed a module, not a different machine: check
`pip show torch diffusers` against `requirements.txt`.

</details>

### E2 — Inspect: the heaviest block

The article gives per-level totals. Using the `trace` list under `unet` in `captures.json`, find the
single top-level U-Net block (a `down_blocks.i`, `mid_block` or `up_blocks.i` entry) with the most
parameters, and say from its sub-blocks why it is the largest.

**Self-check:** a block name, its parameter count to 0.1M, and a reason that names its input widths.

<details><summary>Answer</summary>

`up_blocks.1`, the 16×16 level on the way up, with 258.3M parameters. It has three ResNet blocks
instead of the down path's two, and each concatenates a skip first, so their inputs are 2,560,
2,560 and 1,920 channels wide (49.2M, 49.2M and 41.0M parameters); its three transformer blocks
are 1,280 wide (34.8M each).

</details>

### E3 — Predict: SD 1.5 at 768×768

A 768×768 image gives a 96×96 latent, 2.25 times the positions. Write down your prediction for
SD 1.5's total forward FLOPs, and for the attention-comparison FLOPs alone, before running this:

```python
import torch
from census import META, SD15_UNET, UNet2DConditionModel, count_flops, total
with META:
    unet = UNet2DConditionModel(**SD15_UNET)
    x, t, ctx = torch.randn(1, 4, 96, 96), torch.tensor([500]), torch.randn(1, 77, 768)
flops, _ = count_flops(lambda: unet(x, t, encoder_hidden_states=ctx).sample)
print(total(flops["Global"]) / 1e9, flops["Global"])
```

**Self-check:** the total within 10% of the author's run, and an attention factor near 5 that you
can justify from the article's intuition, not from the run.

<details><summary>Answer</summary>

2,148.1 GFLOP, 2.67 times the 803.3 at 512×512: more than the 2.25 the pixel count suggests. The
convolutions grow by exactly 2.25 (443.95 to 998.88 GFLOP) and the linear layers by almost that
(233.28 to 521.11), because both cost per position. Attention's comparisons grow by 4.98 (126.05 to
628.13), close to $2.25^2 = 5.06$, because they cost per pair of positions; the small cross-attention
part, which compares image positions with 77 fixed text tokens, grows only by 2.25 and pulls the
factor below 5.06.

</details>

### E4 — Diagnose: 750 million parameters

Build diffusers' own DiT class with the published DiT-XL/2 config and count it:

```python
import torch
from diffusers import DiTTransformer2DModel
from census import DiT
with torch.device("meta"):
    theirs = DiTTransformer2DModel(num_attention_heads=16, attention_head_dim=72, in_channels=4,
                                   out_channels=8, num_layers=28, sample_size=32, patch_size=2,
                                   num_embeds_ada_norm=1000, norm_type="ada_norm_zero",
                                   norm_elementwise_affine=False)
    ours = DiT(input_size=32, patch=2)
print(sum(p.numel() for p in theirs.parameters()), sum(p.numel() for p in ours.parameters()))
```

It reports about 750M, against the paper's 675M and this lab's 675.1M. Both load the same
checkpoint. Find the cause.

**Self-check:** the symptom, the cause, the one observation that proves it (an exact parameter
difference), and why neither count is a bug in the network's function.

<details><summary>Answer</summary>

Symptom: 749,826,464 against 675,129,632, a difference of 74,696,832. Cause: in diffusers, every
block's `AdaLayerNormZero` (`transformer_blocks.i.norm1.emb`) holds its own timestep MLP and class
table, 1,624,320 + 1,153,152 = 2,777,472 parameters, where the official model holds one shared copy.
Observation: 27 extra copies are 74,991,744 parameters, and diffusers stores the frozen position
table as a buffer rather than a parameter, which removes the 294,912 that this lab and the official
code count: 74,991,744 − 294,912 = 74,696,832 exactly. diffusers' conversion script fills all 28
copies from the same checkpoint tensors, so the function is identical. The fix is to check that two
counts cover the same modules before comparing models across libraries: here, subtract the 27
duplicated embeddings and add back the 294,912-value position table, and the two implementations
agree to the parameter.

</details>

### E5 — Extend: add SDXL's U-Net

Add a `section_sdxl` to `census.py` that builds SDXL's U-Net from its published config
(`stabilityai/stable-diffusion-xl-base-1.0`, `unet/config.json`) and prints the same per-level table
as `section_unet` for one 1024×1024 image. SDXL needs a 77×2048 text context and an
`added_cond_kwargs` of `{"text_embeds": (1, 1280), "time_ids": (1, 6)}`.

**Self-check:** your section passes all of these:

- 2,567,463,684 parameters, and an output of shape `[1, 4, 128, 128]` for a 128×128 latent;
- per-level parameters that sum to the total, and per-level FLOPs that sum to the counter's
  global total (6,761.2 GFLOP);
- the level that holds the most parameters is not the level that does the most attention
  comparisons.

<details><summary>Answer</summary>

The author's version gives 6,761.2 GFLOP. The 32×32 level, with ten-deep transformers, holds 2,377.1M
parameters (92.6%) and 4,683.1 GFLOP (69.3%); the 64×64 level holds 166.4M (6.5%) and does 437.6 of
the 783.9 GFLOP of attention comparisons (55.8%); the 128×128 level has no attention at all. SDXL
removed attention from its finest level and still spends most of its comparisons at the finest level
that kept it.

</details>

## Safety and cleanup

- Everything runs in this folder's virtual environment. Nothing contacts a server, a model hub or
  any shared service; the configs are written into `census.py`.
- The script writes only `captures.json`, and only when run with no section names.

```bash
deactivate
rm -rf .venv __pycache__
```
