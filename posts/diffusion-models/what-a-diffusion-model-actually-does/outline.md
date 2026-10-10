# Outline — what-a-diffusion-model-actually-does

Series: `diffusion-models`, part 1 of 12. Read `../plan.md` and `../context.md` before editing.

## Brief

- **Subject:** machine learning / generative modelling
- **Tier:** L2 · **Difficulty:** beginner
- **Audience:** a CS student or working engineer who knows what a neural network is and has
  never read a generative-modelling paper.
- **The one question this part owns:** why can a model that only ever learned to undo noise
  invent an image?
- **The three questions that fall out of it, and that the post also owns:**
  1. What does a single denoiser call actually return? (the average of every clean image
     consistent with this noise — which is why one call gives a blur)
  2. Where does the *new* image come from, if the network only ever saw corruptions of old ones?
     (the seed and the stochastic path — with the honest boundary where that stops being true)
  3. Why many small steps rather than one big one? (the reverse of a large corruption is not
     Gaussian; the reverse of a tiny one is)
- **Deliberately deferred:** every network internal → Part 2. The ELBO → Part 3. Solver
  families → Part 6. Guidance → Part 8. Memorisation at length → Part 12.
- **Target:** 3,500 substantive words, 6 figures.
- **Actual:** 4,665 words, 6 figures. Inside the L2 band (3,000–5,000 words, 5–8 figures);
  over the 3,500 plan because the Intuition section and the memorisation numbers both needed
  their conditions stated, and a condition-free number is worse than no number.

## Section budget

L2 midpoint 4,000 discounted to a 3,500 plan; shares from `depth-tiers.md`.

| Section | Budget | Actual | Reader can now… |
|---|---:|---:|---|
| Insights + who this is for | 105 | 130 | say in one sentence what the network learned and what it does not know |
| Why this matters | 140 | 95 | tell which of two failures belongs to the network and which to the procedure |
| The problem | 280 | 400 | state why sampling a data distribution directly is hard, and what the corruption path buys |
| Worked example | 525 | 520 | compute one forward step on 16 real numbers and read off the training target |
| Intuition | 350 | 330 | say what the network is estimating, and why it is a compass rather than a map |
| Where does 0.64 come from? | 300 | 320 | read a schedule curve and say what moving it changes |
| Why does one call blur and many calls draw? | 420 | 480 | explain small-step Gaussianity and the averaging argument together |
| Where does the new image come from? | 330 | 430 | attribute novelty to the seed, and state the measured condition where that breaks |
| What are the four moving parts? | 280 | 350 | name path, schedule, denoiser, sampler and say which survives a swap |
| The math | 350 | 400 | apply the closed form and one ancestral reverse step to the same numbers |
| Implementation | 280 | 260 | run a forward process and one reverse reconstruction in ~25 lines |
| Limitations and common mistakes | 175 | 330 | avoid the four beginner errors named below |
| Key takeaways + exercises + references | 70 | 620 | carry away six complete claims, and check three by hand |

The two sections that ran over are *The problem* and *Limitations*. Both did so for the same
reason: every benchmark number in this post carries its setup, and the setups are long. That is
the tier's cost of not overclaiming, not padding. *Try it yourself* and *References* account for
most of the final row.

Four body sections, totalling 1,580 words. The L2 band allows two to four.

## Figure plan

Route gate run per figure against the real content, per `blog-visuals/references/visual-taxonomy.md`.

| # | File | Section | The one thing it must communicate | Route | Why (the clause that settled it) |
|---:|---|---|---|---|---|
| 1 | fig-01-forward-is-a-formula | The problem | the forward arrow carries a closed-form formula and the reverse arrow does not — the asymmetry *is* the reason a network exists | `placed` | Q4 — the five states must be drawn as real patches at real signal levels; a box labelled "noising" carries none of the decay |
| 2 | fig-02-one-forward-step | Worked example | one forward step on 16 visible numbers: 0.8·x₀ + 0.6·ε = x_t | `placed` | Q4 — a grid of real values where the reader checks 0.48 + 0.84 = 1.32 by eye |
| 3 | fig-03-noise-schedule | Where does 0.64 come from? | the schedule as two curves, with the worked example's √ᾱ = 0.80 marked and the surviving signal at t/T = 0.75 | `plot` | Q1/Q4 — continuous curves evaluated from the published definitions, with axes and marked crossings |
| 4 | fig-04-the-average-is-the-blur | Why one call blurs | many clean patches are consistent with one noisy patch, and their average is the blur | `placed` | Q4 — the point only lands if the candidates and their mean are drawn as patches; boxes cannot show an average |
| 5 | fig-05-one-jump-versus-eight-steps | Why one call blurs | same starting noise, one jump vs eight small steps, beside the error multiplier | `placed` | Q4 — small multiples of one tensor at successive levels; the comparison is the figure |
| 6 | fig-06-the-four-moving-parts | What are the four moving parts? | the whole system: training loop and sampling loop sharing one denoiser, schedule feeding both | `mermaid` | Q3 — the post's one end-to-end view: 13 nodes, two loops that cross at the shared denoiser |

