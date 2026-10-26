# Outline — Evaluating Generative Models: What FID Measures and Hides

Series `diffusion-models`, part 9 of 12 (`series_position: 9`). Private build artifact.

## Brief

- **Answers (plan.md):** what does FID measure, and what does it hide?
- **Tier:** L2 (plan: 4,500 words, 7 figures). One concept (a set-level distance) plus its mechanism
  (two moments of classifier features) plus its failure modes; the smallest honest worked example
  (eight numbers, three generators) fits on one screen. Adjacent option: L3, if the text-to-image
  metrics (CLIPScore, preference models, compositional benchmarks) got their own section.
- **Difficulty:** intermediate, on purpose. This is the decomposition spoke a product person reads, so
  it assumes only Part 1 and the mean and standard deviation of a list. Everything else (Inception,
  covariance, k-nearest-neighbour balls, guidance) is introduced in place. Adjacent option: advanced,
  which would add the KID estimator, the bias derivation and FD-infinity in full.
- **Can assume:** Part 1 only (published). **Must not repeat:** guidance (Part 8) or few-step
  students (Part 7); guidance appears only as a dial whose trade-off the metrics read.
- **Lab:** G1 · runs anywhere. One numpy file, `evaluate.py`, on crescent world (Part 8's world,
  unchanged): every generator's defect is known exactly, so every metric can be graded against the
  truth. Full run 45 s on one core. L2 ladder: E1–E3. No access request (see `../access.md`).
- **Social:** feed cards only, as for Part 8 (owner, 2026-10-19).

## Section budget (target about 4,400 words in the validator's count, references included)

| Section | Target | Job |
|---|---|---|
| Insights + who this is for + notice | 150 | the answer in 90 words; measured vs quoted |
| Why this matters | 130 | two models 0.01 apart in FID, nearly 2× apart in how often people mistook them for real |
| The problem | 260 | compare two sets, three properties, no per-image answer; the protocol; the JPEG-21 scale problem |
| Worked example | 480 | FD on one number, three generators, by hand (FIG_01) |
| Intuition | 230 | moving and stretching one cloud into another; the census analogy and where it breaks |
| What does FID compute on real images? | 360 | Inception pipeline, reference sets, relatives (FIG_02) |
| Which failures does one number hide? | 780 | tied FD, opposite failures; P/R/D/C; the guidance dial (FIG_03, FIG_04, FIG_05) |
| Why don't FIDs compare across papers? | 380 | bias in N, resizing, JPEG, protocol (FIG_06) |
| What can't the Inception network see? | 430 | features decide; ImageNet classes; people; prompts (FIG_07) |
| The math | 300 | equation (1), 1-D collapse, symmetric square root, bias (2), coverage (3) |
| Implementation | 160 | numpy FD and P/R/D/C, practice checklist |
| Limitations and common mistakes | 260 | warning callout plus five mistakes |
| Key takeaways | 100 | four claims |
| Try it yourself | 200 | three exercises answerable from the article |
| References | ~650 | lab downloads + 17 sources |

## Figure plan (route gate run per figure)

