# Asset manifest — hypothesis-testing-p-values-power

Series `statistics-for-data-scientists`, part 5. **Status: local draft assets ready for upload.** Upload the
fourteen PNGs and the eight lab files to the public `media` bucket under the object keys below, write the
resulting URLs to `urls.txt` in table order (COVER, FIG_01–FIG_13, then LAB_01–LAB_08), then run
`fill_urls.py`. Upload the lab zip separately, to the bucket root (see **Lab files**). Nothing has been
published, so every key is new; the names carry the slug because the bucket is flat.

Every figure is our own analysis, drawn from the lab's `captures.json` by `assets/_figs.py` (the cover by
`assets/_cover.py`), which asserts the numbers the article quotes before it draws. The `source` route was
considered first for every paper-backed figure (ledger, **Figure candidates**): Gelman and Carlin's Figure 2 is
SAGE's with no reuse licence, and Figure 8 computes the same curves in closed form and marks both published
studies and the values printed for them (F1); Colquhoun's tree (CC BY 4.0) shows one point of Figure 10's
family, whose two numbers the prose carries (F2); Lakens's Figure 1 is SAGE's, and Figure 13 draws the
project's own 63 failed replications against the bounds (F3); the Open Science Collaboration's Figure 3 is
AAAS's, and Figure 9 is redrawn from the CC0 data with this article's split (F4). No figure is Mermaid: none
is a graph of nodes and edges.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-hypothesis-testing-p-values-power.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 1 reduced to its argument, the plausible-effect curve cut by the significance bar, the tangerine used once on the right-sign tail; no external generator | — | — | cover-hypothesis-testing-p-values-power.png | A normal curve centred at 2 cut by a significance bar at ±15.9: only its far tails count as significant results |
| FIG_01 | assets/fig-01-significance-bar-hypothesis-testing-p-values-power.png | plot | Q4: a computed distribution cut by a threshold, from two published numbers | — | — | fig-01-significance-bar-hypothesis-testing-p-values-power.png | Normal curve of replicated estimates centred at 2 with SD 8.1; only 4.34% beyond +15.9 and 1.37% beyond −15.9 are significant |
| FIG_02 | assets/fig-02-p-value-distributions-hypothesis-testing-p-values-power.png | plot | Q1: simulated histograms against exact bin probabilities, five small multiples | — | — | fig-02-p-value-distributions-hypothesis-testing-p-values-power.png | Histograms of simulated p-values for five signal-to-noise ratios: flat at 0, nearly flat at 0.25, piled near 0 at 2.8 |
| FIG_03 | assets/fig-03-dance-of-p-values-hypothesis-testing-p-values-power.png | plot | Q1: 25 simulated experiments, intervals on one axis with their p-values | — | — | fig-03-dance-of-p-values-hypothesis-testing-p-values-power.png | Twenty-five repeats of one experiment: estimates with 95% intervals, p-values from 0.00007 to 0.33, nineteen significant |
| FIG_04 | assets/fig-04-optional-stopping-hypothesis-testing-p-values-power.png | plot | Q1: an exact curve over 1,000 looks on a log axis, with simulated points | — | — | fig-04-optional-stopping-hypothesis-testing-p-values-power.png | Error rate of a 5% z-test repeated after each observation, rising from 5% at 1 look to 53% at 1,000, with simulated checks |
| FIG_05 | assets/fig-05-fisher-and-neyman-pearson-hypothesis-testing-p-values-power.png | plot | Q4: two computed densities and the areas the two readings cut from them | — | — | fig-05-fisher-and-neyman-pearson-hypothesis-testing-p-values-power.png | Null and alternative t densities for 16 per group: 5% of the null beyond ±2.04, 78.1% of the alternative, and t = 2.28 for p = .03 |
| FIG_06 | assets/fig-06-power-curves-hypothesis-testing-p-values-power.png | plot | Q1: exact power curves with their normal approximations and 13 simulated checks | — | — | fig-06-power-curves-hypothesis-testing-p-values-power.png | Power against sample size per group for effect sizes 0.2, 0.5, 0.8 and 1: exact curves, normal approximations and simulated points |
| FIG_07 | assets/fig-07-observed-power-hypothesis-testing-p-values-power.png | plot | Q1: observed power computed as a function of p for two tests | — | — | fig-07-observed-power-hypothesis-testing-p-values-power.png | Observed power plotted against the p-value for a z-test and for the 16-per-group t-test: 0.50 at p = .05 |
| FIG_08 | assets/fig-08-type-s-and-m-hypothesis-testing-p-values-power.png | plot | Q1: closed-form curves against λ with five published designs and their printed values | — | — | fig-08-type-s-and-m-hypothesis-testing-p-values-power.png | Exaggeration ratio on a log scale and type S rate against λ and power, with the Kanazawa and 2013 designs and their printed values marked |
| FIG_09 | assets/fig-09-replication-effect-sizes-hypothesis-testing-p-values-power.png | plot | Q1: a scatter of real CC0 data with the means split by the original p-value | — | — | fig-09-replication-effect-sizes-hypothesis-testing-p-values-power.png | Original against replication effect size r for 97 pairs, most below the diagonal, coloured by whether the replication was significant |
| FIG_10 | assets/fig-10-false-positive-risk-hypothesis-testing-p-values-power.png | plot | Q1: a computed risk against the prior for two powers above the power-1 floor | — | — | fig-10-false-positive-risk-hypothesis-testing-p-values-power.png | False positive risk of p ≤ .05 results against the prior probability of a real effect, for power 0.2 and 0.8, above the floor set by power 1 |
| FIG_11 | assets/fig-11-p-equals-and-p-less-than-hypothesis-testing-p-values-power.png | plot | Q1: two computed risks for two priors on a log axis, with marked points | — | — | fig-11-p-equals-and-p-less-than-hypothesis-testing-p-values-power.png | False positive risk of an observed p, p-equals and p-less-than, for priors 0.5 and 0.1, with p = .05, .03 and .001 marked |
| FIG_12 | assets/fig-12-equivalence-sample-size-hypothesis-testing-p-values-power.png | plot | Q1: exact TOST bounds and power computed by the lab, with simulated checks | — | — | fig-12-equivalence-sample-size-hypothesis-testing-p-values-power.png | Narrowest equivalence bound against sample size per group: ±1.06 SD at 16, ±0.50 at 69, ±0.10 at 1,713; TOST power at ±0.5 SD |
| FIG_13 | assets/fig-13-failed-replications-equivalence-hypothesis-testing-p-values-power.png | plot | Q1: 63 intervals from real data against two equivalence bands | — | — | fig-13-failed-replications-equivalence-hypothesis-testing-p-values-power.png | Ninety-percent intervals for 63 non-significant replications against bands at ±0.1 and ±0.2: 2 and 17 fall inside |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0, pandas 3.1.0; `all --quick`
takes about 8 s, `all` about 27 s, 0.48 GB of RAM).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/hypothesis-testing-p-values-power/README.md` | grade, provenance, setup, run order, the E1–E5 exercises with answers, cleanup |
| LAB_02 | `lab/testing.py` | `labs/hypothesis-testing-p-values-power/testing.py` | the seven stages of the lab |
| LAB_03 | `lab/requirements.txt` | `labs/hypothesis-testing-p-values-power/requirements.txt` | the pinned NumPy, SciPy, statsmodels and pandas versions |
| LAB_04 | `lab/data/osc2015_rpp_pairs.csv` | `labs/hypothesis-testing-p-values-power/data/osc2015_rpp_pairs.csv` | the Reproducibility Project's 100 coded replications (CC0 1.0), with provenance |
| LAB_05 | `lab/captures.json` | `labs/hypothesis-testing-p-values-power/captures.json` | the author's full run, with the private cross-checks; every figure reads it |
| LAB_06 | `lab/captures-quick.json` | `labs/hypothesis-testing-p-values-power/captures-quick.json` | the author's `--quick` run |
| LAB_07 | `lab/expected-output.txt` | `labs/hypothesis-testing-p-values-power/expected-output.txt` | the full run as printed |
| LAB_08 | `lab/notebook.ipynb` | `labs/hypothesis-testing-p-values-power/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-hypothesis-testing-p-values-power.zip` | `lab-hypothesis-testing-p-values-power.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the CSV key so the zip and the individual files agree. Upload with an accurate
`Content-Type` (`text/markdown`, `text/x-python`, `text/plain`, `text/csv`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

The CSV holds 100 rows of the Reproducibility Project's `rpp_data.csv` (OSF `fgjvw`, sha256 4d87a263…, CC0 1.0
on the project and on its Analysis component), with nine columns renamed and copied unchanged; its header
states the extraction rule.

