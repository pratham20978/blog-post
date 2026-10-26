# Asset manifest — sampling-distribution-central-limit-theorem

Series `statistics-for-data-scientists`, part 2. **Status: local draft assets ready for upload.** Upload the
eleven PNGs and the ten lab files to the public `media` bucket under the object keys below, write the
resulting URLs to `urls.txt` in table order (COVER, FIG_01–FIG_10, then LAB_01–LAB_10), then run
`fill_urls.py`. Upload the lab zip separately, to the bucket root (see **Lab files**). Nothing has been
published, so every key is new; the names carry the slug because the bucket is flat.

Every figure is our own analysis, drawn from the lab's `captures.json` by `assets/_figs.py` (the cover by
`assets/_cover.py`), which asserts every number the article quotes before it draws. The `source` route was
considered first for every paper-backed figure (ledger, **Figure candidates**): Wilcox and Rousselet's Fig. 1
is CC BY 4.0 and relevant, but Figures 2 and 5 show the same mechanism on this post's own data and the lab
reruns their numbers (F1); Hesterberg's Figs. 21–22 carry only arXiv's licence (F2); Morris et al.'s planning
figure is not needed (F3). No figure is Mermaid: none is a graph of nodes and edges.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-sampling-distribution-central-limit-theorem.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 2's n = 30 panel reduced to its argument, the tangerine used once on the true mean; no external generator | — | — | cover-sampling-distribution-central-limit-theorem.png | Means of 30 customers' spend in standard errors, piled left of the tangerine true-mean line, beside the dashed normal curve |
| FIG_01 | assets/fig-01-population-sampling-distribution-central-limit-theorem.png | chart | Q1: the dataset's own distribution (ledger L01), binned by the lab | — | — | fig-01-population-sampling-distribution-central-limit-theorem.png | Customers' net spend on a log scale: median £658, mean £1,926 far to its right, and a bracket over the top 1% holding 29.7% of spend |
| FIG_02 | assets/fig-02-sampling-distributions-sampling-distribution-central-limit-theorem.png | plot | Q4: small multiples of simulated distributions on one standardised axis against one normal curve | — | — | fig-02-sampling-distributions-sampling-distribution-central-limit-theorem.png | Four histograms of simulated means in standard errors: a spike left of the true mean at n = 10 and 30, near-normal but skewed at n = 1,000 |
| FIG_03 | assets/fig-03-sd-and-se-sampling-distribution-central-limit-theorem.png | plot | Q4: theory lines against simulated quantile bands on log–log axes | — | — | fig-03-sd-and-se-sampling-distribution-central-limit-theorem.png | Log–log plot of σ, σ/√n and the simulated SD of means, with the band of s/√n far below σ/√n for small n |
| FIG_04 | assets/fig-04-t-test-tails-sampling-distribution-central-limit-theorem.png | chart | Q1: rejection rates measured by the lab's simulation, with MCSE bars | — | — | fig-04-t-test-tails-sampling-distribution-central-limit-theorem.png | Rejection rates of a 5% t-test against n: the lower tail falls from 41.6% to 7.9%, the upper rises from 0.03% to 3.0% |
| FIG_05 | assets/fig-05-mean-and-sd-move-together-sampling-distribution-central-limit-theorem.png | plot | Q4: a scatter of 3,000 simulated samples with an analytic rejection boundary | — | — | fig-05-mean-and-sd-move-together-sampling-distribution-central-limit-theorem.png | Scatter of 3,000 samples' mean against SD on log axes: rejected samples cluster at low mean and low SD below a boundary curve |
| FIG_06 | assets/fig-06-student-t-sampling-distribution-central-limit-theorem.png | plot | Q4: published data (ledger L07) beside exact densities and a simulated rate | — | — | fig-06-student-t-sampling-distribution-central-limit-theorem.png | A dot strip of 10 sleep differences with mean 1.58, and t with 9 degrees of freedom against the normal, tails beyond ±1.96 shaded |
| FIG_07 | assets/fig-07-skewness-sets-the-pace-sampling-distribution-central-limit-theorem.png | plot | Q4: simulated rates against a first-order curve, a construction across eight populations | — | — | fig-07-skewness-sets-the-pace-sampling-distribution-central-limit-theorem.png | Lower-tail excess over 5% against skewness over √n for seven populations and the spend, against a dashed first-order line |
| FIG_08 | assets/fig-08-berry-esseen-sampling-distribution-central-limit-theorem.png | plot | Q4: exact distances and bounds on log–log axes (ledger L17, L18) | — | — | fig-08-berry-esseen-sampling-distribution-central-limit-theorem.png | Log–log plot of Kolmogorov distance against n: Berry–Esseen bounds far above the exact distances for the spend and the exponential |
| FIG_09 | assets/fig-09-infinite-variance-sampling-distribution-central-limit-theorem.png | plot | Q4: simulated running means and rates in three small multiples | — | — | fig-09-infinite-variance-sampling-distribution-central-limit-theorem.png | Three panels: Cauchy running means that never settle, Pareto running means creeping to 3, and a Pareto t-test error stuck near 26% |
| FIG_10 | assets/fig-10-monte-carlo-error-sampling-distribution-central-limit-theorem.png | plot | Q4: a distribution of simulated estimates with published values (ledger L15, L16) marked | — | — | fig-10-monte-carlo-error-sampling-distribution-central-limit-theorem.png | Histograms of 500 reruns at R = 5,000 and 125 at R = 20,000 of a lognormal t-test rate, with published 0.111 and 0.116 inside each spread |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4 and SciPy 1.18.1; `all --quick` takes about 100 s, `all` about 210 s).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/sampling-distribution-central-limit-theorem/README.md` | grade, provenance, setup, run order, the E1–E4 exercises with answers, cleanup |
| LAB_02 | `lab/sampling.py` | `labs/sampling-distribution-central-limit-theorem/sampling.py` | the seven stages of the lab |
| LAB_03 | `lab/derive_spend.py` | `labs/sampling-distribution-central-limit-theorem/derive_spend.py` | rebuilds the spend CSV from UCI's archive, checked by SHA-256 |
| LAB_04 | `lab/requirements.txt` | `labs/sampling-distribution-central-limit-theorem/requirements.txt` | the pinned NumPy and SciPy versions |
| LAB_05 | `lab/data/online_retail_customer_spend.csv` | `labs/sampling-distribution-central-limit-theorem/data/online_retail_customer_spend.csv` | the 4,317 customers' net spend, CC BY 4.0, with its provenance header |
| LAB_06 | `lab/data/student1908_sleep.csv` | `labs/sampling-distribution-central-limit-theorem/data/student1908_sleep.csv` | Student's ten patients, public domain |
| LAB_07 | `lab/captures.json` | `labs/sampling-distribution-central-limit-theorem/captures.json` | the author's full run, with the R cross-check; every figure reads it |
| LAB_08 | `lab/captures-quick.json` | `labs/sampling-distribution-central-limit-theorem/captures-quick.json` | the author's `--quick` run |
| LAB_09 | `lab/expected-output.txt` | `labs/sampling-distribution-central-limit-theorem/expected-output.txt` | the full run as printed |
| LAB_10 | `lab/notebook.ipynb` | `labs/sampling-distribution-central-limit-theorem/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-sampling-distribution-central-limit-theorem.zip` | `lab-sampling-distribution-central-limit-theorem.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the two CSV keys so the zip and the individual files agree. Upload with an
accurate `Content-Type` (`text/markdown`, `text/x-python`, `text/plain`, `text/csv`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

The spend CSV is a derived work of UCI's Online Retail dataset (CC BY 4.0); its header carries the
attribution, the licence and the changes made, which is what the licence asks of a redistributed copy.

## Series links to add

Earlier parts are named by title or number in plain text; add the link once the target is live.

| Post | Status on 2026-10-26 | Where it is named |
|---|---|---|
| Part 1, *Distributions as Generative Stories: Let the Process Pick* (`distributions-as-generative-stories`) | built, not live | **The problem**, third paragraph: "met in the first part of this series, *Distributions as Generative Stories: Let the Process Pick*, as the story behind the normal" |
| Part 1 (same post) | built, not live | **How fast does the CLT work?**, second paragraph: "Part 1 supplies six: the normal and the unit-variance t₅ …" |
| Part 1 (same post) | built, not live | **When does the CLT never arrive?**, last paragraph: "and Part 1's log–log trap shows how hard that is to rule out" |

Later parts appear only as "later in this series" (resampling methods, in **Limitations**), with no number or title.

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. Fixed on the way: a label plate cutting a gridline
  (Figure 3) and lines (Figures 7, 8); legend swatches that did not match their marks in outline, size or
  opacity (Figures 2, 3, 4, 5); one colour with two meanings (Figures 1, 7, 9); a mislabelled legend ("the
  excess error" for t₉'s whole 8.16% tail, Figure 6); a label crossing a cutoff line (Figure 6); a label over
  the data it named (Figures 5, 9); collapsed SVG spaces detaching a note from its n (Figure 4); and two false
  or loose claims in notes: "none in the upper tail" (the upper test fires in 0.05% of samples, Figure 5) and
  "underestimates beyond about 0.3" (the lognormal sits below the line; Figure 7 now states the measured
  ratios).
- `_overlap.py`: 0 issues on Figures 1–10. Its one report on the cover is the known false positive for
  consecutive serif title lines.
- `lint_visuals.py`: 0 text overflows, 0 arrow reports.
- `_figs.py` and `_cover.py` assert the article's numbers against `captures.json` before drawing; every number
  printed on a figure is computed from the capture, none is typed.
- The Implementation snippet was run as printed: it reproduces the lab's n = 30 rates digit for digit
  (0.39816 and 0.00047).

## Owner actions

- Upload the PNGs, the ten lab files and the zip, then fill `urls.txt` and run `fill_urls.py`.
- The `data-science` category is still missing from the live database (a production write at publish time;
  Part 1 needs it too).
- Part 1 must go live before this part: this part's **Assumes** line names it.
