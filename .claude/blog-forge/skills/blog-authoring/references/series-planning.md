# Series planning: scope and level

This file makes one decision: how many posts a topic is, and what level each one sits at. Make it at brief time, before research, because it changes what is researched — a three-part ladder on diffusion models needs a different sweep for each part, and a sweep run for "diffusion models" as one post will be broad, shallow, and wrong for all three. Deciding scope after the ledger exists means either throwing the ledger away or letting it quietly decide the shape of the writing.

---

## The scope decision

Run this in order. It takes about ten minutes and it is the cheapest ten minutes in the pipeline.

1. **List the reader objectives.** One line each, each phrased "after this the reader can ___". Not topics — capabilities. A topic list hides the dependencies between the items; a capability list exposes them, because a capability names the thing the reader must already be able to do.
2. **Sort them into dependency order.** For each pair, ask which objective's conclusion is the next one's starting assumption. Objectives that do not depend on each other can sit in any order, and that independence is itself a signal — see the two shapes below.
3. **Cut at the prerequisite seams.** Where objective N+1 needs objective N's conclusion to even begin, that is a post boundary. **A prerequisite seam is a better boundary than any word count**, because it is the boundary the reader already feels.
4. **Budget each group against the tier table.** Count the objectives in each group, estimate words and figures with `references/depth-tiers.md`, and write the tier down. One group under 10,000 words is one post.
5. **Decide.** More than one group, or over 10,000 words, or more than about eighteen figures, is a series. Any one of the three is enough.
6. **State the answer with its reason and offer the adjacent option.** "This is a three-part ladder because the sampler discussion cannot start until the reader accepts the reverse process — the alternative is one L4 pillar that covers parts 1 and 2 and drops the math." The user should be able to overrule in one word.

---

## The two shapes

Every series is one of two shapes, or an honest mixture. Say which one in the plan, because the shape decides whether part 2 re-teaches part 1's ground at a deeper level or assumes it.

**Ladder — same territory, rising depth.** Part 1 is the picture, part 2 the mechanism, part 3 the math, part 4 the engineering. Each part covers the same subject again, further down. Each part stands alone, and each ranks for a different search intent — "what is a diffusion model", "how does a U-Net denoise", "DDPM loss derivation" are three different readers, and that is the discovery argument for this shape. Diffusion models are a ladder topic: the territory is one system, and the only honest way to split it is by depth. In a ladder, part 2 **does** restate part 1's ground, briefly and at its own level, because its reader may not have read part 1.

**Decomposition — one subject cut into disjoint parts at the same depth.** PostgreSQL Foundations is a decomposition series that already exists in this repo: memory layer, process layer, storage layer, all at L4, all intermediate, all sharing one lab, each covering a different subsystem. No part is deeper than another; they are siblings. In a decomposition, part 2 **assumes** the shared ground rather than re-teaching it, and links back for it.

**Hybrid — most real series.** A three-rung ladder whose final rung splits into two disjoint engineering posts is a hybrid. Name it as one, and then say per part whether it re-teaches or assumes.

---

## Assigning the level

Tier and difficulty are two different axes and the plan states both for every part.

**Tier** is how much ground the post covers: L1 to L4, a word budget and a figure budget, nothing more. **Difficulty** is who can read it: beginner, intermediate, or advanced — a claim about prerequisites. They move independently. A short L1 post on lock-free memory ordering is advanced. A 9,000-word L4 walk through how a database stores a row can be beginner-friendly throughout. Setting tier and leaving difficulty implied is how a series ends up with a part 3 that is long, shallow, and aimed at nobody.

| Part role | Typical tier | Difficulty | The question it owns |
|---|---|---|---|
| Orientation | L1–L2 | beginner | what is this, why does it exist, what is the smallest complete example |
| Mechanism | L2–L3 | intermediate | how does each component actually work |
| Depth | L3–L4 | advanced | the math, the proofs, the failure modes, the real implementation |
| Practice (optional) | L2–L3 | intermediate | build it, measure it, tune it |

Three rules.

**Difficulty rises monotonically across a ladder series.** A reader who cleared part 2 must not be talked down to in part 3. Dropping back to beginner for one section mid-ladder reads as padding even when the material is new.

**Every part carries a real worked example at its own level.** The orientation post's example is the thing that earns the click on part 2 — a reader who saw ten real numbers move will come back for the derivation behind them. A part whose example is "see part 1" has no reason to be read on its own.

**A part whose prerequisites are "all previous parts" is badly cut.** Each part should name at most one prior part it truly depends on. If part 4 needs 1, 2 and 3 to make sense, the seams were placed by word count rather than by dependency, and the cut should be redone from step 3.

---

