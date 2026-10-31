# Asset manifest — confidence-intervals-coverage

Series `statistics-for-data-scientists`, part 6. **Status: local draft assets ready for upload.** Upload the
eleven PNGs and the nine lab files to the public `media` bucket under the object keys below, write the resulting
URLs to `urls.txt` in table order (COVER, FIG_01–FIG_10, then LAB_01–LAB_09), then run `fill_urls.py`. Upload the
lab zip separately, to the bucket root (see **Lab files**). Nothing has been published, so every key is new; the
names carry the slug because the bucket is flat.

Every figure is our own analysis, drawn from the lab's `captures.json` by `assets/_figs.py` (the cover by
`assets/_cover.py`), which asserts the numbers the article quotes before it draws. The `source` route was
considered first for every paper-backed figure (ledger, **Figure candidates**): Agresti and Coull's Figure 4
(coverage curves at n = 5 and 10) is the publisher's with no reuse licence, and Figure 3 computes the same kind of
curves for five intervals at n = 50 (F1); Brown, Cai and DasGupta's figures could not be read and carry no licence
(F2); the trial's Figure 3 is case accrual, not intervals (F3). No figure is Mermaid: none is a graph of nodes and
edges.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-confidence-intervals-coverage.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 3 reduced to its argument, the Wald interval's coverage at n = 50 in tangerine (the one use) against Clopper–Pearson's; no external generator | — | — | cover-confidence-intervals-coverage.png | Two coverage curves for 95% intervals at n = 50: the Wald interval's jagged and far below 95%, Clopper–Pearson's never below it |
| FIG_01 | assets/fig-01-coverage-by-enumeration-confidence-intervals-coverage.png | plot | Q4: every outcome's interval drawn to scale beside its exact binomial probability | — | — | fig-01-coverage-by-enumeration-confidence-intervals-coverage.png | Wald, Wilson and Clopper–Pearson intervals for each count of errors in 20 audits beside each count's probability; coverage 87.6%, 95.7%, 98.9% |
| FIG_02 | assets/fig-02-intervals-as-inverted-tests-confidence-intervals-coverage.png | plot | Q4: three computed p-value functions cut by the 0.05 line, with the intervals they give | — | — | fig-02-intervals-as-inverted-tests-confidence-intervals-coverage.png | Two-sided p-value against the null value for 2 errors in 20: Wald, score and exact tests, each crossing 0.05 at its interval's endpoints |
| FIG_03 | assets/fig-03-coverage-curves-confidence-intervals-coverage.png | plot | Q1: exact coverage curves for five intervals, small multiples on one scale | — | — | fig-03-coverage-curves-confidence-intervals-coverage.png | Exact coverage of five 95% intervals against p at n = 50: Wald far below 95% for 40% of p, Clopper–Pearson never below 95% |
| FIG_04 | assets/fig-04-wald-oscillation-confidence-intervals-coverage.png | plot | Q1: an exact sawtooth over n on a log axis, with Wilson in its own panel | — | — | fig-04-wald-oscillation-confidence-intervals-coverage.png | The Wald interval's coverage at p = 0.1 for n from 10 to 1,000, zigzagging between 81% and 95%, beside the Wilson interval's steadier curve |
| FIG_05 | assets/fig-05-coverage-and-width-confidence-intervals-coverage.png | plot | Q1: exact means and widths across n, with Agresti and Coull's printed means | — | — | fig-05-coverage-and-width-confidence-intervals-coverage.png | Mean coverage and mean width over a uniform p against n for five intervals, with Agresti and Coull's printed means as rings |
| FIG_06 | assets/fig-06-vaccine-efficacy-intervals-confidence-intervals-coverage.png | plot | Q1: intervals computed from published counts beside the published credible interval, and exact coverage at n = 170 | — | — | fig-06-vaccine-efficacy-intervals-confidence-intervals-coverage.png | Vaccine efficacy intervals from 8 of 170 cases by five methods beside the published credible interval, and each method's exact coverage at n = 170 |
| FIG_07 | assets/fig-07-overlap-rule-confidence-intervals-coverage.png | plot | Q4: the overlap geometry, and Schenker and Gentleman's formula drawn as error-rate and power curves | — | — | fig-07-overlap-rule-confidence-intervals-coverage.png | The overlap rule's type I error against the ratio of standard errors, from 0.56% at 1 toward 5%, and its power against the standard test's |
| FIG_08 | assets/fig-08-overlap-in-a-trial-confidence-intervals-coverage.png | plot | Q1: published counts, exact Poisson intervals and the efficacy interval on two axes | — | — | fig-08-overlap-in-a-trial-confidence-intervals-coverage.png | Severe Covid-19 rates with exact 95% intervals: vaccine 0.25 (0.006 to 1.39), placebo 2.25 (1.03 to 4.26), overlapping; efficacy 20.1% to 99.7% |
| FIG_09 | assets/fig-09-t-interval-coverage-confidence-intervals-coverage.png | plot | Q1: simulated coverage with its MCSE across n, and the misses split by side on a log axis | — | — | fig-09-t-interval-coverage-confidence-intervals-coverage.png | Coverage of the 95% t-interval for mean customer spend against n from 10 to 10,000: 64% to 94%, with nearly all misses below the mean |
| FIG_10 | assets/fig-10-coverage-by-width-confidence-intervals-coverage.png | plot | Q1: simulated and exact coverage by tenth of interval width, two populations | — | — | fig-10-coverage-by-width-confidence-intervals-coverage.png | Coverage of the t-interval at n = 30 by tenth of interval width: spend from 0% to 100%, a normal population from 88% to 99% |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0, pandas 3.1.0; `all --quick` takes
about 11 s, `all` about 17 s, 0.28 GB of RAM).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/confidence-intervals-coverage/README.md` | grade, provenance, setup, run order, the E1–E4 exercises with answers, cleanup |
| LAB_02 | `lab/intervals.py` | `labs/confidence-intervals-coverage/intervals.py` | the six stages of the lab |
| LAB_03 | `lab/requirements.txt` | `labs/confidence-intervals-coverage/requirements.txt` | the pinned NumPy, SciPy, statsmodels and pandas versions |
| LAB_04 | `lab/data/online_retail_customer_spend.csv` | `labs/confidence-intervals-coverage/data/online_retail_customer_spend.csv` | net spend of 4,317 customers (UCI Online Retail, CC BY 4.0), with provenance |
| LAB_05 | `lab/data/bnt162b2_case_splits.csv` | `labs/confidence-intervals-coverage/data/bnt162b2_case_splits.csv` | the trial's 18 published case splits with surveillance times and intervals, with sources |
| LAB_06 | `lab/captures.json` | `labs/confidence-intervals-coverage/captures.json` | the author's full run, with the private cross-checks against R; every figure reads it |
| LAB_07 | `lab/captures-quick.json` | `labs/confidence-intervals-coverage/captures-quick.json` | the author's `--quick` run |
| LAB_08 | `lab/expected-output.txt` | `labs/confidence-intervals-coverage/expected-output.txt` | the full run as printed |
| LAB_09 | `lab/notebook.ipynb` | `labs/confidence-intervals-coverage/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-confidence-intervals-coverage.zip` | `lab-confidence-intervals-coverage.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the two CSV keys so the zip and the individual files agree. Upload with an accurate
`Content-Type` (`text/markdown`, `text/x-python`, `text/plain`, `text/csv`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

The spend CSV is Part 2's file with one added first line saying so (CC BY 4.0, UCI Online Retail, the derivation
script ships with Part 2's lab). The case-split CSV copies 18 rows of counts, surveillance times and intervals from
the trial's NEJM paper (Tables 2 and 3) and the FDA's briefing document (Table 12, a U.S. government work); its
header names both sources.

## Series links to add

Earlier parts are named by title in plain text; add the link once the target is live.

| Post | Status on 2026-10-31 | Where it is named |
|---|---|---|
| Part 5, *p-Values and Power: How Wrong Can a Significant Result Be?* (`hypothesis-testing-p-values-power`) | built, not live | **The problem**, second paragraph: "The fifth part of this series, *p-Values and Power: How Wrong Can a Significant Result Be?*" |
| Part 4, *Likelihood: The MLE, Three Tests, and Where χ² Fails* (`likelihood-mle-fisher-information`) | built, not live | **The problem**, second paragraph: "the score test of the fourth part, *Likelihood: The MLE, Three Tests, and Where χ² Fails*" |
| Part 2, *The Sampling Distribution: The CLT and Where n = 30 Fails* (`sampling-distribution-central-limit-theorem`) | built, not live | **Does the t-interval keep its promise on skewed data?**, first paragraph: "The second part of this series, *The Sampling Distribution: The CLT and Where n = 30 Fails*" |

Later parts appear only as "a later part of this series": the reproduction of the trial's credible interval (end of
**What does a 95% interval promise?**) and intervals that adapt to skew (end of the t-interval section), with no
number or title.

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. The first render had defects in nine of the ten figures,
  none caught by a gate: panel titles colliding with notes (Figure 3), minimum dots floating below curves drawn on
  a coarser grid (Figure 3), a label printed across the Wilson curve (Figure 4, fixed by giving Wilson its own
  panel), notes running off the canvas or into an axis (Figures 5, 6, 8 and 9), legend swatches that did not match
  their marks (an estimate dot in Figure 1's interval swatch; solid Agresti–Coull and Jeffreys bars against dashed
  swatches in Figure 6), one colour carrying two meanings in one figure (Figures 7 and 9), labels on curves
  (Figure 7), and a note promising ±2 MCSE bars that were smaller than their dots (Figure 9; the note now says so).
  Figure 7's dashed 83.4% power curve lies exactly on the standard test's; `_figs.py` asserts that and the figure
  says it.
