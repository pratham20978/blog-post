# Lab — Discrete Diffusion Language Models: Masks, LLaDA, Samplers

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-10-22 · the build machine (laptop CPU, one thread)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs, run on one thread), 14 GB RAM; Python 3.12.15, numpy 2.5.3; `tokens.py` 0be0dfe2a2af. The notebook was built and executed with Python 3.14.4 and the same numpy pin.

This lab reproduces every number the article calls measured. Crescent world is the series' toy: an 8×8
image of one of four crescents, faint or strong, at some brightness. Here every image is a sequence of 64
tokens: each pixel is rounded to one of 28 grey levels (one level per 0.15 of brightness), and the
brightness takes one of nine levels from −0.6 to 0.6, the middle ones likelier. That makes exactly 72
images, each with a known probability, so a sample is valid only if it is one of them, and the exact
denoiser of a partly masked image is a lookup: the images that agree with every token already written,
weighted by their probabilities. If a sampler writes a combination no image has, the denoiser continues
from the images that disagree with the fewest tokens. Every failure below belongs to the sampler, never
to a badly trained network. The one entry point is `tokens.py`; it writes `captures.json` (or the file you
name with `--out`) and prints the same numbers. The article's quoted results (perplexities, benchmark
scores, Gen PPL) come from the papers.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `tokens.py` | G1 | yes | the 72-image world and its exact denoiser, the worked example, every sampler in the article, and MDLM's Gumbel race in float32 and float64, in numpy |
| `requirements.txt` | — | — | the one pinned dependency, numpy |
| `captures.json` | — | — | the author's run, machine-readable; every measured figure in the article reads it |
| `expected-output.txt` | — | — | the same run as printed, to compare with yours |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.29 GB of RAM |
| Software | Python 3 (run on 3.12.15 and 3.14.4) and numpy 2.5.3: `pip install -r requirements.txt` into a virtual environment, or `uv run --with numpy==2.5.3` |
| Privileges | none: no root, no Docker, no network access, nothing outside this folder |
| Disk, network, time | no downloads beyond numpy; `all` takes about two minutes on one core (the capture took 118 s: worked under 1 s, world 16 s, decode 102 s, precision 1 s); `all --quick` takes 31 s |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python tokens.py all --out mine.json          # keeps the shipped captures.json for comparison
```

Each stage also runs alone: `python tokens.py worked`, `world`, `decode` or `precision`. `--quick` cuts the
images per sampler from 4,096 to 1,024 and the race draws from 2,000,000 to 200,000, for a faster and
noisier run. Two flags exist for the exercises: `decode --levels 1` puts every image at one brightness, and
`decode --fault` swaps in an earlier draft of one sampler.

## What to expect

The first line is the provenance line. Then, stage by stage:

- `worked`: Part 1's patch as tokens `[[3, 3, 1, 0], [3, 2, 0, 0], [3, 2, 0, 0], [2, 1, 0, 0]]`; 7 of 16
  masked at ᾱ = 0.64 (Part 1's ε above 0.3585); uniform replacement keeps a token with probability 0.73.
  In the world of the patch's four quarter turns only the upright turn fits the visible tokens; the two
  opposite corners drawn at once belong to a turn 0.5 of the time and are both darkest 0.25 of the time;
  all 16 at once form a turn with probability 3.81 × 10⁻⁶; one token at a time costs ln 4 = 1.386294 nats
  for every turn.
- `world`: 72 images of 64 tokens over 28 grey levels, entropy 4.0968 nats, brightness spread 0.2777. Every
  reveal order gives −log p(image) to 8.9 × 10⁻¹⁶ nats; a random order decides the image after 4 tokens
  (median), 8 (90th percentile), 20 at most.
- `decode`, 4,096 images per sampler: one token per step in random order or ranked by how sure each
  position is, all 72 images and brightness spread 0.276 and 0.281; ranked by the drawn token's probability,
  8 images and spread 0; greedy, 23 images (random order) and 4 (confidence order). Two tokens per step in
  random order, 17.87% valid; four, 0.34%; eight or more, none. MDLM's ancestral update: 51.90%, 86.16% and 95.83% valid
  with 64, 256 and 1,024 steps, revealing 63.08%, 21.98% and 5.97% of tokens alongside another. A
  certainty threshold: 100% valid, all 72 images, 7.24 calls.
- `precision`: the share of its fair chance a token wins MDLM's race, float32 against float64, at token
  weights from 10⁻⁹ to 10⁻⁵ of the mask's: 0, 0.0149, 0.3164, 0.7316 and 0.9917 at 10⁻⁹, 10⁻⁸, 3 × 10⁻⁸,
  10⁻⁷ and 10⁻⁵ in float32, about 1 throughout in float64, against the closed form x/(eˣ − 1) with
  x = 2⁻²⁴/c. Float32 halves a token's chance below c = 4.74 × 10⁻⁸.

Every value is deterministic: two runs on the build machine agreed in every digit. On numpy 2.5.3 with
one thread, expect every share to four decimals; another numpy version may draw a different random
stream, which moves shares in the third decimal and the precision ratios by about 0.01.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden
below it. This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: one token at a time against two

Run the decode stage into your own file and read, for one token per step in random order and for two tokens
per step in random order, the valid share, the number of images found and the brightness spread.

```bash
python tokens.py decode --out mine.json
```

**Self-check:** one per step valid 1.0, 72 images, brightness spread 0.276; two per step valid 0.1787; and
the provenance line printed first.

<details><summary>Answer</summary>

The author's run printed `one token per step, random  : valid 1.0, calls 64.0, images_found 72,
tv_to_world 0.0492, entropy 4.0839, strong 0.5085, brightness_sd 0.276` and `2 per step, random    : valid
0.1787, calls 32.0, images_found 68, ...`. One token per step is exact: every sample is one of the 72
images, in proportions within sampling error of the world's (a total variation of 0.049 is what 4,096 draws
from 72 images give by chance). Two per step halves the calls and leaves fewer than one sample in five
valid. If your shares differ beyond the fourth decimal, compare numpy versions first, then check that you
did not pass `--quick`.

</details>

### E2 — Inspect: when an image is decided

The article says parallel decoding fails because the hidden tokens depend on each other until the image is
decided. Look at that moment directly: run the world stage and read `world` → `decided_after` in your
`mine.json`, the number of tokens a random reveal order needs before only one of the 72 images fits.

```bash
python tokens.py world --out mine.json
```

**Self-check:** state the median, the share of orders decided by the second token, and why the certainty
threshold needs about 7 calls when one token per call needs 64.

<details><summary>Answer</summary>

The author's run gave median 4, mean 4.56, 90th percentile 8 and at most 20; 1.65% of orders are decided by
the first token and 29.12% by the second (1.65% + 27.47%). Until then every hidden token depends on the
others through the crescent's orientation, contrast and brightness, so revealing two at once can pick
values from different images. A certainty threshold reveals every token the denoiser is certain of in one
call, and once the image is decided that is every hidden token, so it finishes in 7.24 calls on average.

</details>

### E3 — Predict: one brightness for every image

Every token shares its image's brightness. Before running, predict what happens to the valid share at two
and at four tokens per step if every image had the same brightness, leaving 8 images (four crescents, faint
or strong). Say which way each moves and roughly how far. Then run:

```bash
python tokens.py decode --levels 1 --out mine.json
```

**Self-check:** both rise, two per step from 0.18 to about 0.45 and four per step from 0.003 to about 0.08,
for the reason that one fewer shared unknown leaves fewer hidden tokens depending on each other.

<details><summary>Answer</summary>

The author's run printed `2 per step, random    : valid 0.4465` and `4 per step, random    : valid
0.0811`, against 0.1787 and 0.0034 with nine brightness levels; MDLM's 64-step ancestral sampler rose from
0.5190 to 0.6716 and the certainty threshold needed 6.35 calls instead of 7.24. With brightness fixed, two
tokens drawn together can only disagree about the crescent's orientation and contrast, so more pairs fit
one image. Parallel decoding still fails often: the 8 images still make every hidden token depend on the
others until two or three tokens are known.

</details>

### E4 — Diagnose: an exact sampler that stopped being exact

Run the decode stage with an earlier draft of one sampler and treat the result as someone else's code: say
what went wrong, the one printed observation that proves it, and the fix.

```bash
python tokens.py decode --fault --out mine.json
```

**Self-check:** the symptom in one line, the cause in one sentence, the printed line that proves it, and a
fix after which `--fault` prints 72 images and a brightness spread near 0.28 on the `position` line.

<details><summary>Answer</summary>

**Symptom.** `one token per step, position` now prints `images_found 8, tv_to_world 0.7958, entropy 2.0781,
... brightness_sd 0.0`: every sample is valid, but only 8 of the 72 images appear, all at one brightness.

**Observation.** The `position` line matches the `drawn` line (8 images, spread 0), while the `random`
line still prints 72 images and spread 0.276. Ranking by how sure each position is should be exact, as the
`random` order is.

**Cause.** In `decode`, the draft ranks positions by `p_drawn`, the probability of the token just drawn at
each position, instead of `sure`, how sure the denoiser is of the position before drawing. That ranking
keeps the draws that happened to land on likely values, so the first tokens written are the commonest
brightness level's, and every image ends at that level.

**Fix and check.** In `decode`, make the `position` rank use `sure` again: delete
`or (rank == "position" and fault)` from the `elif` that sets `score` to `p_drawn`. Rerun the command: the
`position` line prints `images_found 72` and `brightness_sd 0.2814`. Restore the file afterwards, or the
provenance hash of your later runs will not match the shipped one.

</details>

## Safety and cleanup

- The lab reads and writes only files in this folder. It contacts no service, downloads nothing and
  needs no network.
- It writes `captures.json`, or the file named with `--out`; the exercises write `mine.json`, so the
  shipped capture stays as it is.

```bash
rm -f mine.json && rm -rf .venv __pycache__
```