## The plan file

Create `posts/<series-slug>/` and write the plan to `posts/<series-slug>/plan.md`. One plan
defines the whole series. Member posts live below it as
`posts/<series-slug>/<post-slug>/`; do not place new series members directly under `posts/`.

```markdown
# Series plan — <Series title>

**Slug:** <series-slug> · **Shape:** ladder | decomposition | hybrid · **Parts:** N

## Why this is a series and not one post

<the seam that forced the split, two sentences>

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|

## Parts

### Part N — <title>

- **Slug:** <post-slug>
- **Tier:** L2 · **Difficulty:** beginner · **Est. words:** 3,500 · **Figures:** 6
- **Answers:** <the one question this part owns>
- **Assumes:** <prerequisites; for part n>1 name the earlier part and its anchor>
- **Hands off:** <what it deliberately defers, and to which part>
- **Worked example:** <the one concrete instance>
- **Key sources:** <two or three from the sweep>
- **Search intent:** <what a reader types that should land here>

## Publication order and cadence

## Cross-links

## What this series will not cover
```

A filled example, for the topic that most often arrives as one impossible request:

```markdown
# Series plan — Diffusion Models from Noise to Production

**Slug:** diffusion-models · **Shape:** ladder · **Parts:** 3

## Why this is a series and not one post

The objectives split at a hard seam: nothing about prediction targets or samplers can be
explained until the reader accepts that a known corruption path can be walked backwards, and
that acceptance is itself a post. Budgeting all fourteen objectives as one post gives roughly
16,000 words and 24 figures, well past L4.

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | say what a diffusion model is without using the word "denoise" | 1 |
| 2 | follow one forward-noising step on real numbers | 1 |
| 3 | explain why the reverse step needs a learned network at all | 1 |
| 4 | read a noise schedule plot and say what it does to the image | 1 |
| 5 | trace a tensor through a diffusion U-Net and name every block | 2 |
| 6 | say where the timestep and the text condition enter the network | 2 |
| 7 | choose between a U-Net and a diffusion transformer for a given budget | 2 |
| 8 | explain what latent diffusion moves and what it costs | 2 |
| 9 | derive the simplified training objective from the variational bound | 3 |
| 10 | say why epsilon, x0 and v prediction are the same model, reparameterised | 3 |
| 11 | explain classifier-free guidance as an extrapolation, and its coverage cost | 3 |
| 12 | pick a sampler and a step count from the error behaviour, not folklore | 3 |
| 13 | diagnose a model that follows prompts but loses fine detail | 3 |
| 14 | read a diffusion paper's method section unaided | 3 |

## Parts

### Part 1 — What a Diffusion Model Actually Does

- **Slug:** what-a-diffusion-model-actually-does
- **Tier:** L2 · **Difficulty:** beginner · **Est. words:** 3,500 · **Figures:** 6
- **Answers:** why can a model that only ever learned to undo noise produce a new image?
- **Assumes:** Gaussian distributions, what a neural network is. No prior generative modelling.
- **Hands off:** network internals to part 2; the variational bound and guidance to part 3.
- **Worked example:** one 4x4 greyscale patch pushed through five forward steps and pulled
  back, every intermediate value printed.
- **Key sources:** Ho 2020 (DDPM); Sohl-Dickstein 2015; Yang 2023 survey.
- **Search intent:** "what is a diffusion model", "how do diffusion models work"

### Part 2 — Inside the Denoiser

- **Slug:** inside-the-diffusion-denoiser
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 10
- **Answers:** what is the network, block by block, and where does the condition enter?
- **Assumes:** part 1's forward and reverse process — "the reverse step" anchor. Convolution,
  attention, and tensor shapes. Re-teaches the forward process in three sentences, no more.
- **Hands off:** the loss derivation and every sampler question to part 3.
- **Worked example:** a 64x64x3 input traced through every block of a small U-Net, with the
  shape after each one, then the same input through a DiT at patch size 2.
- **Key sources:** Ronneberger 2015 (U-Net); Rombach 2022 (latent diffusion);
  Peebles 2023 (DiT).
- **Search intent:** "diffusion U-Net architecture", "DiT vs U-Net", "how does cross-attention
  conditioning work"

### Part 3 — The Objective, Guidance and the Sampler

- **Slug:** diffusion-objective-guidance-samplers
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** what is the model actually trained to minimise, and how do you get a sample out
  of it in twenty steps instead of a thousand?
- **Assumes:** part 2's denoiser — "the denoiser interface" anchor. Calculus, expectations, and
  reading a stochastic differential equation.
- **Hands off:** distillation and video diffusion — named as out of scope, not deferred.
- **Worked example:** the variational bound reduced to the simple loss by hand on one timestep,
  then the same trajectory integrated by DDPM, DDIM and a second-order solver at 10 steps, with
  the sample error at each.
- **Key sources:** Ho 2022 (classifier-free guidance); Song 2021 (score-based SDE);
  Karras 2022 (EDM); Lu 2022 (DPM-Solver).
- **Search intent:** "DDPM loss derivation", "classifier-free guidance explained",
  "DDIM vs DPM-Solver step count"

## Publication order and cadence

Strict order 1, 2, 3 — part 2 links back to part 1 by anchor. One part per week; the ladder
loses its compounding effect if part 2 arrives a month after part 1 has left the feed.

## Cross-links

Part 1 closes with a forward link to part 2. Part 2 opens with one back link to part 1's
reverse-process section and closes with a forward link to part 3. Part 3 links back to part 2
only. No part links forward to a post that is not yet published — add the link when the later
part goes live, in the later part.

## What this series will not cover

Distillation and few-step models, video and 3-D diffusion, training infrastructure, and the
licensing of pretrained checkpoints. Each is its own series.
```