- Two figure numbers did not match the prose at first: the article had 0.86% where the capture gives 0.8549%
  (now 0.85%), and Agresti–Coull's minimum appeared as 93.4% in the text and 93.5% on a card (both now 93.45%).
  A recheck of the prose against the capture also corrected 98.2% → 98.1%, 98.5 → 98.4, 79.7% → 79.6%, 4.27 → 4.26,
  1.33 → 1.32, 1.49 → 1.48 and "within 1.2 MCSEs" → 1.3.
- Social cards: a label past the panel edge (cards 1 and 6), a label on a reference line (card 7), and two claims
  the cards did not support (card 3's takeaway paired np ≥ 5 with n = 29 and 30, where np is below 5; card 5's
  "low counts need exact intervals" said more than the article), all fixed.
- `_overlap.py` on the final renders: 1 report on the figures and cover, the cover's two serif title lines; 16 on
  the cards, each card's two serif title lines and the lockup's `.in`. All are the checker's documented false
  positives.
- `lint_visuals.py`: 0 text overflows and 0 arrow reports on all 11 files. `render_social.py --check` passes all 8
  cards.
- `_figs.py`, `_cover.py` and `_social.py` assert the article's numbers against `captures.json` before drawing;
  every number printed on a figure or card is computed from the capture.
- Both Implementation snippets were run as printed: the first prints 0.8760 0.9467 0.8085 0.8789, the second the
  library limits the article quotes.

## Owner actions

- Upload the PNGs, the nine lab files and the zip, then fill `urls.txt` and run `fill_urls.py`.
- The `data-science` category is still missing from the live database (a production write at publish time; Parts
  1 to 5 need it too).
- Part 5 must go live before this part: this part's **Assumes** line names it. Parts 2 and 4, named once each, can
  be linked once they are live.
