# Outline — mcmc-diagnostics-metropolis-nuts

Part 12 of *Statistics for Data Scientists*. Private build artifact. Built end to end on 2026-11-27 from the plan's
Part 12 block (the owner's paste with "build" approves the part; no checkpoint stops, as for Parts 1–11).

- **Title:** *MCMC You Can Trust: Metropolis by Hand, R-hat and ESS* (53 characters; the plan's 69-character title
  was too long for the 60 limit). Keywords in front: MCMC, Metropolis, R-hat, ESS.
- **Tier L4 · advanced.** One sampler, four diagnostics (autocorrelation and ESS, MCSE, rank-normalised split R̂,
  bulk and tail ESS), two failure demonstrations and a production tool; the smallest honest check already needs a page.
- **Answers:** when the posterior has no closed form, how do I draw from it, and how do I know the draws describe it?
- **Corrects:** "R̂ below 1.1 means the chain converged."
- **Assumes:** Part 11 by title (the trial's beta(8.700102, 163)); Part 4 and Part 1 by title for the accidents data.
- **Defers:** divergences and the funnel to a later part of this series; HMC/NUTS internals, Gibbs and variational
  inference to a later series on probabilistic machine learning (no title).
- **Four-point angle:** reconcile (chain against closed form and grid; hand diagnostics against ArviZ and R's
  posterior; Vehtari et al.'s appendix reproduced), condition (stationarity, a step size, a mode some chain visited),
  measure (MCSE coverage, R̂ thresholds on 3,200 runs, the unvisited mode), read the output (PyMC/ArviZ defaults).

## Sections and budget (counted words; References add about 1,000)

| Section | Budget | Job | Figures |
|---|---|---|---|
| Insights + Level + Jump to + notice | 280 | the answer: hand Metropolis matches the closed form; 1.1 lets a chain sit one SD away; no R̂ sees an unvisited mode | |
| Why this matters | 200 | R̂ < 1.1 folklore (43 of 100 papers, 2017); MCSE reported in 3 of 39 MCMC papers (2006) | |
| The problem | 400 | no closed form for the negative binomial posterior; a Markov chain whose stationary distribution is the posterior; the two questions; the claim corrected | |
| Worked example | 950 | Metropolis in four steps on beta(8.700102, 163); first eight iterations as a table; four chains from dispersed starts; estimates ± MCSE against the closed form; P(VE ≤ 30%) | 1, 2 |
| Intuition | 450 | why time spent tracks density (detailed balance, in words); analogy with its break; the price: dependence, τ | 3 |
| How big should the step be? | 650 | traces at three steps; efficiency against acceptance in 1-D and 2-D; 2.4/√d, 0.44 → 0.23, 0.234; adapt then freeze | 4, 5 |
| A posterior with no closed form: Greenwood and Yule's accidents | 650 | NB(μ, k) with log-normal priors; sampler on the log scale (no Jacobian needed); adaptive warmup; 801 × 801 grid check; mode against Part 4's MLE | 6 |
| How many independent draws is a chain worth? | 800 | autocorrelation, τ, ESS by Geyer's initial monotone sequence, worked; MCSE; coverage measured (naive vs ESS-based vs quantile); tail quantiles need many draws | 7, 8 |
| What R̂ compares, and what it cannot see | 950 | B, W, var+, split, rank-normalised, folded, max; bulk and tail ESS; quantile MCSE; matched to ArviZ (0.0) and R; what each variant sees | 9, 10 |
| — Is 1.1 close enough to 1? (H3) | 500 | 1.2 → 1.1 → 1.01; Vats–Knudson R̂ ≈ √(1 + m/ESS); Vehtari appendix reproduced (0.31/0.99 SD shift; 0.76/0.36 scale); 3,200 short runs | 11 |
| The mode no chain visited | 550 | constructed 0.7 N(0,1) + 0.3 N(16,1); one-mode starts pass everything; dispersed starts flag it but weight by chain count; long jumps fix it; separation 12 crosses in 37% | 12 |
| NUTS in PyMC: reading the production diagnostics | 550 | NUTS in one paragraph; PyMC's run: ESS ≈ draws, 0 divergences, 2.68 leapfrog steps per draw; PyMC warnings; ArviZ's 89% and 11/89 tail ESS | 13 |
| The math | 650 | Metropolis–Hastings acceptance, detailed balance, the Jacobian; ESS and τ; split R̂; normal scores; quantile MCSE — each back to the worked numbers | |
| Implementation | 500 | the sampler in 15 lines; diagnostics call; the library table | |
| Limitations and common mistakes | 400 | 1.1; dropped rejections; missing Jacobian; thinning; no MCSE; rare events; one chain; ArviZ summary conventions | |
| Key takeaways | 200 | five claims | |
| Try it yourself | 350 | E1–E3 answerable from the article; the lab carries E4 and E5 | |
| References | ~1,000 | Lab downloads + 30 sources | |

Target about 8,600 counted words (L4: 7,500–10,000).

## Figure plan (13 + cover; every route through the gate in `visual-taxonomy.md`)

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 1 | Worked example | one Metropolis step: uphill proposals always accepted, downhill with probability r, a rejection repeats the current point | plot | Q4: the step drawn on the posterior density with the iteration table's real numbers |
| 2 | Worked example | four chains from dispersed starts forget their starts within the warmup, and the kept draws reproduce the exact VE density | plot | Q1: measured traces and a histogram against a closed form |
| 3 | Intuition | a chain's running mean wanders like an independent mean of S/τ draws | plot | Q1: measured running means with bands from τ |
| 4 | Step size | too small crawls, too large sticks, about right mixes | plot | Q1: three measured traces with acceptance and ESS |
| 5 | Step size | efficiency peaks at mid acceptance, flat between ~25% and ~60%, lower in 2-D | plot | Q1: measured sweep, two targets |
| 6 | Accidents | the chain's draws fill the grid posterior; marginals agree; k skews right | plot | Q1: grid contours, draws and marginals |
| 7 | ESS | autocorrelation decays slower for bad steps; Geyer's rule truncates; τ sets ESS | plot | Q1: measured autocorrelation functions |
| 8 | ESS | naive SE covers 30–65%, ESS-based 93–95%, quantile MCSE 86–91% | plot | Q1: measured coverage with MCSE bars |
| 9 | R̂ | how R̂ (bulk and folded), bulk ESS and tail ESS are computed from the draws | placed | Q5: 8 nodes, no crossings; each edge carries the transform |
| 10 | R̂ | which variant sees a shared trend, a shifted chain, a narrow chain, an unvisited mode | plot | Q4: small multiples of traces with the four R̂ values each |
| 11 | 1.1 vs 1.01 | median R̂ against shift and scale, with both thresholds and the crossings | plot | Q1: measured curves reproducing a published appendix |
| 12 | Unvisited mode | the exact bimodal density against three runs' histograms, with their diagnostics | plot | Q1: measured histograms against a closed form |
| 13 | NUTS | rank plots uniform for NUTS, not for stuck chains; ESS per draw for both samplers | plot | Q1: measured rank histograms |
| cover | — | four traces settling into the posterior | placed | template cover, `_cover.py`, series house layout |

No `source` figure. Vehtari et al. 2021's Figure 2 (R̂ histograms under four scenarios) and Figures 21 and 25
(detection curves) would serve sections 10–11, but their reuse rights are not verified: Crossref lists no licence for
the DOI, and the arXiv copy carries arXiv's non-exclusive distribution licence, which grants no reuse. Figure 11
reproduces the appendix computation on our own budget and adds the crossing points: our analysis, not a redraw.

## Term map

| Term | First section | What | Why here | When it matters |
|---|---|---|---|---|
| Markov chain Monte Carlo (MCMC) | The problem | draws from a Markov chain whose stationary distribution is the posterior | the posterior has no closed form | any posterior you cannot sample directly |
| stationary distribution | The problem | the distribution a chain's state keeps once it has it | it is the target | convergence = reaching it |
| random-walk Metropolis | Worked example | propose a nearby point, accept with probability min(1, r) | the simplest valid sampler | by hand; low dimensions |
| proposal step | Worked example | SD of the normal jump | it sets acceptance and mixing | tuning |
| acceptance rate | Worked example | share of proposals accepted | the tuning signal | 0.44 in 1-D, ~0.23 high-d |
| warmup (burn-in) | Worked example | iterations discarded while the chain forgets its start | starts are arbitrary | always; adapt only here |
| detailed balance | Intuition | flow from a to b equals flow from b to a at the target | why Metropolis targets the posterior | proofs; Hastings's correction |
| autocorrelation, τ | Intuition / ESS | correlation of draws t apart; τ = 1 + 2Σρ | dependence costs information | ESS |
| effective sample size (ESS) | ESS | S/τ, independent draws worth as much | sets the MCSE | every reported number |
| Monte Carlo standard error (MCSE) | ESS | SD of an MCMC estimate over reruns | the digits you can trust | report beside every estimate |
| Geyer's initial monotone sequence | ESS | truncation rule for Σρ | noisy long lags | inside every ESS |
| R̂ (potential scale reduction factor) | R̂ | √(var+/W) | between- vs within-chain disagreement | after every run |
| split R̂ | R̂ | R̂ on half-chains | catches trends | default since BDA3 |
| rank normalisation, normal scores | R̂ | ranks → Φ⁻¹((r − 3/8)/(S + 1/4)) | heavy tails, invariance | default since 2021 |
| folded R̂ | R̂ | R̂ of \|θ − median\| | catches scale differences | part of the max |
| bulk ESS, tail ESS | R̂ | ESS of normal scores; min ESS at 5%/95% indicators | centre vs interval reliability | > 400 each |
| rank plot | NUTS | per-chain histogram of pooled ranks | replaces trace plots | many chains, long runs |
| Jacobian | Accidents / Math | \|dθ/dη\| when sampling a transform | keeps the target unchanged | log, logit scales |
| Hamiltonian Monte Carlo (HMC), NUTS | NUTS | gradient-guided proposals; automatic path length | the production sampler | anything beyond a few parameters |
| leapfrog step, tree depth | NUTS | HMC's integrator step; NUTS's doubling count | cost per draw | efficiency comparisons |
| divergence | NUTS (named only) | a failed HMC trajectory | flagged by PyMC | a later part |

## Series links

- Part 11, *Bayesian Inference by Hand: Conjugacy and Credible Intervals* — the trial's posterior (The problem, Worked example).
- Part 4, *Likelihood: The MLE, Three Tests, and Where χ² Fails* — the negative binomial MLE (Accidents).
- Part 1, *Distributions as Generative Stories: Let the Process Pick* — the accidents data and the gamma-mixture story (Accidents).
