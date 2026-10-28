# Asset manifest — estimator-bias-variance-mse

Series `statistics-for-data-scientists`, part 3. **Status: local draft assets ready for upload.** Upload the
twelve PNGs and the nine lab files to the public `media` bucket under the object keys below, write the
resulting URLs to `urls.txt` in table order (COVER, FIG_01–FIG_11, then LAB_01–LAB_09), then run
`fill_urls.py`. Upload the lab zip separately, to the bucket root (see **Lab files**). Nothing has been
published, so every key is new; the names carry the slug because the bucket is flat.

Every figure is our own analysis, drawn from the lab's `captures.json` by `assets/_figs.py` (the cover by
`assets/_cover.py`), which asserts every number the article quotes before it draws. The `source` route was
considered first for every paper-backed figure (ledger, **Figure candidates**): Efron and Morris's 1977 figures
are Scientific American's copyright with no licence, and Figure 8 adds the truth and a regression line they do
not show (F1, F2); Simon's table is facts, drawn here as Figure 4 (F3); Clark et al.'s Figure 2 reproduces a
wiki (F4). No figure is Mermaid: none is a graph of nodes and edges.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-estimator-bias-variance-mse.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 2 reduced to its argument, the MLE walled at the true N beside the MVUE, the tangerine used once on N; no external generator | — | — | cover-estimator-bias-variance-mse.png | Sampling distributions of two tank-count estimators: the MLE piled against a wall at the true 342, the MVUE centred on it |
| FIG_01 | assets/fig-01-one-capture-estimator-bias-variance-mse.png | plot | Q4: five data points on a scaled number line with constructed estimates | — | — | fig-01-one-capture-estimator-bias-variance-mse.png | Five captured serial numbers on a line from 0 to 560, with the MLE at 303, the MVUE at 362.6 and the true N = 342 marked |
| FIG_02 | assets/fig-02-sampling-distributions-estimator-bias-variance-mse.png | plot | Q4: simulated distributions, binned by the maximum, against the exact distribution of the maximum | — | — | fig-02-sampling-distributions-estimator-bias-variance-mse.png | Three histograms of a million estimates of N = 342: the MLE stops at 342, the MVUE centres on it, 2 × mean − 1 spreads widest |
| FIG_03 | assets/fig-03-bias-variance-mse-estimator-bias-variance-mse.png | chart | Q1: exact MSE decompositions with simulated checks | — | — | fig-03-bias-variance-mse-estimator-bias-variance-mse.png | Stacked bars of MSE as variance plus bias² for four estimators: MLE 5,448 with bias² 3,155; MVUE 3,303; m(k+2)/(k+1) − 1 3,212 |
| FIG_04 | assets/fig-04-statistics-against-spies-estimator-bias-variance-mse.png | chart | Q1: published numbers (ledger L03) on a log axis | — | — | fig-04-statistics-against-spies-estimator-bias-variance-mse.png | Log-scale dots for June 1940, June 1941 and August 1942: intelligence 1,000 to 1,550 tanks, serial numbers 169 to 327, records 122 to 342 |
| FIG_05 | assets/fig-05-rao-blackwell-estimator-bias-variance-mse.png | plot | Q4: a scatter of 3,000 simulated captures with conditional means from a million | — | — | fig-05-rao-blackwell-estimator-bias-variance-mse.png | Scatter of 2 × mean − 1 against the largest serial for 3,000 captures, with conditional means lying on the line m(1 + 1/k) − 1 |
| FIG_06 | assets/fig-06-consistency-estimator-bias-variance-mse.png | plot | Q4: exact RMSE curves on log–log axes with simulated points | — | — | fig-06-consistency-estimator-bias-variance-mse.png | Log–log RMSE against tanks captured: one-tank estimator flat at 197.5, mean-based falling like 1/√k, maximum-based like 1/k |
| FIG_07 | assets/fig-07-variance-divisors-estimator-bias-variance-mse.png | plot | Q4: exact MSE curves in the divisor with simulated points | — | — | fig-07-variance-divisors-estimator-bias-variance-mse.png | MSE of the sum of squares divided by d at n = 10: minimum at 11 for normal, 9.92 for uniform and 16.4 for exponential data |
| FIG_08 | assets/fig-08-shrinkage-as-regression-estimator-bias-variance-mse.png | plot | Q4: published data (ledger L13) with constructed prediction lines | — | — | fig-08-shrinkage-as-regression-estimator-bias-variance-mse.png | Rest-of-season against first-45 batting averages for 18 players, with slope-1, James–Stein (0.212) and hindsight (0.190) lines |
| FIG_09 | assets/fig-09-per-player-errors-estimator-bias-variance-mse.png | chart | Q1: per-player errors computed from the published table | — | — | fig-09-per-player-errors-estimator-bias-variance-mse.png | Per-player squared errors for 18 batters: James–Stein closer for 16, further for Swoboda and Rodriguez; totals 0.0753 and 0.0213 |
| FIG_10 | assets/fig-10-replayed-seasons-estimator-bias-variance-mse.png | plot | Q4: a simulated distribution with the observed value marked | — | — | fig-10-replayed-seasons-estimator-bias-variance-mse.png | Histogram of 200,000 replayed seasons' error ratios: 96.2% above break-even, median 3.05, the real 1970 ratio 3.53 in the top quarter |
| FIG_11 | assets/fig-11-stein-risk-estimator-bias-variance-mse.png | plot | Q4: an exact risk curve (ledger L11) with simulated points | — | — | fig-11-stein-risk-estimator-bias-variance-mse.png | James–Stein risk against the spread of 18 true means: 3 when equal, 6.81 at the batters' spread, rising toward the flat 18 |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4 and SciPy 1.18.1; `all --quick` takes about 3 s, `all` about 13 s, 0.13 GB of RAM).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/estimator-bias-variance-mse/README.md` | grade, provenance, setup, run order, the E1–E4 exercises with answers, cleanup |
| LAB_02 | `lab/estimators.py` | `labs/estimator-bias-variance-mse/estimators.py` | the five stages of the lab |
| LAB_03 | `lab/requirements.txt` | `labs/estimator-bias-variance-mse/requirements.txt` | the pinned NumPy and SciPy versions |
| LAB_04 | `lab/data/efron_morris_1975_batting.csv` | `labs/estimator-bias-variance-mse/data/efron_morris_1975_batting.csv` | the 18 players of 1970, transcribed from Efron and Morris's Table 1 with provenance |
| LAB_05 | `lab/data/ruggles_brodie_1947_tanks.csv` | `labs/estimator-bias-variance-mse/data/ruggles_brodie_1947_tanks.csv` | three months of tank estimates and records, as reproduced from Ruggles and Brodie |
| LAB_06 | `lab/captures.json` | `labs/estimator-bias-variance-mse/captures.json` | the author's full run, with the R cross-check; every figure reads it |
| LAB_07 | `lab/captures-quick.json` | `labs/estimator-bias-variance-mse/captures-quick.json` | the author's `--quick` run |
| LAB_08 | `lab/expected-output.txt` | `labs/estimator-bias-variance-mse/expected-output.txt` | the full run as printed |
| LAB_09 | `lab/notebook.ipynb` | `labs/estimator-bias-variance-mse/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-estimator-bias-variance-mse.zip` | `lab-estimator-bias-variance-mse.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the two CSV keys so the zip and the individual files agree. Upload with an
accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`, `text/csv`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

