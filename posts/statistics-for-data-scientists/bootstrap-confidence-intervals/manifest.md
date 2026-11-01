# Asset manifest — bootstrap-confidence-intervals

Series `statistics-for-data-scientists`, part 7. **Status: local draft assets ready for upload.** Upload the
fourteen PNGs and the eleven lab files to the public `media` bucket under the object keys below, write the resulting
URLs to `urls.txt` in table order (COVER, FIG_01–FIG_13, then LAB_01–LAB_11), then run `fill_urls.py`. Upload the
lab zip separately, to the bucket root (see **Lab files**). Nothing has been published, so every key is new; the
names carry the slug because the bucket is flat.

Every figure is our own analysis, drawn from the lab's `captures.json` by `assets/_figs.py` (Figure 1 also reads the
lab's law-school CSV; the cover is drawn by `assets/_cover.py`), which asserts the numbers the article quotes before
it draws. The `source` route was considered first for every paper-backed figure (ledger, **Figure candidates**): Efron
and Hastie's bootstrap-correlation figures are in a book whose free copy is for personal use only (F1), Hesterberg's
coverage figures carry no reuse licence (F2), and Horowitz's review has no figure for these examples (F3). No figure
is Mermaid: Figure 5, the only diagram, has six nodes in two rows and no crossings.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-bootstrap-confidence-intervals.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 10 reduced to its argument, the bootstrap cdf of the tank maximum in tangerine (the one use) against the true cdf; no external generator | — | — | cover-bootstrap-confidence-intervals.png | Two cdfs of the largest of five tank serials: the bootstrap's jumps by 0.67 at 303 and stops there; the true one rises smoothly to 342 |
| FIG_01 | assets/fig-01-law-school-sample-bootstrap-confidence-intervals.png | plot | Q1: a scatter of the 82 schools' real values with the 15 sampled ones marked | — | — | fig-01-law-school-sample-bootstrap-confidence-intervals.png | LSAT against GPA for 82 law schools with the 15 sampled schools highlighted; correlation 0.776 in the sample, 0.760 in all 82 |
| FIG_02 | assets/fig-02-bootstrap-against-truth-bootstrap-confidence-intervals.png | plot | Q1: two computed distributions on one axis, the bootstrap's and the true one from the 82 | — | — | fig-02-bootstrap-against-truth-bootstrap-confidence-intervals.png | Histogram of 10,000 bootstrap correlations beside the true sampling distribution from the 82 schools; both skewed left, SE 0.135 and 0.130 |
| FIG_03 | assets/fig-03-jackknife-acceleration-bootstrap-confidence-intervals.png | plot | Q4: one dot per school with its distance from the jackknife mean, to scale | — | — | fig-03-jackknife-acceleration-bootstrap-confidence-intervals.png | The 15 leave-one-out correlations: 14 between 0.73 and 0.82, school 6 at 0.893; the acceleration is −0.0757 |
| FIG_04 | assets/fig-04-seven-intervals-bootstrap-confidence-intervals.png | plot | Q4: seven intervals drawn to scale on one axis | — | — | fig-04-seven-intervals-bootstrap-confidence-intervals.png | Seven 95% intervals for the same 15 schools, from the percentile's 0.45 to 0.96 to the studentized −0.46 to 1.00 and the basic past 1 |
| FIG_05 | assets/fig-05-bootstrap-world-bootstrap-confidence-intervals.png | placed | Q5: six nodes in two parallel rows, no crossing edges; every node and edge carries a law-school number | — | — | fig-05-bootstrap-world-bootstrap-confidence-intervals.png | Two parallel chains: the 82 schools generate samples and r around rho; the 15 schools generate resamples and r* around r |
| FIG_06 | assets/fig-06-bca-levels-bootstrap-confidence-intervals.png | plot | Q4: computed level maps on a probit scale | — | — | fig-06-bca-levels-bootstrap-confidence-intervals.png | BCa's adjusted levels against nominal levels for z0 = −0.093 and a = −0.076, beside BC's curve and the percentile method's diagonal |
| FIG_07 | assets/fig-07-law-school-coverage-bootstrap-confidence-intervals.png | plot | Q1: simulated coverage with MCSE and misses by side | — | — | fig-07-law-school-coverage-bootstrap-confidence-intervals.png | Coverage of seven 95% intervals over 20,000 samples of 15 from the 82 schools, split into misses on each side; 80.7% to 95.7% |
| FIG_08 | assets/fig-08-monte-carlo-error-by-b-bootstrap-confidence-intervals.png | plot | Q1: measured endpoint SDs over reruns, on log axes | — | — | fig-08-monte-carlo-error-by-b-bootstrap-confidence-intervals.png | Monte Carlo SD of the percentile and BCa endpoints against B on log axes; BCa's lower limit needs about five times the replicates |
| FIG_09 | assets/fig-09-skewed-mean-coverage-bootstrap-confidence-intervals.png | plot | Q1: simulated coverage, overall and split by sample composition | — | — | fig-09-skewed-mean-coverage-bootstrap-confidence-intervals.png | Coverage of six intervals for mean spend at n = 30 and 100, overall and split by whether the sample holds a top-1% customer |
| FIG_10 | assets/fig-10-tank-maximum-bootstrap-confidence-intervals.png | plot | Q1: two exact cdfs, the bootstrap's and the sampling distribution's | — | — | fig-10-tank-maximum-bootstrap-confidence-intervals.png | Bootstrap distribution of the maximum of five tank serials, 67% on 303, beside the true distribution of the maximum for N = 342 |
| FIG_11 | assets/fig-11-tank-intervals-bootstrap-confidence-intervals.png | plot | Q4: intervals to scale with N marked, and their exact coverage | — | — | fig-11-tank-intervals-bootstrap-confidence-intervals.png | Intervals for the tank count from five serials: percentile, basic and two BCa variants stop at 334 or below; N = 342; exact bound 549 |
| FIG_12 | assets/fig-12-infinite-variance-bootstrap-confidence-intervals.png | plot | Q1: computed bootstrap histograms by copies of the maximum, and simulated coverage against n | — | — | fig-12-infinite-variance-bootstrap-confidence-intervals.png | Bootstrap distributions of the mean for three Pareto samples, coloured by copies of the largest value, and coverage rising from 66% to 85% |
| FIG_13 | assets/fig-13-dependent-data-bootstrap-confidence-intervals.png | plot | Q1: a simulated series and its resample, and measured standard errors | — | — | fig-13-dependent-data-bootstrap-confidence-intervals.png | An AR(1) series and one bootstrap resample of it: lag-1 autocorrelation 0.487 against −0.005; the bootstrap SE is 57% of the true one |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4, SciPy 1.18.1; optional R 4.5.2 with boot 1.3.32; `all --quick` takes
about 23 s, `all` about 3.5 minutes, 0.46 GB of RAM).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/bootstrap-confidence-intervals/README.md` | grade, provenance, setup, run order, the E1–E5 exercises with answers, cleanup |
| LAB_02 | `lab/bootstrap.py` | `labs/bootstrap-confidence-intervals/bootstrap.py` | the seven stages of the lab |
| LAB_03 | `lab/crosscheck.R` | `labs/bootstrap-confidence-intervals/crosscheck.R` | the optional R cross-check with the boot package |
| LAB_04 | `lab/crosscheck-r.csv` | `labs/bootstrap-confidence-intervals/crosscheck-r.csv` | R's intervals, constants, influence values and 2,000 replicates |
| LAB_05 | `lab/data/law_school_82.csv` | `labs/bootstrap-confidence-intervals/data/law_school_82.csv` | the 82 law schools and the 15-school sample (BSD 3-clause), with provenance |
| LAB_06 | `lab/data/online_retail_customer_spend.csv` | `labs/bootstrap-confidence-intervals/data/online_retail_customer_spend.csv` | net spend of 4,317 customers (UCI Online Retail, CC BY 4.0), with provenance |
| LAB_07 | `lab/requirements.txt` | `labs/bootstrap-confidence-intervals/requirements.txt` | the pinned NumPy and SciPy versions |
| LAB_08 | `lab/captures.json` | `labs/bootstrap-confidence-intervals/captures.json` | the author's full run; every figure and card reads it |
| LAB_09 | `lab/captures-quick.json` | `labs/bootstrap-confidence-intervals/captures-quick.json` | the author's `--quick` run |
| LAB_10 | `lab/expected-output.txt` | `labs/bootstrap-confidence-intervals/expected-output.txt` | the full run as printed |
| LAB_11 | `lab/notebook.ipynb` | `labs/bootstrap-confidence-intervals/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-bootstrap-confidence-intervals.zip` | `lab-bootstrap-confidence-intervals.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the two CSV keys so the zip and the individual files agree. Upload with an accurate
`Content-Type` (`text/markdown`, `text/x-python`, `text/plain` for `crosscheck.R`, `text/csv`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

The spend CSV is Part 2's file with one added first line saying so (CC BY 4.0, UCI Online Retail; the derivation
script ships with Part 2's lab), byte-identical to Part 6's copy. The law-school CSV exports the CRAN package
`bootstrap` 2019.6's datasets `law82` and `law` unchanged; the package is BSD 3-clause, and the CSV header carries its
copyright notice, conditions and disclaimer, as the licence requires for redistribution.

## Series links to add

Earlier parts are named by title in plain text; add the link once the target is live.

| Post | Status on 2026-11-01 | Where it is named |
|---|---|---|
| Part 6, *Confidence Intervals: What 95% Means, Measured* (`confidence-intervals-coverage`) | built, not live | **Which interval keeps its promise for the law schools?**, first paragraph: "as the sixth part of this series, *Confidence Intervals: What 95% Means, Measured*, measured it for proportions"; also **Does the bootstrap rescue the skewed mean?**, first paragraph ("The sixth part of this series ended on a failure") |
| Part 3, *Estimators and Their Errors: Why the Best One Can Be Biased* (`estimator-bias-variance-mse`) | built, not live | **When does the bootstrap fail?**, *The maximum*, first paragraph: "The third part of this series, *Estimators and Their Errors: Why the Best One Can Be Biased*" |
| Part 4, *Likelihood: The MLE, Three Tests, and Where χ² Fails* (`likelihood-mle-fisher-information`) | built, not live | **Limitations and common mistakes**, the extremes bullet: "The fourth part of this series, *Likelihood: The MLE, Three Tests, and Where χ² Fails*" |

No later part is named. The block bootstrap is described as a time-series method outside this part, with no series
named, as the plan's hand-off to DS-4 allows.

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. The first render had defects in twelve of the thirteen figures,
  none caught by a gate: percentile labels printed over the histogram and past the axis end (Figure 2), a legend with
  two identical solid swatches (Figure 2) and one with five of seven styles (Figure 4), a label on its own line and a
  swatch darker than its marks (Figure 3), a connector riding two box borders and crossing an eyebrow, and arrow
  labels wider than the gaps they sat in (Figure 5), labels across reference lines and gridlines (Figures 6, 7, 10
  and 11), the eyebrow's uppercasing turning z0 and a into "Z0" and "A" (Figure 6), a collision between "18.7%" and
  ">1 in 69.6%" (Figure 7), a note printed over the tick labels (Figure 8), a jump bracket that read as a second cdf
  step (Figure 10), missing tick labels (Figure 13), and two false notes: "with one, every interval covers" (Figure 9;
  the basic interval covers 92.2% at n = 100) and Figure 12's lumps, which overlap into one hump, so the article's
  "four separate humps" was rewritten around what the capture shows (the largest value supplies 52% of the bootstrap
  variance in sample 1, 21% in sample 3).
- Rounding: shares are counts over R, so exact ties occur (2.15%, 78.65%, 80.25%, 80.85%). The lab first printed
  them with float formatting, which rounds some ties down; `bootstrap.py` now rounds half up from the exact decimal,
  the captures were regenerated with it (script e3a939a03bc4, values unchanged), and the article, README, figures and
  cards use the same rule. Two article numbers moved: the bootstrap-t at n = 100 (80.2% → 80.3%) and BCa at n = 300
  on Pareto data (80.8% → 80.9%). A third slip was a double rounding: sample 3's lump spacing 0.174945 had been
  written 0.18 from the printed 0.175; it is 0.17.
- Social cards: values past the panel edge, a band label colliding with a tick (card 3), a 95% line through value
  labels and bars from a non-zero baseline (card 5, redrawn as a dot plot), all fixed. `render_social.py --check`
  passes all 8 cards.
- `_overlap.py` on the final renders: 1 report on the figures and cover, the cover's two serif title lines; 16 on the
  cards, each card's serif title lines and the lockup's `.in`. All are the checker's documented false positives.
- `lint_visuals.py`: 0 text overflows on all 14 files; 1 arrow report, Figure 10's annotation arrow, which points at
  the cdf's jump by design and lands on it in the render.
- `_figs.py`, `_cover.py` and `_social.py` assert the article's numbers against `captures.json` before drawing;
  every number printed on a figure or card is computed from the capture.
- The Implementation snippet was run as printed: it prints r 0.7764, z0 −0.0929, a −0.07567, levels 0.00581 and
  0.93859, percentile 0.4523 to 0.9624 and BCa 0.3273 to 0.9421, the lab's worked example to the digit.

## Owner actions

- Upload the PNGs, the eleven lab files and the zip, then fill `urls.txt` and run `fill_urls.py`.
- The `data-science` category is still missing from the live database (a production write at publish time; Parts
  1 to 6 need it too).
- Part 6 must go live before this part: this part's **Assumes** line names it. Parts 3 and 4, named once each, can
  be linked once they are live.