## Series links to add

Earlier parts are named by title or by number in plain text; add the link once the target is live.

| Post | Status on 2026-10-29 | Where it is named |
|---|---|---|
| Part 2, *The Sampling Distribution: The CLT and Where n = 30 Fails* (`sampling-distribution-central-limit-theorem`) | built, not live | **The problem**, first paragraph: "The second part of this series, *The Sampling Distribution: The CLT and Where n = 30 Fails*" |
| Part 4, *Likelihood: The MLE, Three Tests, and Where χ² Fails* (`likelihood-mle-fisher-information`) | built, not live | **The problem**, first paragraph: "The fourth part, *Likelihood: The MLE, Three Tests, and Where χ² Fails*" |
| Part 4 (same post) | built, not live | **Limitations and common mistakes**, the last bullet: "as the fourth part's exact sizes showed" |

Later parts appear only as "a later part of this series" (correcting for many tests, in Limitations), with no
number or title. Sequential designs are "experimentation practice, which this series does not cover".

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. The first render had at least one defect in every
  figure, none caught by a gate: labels printed across curves or on gridlines (Figures 1, 2, 5, 6, 7, 8, 10,
  11, 12), labels colliding with each other or with the axis title (Figures 1, 2, 8, 9), footnotes running into
  the legend rule (Figure 2) or the axis title (Figure 9), legend swatches that did not match their marks
  (vertical swatches for horizontal intervals in Figure 3, a line for a cross in Figure 9, ±2 MCSE bars
  promised in Figure 4's legend that sit inside the circles), an interval clipped without notice at −0.75 and
  ticks on odd tenths (Figure 13), and dead bands above the legend (Figures 1, 3).
- Figure 6 first drew no exact curves for d = 1 and d = 0.8: SciPy 1.18.1's `nct.cdf(-c, df, λ)` returns NaN
  from λ of about 8, and one NaN point makes the browser drop the whole polyline, so the simulated circles sat
  off the only (normal-approximation) line of their colour. The lab now takes the lower tail as
  `nct.sf(c, df, -λ)`, `_figs.py` asserts that no curve holds a NaN, and the article reports that statsmodels
  0.15.0 returns `nan` for such designs.
- Figure 10 first drew four curves in three greys crowded into the left fifth; it now shows power 20% and 80%
  over the shaded power-1 floor, with the 50% value in the notes. Figure 12 first plotted two sample-size
  curves 9% apart that read as one line; it now shows the narrowest bound each sample size establishes.
- Figure 8's note first said the printed values "match" the closed form; Gelman and Carlin's prose gives 25
  where the closed form gives 25.6, so the note and the article now give both numbers.
- `_overlap.py` on the final renders: 4 reports, all checked against the PNGs and none a defect. Three are
  labels that run a few pixels past their plot frame into empty margin ("no difference (H₀)" in Figure 5 by
  2.3 px, "80% power: 1.13" in Figure 8 by 27 px into the gap between panels, "same size" in Figure 9 by
  1.4 px); the fourth is the cover's two serif title lines, the checker's documented false positive.
- `lint_visuals.py`: 0 text overflows and 0 arrow reports on all 14 files.
- `_figs.py` and `_cover.py` assert the article's numbers against `captures.json` before drawing; every number
  printed on a figure is computed from the capture.
- Both Implementation snippets were run as printed: the first prints power 0.0570, type S 0.2396 and
  exaggeration 9.5366 (simulated 9.61 with its seed), the second the same TOST p-value twice (0.0399).

## Owner actions

- Upload the PNGs, the eight lab files and the zip, then fill `urls.txt` and run `fill_urls.py`.
- The `data-science` category is still missing from the live database (a production write at publish time;
  Parts 1 to 4 need it too).
- Part 2 must go live before this part: this part's **Assumes** line names it. Part 4, named twice, can be
  linked once it is live.
