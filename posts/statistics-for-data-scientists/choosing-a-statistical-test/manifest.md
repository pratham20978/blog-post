# Asset manifest — choosing-a-statistical-test

Series `statistics-for-data-scientists`, part 8. **Status: local draft assets ready for upload.** Upload the twelve
PNGs and the nine lab files to the public `media` bucket under the object keys below, write the resulting URLs to
`urls.txt` in table order (COVER, FIG_01–FIG_11, then LAB_01–LAB_09), then run `fill_urls.py`. Upload the lab zip
separately, to the bucket root (see **Lab files**). Nothing has been published, so every key is new; the names carry
the slug because the bucket is flat.

Every figure is our own analysis, drawn from the lab's `captures.json` by `assets/_figs.py` (Figures 1 and 10 also
read the lab's CSV files; the cover is drawn by `assets/_cover.py`), which asserts the numbers the article quotes
before it draws. Figure 3 is laid out by Mermaid from `assets/fig-03-design-to-test-choosing-a-statistical-test.mmd` through
`assets/_mermaid.py`. The `source` route was considered first for every paper-backed figure (ledger, **Figure
candidates**): Delacre et al.'s figures are CC BY 4.0 but measure other designs, so this post's own exact curves on
its worked designs replace them (F1–F3), and Campbell's figures carry no reuse licence (F4).

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-choosing-a-statistical-test.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 4 reduced to its argument, Student's exact type I error in tangerine (the one use) against Welch's flat 5%; no external generator | — | — | cover-choosing-a-statistical-test.png | Type I error of Student's and Welch's t-tests against the SD ratio for groups of 10 and 40: Student's climbs to 29%, Welch's stays at 5% |
| FIG_01 | assets/fig-01-ten-patients-choosing-a-statistical-test.png | plot | Q1: the ten patients' real paired values, as lines and as a scatter | — | — | fig-01-ten-patients-choosing-a-statistical-test.png | Ten patients' extra hours of sleep on two drugs, joined by lines, and drug 2 plotted against drug 1; correlation 0.795 |
| FIG_02 | assets/fig-02-two-standard-errors-choosing-a-statistical-test.png | plot | Q4: two computed null densities on one hours axis, with the observed difference | — | — | fig-02-two-standard-errors-choosing-a-statistical-test.png | Null distributions of the mean difference as two groups (SE 0.849, p = 0.079) and paired (SE 0.389, p = 0.0028); observed 1.58 |
| FIG_03 | assets/fig-03-design-to-test-choosing-a-statistical-test.png | mermaid | Q2: 12 nodes in three parallel branches plus a two-level split; laid out by Mermaid from the kept `.mmd` | — | — | fig-03-design-to-test-choosing-a-statistical-test.png | Design-to-test map: paired units to the paired t-test, independent groups to Welch's tests, a 2 × 2 table by its fixed margins |
| FIG_04 | assets/fig-04-student-against-welch-choosing-a-statistical-test.png | plot | Q1: exact curves by quadrature with simulated checks, on a log ratio axis | — | — | fig-04-student-against-welch-choosing-a-statistical-test.png | Exact type I error of Student's and Welch's t-tests against the SD ratio for 10 and 40 and for 25 and 25; Student's reaches 29.4% |
| FIG_05 | assets/fig-05-the-price-of-welch-choosing-a-statistical-test.png | plot | Q4: computed power curves for two designs | — | — | fig-05-the-price-of-welch-choosing-a-statistical-test.png | Power of Student's and Welch's tests with equal SDs, for 25 and 25 and for 10 and 40; Welch loses up to 4.6 points of power |
| FIG_06 | assets/fig-06-pre-testing-choosing-a-statistical-test.png | plot | Q1: simulated rates of four procedures with MCSE, and the pre-test's rejection rate | — | — | fig-06-pre-testing-choosing-a-statistical-test.png | Type I error of always-Student, always-Welch, Levene-decides and the full pre-testing habit by SD ratio, with Levene's power |
| FIG_07 | assets/fig-07-tea-tasting-choosing-a-statistical-test.png | plot | Q4: an exact distribution beside its 2 × 2 table | — | — | fig-07-tea-tasting-choosing-a-statistical-test.png | The tea-tasting design's null distribution: 1, 16, 36, 16 and 1 of 70 ways to pick 0 to 4 milk-first cups; P(all right) = 1/70 |
| FIG_08 | assets/fig-08-eight-tests-one-table-choosing-a-statistical-test.png | plot | Q4: eight p-values to scale on one axis, beside the table | — | — | fig-08-eight-tests-one-table-choosing-a-statistical-test.png | The malocclusion table and its eight p-values, from 0.112 (mid-p) and 0.122 (Pearson) to 0.286 (Yates) and 0.287 (doubled Fisher) |
| FIG_09 | assets/fig-09-exact-size-of-2x2-tests-choosing-a-statistical-test.png | plot | Q1: exact sums over every table, as curves in π for two designs | — | — | fig-09-exact-size-of-2x2-tests-choosing-a-statistical-test.png | Exact size of five 2 × 2 tests against π for groups of 20 and 22 and of 10 and 40; Pearson reaches 9.1% in the second |
| FIG_10 | assets/fig-10-anova-as-a-ratio-choosing-a-statistical-test.png | plot | Q1: the 30 real weights by group, with the two mean squares | — | — | fig-10-anova-as-a-ratio-choosing-a-statistical-test.png | PlantGrowth's 30 dried weights in three groups with their means and the grand mean; between mean square 1.883, within 0.389, F 4.85 |
| FIG_11 | assets/fig-11-anova-type-i-error-choosing-a-statistical-test.png | plot | Q1: simulated rates with ±2 MCSE in four designs | — | — | fig-11-anova-type-i-error-choosing-a-statistical-test.png | Type I error of F, Welch's W and Brown–Forsythe's F* in four three-group designs; F reaches 16.1% under negative pairing |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0, pandas 3.1.0; `all --quick` takes
about 30 s, `all` about 61 s, 0.21 GB of RAM).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/choosing-a-statistical-test/README.md` | grade, provenance, setup, run order, the E1–E4 exercises with answers, cleanup |
| LAB_02 | `lab/choosing.py` | `labs/choosing-a-statistical-test/choosing.py` | the five stages of the lab |
| LAB_03 | `lab/data/student1908_sleep.csv` | `labs/choosing-a-statistical-test/data/student1908_sleep.csv` | Student's ten patients on two drugs (public domain), with provenance |
| LAB_04 | `lab/data/plant_growth.csv` | `labs/choosing-a-statistical-test/data/plant_growth.csv` | R's PlantGrowth (part of R, GPL-2 or GPL-3), with provenance |
| LAB_05 | `lab/requirements.txt` | `labs/choosing-a-statistical-test/requirements.txt` | the pinned NumPy, SciPy, statsmodels and pandas versions |
| LAB_06 | `lab/captures.json` | `labs/choosing-a-statistical-test/captures.json` | the author's full run with the private R cross-check; every figure and card reads it |
| LAB_07 | `lab/captures-quick.json` | `labs/choosing-a-statistical-test/captures-quick.json` | the author's `--quick` run |
| LAB_08 | `lab/expected-output.txt` | `labs/choosing-a-statistical-test/expected-output.txt` | the full run as printed |
| LAB_09 | `lab/notebook.ipynb` | `labs/choosing-a-statistical-test/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-choosing-a-statistical-test.zip` | `lab-choosing-a-statistical-test.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the two CSV keys so the zip and the individual files agree. Upload with an accurate
`Content-Type` (`text/markdown`, `text/x-python`, `text/csv`, `text/plain`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

The sleep CSV is Part 2's file with one added first line saying so, byte-identical after it. The PlantGrowth CSV is
R 4.5.2's `datasets::PlantGrowth` exported unchanged; R's datasets package is part of R (GPL-2 or GPL-3), and the CSV
header names the package, its licence and Dobson's 1983 book, which the help page gives as the source.

## Series links to add

Earlier parts are named by title in plain text; add the link once the target is live.

| Post | Status on 2026-11-01 | Where it is named |
|---|---|---|
| Part 5, *p-Values and Power: How Wrong Can a Significant Result Be?* (`hypothesis-testing-p-values-power`) | built, not live | **The problem**, first paragraph: "The fifth part of this series, *p-Values and Power: How Wrong Can a Significant Result Be?*, defined that promise" |
| Part 2, *The Sampling Distribution: The CLT and Where n = 30 Fails* (`sampling-distribution-central-limit-theorem`) | built, not live | **Worked example**, first paragraph: "The second part of this series, *The Sampling Distribution: The CLT and Where n = 30 Fails*, used the same ten patients" |

Later parts are "a later part of this series" (what the rank test tests) and "later in this series" (the t-test and
ANOVA as regressions), with no number or title, as the plan's hand-offs to Parts 10 and 13 allow.

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. The first renders had defects in nine of the eleven figures,
  none caught by a gate: a label across a y-axis (Figure 1), a label crossed by a reference line (Figures 2 and 10),
  half-clipped simulation dots at the plot edge and a value label with no marker (Figure 4), a legend entry whose
  curve was invisible because it coincides with another, then a note placed across the y-axis (Figure 5), two labels
  crossed by curves (Figure 6), a value printed above its own label (Figure 7), a swatch lighter than its marks
  (Figure 8), and a notes block and a "5%" label sitting on a curve, with a legend claim ("Yates = doubled Fisher")
  true in only one of the two panels (Figure 9). Figure 3 was first laid out left to right at 3.4:1, too wide to read
  in the article column; it was re-laid top to bottom.
- Figure 9 also exposed a wrong claim in the draft: with groups of 10 and 40, Boschloo's size falls below Fisher's at
  small π, so Boschloo's region does not contain Irwin's-rule Fisher's there. SciPy's two-sided Boschloo doubles the
  smaller one-sided p, which guarantees containment only of the doubled-tail Fisher test. The lab now checks both
  designs (`unbalanced_nested`: 4 tables Fisher rejects and Boschloo does not), and the article states the
  containment for the 20-and-22 design only.
- Cards were checked the same way: an unfinished label (card 1), a takeaway that named the wrong variance (card 2:
  pairing removes 2 Cov = 5.697, not 7.21; the article's first key takeaway had the same slip and was fixed),
  a headline that reused "pairing" in a second sense (card 3), and a closing card that dropped the designs its
  numbers depend on (card 8). `render_social.py --check` passes all 8 cards.
- `_overlap.py` on the final renders: 0 reports on the ten plot figures; 1 on the cover (its two serif title lines);
  2 per card (each card's serif title lines and the lockup's `.in`), all documented false positives. Figure 3's 76
  reports are Mermaid's edge labels, which sit in transformed groups that the checker reads at one local origin;
  the rendered PNG has no overlapping labels.
- `lint_visuals.py`: 0 text overflows on all 12 files; 11 arrow reports, all on Figure 3, where Mermaid draws
  nodes the linter does not recognise; every arrow lands on a node edge in the render.
- `_figs.py`, `_cover.py` and `_social.py` assert the article's numbers against `captures.json` before drawing;
  every number printed on a figure or card is computed from the capture.
- A script matched every number in the prose to the capture; the ones it could not match were checked by hand
  (the fault run's p = 0.000007, Yates's P(a = 4) = 0.1253, the untransposed Boschloo call, the E1 and E3
  arithmetic, the 451 tables).
- The Implementation snippet was extracted from `blog.md` and run as printed: paired t 4.0621, p 0.002833;
  `ttest_ind` 0.079187 and 0.079394; 0.2857, 0.1224, 0.1745, 0.1747 for the 2 × 2 tests.

## Owner actions

- Upload the PNGs, the nine lab files and the zip, then fill `urls.txt` and run `fill_urls.py`.
- The `data-science` category is still missing from the live database (a production write at publish time; Parts
  1 to 7 need it too).
- Part 5 must go live before this part: this part's **Assumes** line names it. Part 2, named once, can be linked once
  it is live.