---

## The living series context

Create `posts/<series-slug>/context.md` beside `plan.md` from
`assets/series-context-template.md`. The two files have different jobs:

- `plan.md` is the approved scope: parts, order, levels, seams, and handoffs. It changes only
  when the user explicitly rescopes the series.
- `context.md` is the model's compact memory of what the series has actually established. Read
  it before researching or outlining every member, then update it after that member passes the
  gate.

Do not pre-fill planned ideas as completed knowledge. After a part is finished, analyse its final
`blog.md`, outline, ledger, figures, and lab, then record only durable information the next writer
needs:

- the part's status, slug, canonical question, and actual handoff;
- up to eight bullets of knowledge the published part established;
- terminology, notation, examples, datasets, diagrams, or design decisions that must stay
  consistent;
- what later parts may assume, what they must not re-teach, and any unresolved or corrected
  point;
- a rewritten brief for the next unfinished part: can assume, must teach, must not repeat,
  evidence still needed, and intended handoff.

Keep `context.md` under 2,000 words. It is a high-signal handoff, not a second archive: never copy
article paragraphs, outlines, claim ledgers, source lists, or figure descriptions into it. When it
grows, consolidate older bullets into stable series-level decisions rather than appending more
summary. The context guides the model; it never replaces the current part's research ledger as
evidence.

The series directory therefore looks like this:

```text
posts/<series-slug>/
├── plan.md
├── context.md
├── <part-1-slug>/
│   ├── blog.md
│   └── ...
└── <part-2-slug>/
    ├── blog.md
    └── ...
```

At Checkpoint S, create the series directory, `plan.md`, and initial `context.md`. Create a member
post folder when work on that approved part begins; empty folders for every future part add no
useful state.

---

## Frontmatter and cross-linking

Every member post carries two frontmatter keys, and the platform parser reads both:

```yaml
series: diffusion-models
series_position: 2
```

`series` is the lowercase-hyphenated series slug and matches the folder at
`posts/<series-slug>/`. `series_position` is an integer starting at 1. **Both appear together or
neither appears** — a `series` with no position cannot be ordered, and a position with no series
belongs to nothing.

Cross-post links go to the published canonical URL with a GitHub-style heading anchor, never a local path: `https://canery.in/blogs/what-a-diffusion-model-actually-does#the-reverse-step`. A local path is a private build artifact leaking into a published file, and the validator fails it.

Publishing a later part does not mean editing an earlier published part. An already-published post has been reviewed and indexed; reopening it to add a forward link risks its content for a link the series index already provides. Add the forward link only when the earlier part is genuinely incomplete without it, and then treat it as an expansion — re-run the gate and bump `updated`.

---

## Checkpoint S

**The series plan is approved by the user before research starts.** Present the plan, the shape, and the tier and difficulty of every part, then stop. Do not sweep sources, do not outline, do not draft.

Approving a four-post plan costs a minute. Discovering at part 3 that the cut was wrong costs three posts, because the seams decided what each earlier post taught and what it deferred, and both are now published.

---

## When not to make a series

Three failure cases, all of which look productive.

**The topic is one capability.** If every objective on the list is a step toward one thing the reader can do, it is one post, however long. Say so, recommend the tier, and do not invent parts.

**The series exists to inflate post count.** Three 1,500-word posts are not a series; they are one L2 post that was cut into thirds and now repeats its own setup three times.

**The parts cannot each stand alone in search.** If part 2 has no search intent of its own — nobody types anything that should land there first — it is a section, not a post. **A series of posts nobody can read out of order is one post that was split for the author's convenience.**
