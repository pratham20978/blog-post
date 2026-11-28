# Asset manifest — mcmc-diagnostics-metropolis-nuts

Series `statistics-for-data-scientists`, part 12. **Status: local draft assets ready for upload.** Upload the fourteen
PNGs and the nine lab files to the public `media` bucket under the object keys below, write the resulting URLs to
`urls.txt` in table order (COVER, FIG_01–FIG_13, then LAB_01–LAB_09), then run `fill_urls.py`. Upload the lab zip
separately, to the bucket root (see **Lab files**). Nothing has been published, so every key is new; the names carry
the slug because the bucket is flat. If a figure is ever re-rendered, keep its exact file name and purge its URL in
Cloudflare after the upload, since `media/` is served immutable.

Every figure is our own analysis. Twelve are drawn from the lab's `captures.json` by `assets/_figs.py`, which asserts the
numbers the article quotes before it draws; Figure 9 is laid out by Mermaid from `assets/fig-09-…mmd`, which
`assets/_fig09.py` writes from the same capture; the cover is built by `assets/_cover.py`. The `source` route was
considered first for three paper figures that would serve a section (ledger, **Figure candidates**): Vehtari et al.'s
Figure 2 and Figures 21 and 25, and Roy's Figure 12. Their reuse rights are not verified (Crossref lists no licence;
the arXiv copies carry arXiv's non-exclusive distribution licence), so Figures 10, 11 and 12 compute our own cases.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-mcmc-diagnostics-metropolis-nuts.png | placed | template cover in the series house layout, built by `_cover.py`: Figure 2 reduced to its argument, four chains settling into the exact central 95% band in tangerine (the one use); no external generator | — | — | cover-mcmc-diagnostics-metropolis-nuts.png | Four Metropolis chains started far apart settle into the band holding the central 95% of a vaccine trial's posterior |
| FIG_01 | assets/fig-01-one-metropolis-step-mcmc-diagnostics-metropolis-nuts.png | plot | Q4: the eight iterations of Table 1 drawn on the posterior density, with the chain's trace beside them | — | — | fig-01-one-metropolis-step-mcmc-diagnostics-metropolis-nuts.png | Left: eight Metropolis proposals drawn on the beta(8.700102, 163) density, two accepted and six rejected. Right: the chain's state over the eight iterations, flat while proposals are rejected |
| FIG_02 | assets/fig-02-four-chains-to-the-posterior-mcmc-diagnostics-metropolis-nuts.png | plot | Q1: measured warmup traces from four starts, and 20,000 kept draws against the closed-form density | — | — | fig-02-four-chains-to-the-posterior-mcmc-diagnostics-metropolis-nuts.png | Left: four chains from starting values 0.005 to 0.4 enter the exact central 95% band within 26 iterations. Right: a histogram of 20,000 kept draws of efficacy against the exact density, with the exact and estimated 95% limits |
| FIG_03 | assets/fig-03-running-means-dependence-mcmc-diagnostics-metropolis-nuts.png | plot | Q1: measured running means of one chain and of independent exact draws, with bands from τ | — | — | fig-03-running-means-dependence-mcmc-diagnostics-metropolis-nuts.png | Running mean of efficacy for one Metropolis chain and for independent exact draws, with 95% bands that are 2.25 times wider for the chain |
| FIG_04 | assets/fig-04-step-size-traces-mcmc-diagnostics-metropolis-nuts.png | plot | Q1: three measured traces at three proposal steps, with their acceptance and ESS | — | — | fig-04-step-size-traces-mcmc-diagnostics-metropolis-nuts.png | Traces of one chain at proposal steps 0.002, 0.04 and 1.0, with acceptance rates of 95.7%, 41.0% and 2.6% |
| FIG_05 | assets/fig-05-efficiency-against-acceptance-mcmc-diagnostics-metropolis-nuts.png | plot | Q1: a measured sweep of ESS per draw against acceptance over 25 scales, in one and two dimensions | — | — | fig-05-efficiency-against-acceptance-mcmc-diagnostics-metropolis-nuts.png | Effective sample size per draw against acceptance rate over 25 proposal scales, peaking at 42% acceptance in one dimension and at 31% in two |
| FIG_06 | assets/fig-06-accidents-posterior-grid-mcmc-diagnostics-metropolis-nuts.png | plot | Q1: warmup paths, kept draws and marginals against the 801 × 801 grid's regions | — | — | fig-06-accidents-posterior-grid-mcmc-diagnostics-metropolis-nuts.png | Left: warmup paths of four chains from the corners of a wide box into the posterior. Right: kept draws of mean and shape inside the grid posterior's 50%, 90% and 99% regions, with marginal densities from grid and chain |
| FIG_07 | assets/fig-07-autocorrelation-and-tau-mcmc-diagnostics-metropolis-nuts.png | plot | Q1: measured autocorrelation functions at three steps, with Geyer's stopping lag | — | — | fig-07-autocorrelation-and-tau-mcmc-diagnostics-metropolis-nuts.png | Autocorrelation against lag for proposal steps 0.002, 0.04 and 1.0, with integrated autocorrelation times of 430.6, 5.50 and 67.7 |
| FIG_08 | assets/fig-08-mcse-coverage-mcmc-diagnostics-metropolis-nuts.png | plot | Q1: measured coverage of three standard errors over 2,000 runs per step, with MCSE bars | — | — | fig-08-mcse-coverage-mcmc-diagnostics-metropolis-nuts.png | Coverage of the exact posterior mean by estimate plus or minus 1.96 standard errors: 30% to 65% with the naive standard error, 93% to 95% with the ESS-based one, and 86% to 91% for the 2.5% quantile's MCSE |
| FIG_09 | assets/fig-09-how-rhat-and-ess-are-computed-mcmc-diagnostics-metropolis-nuts.png | mermaid | Q3: 12 nodes and four parallel paths from the draws to R-hat, bulk ESS, tail ESS and the MCSE; generated by `_fig09.py` from the captures, rendered by `_mermaid.py` | — | — | fig-09-how-rhat-and-ess-are-computed-mcmc-diagnostics-metropolis-nuts.png | Flow from the draws to split half-chains, then to normal scores, folded scores, tail indicators and raw values, ending in bulk and folded R-hat, the reported R-hat, bulk ESS, tail ESS and the MCSE of the mean |
| FIG_10 | assets/fig-10-what-each-rhat-sees-mcmc-diagnostics-metropolis-nuts.png | plot | Q4: a grid of real values, four R-hat versions against four failures, shaded by threshold | — | — | fig-10-what-each-rhat-sees-mcmc-diagnostics-metropolis-nuts.png | A grid of four R-hat versions against four failures: a shared trend caught by split and rank-normalised R-hat, a shifted chain caught by all but the folded version, a narrow chain caught only by folded R-hat, and an unvisited mode caught by none |
| FIG_11 | assets/fig-11-rhat-thresholds-mcmc-diagnostics-metropolis-nuts.png | plot | Q1: measured median R-hat against shift and against spread, reproducing a published appendix with its crossings | — | — | fig-11-rhat-thresholds-mcmc-diagnostics-metropolis-nuts.png | Median split R-hat against the shift of one chain, crossing 1.01 at 0.31 SD and 1.1 at 0.99 SD, and median folded R-hat against the spread of one chain, crossing 1.01 at 0.76 and 1.1 at 0.36 |
| FIG_12 | assets/fig-12-the-mode-no-chain-visited-mcmc-diagnostics-metropolis-nuts.png | plot | Q1: three runs' measured histograms against the exact bimodal density, with their diagnostics | — | — | fig-12-the-mode-no-chain-visited-mcmc-diagnostics-metropolis-nuts.png | Three runs on a bimodal posterior against its exact density: chains started in one mode see only that mode; chains started in both see both in the wrong proportions; long proposals find both in the right proportions |
| FIG_13 | assets/fig-13-nuts-rank-plots-mcmc-diagnostics-metropolis-nuts.png | plot | Q1: measured rank histograms for NUTS and for stuck chains, and ESS per draw for both samplers | — | — | fig-13-nuts-rank-plots-mcmc-diagnostics-metropolis-nuts.png | Rank histograms for four NUTS chains, all near uniform, and for the stuck bimodal chains, two piled at low ranks and two at high; and bulk ESS per draw for Metropolis and NUTS |