The batting CSV transcribes the facts in a 1975 published table, cited in its header and cross-checked against
Rdatasets' `pscl::EfronMorris`; the tank CSV carries three published monthly figures, with both reproductions
cited. Neither copies another dataset's file.

## Series links to add

Earlier parts are named by title or number in plain text; add the link once the target is live.

| Post | Status on 2026-10-28 | Where it is named |
|---|---|---|
| Part 2, *The Sampling Distribution: The CLT and Where n = 30 Fails* (`sampling-distribution-central-limit-theorem`) | built, not live | **The problem**, first paragraph: "come from the second part of this series, *The Sampling Distribution: The CLT and Where n = 30 Fails*" |
| Part 2 (same post) | built, not live | **Is unbiased the same as consistent?**, third paragraph: "the rate the second part of this series found for every mean" |

Later parts appear only as "later in this series": likelihood (Worked example), partial pooling and the
bootstrap's failure on the maximum (Limitations), with no number or title. Prediction error is named as
"machine-learning practice, outside this series".

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. Fixed on the way: 5-tank bins that aliased against the
  estimators' discrete support and drew a false sawtooth and a false drop at N (Figure 2, now binned by the
  maximum with the exact distribution overlaid); a grey baseline through a label (Figure 1); legend swatches
  without the bars' outlines (Figure 3); a label running past the plot frame (Figure 4); a ±1 SD bracket drawn
  30 px from the m it described, and a label plate hiding data (Figure 5); dots half-clipped at the frame
  (Figures 6, 11); axis labels over the y-axis title, a label plate cutting a gridline, and two dark curves
  hard to tell apart (Figure 7); a dash pattern that did not match its swatch, and two players sharing one
  point, now noted (Figure 8); a dead band under the axis (Figure 9); y ticks stopping below the bars and an
  MCSE printed as ± 0.00 (Figure 10); a label plate cutting the risk curve (Figure 11).
- Social cards, read the same way: a label collision on the number line (feed 2), a redundant "3,303 =
  3,303" (feed 4), the winner shown in grey instead of tangerine (story 1), and two claims tightened:
  "spies" became "intelligence" (the estimates also came from prewar capacity and prisoners, ledger L02), and
  "not accuracy" became "not the smallest error" (feed 6).
- `_overlap.py`: 0 issues on Figures 1–11. On the cover and the social cards it reports only its known false
  positives: consecutive serif title lines and the lockup's `.in`.
- `lint_visuals.py`: 0 text overflows, 0 arrow reports.
- `_figs.py`, `_cover.py` and `_social.py` assert the article's numbers against `captures.json` before
  drawing; every number printed on a figure or card is computed from the capture.
- Both Implementation snippets were run as printed: the tank snippet prints the three lines quoted, and the
  James–Stein snippet prints 0.2654, 0.2117, 0.0753 and 0.0213, matching the lab.

## Owner actions

- Upload the PNGs, the nine lab files and the zip, then fill `urls.txt` and run `fill_urls.py`.
- The `data-science` category is still missing from the live database (a production write at publish time;
  Parts 1 and 2 need it too).
- Part 2 must go live before this part: this part's **Assumes** line names it, and Part 2 needs Part 1.
