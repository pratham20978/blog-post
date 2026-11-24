# Asset manifest — permutation-and-rank-tests

Series `statistics-for-data-scientists`, part 10. **Status: local draft assets ready for upload.** Upload the eleven
PNGs and the nine lab files to the public `media` bucket under the object keys below, write the resulting URLs to
`urls.txt` in table order (COVER, FIG_01–FIG_10, then LAB_01–LAB_09), then run `fill_urls.py`. Upload the lab zip
separately, to the bucket root (see **Lab files**). Nothing has been published, so every key is new; the names carry
the slug because the bucket is flat.

Every figure is our own analysis, drawn from the lab's `captures.json` by `assets/_figs.py` (the cover by
`assets/_cover.py`), which asserts the numbers the article quotes before it draws. The `source` route was considered
first for every paper-backed figure (ledger, **Figure candidates**): Darwin's printed Table XCVII is public domain but
its scan carries Darwin Online's notice, whose reuse terms were not verified, so Figure 1 plots the same numbers (F1);
Phipson and Smyth's Figure A is under arXiv's non-exclusive licence, so Figure 4b computes the family-wise consequence
instead (F2); Fay and Proschan's Figure 4 has no verified licence, so Figure 9 measures power instead (F3).

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-permutation-and-rank-tests.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 2 reduced to its argument, the tails beyond Darwin's 314 eighths in tangerine (the one use); no external generator | — | — | cover-permutation-and-rank-tests.png | Totals of all 32,768 sign assignments of Darwin's 15 differences, the tails beyond the observed 314 eighths in orange; p = 0.0527 |
| FIG_01 | assets/fig-01-darwins-pairs-permutation-and-rank-tests.png | plot | Q1: Darwin's 15 real pairs by pot, and their differences on one line | — | — | fig-01-darwins-pairs-permutation-and-rank-tests.png | Darwin's 15 pairs of crossed and self-fertilised maize heights by pot, and the 15 differences; two negatives, −67 and −48 eighths |
| FIG_02 | assets/fig-02-every-sign-assignment-permutation-and-rank-tests.png | plot | Q4: an exact distribution, all 32,768 totals, with the observed one and both tails | — | — | fig-02-every-sign-assignment-permutation-and-rank-tests.png | Histogram of the totals of all 32,768 sign assignments; 863 at or above 314 and 863 at or below −314 shaded; two-sided p 0.0527 |
| FIG_03 | assets/fig-03-four-tests-one-dataset-permutation-and-rank-tests.png | plot | Q4: the same data as values, signed ranks and signs, beside four p-values on one axis | — | — | fig-03-four-tests-one-dataset-permutation-and-rank-tests.png | The 15 differences as values, as signed ranks and as signs, with the t, randomisation, signed-rank and sign-test p-values |
| FIG_04 | assets/fig-04-monte-carlo-p-values-permutation-and-rank-tests.png | plot | Q1: two computed distributions, the binomial law of SciPy's Monte Carlo p and Phipson and Smyth's family-wise error formulas | — | — | fig-04-monte-carlo-p-values-permutation-and-rank-tests.png | Distribution over reruns of SciPy's default Monte Carlo p on Darwin's pairs, 19.4% at or below 0.05; family-wise error of b/m and (b + 1)/(m + 1) |
| FIG_05 | assets/fig-05-permutation-test-of-means-permutation-and-rank-tests.png | plot | Q1: simulated rates of four tests on a log ratio axis, two designs | — | — | fig-05-permutation-test-of-means-permutation-and-rank-tests.png | Size of raw and studentised two-sample permutation tests and of Student's and Welch's t against the SD ratio, groups of 10 and 40 and of 25 and 25 |
| FIG_06 | assets/fig-06-equal-medians-different-shapes-permutation-and-rank-tests.png | plot | Q4: closed-form densities with their medians and P(X > Y) | — | — | fig-06-equal-medians-different-shapes-permutation-and-rank-tests.png | Normal and shifted exponential densities: equal medians with P(X > Y) = 0.443, and medians 0 and −0.183 with P(X > Y) = 0.5 |
| FIG_07 | assets/fig-07-what-mann-whitney-rejects-permutation-and-rank-tests.png | plot | Q1: simulated rejection rates of three tests in three designs | — | — | fig-07-what-mann-whitney-rejects-permutation-and-rank-tests.png | Rejection rates of Mann–Whitney, Brunner–Munzel and Welch: by n per group in both designs of Figure 6, and by SD ratio for normal groups of 10 and 40 |
| FIG_08 | assets/fig-08-hodges-lehmann-permutation-and-rank-tests.png | plot | Q4: 120 computed order statistics with the estimate and the interval's ends | — | — | fig-08-hodges-lehmann-permutation-and-rank-tests.png | Darwin's 120 Walsh averages in order; median 3.125; the 26th smallest, 0.5, and the 26th largest, 5.1875, bound the interval |
| FIG_09 | assets/fig-09-price-of-ranks-permutation-and-rank-tests.png | plot | Q1: computed AREs and simulated power for eight shapes | — | — | fig-09-price-of-ranks-permutation-and-rank-tests.png | Power of Welch's t and Mann–Whitney at n = 20 per group for eight distributions, with each one's ARE, from 0.864 to 1.900 |
| FIG_10 | assets/fig-10-rank-correlation-permutation-and-rank-tests.png | plot | Q1: 15 real pairs as values and as ranks, with three coefficients and five p-values | — | — | fig-10-rank-correlation-permutation-and-rank-tests.png | Law-school GPA against LSAT for 15 schools, as values and as ranks, with r 0.776, ρ 0.796, τ 0.638 and their p-values |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4, SciPy 1.18.1; `all --quick` takes about 20 s, `all` about 2 min 38 s,
0.30 GB of RAM).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/permutation-and-rank-tests/README.md` | grade, provenance, setup, run order, the E1–E4 exercises with answers, cleanup |
| LAB_02 | `lab/permutation.py` | `labs/permutation-and-rank-tests/permutation.py` | the five stages of the lab |
| LAB_03 | `lab/data/darwin1876_zea_mays.csv` | `labs/permutation-and-rank-tests/data/darwin1876_zea_mays.csv` | Darwin's 15 pairs (1876, public domain), with provenance |
| LAB_04 | `lab/data/law_school_82.csv` | `labs/permutation-and-rank-tests/data/law_school_82.csv` | the law-school data (CRAN `bootstrap`, BSD 3-clause), with provenance |
| LAB_05 | `lab/requirements.txt` | `labs/permutation-and-rank-tests/requirements.txt` | the pinned NumPy and SciPy versions |
| LAB_06 | `lab/captures.json` | `labs/permutation-and-rank-tests/captures.json` | the author's full run with the private R cross-check; every figure and card reads it |
| LAB_07 | `lab/captures-quick.json` | `labs/permutation-and-rank-tests/captures-quick.json` | the author's `--quick` run |
| LAB_08 | `lab/expected-output.txt` | `labs/permutation-and-rank-tests/expected-output.txt` | the full run as printed |
| LAB_09 | `lab/notebook.ipynb` | `labs/permutation-and-rank-tests/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-permutation-and-rank-tests.zip` | `lab-permutation-and-rank-tests.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the two CSV keys so the zip and the individual files agree. Upload with an accurate
`Content-Type` (`text/markdown`, `text/x-python`, `text/csv`, `text/plain`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

The Darwin CSV was typed from the 1876 page scans of pp. 16 and 234 (public domain); its header records that Darwin
Online's text transcription misreads two fractions and that the scans' values reproduce the printed column totals.
The law-school CSV is Part 7's file with one added first line saying so, byte-identical after it.

## Series links to add

Earlier parts are named by title in plain text; add the link once the target is live.

| Post | Status on 2026-11-23 | Where it is named |
|---|---|---|
| Part 8, *Which Statistical Test? The Design Decides, Not the Data* (`choosing-a-statistical-test`) | built, not live | **The problem**, first paragraph: "The eighth part of this series, *Which Statistical Test? The Design Decides, Not the Data*, measured how far"; again, unnamed, in **What does the Mann–Whitney test test?**: "The eighth part of this series found Mann–Whitney erring" |
| Part 7, *The Bootstrap: From Percentile to BCa, and Where It Breaks* (`bootstrap-confidence-intervals`) | built, not live | **What does the Mann–Whitney test test?**, last paragraph: "a bootstrap interval for the difference in medians from the seventh part, *The Bootstrap: From Percentile to BCa, and Where It Breaks*"; again in **Rank correlations**: "the law-school sample the seventh part bootstrapped" |

No later part is named. Randomisation inference for experiments is said to belong "with experiment design, outside
this series", as the plan's hand-off to DS-2 and DS-3 allows.

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. The first renders had defects in all ten figures, none caught
  by a gate: dead bands above the legend (Figures 1, 2, 4, 5, 6, 10); a label printed over the histogram's bars and a
  gridline through the headline label (Figure 2); p-value rows that did not line up with the views they belong to
  (Figure 3); a label on top of two curves (Figure 4b); a legend entry whose curve was invisible because Student's
  t coincides with the raw permutation test, then a note that ran into the next panel's tick labels (Figure 5); a
  second median line drawn over the first because the captured c is rounded to six digits (Figure 6a); two labels
  crossed by the Welch curve (Figure 7); interval and median labels on dots and on a dashed line (Figure 8); value
  labels with no key to their order (Figure 9); and axis names colliding with panel titles (Figure 10).
- Reading the prose against the capture changed five numbers in the draft: the studentised test's range at 10 and
  40 is 3.9% to 5.9%, not to 5.8% (Figure 5's caption); Welch's parametric range there is 4.95% to 5.19%, not 5.0% to
  5.4%; the largest power gain of ranks is 10.9 points, not 11 (Figure 9's caption and a key takeaway); the
  25-and-25 range is 5.06% to 5.57% at the final budget, not the earlier run's 4.93%; and "Welch rejects more often
  than either" holds only from 25 per group on.
- The read-through changed four statements: the article's E3 asked for a prediction Figure 5b already shows, and now
  asks what tenfold resamples do on Darwin's pairs (0.38% of runs, an exact binomial sum worked in the answer);
  "keeps its level only for identical distributions" became "is exact only for", since with different shapes and
  P(X > Y) = ½ Mann–Whitney stayed near 5%; two flat "5%" became "about 5%" (4.7% to 5.7%); and Part 8 is described
  as measuring the t-tests when their conditions fail, not when their normal model is wrong.
- Card 2's three counts ran together because SVG collapses repeated spaces; they are now three columns.
- `_overlap.py` on the final renders: 0 reports on the ten plot figures; 2 on the cover (its stacked serif title
  lines), a documented false positive; 2 per card (its serif title lines and the lockup's `.in`), the same. `render_social.py
  --check` passes all 8 cards. `lint_visuals.py`: 0 text overflows and 0 arrow reports on all 11 files.
- `_figs.py`, `_cover.py` and `_social.py` assert the article's numbers against `captures.json` before drawing;
  every number printed on a figure or card is computed from the capture.
- The Implementation snippet was extracted from `blog.md` and run as printed: 863 and 0.052673; SciPy's exact
  `permutation_test` 0.052673; t 0.049703, signed-rank 0.041260, sign 0.007385; Hodges–Lehmann 3.125, 0.5 to 5.1875.
- Fisher's continuity-adjusted t (2.139 in his Table 5) does not follow from rescaling t by 313/314 (2.1412); the
  article does not quote it (ledger, **Open questions**).

## Owner actions

- Upload the PNGs, the nine lab files and the zip, then fill `urls.txt` and run `fill_urls.py`.
- The `data-science` category is still missing from the live database (a production write at publish time; Parts
  1 to 9 need it too).
- Part 8 must go live before this part: this part's **Assumes** line names it. Part 7, named twice, can be linked
  once it is live.