## Lab files

**Lab grade:** G1 · runs anywhere (NumPy 2.5.4, SciPy 1.18.1, PyMC 6.4.0, PyTensor 3.3.8, ArviZ 1.3.0; `all --quick`
takes about 23 s and `all` about 2 min 25 s, 0.48 GB of RAM at most; the install is about 440 MB).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/mcmc-diagnostics-metropolis-nuts/README.md` | grade, provenance, setup, run order, the E1–E5 exercises with answers, cleanup |
| LAB_02 | `lab/mcmc.py` | `labs/mcmc-diagnostics-metropolis-nuts/mcmc.py` | the eight stages of the lab |
| LAB_03 | `lab/data/greenwood_yule1920_accidents.csv` | `labs/mcmc-diagnostics-metropolis-nuts/data/greenwood_yule1920_accidents.csv` | Greenwood and Yule's 647 women by number of accidents, with provenance (Part 1's file plus one line) |
| LAB_04 | `lab/data/clarke1946_flying_bombs.csv` | `labs/mcmc-diagnostics-metropolis-nuts/data/clarke1946_flying_bombs.csv` | Clarke's 576 squares by flying-bomb hits, for E5, with provenance (Part 1's file plus one line) |
| LAB_05 | `lab/requirements.txt` | `labs/mcmc-diagnostics-metropolis-nuts/requirements.txt` | the pinned dependencies |
| LAB_06 | `lab/captures.json` | `labs/mcmc-diagnostics-metropolis-nuts/captures.json` | the author's full run with the private R cross-check; every figure and card reads it |
| LAB_07 | `lab/captures-quick.json` | `labs/mcmc-diagnostics-metropolis-nuts/captures-quick.json` | the author's `--quick` run |
| LAB_08 | `lab/expected-output.txt` | `labs/mcmc-diagnostics-metropolis-nuts/expected-output.txt` | the full run as printed |
| LAB_09 | `lab/notebook.ipynb` | `labs/mcmc-diagnostics-metropolis-nuts/notebook.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-mcmc-diagnostics-metropolis-nuts.zip` | `lab-mcmc-diagnostics-metropolis-nuts.zip` (bucket root) | every lab file in one zip, with the `data` folder in place; its final URL is already written in `blog.md` |

Keep the `data/` prefix in the two CSV keys so the zip and the individual files agree. Upload with an accurate
`Content-Type` (`text/markdown`, `text/x-python`, `text/csv`, `text/plain`, `application/json`,
`application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

