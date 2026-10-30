# Asset manifest — likelihood-mle-fisher-information

Series `statistics-for-data-scientists`, part 4. **Status: local draft assets ready for upload.** Upload the
fourteen PNGs and the ten lab files to the public `media` bucket under the object keys below, write the
resulting URLs to `urls.txt` in table order (COVER, FIG_01–FIG_13, then LAB_01–LAB_10), then run
`fill_urls.py`. Upload the lab zip separately, to the bucket root (see **Lab files**). Nothing has been
published, so every key is new; the names carry the slug because the bucket is flat.

Every figure is our own analysis, drawn from the lab's `captures.json` by `assets/_figs.py` (the cover by
`assets/_cover.py`), which asserts the numbers the article quotes before it draws. The `source` route was
considered first for every paper-backed figure (ledger, **Figure candidates**): Buse's three diagrams are the
American Statistical Association's copyright with no reuse licence, and Figures 2 and 3 draw the same
geometry on real curves with their numbers (F1); CSN's Figure 5.1 is SIAM's, and Figure 13 measures the same
behaviour on the first part's own sample (F2); Brazzale and Mameli's Figure 3 is the IMS's, and the
one-parameter case is drawn from the lab's simulation (F3). No figure is Mermaid: none is a graph of nodes and
edges.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-likelihood-mle-fisher-information.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 2 reduced to its argument, the three distances on Clarke's curve, the tangerine used once on the score's slope; no external generator | — | — | cover-likelihood-mle-fisher-information.png | Clarke's V-1 log-likelihood with three distances to a null value: a horizontal gap, a drop in height and a tangent's slope |
| FIG_01 | assets/fig-01-likelihood-and-score-likelihood-mle-fisher-information.png | plot | Q4: a log-likelihood and its quadratic, and the score and its tangent, computed from Clarke's table | — | — | fig-01-likelihood-and-score-likelihood-mle-fisher-information.png | Clarke's Poisson log-likelihood peaks at 0.9323 with curvature 617.8; below it the score crosses zero at the same point |
| FIG_02 | assets/fig-02-three-distances-likelihood-mle-fisher-information.png | plot | Q4: geometry on a computed curve: a gap, a drop and a tangent | — | — | fig-02-three-distances-likelihood-mle-fisher-information.png | On Clarke's log-likelihood the gap to 0.85 gives Wald 4.18, the drop gives LR 4.45, and the slope there gives score 4.59 |
| FIG_03 | assets/fig-03-small-sample-geometry-likelihood-mle-fisher-information.png | plot | Q4: the same geometry on a lopsided curve, with Wald's quadratic drawn against it | — | — | fig-03-small-sample-geometry-likelihood-mle-fisher-information.png | Corps XI's lopsided log-likelihood: Wald 6.55, likelihood ratio 10.27 and score 13.43 for the same null rate of 0.61 |
| FIG_04 | assets/fig-04-exact-sizes-likelihood-mle-fisher-information.png | plot | Q1: exact error rates computed at 403 expected counts, a curve on a log axis | — | — | fig-04-exact-sizes-likelihood-mle-fisher-information.png | Exact rejection rates of 5% Wald, score and likelihood-ratio tests against the expected count: erratic below 20, all near 5% by 537 |
| FIG_05 | assets/fig-05-wald-depends-on-scale-likelihood-mle-fisher-information.png | plot | Q1: Wald statistics computed across 61 scales, against two constants | — | — | fig-05-wald-depends-on-scale-likelihood-mle-fisher-information.png | Wald statistics for one null across scales λ^c: corps XI from 3.63 to 27.52, Clarke 3.82 to 5.03; score and LR stay flat |
| FIG_06 | assets/fig-06-nb-likelihood-surface-likelihood-mle-fisher-information.png | plot | Q4: likelihood regions traced in two dimensions against an ellipse | — | — | fig-06-nb-likelihood-surface-likelihood-mle-fisher-information.png | Negative binomial likelihood regions in mean and shape: the 95% region reaches k = 1.58, while the Wald ellipse stops at 1.32 |
| FIG_07 | assets/fig-07-profile-intervals-likelihood-mle-fisher-information.png | plot | Q4: profile curves, their quadratics and the intervals they cut, on one scale | — | — | fig-07-profile-intervals-likelihood-mle-fisher-information.png | Profile log-likelihoods for k and the dispersion index cut at −1.92: the profile intervals are lopsided, the Wald ones symmetric |
| FIG_08 | assets/fig-08-k-sampling-distribution-likelihood-mle-fisher-information.png | plot | Q1: a simulated distribution against the normal the Wald SE implies | — | — | fig-08-k-sampling-distribution-likelihood-mle-fisher-information.png | Histogram of 20,000 re-estimated k: skewed right, with 7.47% above the upper Wald limit and 0.14% below the lower |
| FIG_09 | assets/fig-09-boundary-profiles-likelihood-mle-fisher-information.png | plot | Q4: two computed curves meeting the edge of the parameter space | — | — | fig-09-boundary-profiles-likelihood-mle-fisher-information.png | Profile log-likelihood in α: Clarke's peaks inside at 0.040 with LR 0.41; a simulated Poisson data set peaks on the edge, α = 0 |
| FIG_10 | assets/fig-10-boundary-null-distribution-likelihood-mle-fisher-information.png | plot | Q1: simulated survival functions on a log axis against two reference curves | — | — | fig-10-boundary-null-distribution-likelihood-mle-fisher-information.png | Simulated shares above each likelihood ratio: inside they follow χ²₁; on the boundary 52.6% sit at 0 and the mixture fits |
| FIG_11 | assets/fig-11-tank-likelihood-likelihood-mle-fisher-information.png | plot | Q4: an exact likelihood and an exact error distribution against a normal | — | — | fig-11-tank-likelihood-likelihood-mle-fisher-information.png | German tank log-likelihood falls from a wall at 303 with no peak; the MLE's error is skewed, and a normal would put 12% below 0 |
| FIG_12 | assets/fig-12-power-law-or-lognormal-likelihood-mle-fisher-information.png | plot | Q1: data on log–log axes with two fitted curves | — | — | fig-12-power-law-or-lognormal-likelihood-mle-fisher-information.png | The top 1,000 values of the first part's lognormal sample on log–log axes: the lognormal fit follows the bend, the power law overshoots |
| FIG_13 | assets/fig-13-vuong-by-threshold-likelihood-mle-fisher-information.png | plot | Q1: computed statistics against tail size, with simulated spreads | — | — | fig-13-vuong-by-threshold-likelihood-mle-fisher-information.png | Vuong's normalised ratio against tail size: 1.10 at 100 points, 2.29 at 1,000 and 12.49 at 5,000; undecided below about 1,000 |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0, pandas 3.1.0; `all --quick`
takes about 16 s, `all` about 100 s, 0.27 GB of RAM).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/likelihood-mle-fisher-information/README.md` | grade, provenance, setup, run order, the E1–E5 exercises with answers, cleanup |
| LAB_02 | `lab/likelihood.py` | `labs/likelihood-mle-fisher-information/likelihood.py` | the five stages of the lab |
| LAB_03 | `lab/requirements.txt` | `labs/likelihood-mle-fisher-information/requirements.txt` | the pinned NumPy, SciPy, statsmodels and pandas versions |
| LAB_04 | `lab/data/clarke1946_flying_bombs.csv` | `labs/likelihood-mle-fisher-information/data/clarke1946_flying_bombs.csv` | Clarke's 576 squares by number of hits, with provenance |
| LAB_05 | `lab/data/greenwood_yule1920_accidents.csv` | `labs/likelihood-mle-fisher-information/data/greenwood_yule1920_accidents.csv` | Greenwood and Yule's 647 women by number of accidents, with provenance |
| LAB_06 | `lab/data/bortkiewicz1898_horse_kicks.csv` | `labs/likelihood-mle-fisher-information/data/bortkiewicz1898_horse_kicks.csv` | horse-kick deaths by corps and year, with provenance |
| LAB_07 | `lab/captures.json` | `labs/likelihood-mle-fisher-information/captures.json` | the author's full run, with the private cross-checks; every figure reads it |
| LAB_08 | `lab/captures-quick.json` | `labs/likelihood-mle-fisher-information/captures-quick.json` | the author's `--quick` run |
| LAB_09 | `lab/expected-output.txt` | `labs/likelihood-mle-fisher-information/expected-output.txt` | the full run as printed |
| LAB_10 | `lab/notebook.ipynb` | `labs/likelihood-mle-fisher-information/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-likelihood-mle-fisher-information.zip` | `lab-likelihood-mle-fisher-information.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the three CSV keys so the zip and the individual files agree. Upload with an
accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`, `text/csv`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

The three CSVs are the first part's files, unchanged (their provenance headers cite Clarke 1946, Greenwood and
Yule 1920 through two reproductions, and Bortkiewicz 1898); they transcribe the facts in published tables.

## Series links to add

Earlier parts are named by title or by number in plain text; add the link once the target is live.

| Post | Status on 2026-10-28 | Where it is named |
|---|---|---|
| Part 3, *Estimators and Their Errors: Why the Best One Can Be Biased* (`estimator-bias-variance-mse`) | built, not live | **The problem**, first paragraph: "The third part of this series, *Estimators and Their Errors: Why the Best One Can Be Biased*" |
| Part 3 (same post) | built, not live | **Which conditions does the likelihood's promise need?**, the tank paragraph: "The third part found these errors shrinking like 1/k" |
| Part 1, *Distributions as Generative Stories: Let the Process Pick* (`distributions-as-generative-stories`) | built, not live | **Worked example**, first paragraph: "The first part of this series, *Distributions as Generative Stories: Let the Process Pick*" |
| Part 1 (same post) | built, not live | **What changes with a second parameter?** ("The first part explained it as accident proneness"), **The delta method** ("whose moment value in the first part was 1.49"), and **Power law or lognormal** ("The first part drew 10,000 values") |

Later parts appear only as "a later part of this series": what a p-value means (Worked example), interval
coverage (profile-likelihood section) and variance components (boundary section), with no number or title.

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. The first render had a defect in all thirteen figures,
  none caught by a gate: the combining hat on Greek letters (λ̂, α̂, μ̂, σ̂) does not render in Geist Mono and
  printed as "λˆ", which turned "−617.8 (λ − λ̂)²" into "(λ − λ)" (Figures 1–3, 9, 12; now "MLE" wording; k̂
  and D̂ render and stay); eyebrows uppercased notation, k to K and λ^c to λ^C (Figures 5, 6, 8, 9, 10, 11);
  label plates cut gaps in curves, tangents, contours or gridlines (Figures 1–5, 7, 9, 11, 13) and interval
  labels were printed across curves (Figure 7); the likelihood ratio's ink matched the log-likelihood's in
  the legend (Figures 2, 3); the 50% contour was ink while its legend swatch was grey (Figure 6); the lab's
  clipped last bin drew a false spike at the axis edge (Figure 8, now omitted and its 0.13% stated); the
  "α < 0" band sat on the y tick labels (Figure 9); dotted reference lines ran through text (Figure 10); a
  note touched the zero line it described (Figure 11); simulated bars at 55% opacity had solid swatches
  (Figure 13); and most canvases had a dead band above the legend.
- The profile interval's lower end is 0.585471: the figure's assert caught a first draft that rounded it to
  0.586.
- `_overlap.py`: 0 issues on Figures 1–13.
- `lint_visuals.py`: 0 text overflows; 4 arrow reports, all the double-headed distance arrows of Figures 2
  and 3, which measure a gap and touch no node by design.
- `_figs.py` and `_cover.py` assert the article's numbers against `captures.json` before drawing; every number
  printed on a figure is computed from the capture.
- Both Implementation snippets were run as printed: the negative binomial snippet prints the two lines quoted,
  and the boundary snippet prints 0.5267.

## Owner actions

- Upload the PNGs, the ten lab files and the zip, then fill `urls.txt` and run `fill_urls.py`.
- The `data-science` category is still missing from the live database (a production write at publish time;
  Parts 1 to 3 need it too).
- Part 3 must go live before this part: this part's **Assumes** line names it, and Part 3 needs Part 2.