| # | Section | One thing it must communicate | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| FIG_01 | Worked example | FD on one number ranks a generator with half its crescents at impossible contrasts first, and the one with every crescent right last | plot | Q4 — real values on number lines, per generator, with the two terms printed | The moment-matched generator scores a perfect 0 while half its values fall between the real clusters |
| FIG_02 | What does FID compute | the pipeline with a shape on every edge, and the five places a protocol choice enters | placed | Q5 — 9 nodes in two parallel chains, no crossing; shapes on every edge need hand placement | Everything FID knows about 50,000 images is 2,048 means and 2.1 million covariances |
| FIG_03 | Which failures does one number hide | two generators tie at FD 3.6221 with opposite failures; a Gaussian blob and a copier score like the perfect generator | placed | Q4 — real 8×8 samples from the lab beside measured numbers | Same FD, opposite failures; precision, recall and coverage tell them apart, and nothing here sees the copier |
| FIG_04 | (same, P/R/D/C subsection) | one stray sample's large ball buys 100% recall while coverage does not move | plot | Q4 — intervals on a number line, computed by the lab | Recall builds balls around generated samples, so one isolated sample can claim a whole missing mode |
| FIG_05 | (same, guidance subsection) | turning guidance up: FD and coverage worsen steadily, recall falls then rebounds at w = 7.5 | chart | Q1 — lab measurements across seven weights | k-NN recall rebounds at w = 7.5 because four stray faint samples have huge balls; coverage does not |
| FIG_06 | Why don't FIDs compare | FD falls like 1/N; a perfect generator at 1,000 samples scores worse than a flawed one at 4,000 | chart | Q1 — lab measurements, 24 repeats per point, with the fitted lines | FD is biased upward by K/N; only scores at the same N compare |
| FIG_07 | What can't the Inception network see | people's ability to spot fakes does not rise along FID's ranking | source | source check — Stein et al.'s Figure 2 is the evidence itself, CC BY 4.0 (ledger F1) | Reproduced from Stein et al. 2023, Figure 2, CC BY 4.0 |
| COVER | — | the series' house template cover | placed | template cover, as Parts 6–8 | — |

## Term map

| Term | First section | What | Why used here | When it matters |
|---|---|---|---|---|
| FID (Fréchet Inception Distance) | Insights / What does FID compute | a single score: the Fréchet distance between Gaussian fits of two sets of Inception-v3 features | it is the field's headline number | whenever two generators are ranked |
| Fréchet distance (FD) | Worked example | the cost of turning one bell curve into another: mean gap squared plus spread gap squared in 1-D | it is the arithmetic inside FID | read its two terms to see which kind of mismatch dominates |
| fidelity / diversity / novelty | The problem | each image looks real / the set spans the real variety / the images are not copies | the three things a generator must get right | name which one a metric measures before trusting it |
| Inception-v3, pool3 features | What does FID compute | an ImageNet classifier; its last pooling layer gives 2,048 numbers per image | FID's feature space | it decides what FID can see |
| reference set | What does FID compute | the real images FID compares against (training set, or COCO-30K) | part of the protocol | must match for scores to compare |
| moments (mean, covariance) | Intuition | average per feature, and how each pair of features varies together | all FID keeps | anything beyond them is invisible to FID |
| precision / recall (k-NN) | Which failures… | share of generated samples inside the real samples' balls / share of real samples inside the generated samples' balls | separate fidelity from diversity | read against a real-vs-real baseline; recall is fooled by strays |
| k-nearest-neighbour ball | Which failures… | a ball around a sample reaching its k-th nearest neighbour in the same set | how P/R/D/C estimate where data lives | its radius grows where samples are sparse |
| density / coverage | Which failures… | real balls per generated sample / share of real samples whose own ball holds a generated sample | robust to outliers | prefer coverage to recall for mode loss |
| guidance weight w | Which failures… | the dial Part 8 explains: higher w follows the class more strongly | a real fidelity-for-variety knob | the example the metrics read |
| bias (of an estimator) | Why don't FIDs compare | the gap between an estimate's average and the true value | FID's grows as 1/N | fix N; or extrapolate |
| FD-infinity | Why don't FIDs compare | FD extrapolated to infinitely many samples by a line in 1/N | removes most of the bias | comparing across N |
| KID | What does FID compute | squared MMD with a cubic kernel on the same features; unbiased | the standard alternative | small sample counts |
| human error rate | What can't Inception see | share of real-or-fake judgements people get wrong | Stein et al.'s ground truth for realism | fidelity only; it cannot see diversity |
| CLIPScore / PickScore | What can't Inception see | prompt-image agreement from CLIP / a model trained on people's choices | FID never reads the prompt | text-to-image evaluation |
| perceptual null space | What can't Inception see | changes that move FID without visibly changing images | why FID can be gamed | never optimise against FID itself |

## Series handoffs

- Names Part 1 (published: "the four moving parts", "where new images come from") and Part 8 (not
  published: the guidance dial) in plain text; Part 7 (not published) only in one limitation.
- Defers memorisation ("when does a sample stop being new") to a later part, unnamed.
- Hands Part 10 the rule that every quoted score carries its model, dataset and protocol.