Both CSVs are byte-identical copies of the files in Part 1's lab (*Distributions as Generative Stories: Let the Process
Pick*) under one added `#` line naming that lab, as the series' rule for reused data says.

## Series links to add

Earlier parts are named by title in plain text; add the link once the target is live.

| Post | Status on 2026-11-27 | Where it is named |
|---|---|---|
| Part 11, *Bayesian Inference by Hand: Conjugacy and Credible Intervals* (`bayesian-inference-conjugate-priors`) | built, not live | **The problem**, first paragraph: "The eleventh part of this series, *Bayesian Inference by Hand: Conjugacy and Credible Intervals*, built posteriors in closed form" |
| Part 1, *Distributions as Generative Stories: Let the Process Pick* (`distributions-as-generative-stories`) | built, not live | **The problem**, first paragraph: "the first part of this series, *Distributions as Generative Stories: Let the Process Pick*, explained the extra variance" |
| Part 4, *Likelihood: The MLE, Three Tests, and Where χ² Fails* (`likelihood-mle-fisher-information`) | built, not live | **A posterior with no closed form**, first paragraph: "The fourth part of this series, *Likelihood: The MLE, Three Tests, and Where χ² Fails*, fitted Greenwood and Yule's counts" |

No later part is named by number or title: divergences are "a later part of this series".

## Checks the gate cannot make, and their results

- Every PNG was opened and read after its last render. The first renders had defects in ten of the thirteen figures,
  none caught by a gate: start and band labels crossed by traces (Figure 2) and an off-by-one in how the trace's
  iterations were numbered; a label crossed by both running means and two fills blending into a shade no swatch showed
  (Figure 3); notes running off the canvas (Figures 4, 10, 11, 12); a legend calling the two-dimensional efficiency
  "log mu, log k" when only log μ was measured (Figure 5); a title off the canvas and an ambiguous "N(0, 4)" (Figure 6);
  a note on a curve and a stopping line drawn one lag early (Figure 7); value labels on the 95% line (Figure 8); a
  legend swatch without the outline it names (Figure 10); labels crossed by their curves (Figure 11); clipped
  histograms (Figure 12); and one colour meaning two things (Figure 13). `_overlap.py` then reported 0 issues on all
  thirteen; on the cover it reports only its known false positive, the two serif title lines.
- Figure 2's histogram was checked numerically when it looked taller than the curve: both integrate to 1 (0.99985
  and 0.9995), and the bins fall on both sides of the curve; the impression was autocorrelated Monte Carlo noise.
- Card headlines are claims: card 3's "every move is accepted" became "almost every" (95.5% and 2.2%), card 8's
  "passes a 0.99 SD shift" became "passes shifts up to 0.99 SD", card 2's table had lost its columns to SVG's
  whitespace collapsing, and card 3's longest label ran off the card. The NUTS R-hat for k is printed as the lab printed
  it, 1.0014: the capture stores 1.00145, which a second rounding would turn into 1.0015.
- `lint_visuals.py`: 0 text overflows; its 12 arrow reports are all in Figure 9, where Mermaid draws nodes inside transformed groups the lint cannot resolve; the PNG shows every arrow landing on its node, so they are false positives.
- KaTeX: rendered with the site's own unified, remark-math and rehype-katex: 0 errors in 6 display and 6 inline equations. Equation 6 first measured 917 px against the 686-px column and was split over two aligned lines; all six now fit.
- Alt text: each figure's alt text above is extracted from `blog.md`, so the two cannot drift.
- Numbers: the hand diagnostics equal ArviZ's to the last bit on every quantity, and R's `posterior` 1.8.1 agrees to
  5.0 × 10⁻¹²; the article's code block was run and reproduces Table 2 and the diagnostics exactly.
