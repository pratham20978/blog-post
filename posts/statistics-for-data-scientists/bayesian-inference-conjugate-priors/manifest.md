# Asset manifest — bayesian-inference-conjugate-priors

Series `statistics-for-data-scientists`, part 11. **Status: local draft assets ready for upload.** Upload the twelve
PNGs and the nine lab files to the public `media` bucket under the object keys below, write the resulting URLs to
`urls.txt` in table order (COVER, FIG_01–FIG_11, then LAB_01–LAB_09), then run `fill_urls.py`. Upload the lab zip
separately, to the bucket root (see **Lab files**). Nothing has been published, so every key is new; the names carry
the slug because the bucket is flat.

Every figure is our own analysis, drawn from the lab's `captures.json` by `assets/_figs.py` (the cover by
`assets/_cover.py`), which asserts the numbers the article quotes before it draws. The `source` route was considered
first for the two paper figures that would serve a section (ledger, **Figure candidates**): Senn's Figure 4 (the prior
on θ with alternatives) is CC BY-NC-ND 4.0, which forbids adaptation and commercial use, so Figure 9 draws our own
priors on two scales (F1); BDA3's Figure 2.2 (central against highest-density intervals) comes from an electronic
edition for non-commercial use only, so Figure 5 computes both intervals for the trial's severe-case posterior (F2).

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-bayesian-inference-conjugate-priors.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 2 reduced to its argument, the trial's efficacy posterior with its 95% credible interval in tangerine (the one use); no external generator | — | — | cover-bayesian-inference-conjugate-priors.png | Posterior density of the vaccine trial's efficacy after 8 of 170 cases, its 95% credible interval from 90.3% to 97.6% shaded in orange |
| FIG_01 | assets/fig-01-laplace-paris-baptisms-bayesian-inference-conjugate-priors.png | plot | Q4: a closed-form posterior on a linear and a log scale, the second showing the 10^-42 tail | — | — | fig-01-laplace-paris-baptisms-bayesian-inference-conjugate-priors.png | Posterior density of the chance that a Paris birth is a boy, beta(251,528, 241,946), on a linear and a log scale; at one half the log10 density is −37.66 |
| FIG_02 | assets/fig-02-trial-prior-to-posterior-bayesian-inference-conjugate-priors.png | plot | Q4: the protocol's prior on θ with the efficacy each share implies, and the posterior of VE with the published interval | — | — | fig-02-trial-prior-to-posterior-bayesian-inference-conjugate-priors.png | Left: the trial's beta(0.700102, 1) prior on the vaccine group's share of cases. Right: the posterior density of vaccine efficacy with its 95% credible interval, 90.3% to 97.6% |
| FIG_03 | assets/fig-03-posterior-as-compromise-bayesian-inference-conjugate-priors.png | plot | Q4: prior, scaled likelihood and posterior to scale for 4 and 170 cases | — | — | fig-03-posterior-as-compromise-bayesian-inference-conjugate-priors.png | Prior, scaled likelihood and posterior for the vaccine group's share of cases, with 1 against 3 cases and with 8 against 162 |
| FIG_04 | assets/fig-04-gamma-poisson-normal-normal-bayesian-inference-conjugate-priors.png | plot | Q4: two closed-form conjugate updates, each arm's gamma posterior and a precision-weighted normal update | — | — | fig-04-gamma-poisson-normal-normal-bayesian-inference-conjugate-priors.png | Posteriors of the two trial arms' case rates per 1,000 person-years, and a normal prior from 1745-1770 combined with the 1782 baptisms by precision weights |
| FIG_05 | assets/fig-05-equal-tailed-and-highest-density-bayesian-inference-conjugate-priors.png | plot | Q4: one posterior density with three computed intervals under it, for two endpoints | — | — | fig-05-equal-tailed-and-highest-density-bayesian-inference-conjugate-priors.png | Posterior densities of efficacy for 1 against 3 and 8 against 162 cases, with the equal-tailed interval and two highest-density intervals drawn as bars under each |
| FIG_06 | assets/fig-06-credible-interval-coverage-bayesian-inference-conjugate-priors.png | plot | Q1: exact coverage curves of two intervals against the true efficacy, two sample sizes | — | — | fig-06-credible-interval-coverage-bayesian-inference-conjugate-priors.png | Exact coverage of the trial's 95% credible interval and of the Clopper-Pearson interval against the true efficacy, for 170 cases and for 4 |
| FIG_07 | assets/fig-07-predictive-futility-rule-bayesian-inference-conjugate-priors.png | plot | Q1: two computed predictive distributions and the predictive probability of success at three interim analyses | — | — | fig-07-predictive-futility-rule-bayesian-inference-conjugate-priors.png | Beta-binomial predictive distributions of future vaccine cases after 14 and 15 of 32, and the predictive probability of final success against the cases so far |
| FIG_08 | assets/fig-08-prior-sensitivity-bayesian-inference-conjugate-priors.png | plot | Q1: a computed sweep of the credible interval over prior strength, two prior centres, two endpoints | — | — | fig-08-prior-sensitivity-bayesian-inference-conjugate-priors.png | Credible interval of efficacy against the prior's weight in cases, for priors centred at VE 30% and at VE 0%, for the primary and the severe endpoints |
| FIG_09 | assets/fig-09-flat-depends-on-the-scale-bayesian-inference-conjugate-priors.png | plot | Q4: three priors as densities on two scales, with an improper flat prior marked | — | — | fig-09-flat-depends-on-the-scale-bayesian-inference-conjugate-priors.png | Uniform, Jeffreys and the trial's priors as densities of the vaccine group's share and of its log-odds, with Haldane's improper flat prior on the log-odds |
| FIG_10 | assets/fig-10-lindley-paris-years-bayesian-inference-conjugate-priors.png | plot | Q1: computed p-values against Bayes factors for 14 real years | — | — | fig-10-lindley-paris-years-bayesian-inference-conjugate-priors.png | Exact p-value against the Bayes factor for one half, for each year of Paris baptisms 1771 to 1784; four years reject at 5% while the Bayes factor exceeds 1 |
| FIG_11 | assets/fig-11-bayes-factor-prior-and-n-bayesian-inference-conjugate-priors.png | plot | Q1: computed Bayes factor curves against the prior's concentration and against n | — | — | fig-11-bayes-factor-prior-and-n-bayesian-inference-conjugate-priors.png | Bayes factor for the 1782 baptisms against the concentration of a symmetric beta prior, and against the number of births at a fixed z |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4, SciPy 1.18.1; `all --quick` takes about 7 s, `all` about 10 s, 0.14 GB
of RAM).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/bayesian-inference-conjugate-priors/README.md` | grade, provenance, setup, run order, the E1–E4 exercises with answers, cleanup |
| LAB_02 | `lab/bayes.py` | `labs/bayesian-inference-conjugate-priors/bayes.py` | the six stages of the lab |
| LAB_03 | `lab/data/paris_baptisms_1745_1784.csv` | `labs/bayesian-inference-conjugate-priors/data/paris_baptisms_1745_1784.csv` | Laplace's Paris baptisms by sex (public-domain works), with provenance |
| LAB_04 | `lab/data/bnt162b2_bayesian_rows.csv` | `labs/bayesian-inference-conjugate-priors/data/bnt162b2_bayesian_rows.csv` | the trial's case splits and surveillance times behind its credible intervals, with sources |
| LAB_05 | `lab/requirements.txt` | `labs/bayesian-inference-conjugate-priors/requirements.txt` | the pinned NumPy and SciPy versions |
| LAB_06 | `lab/captures.json` | `labs/bayesian-inference-conjugate-priors/captures.json` | the author's full run with the private R cross-check; every figure and card reads it |
| LAB_07 | `lab/captures-quick.json` | `labs/bayesian-inference-conjugate-priors/captures-quick.json` | the author's `--quick` run |
| LAB_08 | `lab/expected-output.txt` | `labs/bayesian-inference-conjugate-priors/expected-output.txt` | the full run as printed |
| LAB_09 | `lab/notebook.ipynb` | `labs/bayesian-inference-conjugate-priors/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-bayesian-inference-conjugate-priors.zip` | `lab-bayesian-inference-conjugate-priors.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the two CSV keys so the zip and the individual files agree. Upload with an accurate
`Content-Type` (`text/markdown`, `text/x-python`, `text/csv`, `text/plain`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

The Paris CSV holds Laplace's counts as printed in the 1781 memoir, the 1783 memoir's yearly table and the 1820 edition
of the *Théorie analytique* (public-domain works, read in R. J. Pulskamp's translations); its header records that the
1783 table's printed total row does not equal its own columns, whose sums reproduce the 1812 totals. The trial CSV is a
new file (not Part 6's, which lacks the FDA's severe-case credible row): three credible-interval rows and one subgroup
row for E3, with their sources.

## Series links to add

Earlier parts are named by title in plain text; add the link once the target is live.

| Post | Status on 2026-11-25 | Where it is named |
|---|---|---|
| Part 4, *Likelihood: The MLE, Three Tests, and Where χ² Fails* (`likelihood-mle-fisher-information`) | built, not live | **The problem**, first paragraph: "the object the fourth part of this series, *Likelihood: The MLE, Three Tests, and Where χ² Fails*, built" |
| Part 6, *Confidence Intervals: What 95% Means, Measured* (`confidence-intervals-coverage`) | built, not live | **What does a credible interval promise?**, first paragraph: "The sixth part of this series, *Confidence Intervals: What 95% Means, Measured*, measured that promise" |

No later part is named. Posteriors with no closed form are "the subject of the next part of this series", with no
number or title, as the plan's hand-off to Part 12 allows.

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. The first renders had defects in nine of the eleven figures,
  none caught by a gate: y-axis labels printed over panel titles (Figures 1, 2, 4, 10, 11); a fill in Figure 1a that the
  legend called the tail; notes crossed by both dashed lines (Figure 2a) and by the spike they describe (Figure 4b);
  the placebo posterior clipped off the top of Figure 4a; the severe posterior clipped and panel (a)'s values printed
  into panel (b)'s labels (Figure 5); notes on the curves, two shaded regions blending into a colour the legend did not
  show, and colliding boundary labels (Figure 7); marker labels on the bands, blended bands and a vague note (Figure 8);
  overlapping year labels (Figure 10); and two labels on one line (Figure 11a). Figure 2's top tick read 95% at θ =
  0.05, where VE is 94.7%; it now sits at θ = 1/21.
- A capture-rounding trap: the capture stores six significant digits, so a figure title printed beta(8.700100, 163).
  The figures now take the posterior shapes from the prior and the split.
- Reading the prose against the sources changed five statements: the paper's "confidence interval" wording is in its
  Results on efficacy, not its Discussion; Robert's abstract warns about improper priors in tests rather than ruling
  them out; Gelman, Simpson and Betancourt say a prior can *often* only be understood with its likelihood; the E3
  answer's Haldane posterior is beta(0, 5), not beta(0, 6); and R's check covers the intervals, tails, boundaries and
  Bayes factors, not every number.
- Card 8's mono line printed 10⁻⁴² in a fallback font (Geist Mono has no superscript digits); it now reads 1.1461e-42.
- The Implementation snippet was extracted from `blog.md` and run as printed: 1.146058490156627e-42; 0.90317129 and
  0.97616944; 2.456e-28; 0.9904 and 0.9853; POS 0.0311; BF01 8.5968 and p 0.024122.
- The protocol's Table 8 prints an overall probability of success above 0.999 at VE 70%; the exact sequential value is
  0.994, which is also the sum of the table's own success columns. The other 44 printed operating characteristics
  reproduce (ledger, **Open questions**).

## Owner actions

- Upload the PNGs, the nine lab files and the zip, then fill `urls.txt` and run `fill_urls.py`.
- The `data-science` category is still missing from the live database (a production write at publish time; Parts
  1 to 10 need it too).
- Part 4 must go live before this part: this part's **Assumes** line names it. Part 6, also named, can be linked once
  it is live.