**Numbering note.** Figures 3, 4 and 5 were built in a different order than they are read, so the
files were renumbered to match order of appearance before the manifest was written. `_figures.py`
keys its `FIGURES` map by the post's number, not by definition order.

Figure budget check: 6 figures over 4,665 words is one per 778 words. That is just outside the
500–700 guidance, and it is the right call here — a seventh figure would have had to repeat one of
the six at a different zoom, which `visual-taxonomy.md` lists under "when not to draw".

Alt text is written once, in `manifest.md`, and copied verbatim into `blog.md`.

### Paper-figure (`source` route) check

Inspected for reuse before planning originals: Ho 2020 Fig. 2 (the graphical model), Song &
Ermon 2019 Fig. 1 (score field), Nichol & Dhariwal 2021 Fig. 1 (linear vs cosine). All three are
covered only by the arXiv perpetual non-exclusive distribution licence, which is not a reuse
licence, so none takes the `source` route. Every figure here is our own analysis on our own
worked numbers rather than a redraw of a paper composition — which is also the stronger figure
for this post, because the values in figures 2, 3 and 4 are the post's own arithmetic.

## Term map

Every term is introduced at its first meaningful use with name, what, why and when — never sent
to this table.

| Term | First section | What it is | Why it is used here | When it matters |
|---|---|---|---|---|
| diffusion model | Insights | a generative model built from a fixed corruption path plus a learned reversal | it is the object the whole post explains | throughout |
| forward process (noising) | The problem | a fixed, known recipe that adds Gaussian noise in steps | it manufactures training pairs for free | when you need to know why no labels are required |
| reverse process | The problem | the learned walk from noise back toward data | it is the generative direction | every time you sample |
| Gaussian noise | The problem | a random draw from a bell curve, mean 0, spread 1 | it is the corruption whose reverse is tractable | reading any diffusion equation |
| timestep *t* | Worked example | an index into the corruption path | the network must be told how noisy its input is | every call to the denoiser |
| noise schedule | Where does 0.64 come from? | the fixed sequence β₁…β_T setting how fast signal dies | it decides which noise levels the network ever practises | choosing or debugging training |
| ᾱ_t (alpha-bar) | Worked example | the cumulative fraction of signal power surviving at step *t* | it is what lets training jump to any *t* in one operation | any closed-form forward step |
| ε-prediction | Worked example | the network outputs the noise it thinks was added | the target is free, because we drew the noise ourselves | reading DDPM-style code |
| score | Intuition | the gradient of the log density, a field pointing toward denser data | it is the same output as ε-prediction, rescaled — named so part 3 can build on it | reading any score-based paper |
| denoiser | Intuition | the trained network, the only learned component | it estimates the corruption, not the picture | whenever someone says "the model" |
| conditional mean / MMSE estimate | Intuition | the average of every clean image consistent with this noisy one | it is literally what a squared-error-trained network converges to | explaining why one step blurs |
| sampler | Four moving parts | the numerical procedure that repeatedly calls the denoiser | it is swappable without retraining | changing step counts |
| signal-to-noise ratio | Where novelty comes from | how much signal remains relative to noise at step *t* | it names the difficulty of one denoising call | reading schedule plots |
| seed / initial noise x_T | Where novelty comes from | the random tensor a sample starts from | it is the input that makes the output new | reproducing a generation |
| latent diffusion | Four moving parts (one sentence) | denoising a compressed code instead of pixels | it explains why real systems are affordable | named, then handed to Part 2 |

## Limitations section — the four beginner errors it must name

1. "The model removes noise from my image" — it estimates the noise in a *synthetically* noised
   input at a *known* level; it is not a photo restoration tool.
2. "More steps is always better" — steps past the point where discretisation error stops
   dominating buy nothing, and the sampler, not the network, sets that point.
3. "It's just memorising" — mostly wrong, occasionally right, and the condition that separates
   the two is duplicated training data. Carry the real numbers, not a reassurance.
4. "Diffusion means DDPM" — the modern text-to-image transformer line trains with rectified flow;
   the family name is broader than the 2020 objective. One sentence, handed to Part 2.

## Handoffs this post must make explicitly

- The denoiser box in Figure 6 is the object Part 2 opens up.
- The loss is stated, not derived. The derivation is Part 3's.
- "Twenty steps instead of a thousand" is named as possible and not explained. Part 6.
- Prompts are mentioned once, as conditioning that this post does not cover. Part 8.

## Gate

```bash
python3 .claude/blog-forge/scripts/validate_post.py posts/diffusion-models/what-a-diffusion-model-actually-does/
python3 .claude/blog-forge/scripts/lint_visuals.py posts/diffusion-models/what-a-diffusion-model-actually-does/assets/
```
