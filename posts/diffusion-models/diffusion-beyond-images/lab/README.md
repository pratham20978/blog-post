# Lab — Diffusion Beyond Images: Video, Audio, 3-D and Molecules

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-10-21 · the build machine (laptop CPU, one thread)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs, run on one thread), 14 GB RAM; Python 3.12.15, numpy 2.5.3; `beyond.py` 970b6b049450. The notebook was built and executed with Python 3.14.4 and the same numpy pin.

This lab reproduces every number the article calls measured. Crescent world is the series' toy: every
8×8 frame shows one of four crescents, faint or strong, with a random brightness and a little pixel
noise. Here it also moves: in a clip of four frames the crescent turns a quarter turn per frame, always
the same way, keeping one contrast and one brightness. Both the frame distribution and the clip
distribution are Gaussian mixtures, so both have exact denoisers, and every failure the lab shows
belongs to how a sampler is driven or conditioned, never to a badly trained network. The one entry point
is `beyond.py`; it writes `captures.json` (or the file you name with `--out`) and prints the same
numbers. The article's size census and wrapped-normal numbers are computed by the same file from the
papers' stated configurations; its quoted results (FVD, molecule stability, CRPS) come from the papers.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `beyond.py` | G1 | yes | crescent world in motion, the exact frame and clip denoisers, the noise schemes, forecasting by replacement and by exact conditioning, score distillation, and the size census, in numpy |
| `requirements.txt` | — | — | the one pinned dependency, numpy |
| `captures.json` | — | — | the author's run, machine-readable; every measured figure in the article reads it |
| `expected-output.txt` | — | — | the same run as printed, to compare with yours |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.32 GB of RAM |
| Software | Python 3 (run on 3.12.15 and 3.14.4) and numpy 2.5.3: `pip install -r requirements.txt` into a virtual environment, or `uv run --with numpy==2.5.3` |
| Privileges | none: no root, no Docker, no network access, nothing outside this folder |
| Disk, network, time | no downloads beyond numpy; `all` takes about a minute on one core (the capture took 63 s: worked 22 s, video 19 s, forecast 7 s, sds 14 s); `all --quick` takes 14 s |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python beyond.py all --out mine.json          # keeps the shipped captures.json for comparison
```

Each stage also runs alone: `python beyond.py worked`, `video`, `forecast`, `sds` or `census`.
`--quick` cuts the clips from 4,096 to 1,024 and the SDS runs from 256 to 64, for a faster and noisier
run. Two flags exist for the exercises: `video --warp-variance V` scales the variance of the warped
frames' noise, and `video --fault` swaps in an earlier draft of the warp.

## What to expect

The first line is the provenance line. Then, stage by stage:

- `worked`: the top-left forward step, 0.8 × 0.95 + 0.6 × −0.55 = 0.43; the clip reading's mean change
  between frames, 0.1833 clean and 0.8050 noisy (4.39×); the noise centroid (0.15, −0.0125); then the
  one-pixel video, whose two frames agree 0.4990, 0.6665, 0.8550, 0.9550 and 1.0000 of the time at
  ρ = 0, 0.5, 0.9, 0.99 and 1, against 1/2 + arcsin(ρ)/π = 0.5000, 0.6667, 0.8564, 0.9549 and 1.
- `video`: real clips are 99.46% coherent. The per-frame model with independent noise gives 0 coherent
  clips of 4,096, with 81.6% of frame changes flickering and 49.1% flipping contrast; mixed noise trades
  flicker for freezing (at ρ = 0.9, 44.9% flicker and 74.1% of changes without a turn); shared noise
  freezes every clip; warped noise gives 99.56% coherent clips and the joint model 99.39%. The last line
  checks the warp: a quarter turn commutes with the frame denoiser to 2.9 × 10⁻¹⁵ and repeats every 4
  frames.
- `forecast`: replacement continues 17.38%, 63.33% and 95.97% of clips coherently from 1, 2 and 3
  observed frames; exact conditioning 99.34%, 99.44% and 99.49%.
- `sds`: at w = 1 the 256 SDS runs end 53.1% faint, 11.3% between the modes and 35.5% strong, with
  brightness spread 0.0119 (real 0.306) and pixel detail 0.0005 (real 0.0995); from w = 2 every run is
  strong; at w = 7.5, 81.6% exceed the brightest real crescent; at w = 101 the mean contrast is 2.350.
- `census`: sizes from 7.9 torsion angles to 24,772,608 pixel values; compression 32× (Stable Audio),
  5× (AudioLDM against the waveform) and 48× (SVD); DiffWave's 6,139-sample reach, 0.384 s; the
  wrapped normal's peak over trough, 1.0292 at σ = π.

Every value is deterministic: two runs on the build machine agreed in every digit. On numpy 2.5.3 with
one thread, expect the shares to four decimals; a different BLAS or numpy may move the last digit of a
share, because a sample that sits exactly on a threshold can fall either side.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden
below it. This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: flicker, freezing and motion

Run the video stage into your own file and read the coherent-clip share for independent noise, shared
noise, warped noise and the joint model, and the flicker share for independent noise.

```bash
python beyond.py video --out mine.json
```

**Self-check:** independent 0.0000, shared 0.0000, warped 0.9956, joint 0.9939; independent flicker
0.816; and the provenance line printed first.

<details><summary>Answer</summary>

The author's run printed `independent: ... flicker 0.816 | clips: frozen 0.0171, moving 0.0281,
coherent 0.0000`, `shared: ... frozen 1.0000 ... coherent 0.0000`, `warped: ... coherent 0.9956` and
`joint: ... coherent 0.9939`, against `data: ... coherent 0.9946` for real clips. Every frame is a valid
crescent in every scheme (99.5–99.8%); what differs is only whether the frames belong together. If
your shares differ beyond the fourth decimal, compare numpy versions first, then check that you did not
pass `--quick`, which samples 1,024 clips instead of 4,096.

</details>

### E2 — Inspect: what correlation does to motion

The article says no noise correlation produced a coherent clip. Look one level down: in your
`mine.json`, under `video` → `schemes`, read `motion_clips` (clips whose crescent turns one consistent
quarter turn per frame, whatever their contrast and brightness) and `frozen_clips` for `independent`
and for every `mixed` correlation, in order of ρ.

**Self-check:** state which way each share moves as ρ rises, and where the independent value of
`motion_clips` comes from.

<details><summary>Answer</summary>

`motion_clips` falls from 0.0281 (independent) to 0.0125, 0.0051, 0.0024, 0.0010 and then 0 at ρ = 0.25,
0.5, 0.75, 0.9 and 0.95, while `frozen_clips` rises from 0.0171 to 0.0618, 0.1575, 0.3433, 0.5540,
0.6748 and 0.8450 at 0.99. Correlation never buys motion; it buys sameness. The 2.8% at ρ = 0 is chance:
the first change must be some quarter turn (1/2) and the next two must repeat it (1/4 each), about 3%.

</details>

### E3 — Predict: a warp that lost variance

A warp that shifts noise by part of a pixel and interpolates leaves it with variance α² + (1 − α)², half
at half a pixel. Before running, predict what happens to the warped scheme when frames 2 to 4 get
exactly that: their quarter-turned noise scaled to variance 0.5. Say which of motion, contrast and
brightness break, and roughly how often. Then run:

```bash
python beyond.py video --warp-variance 0.5 --out mine.json
```

**Self-check:** motion stays above 0.98; coherence falls to between 0.5 and 0.7; flicker and contrast
flips appear only at the first frame change; for the reason that turning and shrinking the noise keeps
its direction but shrinks the brightness and contrast it encodes.

<details><summary>Answer</summary>

The author's run printed `warped: frames valid 0.9974 | turns: frozen 0.001, quarter 0.996, half 0.002 |
contrast flips 0.066, flicker 0.083 | clips: frozen 0.0000, moving 0.9893, coherent 0.5930`. The turn
survives because a scaled quarter-turned noise still points the quarter-turned way, and the frame model
follows it. Brightness does not: along the brightness direction the exact sampler is linear, so frames
2–4 come out with about 0.71 of frame 1's brightness, which is a jump bigger than 0.1 whenever frame 1's
brightness is larger than about 0.34 in size, roughly a quarter of clips. Frames 2–4 share one scaled
noise, so the flicker happens only at the first change: 8.3% of all changes is 25% of clips, and the
6.6% of changes that flip contrast are 20% of clips. Coherence falls from 0.9956 to 0.5930.

</details>

### E4 — Diagnose: warped clips that stopped moving

Run the video stage with the earlier draft of the warp and treat the result as someone else's code:
say what went wrong, the one printed observation that proves it, and the fix.

```bash
python beyond.py video --fault --out mine.json
```

**Self-check:** the symptom in one line, the cause in one sentence, the printed line that proves it,
and a fix after which `--fault` prints warped coherence above 0.99, a commute error below 10⁻¹⁰ and a
period of 4.

<details><summary>Answer</summary>

**Symptom.** `warped` now prints `turns: frozen 0.307, quarter 0.382, half 0.311 | contrast flips 0.185,
flicker 0.000 | clips: frozen 0.3066, moving 0.0000, coherent 0.0000`: frames are still valid and
brightness is steady (one shared noise), but the crescent jumps about at random and 31% of clips freeze.

**Observation.** The last line reads `warp in use: max |D(warp x) - warp D(x)| at sigma 2 = 2.29e+00;
it repeats every 2 frames`. A quarter turn commutes with the frame denoiser to 2.9 × 10⁻¹⁵ and repeats
every 4 frames.

**Cause.** The draft's `warp` swaps the two image axes, which is a reflection across the diagonal, not a
quarter turn. Crescent world contains no reflected crescents, so the image model does not follow that
warp, and reflecting twice returns the original, so frames 1 and 3 get the same noise and so do frames
2 and 4.

**Fix and check.** A quarter turn is a transpose followed by a flip, which is what `np.rot90` does: in
`warp`, make the `fault` branch return `rot(z, k)`, which turns the noise the clip's own way. Rerun
the command: the warped line prints `coherent 0.9956`, and the last line `2.89e-15` and `4 frames`.
Restore the file afterwards, or the provenance hash of your later runs will not match the shipped one.

</details>

## Safety and cleanup

- The lab reads and writes only files in this folder. It contacts no service, downloads nothing and
  needs no network.
- It writes `captures.json`, or the file named with `--out`; the exercises write `mine.json`, so the
  shipped capture stays as it is.

```bash
rm -f mine.json && rm -rf .venv __pycache__
```
