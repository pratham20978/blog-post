---
title: "MCMC You Can Trust: Metropolis by Hand, R-hat and ESS"
slug: mcmc-diagnostics-metropolis-nuts
date: 2026-11-27
updated: 2026-11-27
summary: "A Metropolis sampler written by hand reproduces a vaccine trial's posterior; R-hat, ESS and MCSE, computed by hand, show why R-hat under 1.1 is not convergence."
tags: [data-science, statistics, bayesian-inference, mcmc, metropolis-hastings, convergence-diagnostics, effective-sample-size]
category: data-science
series: statistics-for-data-scientists
series_position: 12
tier: L4
difficulty: advanced
prerequisites: ["Bayesian posteriors and credible intervals", "the likelihood function", "Python with NumPy"]
reading_minutes: 36
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts"
---

![Four Metropolis chains started far apart settle into the band holding the central 95% of a vaccine trial's posterior](COVER)

> [!NOTE]
> **Insights** — Random-walk Metropolis fits in twenty lines and needs nothing but the posterior up to a constant. Run on a vaccine trial's posterior, whose answer is known exactly, 20,000 draws give a 95% credible interval of 90.47% to 97.52% against the exact 90.32% to 97.62%, each end within 3 Monte Carlo standard errors. Dependent draws are worth fewer independent ones: here 4,032 of 20,000, so the naive standard error is 2.2 times too small, and in repeated runs it covered the exact mean 65% of the time, not 95%. R̂ below 1.1 does not mean converged. At 1.1, split R̂ still passes a chain shifted by almost a whole posterior standard deviation; at 1.01, the threshold used since 2021, it catches a shift of a third of one. And no R̂ can see a mode no chain visited: chains started in one mode of a bimodal posterior scored R̂ 1.0006 and an ESS of 4,295 while missing 30% of the probability.

**Level:** advanced · **You need:** Bayesian posteriors and credible intervals; the likelihood function; Python with NumPy · **Time:** ~36 min

**Jump to:** [worked example](#worked-example) · [step size](#how-big-should-the-step-be) · [no closed form](#a-posterior-with-no-closed-form-greenwood-and-yule-s-accidents) · [ESS and MCSE](#how-many-independent-draws-is-a-chain-worth) · [R-hat](#what-r-hat-compares-and-what-it-cannot-see) · [1.1 or 1.01](#is-1-1-close-enough-to-1) · [unvisited mode](#the-mode-no-chain-visited) · [NUTS](#nuts-in-pymc-reading-the-production-diagnostics) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **computed** or **measured** come from its lab: one script, `mcmc.py`, whose sampler and diagnostics are written from scratch and match ArviZ's to the last bit and R's `posterior` package to 5 × 10⁻¹². Every simulated rate prints with its Monte Carlo standard error (MCSE). Published numbers are **quoted**, with their sources.

## Why this matters

A sampler always returns numbers. Whether they describe the posterior is a separate question, and the usual answer is R̂, the primary convergence diagnostic in Stan, JAGS, the BUGS family, PyMC and NIMBLE, <!-- L23 --> read with a rule of thumb: R̂ below 1.1. In a random sample of 100 papers from 2017 citing the diagnostic, 43 used that cutoff. <!-- L25 --> The Monte Carlo error of the reported estimates goes unreported even more often: of 39 papers using Markov chain Monte Carlo in the 2006 volumes of three leading statistics journals, three addressed it. <!-- L28 --> This part writes a sampler by hand, checks it against two posteriors whose answers are known, and measures what each diagnostic promises and where the promise ends.

## The problem

The eleventh part of this series, *Bayesian Inference by Hand: Conjugacy and Credible Intervals*, built posteriors in closed form. Most posteriors have none. Greenwood and Yule's 647 munition workers had 447, 132, 42, 21, 3 and 2 accidents for 0 to 5 over five weeks <!-- L41 -->, and the first part of this series, *Distributions as Generative Stories: Let the Process Pick*, explained the extra variance with a negative binomial of mean μ and shape k. Put priors on μ and k and the posterior is proportional to a product of 647 negative binomial probabilities and two prior densities. Its normalising constant is a two-dimensional integral with no formula, and every posterior summary, a mean, a quantile, a probability, is another such integral.

**Markov chain Monte Carlo** (MCMC) replaces the integrals by averages over draws. It builds a **Markov chain**, a sequence in which each draw depends only on the one before, whose **stationary distribution**, the distribution the chain keeps once it has reached it, is the posterior. Run long enough, the chain's draws describe the posterior, and averages over them estimate posterior expectations. Two questions follow, and the first is the easy one. How do I draw from a posterior known only up to a constant? And how do I know that the draws I have describe it, given that they are dependent and start from a point I chose? This part corrects one answer to the second question: **"R̂ below 1.1 means the chain converged."**

## Worked example

Start where the answer is known. Part 11's trial posterior for the vaccine group's share of cases θ is beta(8.700102, 163): the protocol's beta(0.700102, 1) prior updated by 8 vaccine and 162 placebo cases. <!-- L42 --> Its 95% credible interval for vaccine efficacy, VE = 1 − θ/((1 − θ)r) with r = 2.214/2.222 the ratio of surveillance times, runs from 90.317% to 97.617%, and its mean θ is 0.050670 with standard deviation (SD) 0.016689. A sampler that cannot reproduce those numbers cannot be trusted with a posterior that has no formula.

**Random-walk Metropolis** is the simplest valid sampler. From the current value θ it takes four steps:

1. Draw a **proposal** θ* = θ + ε, with ε normal with mean 0 and SD s, the **proposal step**.
2. Compute the ratio of posterior densities, r = p(θ*)/p(θ). The normalising constant cancels, so only the unnormalised density is needed.
3. Draw u uniform on 0 to 1. If u is below r, move to θ*; otherwise stay at θ.
4. Record the new state, whether it moved or not, and repeat.

An uphill proposal, with r at least 1, is always accepted; a downhill one is accepted with probability r. The algorithm is the one Metropolis, the Rosenbluths and the Tellers published in 1953 for a system of rigid spheres, where a move was accepted with probability min(1, exp(−ΔE/kT)) and a rejected move counted the old configuration again in the average. <!-- L01 --> Their runs were short: 16 steps of burn-in and 48 to 64 more, four to five hours on Los Alamos's MANIAC. <!-- L02 --> Marshall Rosenbluth later recalled that Teller suggested the ensemble average and that he and Arianna Rosenbluth did the work. <!-- L03 --> Hastings generalised it in 1970 to proposals that need not be symmetric. <!-- L04 -->

Table 1 runs it by hand from θ = 0.10 with step 0.04. Figure 1 draws the same eight iterations on the density.

| t | θ | proposal θ* | r = p(θ*)/p(θ) | u | decision |
|---|---|---|---|---|---|
| 1 | 0.1000 | 0.1166 | 0.159 | 0.426 | reject: stay at 0.1000 |
| 2 | 0.1000 | 0.0684 | 14.39 | 0.741 | accept |
| 3 | 0.0684 | 0.0533 | 1.983 | 0.633 | accept |
| 4 | 0.0533 | 0.0890 | 0.102 | 0.511 | reject: stay at 0.0533 |
| 5 | 0.0533 | 0.0174 | 0.075 | 0.138 | reject |
| 6 | 0.0533 | 0.0319 | 0.717 | 0.897 | reject |
| 7 | 0.0533 | 0.1700 | 4.2 × 10⁻⁶ | 0.506 | reject |
| 8 | 0.0533 | 0.0328 | 0.765 | 0.829 | reject |

*Table 1. The first eight iterations of one chain. The state after each iteration is the proposal if accepted and the old θ if not.*

![Left: eight Metropolis proposals drawn on the beta(8.700102, 163) density, two accepted and six rejected. Right: the chain's state over the eight iterations, flat while proposals are rejected](FIG_01)
*Figure 1. Two proposals accepted, six rejected. Every rejection repeats θ, and the repeats are draws.*

Iteration 6 shows the rule at work: the proposal 0.0319 has 72% of the current density, but u = 0.897 exceeds 0.717, so the chain stays. Five rejections in a row leave five copies of 0.0533 in the record, and they belong there: a value the chain is slow to leave is a value of high posterior density.

Now run four chains from points chosen to be far apart, θ = 0.005, 0.03, 0.15 and 0.4, when the posterior holds 95% of its mass between 0.0232 and 0.0880. The first 1,000 iterations of each are the **warmup** (or burn-in), discarded because they still remember where they started; the next 5,000 are kept. The chain from 0.4 enters the posterior's central 95% at iteration 26, the one from 0.15 at iteration 6 (Figure 2a). About 43% of proposals are accepted in each chain.

![Left: four chains from starting values 0.005 to 0.4 enter the exact central 95% band within 26 iterations. Right: a histogram of 20,000 kept draws of efficacy against the exact density, with the exact and estimated 95% limits](FIG_02)
*Figure 2. The chains forget their starts within the warmup, and the kept draws reproduce the exact posterior of efficacy.*

Table 2 compares the 20,000 kept draws with the closed form. Each estimate carries its **Monte Carlo standard error** (MCSE), the standard deviation the estimate would show across reruns of the whole simulation, computed as the next sections derive.

| VE, posterior | chain ± MCSE | exact | z |
|---|---|---|---|
| mean | 94.620% ± 0.029 | 94.610% | +0.34 |
| 2.5% point | 90.474% ± 0.130 | 90.317% | +1.20 |
| median | 94.842% ± 0.031 | 94.836% | +0.17 |
| 97.5% point | 97.519% ± 0.037 | 97.617% | −2.61 |

*Table 2. Twenty thousand draws against the closed form; z is the error in MCSEs.*

Every estimate lies within 3 MCSEs of the truth, the check this lab applies. The interval's ends show how much a 95% interval asks of a chain: the lower end has an MCSE of 0.13 points, so its first decimal is not settled. The MCSE falls as one over the square root of the number of effective draws, and pinning 90.3 to ±0.05 at 95% would take about 27 times as many, roughly 120,000 effective draws at that tail. The posterior also gives P(VE ≤ 30%) = 2.46 × 10⁻²⁸, and the chain's share of draws at or below 30% is 0 of 20,000: a sampler estimates probabilities well only when they are large compared with one over the number of effective draws.

## Intuition

Why does accepting downhill moves with probability r produce draws from the posterior? Picture many chains spread over the parameter space exactly as the posterior. Take two values a and b, with p(b) below p(a). Chains at a propose b as often as chains at b propose a, because the proposal is symmetric. From a, a move to b is accepted with probability p(b)/p(a); from b, a move to a always. The flow from a to b, p(a) × p(b)/p(a), equals the flow from b to a, p(b) × 1. This **detailed balance** means the posterior, once reached, is kept. Hastings's version adds a correction to the ratio for an asymmetric proposal, so the flows still balance. <!-- L04 -->

A useful picture is a hiker in fog who records altitude, not position, each minute, always taking an uphill step and taking a downhill one with probability equal to the ratio of heights. The time spent at each height follows the landscape. The picture breaks where the chain's memory matters: a hiker's next minute depends only on where they stand, but the record of minutes spent near one summit says nothing about a second summit across a deep valley the hiker never crossed. That failure gets its own section below.

The price of the method is dependence. Consecutive draws are close, so 20,000 draws carry less information than 20,000 independent draws. Figure 3 runs one chain's mean of VE beside the mean of as many independent exact draws.

![Running mean of efficacy for one Metropolis chain and for independent exact draws, with 95% bands that are 2.25 times wider for the chain](FIG_03)
*Figure 3. A chain's running mean behaves like an independent mean of a smaller sample.*

The chain's mean wanders further, and its band is the independent band widened by √τ, where τ, here 5.08 for this chain, is the **integrated autocorrelation time**: the factor by which dependence inflates the variance of an average. After 5,000 draws the independent mean is within ±0.05 points of the truth at 95%, the chain's within ±0.12.

## How big should the step be?

The proposal step trades two failures. A tiny step is almost always accepted but moves nowhere; a huge one goes far but is almost always rejected. Figure 4 shows both and the middle.

![Traces of one chain at proposal steps 0.002, 0.04 and 1.0, with acceptance rates of 95.7%, 41.0% and 2.6%](FIG_04)
*Figure 4. Too small crawls, too large sticks. Effective sample size is what both lose.*

Over four chains of 5,000 draws, step 0.002 accepts 95.5% of proposals and yields an effective sample size of 46; step 1.0 accepts 2.2% and yields 296; step 0.04 accepts 42.8% and yields 3,638. The **acceptance rate**, the share of proposals accepted, is the dial practitioners watch because it is visible while the sampler runs. Theory says where to set it. For a normal target, BDA3 puts the most efficient random-walk scale at about 2.4/√d posterior SDs in d dimensions, with acceptance near 0.44 in one dimension falling to about 0.23 beyond five; <!-- L09 --> Roberts, Gelman and Gilks proved 0.234 the asymptotically optimal rate as the dimension grows. <!-- L11 --> Step 0.04 is 2.40 posterior SDs of θ.

![Effective sample size per draw against acceptance rate over 25 proposal scales, peaking at 42% acceptance in one dimension and at 31% in two](FIG_05)
*Figure 5. Efficiency peaks at middling acceptance and is flat near the peak.*

A sweep over 25 scales (Figure 5) measures it on the trial's posterior and on the two-parameter accidents posterior of the next section. In one dimension the best scale tried is 2.47 SDs, with 42.1% acceptance and 0.207 effective draws per draw; in two, measured on log μ, 1.87 SDs, with 31.2% acceptance and 0.135. Both curves are flat near the top: in one dimension efficiency stays within 20% of the best for acceptance between 27% and 51%. A sampler is tuned when its acceptance is in that range, not at a magic number.

Tuning has to stop before the draws are used. A rule that keeps changing the proposal from the chain's own past breaks the Markov property the stationary distribution rests on, so BDA3 adapts during a first phase, freezes the proposal and keeps only the draws from the fixed phase. <!-- L10 --> The next section's sampler does exactly that, and so does PyMC's.

## A posterior with no closed form: Greenwood and Yule's accidents

The fourth part of this series, *Likelihood: The MLE, Three Tests, and Where χ² Fails*, fitted Greenwood and Yule's counts by maximum likelihood: μ̂ = 0.4652, the sample mean, and k̂ = 0.865. Now put weak priors on both, log μ and log k each normal with mean 0 and SD 2. Each prior puts 95% of its mass between 0.0198 and 50.4, a range that rules out nothing the data could say. Because log k = −log(1/k), the same prior describes the dispersion 1/k, so the choice does not depend on which of the two the software calls the dispersion.

The sampler works on (log μ, log k). Positive parameters on the log scale make a normal random walk sensible, and because the priors are stated on those coordinates, the target needs no extra term. Had the prior been stated on k itself, the log-scale sampler would need the **Jacobian**, the factor k by which the density of log k differs from that of k; the math section gives the rule, and the lab's diagnostic exercise is built around forgetting it. Warmup is adaptive: 400 iterations at step 0.1, then twice the BDA3 scale 2.4/√2 times the SDs of the window before, then freeze. The frozen steps are 0.130 for log μ and 0.383 for log k, and the four chains accept 33% to 34% of proposals. They start at the corners of a wide box, log μ at −2 or 1 and log k at −2 or 2, and run 2,000 warmup and 5,000 kept iterations each.

The check is brute force: the same posterior evaluated on an 801 by 801 grid of (log μ, log k) spanning nine or more posterior SDs each way, which leaves 1.7 × 10⁻¹² of the mass on the edges. Figure 6 overlays the two.

![Left: warmup paths of four chains from the corners of a wide box into the posterior. Right: kept draws of mean and shape inside the grid posterior's 50%, 90% and 99% regions, with marginal densities from grid and chain](FIG_06)
*Figure 6. The sampler against a brute-force grid. The shape k is skewed right; μ and k are nearly uncorrelated.*

| quantity | chain ± MCSE | grid | z |
|---|---|---|---|
| mean of μ | 0.46616 ± 0.00064 | 0.46651 | −0.55 |
| 97.5% point of μ | 0.53653 ± 0.00197 | 0.53498 | +0.79 |
| mean of k | 0.91424 ± 0.00432 | 0.90878 | +1.26 |
| 2.5% point of k | 0.58469 ± 0.00507 | 0.59134 | −1.31 |
| median of k | 0.88215 ± 0.00428 | 0.87692 | +1.22 |
| 97.5% point of k | 1.41831 ± 0.01247 | 1.41126 | +0.57 |

*Table 3. Chain against grid for Greenwood and Yule's negative binomial; all eight estimates the lab checks are within 1.4 MCSEs.*

The posterior mode, (0.4657, 0.8666), lies within 0.002 of Part 4's maximum likelihood estimate, (0.4652, 0.8651), as weak priors should leave it. The posterior mean of k, 0.909, is above its mode because k's posterior is skewed right: its 95% interval runs from 0.591 to 1.411, about 0.28 below the mode and 0.54 above, the shape Part 4's profile likelihood showed. The draws' correlation between log μ and log k is +0.013, the orthogonality Part 4 found in the information matrix. Both R̂ values are at most 1.0031 and every effective sample size exceeds 2,500.

## How many independent draws is a chain worth?

The **autocorrelation** at lag t, ρ_t, is the correlation between draws t iterations apart. For the trial chains of the worked example, pooled over eight half-chains, ρ₁ to ρ₇ are 0.644, 0.416, 0.278, 0.190, 0.135, 0.094 and 0.068. The variance of an average of S dependent draws is the independent variance times τ = 1 + 2(ρ₁ + ρ₂ + …), so the **effective sample size** (ESS), the number of independent draws that would give the same variance, is S/τ. The MCSE of a posterior mean is then SD/√ESS.

The sum cannot run over every lag: estimated autocorrelations at long lags are noise, and noise summed over thousands of lags swamps the signal. Geyer's **initial monotone sequence** cuts it. Autocorrelations of a reversible Markov chain, summed in adjacent pairs from lag 0, are positive and decreasing, so the sum stops at the first pair that turns negative and every later pair is held no larger than the one before. <!-- L15 --> For the trial chains the first negative pair falls at lags 14 and 15, which gives τ = 4.961 and ESS = 20,000/4.961 = 4,032. Figure 7 shows how the step changes the picture.

![Autocorrelation against lag for proposal steps 0.002, 0.04 and 1.0, with integrated autocorrelation times of 430.6, 5.50 and 67.7](FIG_07)
*Figure 7. Autocorrelation is what ESS charges for. In separate runs of four chains per step, τ is 5.50 at the good step, 67.7 and 430.6 at the bad ones.*

Vehtari and co-authors combine the autocorrelations of several chains with the between-chain variance, so chains that disagree also lower the ESS, and they cap it at S log₁₀ S. <!-- L15 --> The lab's hand implementation reproduces ArviZ 1.3's ESS, R̂ and MCSE to the last bit on every quantity here, and R's `posterior` package to 5 × 10⁻¹².

Does SD/√ESS deliver what a standard error promises? The lab measures it. It runs 2,000 independent replicates of the trial sampler at each of three steps, four chains of 1,000 kept draws each, all started from exact posterior draws, so any shortfall belongs to the standard error and not to the warmup. Each replicate's mean ± 1.96 standard errors either contains the exact mean or does not (Figure 8).

![Coverage of the exact posterior mean by estimate plus or minus 1.96 standard errors: 30% to 65% with the naive standard error, 93% to 95% with the ESS-based one, and 86% to 91% for the 2.5% quantile's MCSE](FIG_08)
*Figure 8. The naive standard error misleads at every step size; the ESS-based one is close to honest.*

The naive SD/√S ignores the dependence and covers 29.8%, 65.1% and 34.3% at steps 0.008, 0.04 and 0.25. The ESS-based MCSE covers 93.2%, 94.9% and 94.9%, each ± 0.6 points or less; at step 0.04 the median ESS-based standard error, 5.77 × 10⁻⁴, matches the actual run-to-run SD of the estimate, 5.63 × 10⁻⁴, while the naive one is 2.63 × 10⁻⁴. The shortfall at step 0.008 is the ESS's own estimation error: its median ESS is 157, and Vehtari and co-authors ask for more than 400 before an ESS or R̂ is relied on. <!-- L14 --> Quantiles are harder. The MCSE of the 2.5% point of VE, computed by the beta-quantile method below, covers 91.4% at the good step and 86.5% at the slow one, which matches the authors' warning that the method has high variance in extreme tails. <!-- L18 --> Report it, and read it as a lower bound on the error.

## What R-hat compares, and what it cannot see

ESS assumes the chains sample the posterior. R̂, the **potential scale reduction factor** of Gelman and Rubin, asks whether they do, by running several chains from overdispersed starting points and comparing them. <!-- L05 --> For M chains of N draws, W is the average within-chain variance and B/N the variance of the chain means. Their weighted sum var⁺ = (N − 1)/N · W + B/N overestimates the posterior variance while the chains still differ, and W underestimates it while each chain has explored only part of it. R̂ = √(var⁺/W) falls to 1 as they agree.

Three refinements make the modern version, each answering a failure (Figure 9). BDA3 computes R̂ on **split chains**, each chain cut in two, so a trend inside a chain shows as halves that disagree. <!-- L08 --> Vehtari and co-authors then **rank-normalise**: pool all S draws, rank them, and replace each rank r by the normal quantile of (r − 3/8)/(S + 1/4), Blom's offset. <!-- L16 --> The result, the bulk R̂, cannot be dominated by a heavy tail and does not change under a monotone transformation. Finally they **fold**: the same computation on |θ − median|, which turns a difference in spread into a difference in location. The reported R̂ is the larger of the bulk and folded values, and the **bulk ESS** is the ESS of the normal scores. <!-- L16 --> The **tail ESS** is the smaller ESS of the two indicators "θ at or below its 5% point" and "θ at or below its 95% point". <!-- L17 --> The MCSE of a quantile at probability α propagates the 16% and 84% points of a beta(ESS α + 1, ESS (1 − α) + 1) distribution through the sorted draws. <!-- L18 -->

![Flow from the draws to split half-chains, then to normal scores, folded scores, tail indicators and raw values, ending in bulk and folded R-hat, the reported R-hat, bulk ESS, tail ESS and the MCSE of the mean](FIG_09)
*Figure 9. How R-hat, bulk ESS, tail ESS and the MCSE are computed from the same draws, with the worked example's values.*

On the worked example's θ, split into eight half-chains of 2,500, W = 2.5904 × 10⁻⁴ and B = 8.9091 × 10⁻⁴, so var⁺ = 2.5929 × 10⁻⁴ and split R̂ = 1.00049. The bulk and folded values are 1.00035 and 1.00079, so the reported R̂ is 1.00079. The 2.5% point of VE has an indicator ESS of 4,602; the beta quantiles 0.02290 and 0.02751 map through the sorted draws to an MCSE of 0.13 points, the value in Table 2.

Each refinement was added because the previous version missed a failure, and Figure 10 shows which version sees which. Four chains started together at θ = 0.30 with a small step and no warmup drift down together: unsplit R̂ is 0.999 because every chain drifts alike, while split R̂ is 1.73. Two failures built, as in Vehtari and co-authors' appendix, from independent normal draws follow: one chain shifted by half an SD and one with half the others' spread. <!-- L20 --> The shift moves the location-based versions to about 1.03; only the folded R̂ sees the narrow chain, at 1.054.

![A grid of four R-hat versions against four failures: a shared trend caught by split and rank-normalised R-hat, a shifted chain caught by all but the folded version, a narrow chain caught only by folded R-hat, and an unvisited mode caught by none](FIG_10)
*Figure 10. Which R-hat sees which failure. The last column passes everything.*

### Is 1.1 close enough to 1?

Gelman and Rubin read a potential scale reduction near 1 as little to gain from running longer, and Brooks and Gelman showed that the between-chain variance can fall before it rises, so the ratio can dip early. <!-- L06 --> The threshold has moved twice. Brooks and Gelman described 1.2 as sometimes used as a guide; <!-- L07 --> BDA3's authors say they have generally been satisfied with 1.1; <!-- L08 --> Vehtari and co-authors use a sample only below 1.01, having seen R̂ dip under 1.1 well before convergence. <!-- L13 --> The dip is old news: in Brooks and Gelman's own Weibull example the factor fell below 1.1 between iterations 800 and 1,300, before one of five chains found the rest of the parameter space. <!-- L07 --> Vats and Knudson give the arithmetic. For their version of R̂, R̂ ≈ √(1 + m/ESS) for m chains, so 1.1 corresponds to an ESS of about 5m, five effective draws per chain. <!-- L24 --> At 1.01 the same relation gives about 50 per chain, the figure Vehtari and co-authors require of each split chain before R̂ is relied on. <!-- L14 -->

The lab reproduces Vehtari and co-authors' appendix, which built four chains of independent standard normal draws and altered one. <!-- L20 --> <!-- L21 --> Figure 11 gives the median of each R̂ over 400 runs per point.

![Median split R-hat against the shift of one chain, crossing 1.01 at 0.31 SD and 1.1 at 0.99 SD, and median folded R-hat against the spread of one chain, crossing 1.01 at 0.76 and 1.1 at 0.36](FIG_11)
*Figure 11. What 1.1 lets through: a chain shifted by almost a whole SD, or one 0.36 times as wide as the others.*

Split R̂ reaches 1.01 when one chain is shifted by 0.31 SD and 1.1 only at 0.99 SD, with 1,000 or 250 draws per chain alike. Folded R̂ reaches 1.01 when one chain's SD falls to 0.76 of the others' and 1.1 only at 0.36; split R̂ stays at 1.000 however narrow the chain, since it compares locations. The first three crossings match the appendix's third, one and three quarters. For the fourth the appendix gives a quarter, which is what a grid of quarters shows: the folded R̂ is 1.054 at a half and 1.162 at a quarter, and the finer grid places the crossing at 0.36. <!-- L21 -->

What does that leniency cost on a real posterior? The lab ran the trial sampler with a slow step, 0.008, from the dispersed starts, 400 times at each of eight lengths from 25 to 3,200 kept draws per chain, and recorded each run's R̂, ESS and lower efficacy limit. Of the 1,762 runs whose R̂ was below 1.1, 10.6% had the lower limit off by more than a full point, and the worst by 3.96 points. Of the 296 with R̂ below 1.01 and both ESS values above 400, none was off by more than a point; the worst was 0.87, and the root-mean-square error fell from 0.62 to 0.30 points. The modern rule is two conditions, and the ESS half matters as much as the 1.01.

## The mode no chain visited

Every diagnostic so far compares chains with each other or with themselves. None compares them with the posterior. Take a posterior with two modes, here constructed so its exact answer is known: 0.7 N(0, 1) + 0.3 N(16, 1), with mean 4.8 and probability 0.3 above 8. Start four well-tuned chains near 0 with step 2.4 (Figure 12a).

![Three runs on a bimodal posterior against its exact density: chains started in one mode see only that mode; chains started in both see both in the wrong proportions; long proposals find both in the right proportions](FIG_12)
*Figure 12. Perfect diagnostics, 30% of the posterior missing.*

The four chains score R̂ 1.0006, bulk ESS 4,295 and tail ESS 4,994. Every check above passes. Their mean is 0.006 against the exact 4.8, and their probability above 8 is 0, against 0.3: none of 24,000 iterations crossed the valley. Roy's survey records the same failure with a six-modal target, where chains stuck in one mode led R̂ and its multivariate version to declare convergence, and Cowles and Carlin concluded in 1996 that every one of 13 diagnostics can miss the failure it was designed for. <!-- L26 --> <!-- L27 -->

Start two chains near 0 and two near 16 and R̂ jumps to 1.60, and the bulk ESS collapses to 6.7 from 20,000 draws: the multi-chain ESS counts the chains' disagreement, as it was designed to. <!-- L19 --> The diagnostic now sees the problem, but pooling the chains gives the wrong answer in a new way: P(θ > 8) = 0.467, because the pooled draws weight each mode by the number of chains in it, not by its probability. One chain did cross the valley once, late in its run. Stacking, which Yao, Vehtari and Gelman propose for runs that do not mix, estimates those weights instead of trusting the chain count. <!-- L40 --> The fix that works here is in the sampler, not the diagnostic: proposals with SD 16 reach the other mode, accept 12% of the time, cross 926 times, and give P(θ > 8) = 0.301 ± 0.015 with R̂ 1.0036.

The separation was chosen so that no chain crosses. Whether a chain finds a second mode is a matter of valley depth and run length: of 1,000 chains started near 0 with step 2.4 and run 6,000 iterations, 99.7% reached the other mode at a separation of 10, 40.2% at 12, 3.2% at 14 and 0.1% at 16. A posterior with modes a little closer than this one fails intermittently, which is worse, because a rerun can look fine. Multiple chains from widely dispersed starts, knowledge of where the model can have modes, and checks of the fitted model against data are the defences; no within-chain or between-chain statistic replaces them.

## NUTS in PyMC: reading the production diagnostics

Random-walk Metropolis is a teaching sampler. Its efficiency falls with dimension, as about 0.3/d at the optimal scale, <!-- L09 --> and production tools use **Hamiltonian Monte Carlo** (HMC), which steers proposals with the gradient of the log posterior, simulating a trajectory in a series of **leapfrog steps**. The **No-U-Turn Sampler** (NUTS) removes HMC's hardest setting, the trajectory length, by stopping when the trajectory starts to double back, and adapts its step size during warmup by dual averaging. <!-- L30 --> PyMC's `pm.sample` runs it by default: 1,000 tuning steps, 1,000 draws, at least two chains and a target acceptance of 0.8. <!-- L32 --> How NUTS builds its trajectories is outside this series; here it is a tool, read through its output.

The accidents model goes into PyMC <!-- L43 --> with the same priors, as `pm.LogNormal("mu", 0, 2)` and `pm.LogNormal("k", 0, 2)`, and four chains of 1,000 draws. PyMC samples both on the log scale and adds the Jacobian of that transformation itself. <!-- L44 --> Its answer agrees with the grid: every estimate the lab checks is within 1.6 MCSEs. Its diagnostics read as follows.

- **R̂** is 1.0005 for μ and 1.0014 for k, below 1.01.
- **Bulk ESS** is 3,769 and 3,943 of 4,000 draws, close to one effective draw per draw, against 0.138 and 0.128 for Metropolis on the same posterior. Dynamic HMC can even exceed one, because successive draws can be negatively correlated. <!-- L22 -->
- **Tail ESS** is 2,945 and 2,957, so the interval ends are well resolved.
- **Divergences**, which PyMC counts and warns about, are 0; what they signal and how to remove them belong to a later part of this series. <!-- L33 -->
- **Cost**: 2.68 leapfrog steps per draw, each needing a gradient, with tree depths of 1 or 2 and a step size of 1.10. Per leapfrog step NUTS still gets about 0.35 effective draws, against Metropolis's 0.13 per density evaluation.

PyMC warns when any R̂ exceeds 1.01 or the ESS per chain falls below 100, the 2021 thresholds. <!-- L33 --> Rank plots replace trace plots for many chains (Figure 13): each chain's draws are ranked among all chains and histogrammed, and chains that sample the same distribution give flat histograms. <!-- L12 -->

![Rank histograms for four NUTS chains, all near uniform, and for the stuck bimodal chains, two piled at low ranks and two at high; and bulk ESS per draw for Metropolis and NUTS](FIG_13)
*Figure 13. Rank plots show what R-hat summarises: NUTS's four chains agree; the stuck chains do not.*

## The math

| Symbol | Meaning |
|---|---|
| p(θ) | the posterior density up to a constant; the target |
| q(θ* ∣ θ) | the proposal density; s its SD for a random walk |
| M, N, S | chains, draws per chain, S = MN |
| W, B | mean within-chain variance; N times the variance of chain means |
| ρ_t, τ | autocorrelation at lag t; integrated autocorrelation time |

**Metropolis–Hastings acceptance**, for a proposal θ* from q(θ* ∣ θ):

$$
\alpha(\theta, \theta^*) = \min\!\left(1,\ \frac{p(\theta^*)\, q(\theta \mid \theta^*)}{p(\theta)\, q(\theta^* \mid \theta)}\right) \tag{1}
$$

For a symmetric random walk the q terms cancel and α = min(1, r), the rule of Table 1. Equation (1) makes p(θ)q(θ* ∣ θ)α(θ, θ*) symmetric in θ and θ*, which is detailed balance, so p is stationary. <!-- L04 -->

**Sampling a transformed parameter.** If the chain runs on η = g(θ), the target in η must include the Jacobian:

$$
p_\eta(\eta) = p\big(g^{-1}(\eta)\big)\,\left\lvert \frac{d\theta}{d\eta} \right\rvert \tag{2}
$$

For η = logit θ the factor is θ(1 − θ), and dropping it samples beta(7.700102, 162) instead of beta(8.700102, 163): in the lab's diagnostic exercise, on its quick budget, the mean of VE moves by 13 MCSEs while R̂ stays at 1.0035.

**Effective sample size** with Geyer's truncation, for the pooled autocorrelation estimates ρ̂_t:

$$
\mathrm{ESS} = \frac{S}{\hat\tau}, \qquad \hat\tau = 1 + 2\sum_{t=1}^{T} \hat\rho_t \tag{3}
$$

where T is the lag at which the first pair ρ̂_{2k} + ρ̂_{2k+1} turns negative, the pairs before it held non-increasing; Vehtari and co-authors also count the next even lag once. <!-- L15 --> For the worked example, τ̂ = 4.961 and ESS = 4,032 of 20,000, and the MCSE of the mean of θ is its SD divided by √4,032.

**Split R̂**, computed on the 2M half-chains of length n = N/2:

$$
\hat R = \sqrt{\frac{\frac{n-1}{n} W + \frac{1}{n} B}{W}} \tag{4}
$$

With n = 2,500, W = 2.5904 × 10⁻⁴ and B = 8.9091 × 10⁻⁴ it gives 1.00049. The rank-normalised versions apply (4) to normal scores:

$$
z = \Phi^{-1}\!\left(\frac{r - 3/8}{S + 1/4}\right) \tag{5}
$$

where r is a draw's rank among all S draws (Blom's offset). <!-- L16 --> Applied to the draws it gives the bulk R̂, applied to their distances from the median it gives the folded R̂, and the reported R̂ is the larger.

**MCSE of a quantile** at probability α, from the ESS of the indicator I(θ ≤ θ̂_α):

$$
\begin{aligned}
a, b &= F^{-1}_{\mathrm{Beta}(\mathrm{ESS}\,\alpha + 1,\ \mathrm{ESS}\,(1 - \alpha) + 1)}(0.1587,\ 0.8413) \\
\mathrm{MCSE} &= \tfrac{1}{2}\big(\theta_{(\lceil bS \rceil)} - \theta_{(\lfloor aS \rfloor)}\big)
\end{aligned} \tag{6}
$$

the sorted draws θ₍ᵢ₎ standing in for the unknown quantile function. <!-- L18 --> For the 2.5% point of VE, ESS 4,602 gives a = 0.02290, b = 0.02751 and an MCSE of 0.0013, 0.13 points.

## Implementation

The worked example in NumPy, with ArviZ's diagnostics. Run as printed, it reproduces the lab's draws and every number in Table 2.

```python
import numpy as np
import arviz_stats as azs

a, b, r = 0.700102 + 8, 1 + 162, 2.214 / 2.222            # Part 11's posterior for theta; surveillance-time ratio


def log_post(theta):                                       # log beta(a, b) density up to a constant
    with np.errstate(divide="ignore", invalid="ignore"):
        lp = (a - 1) * np.log(theta) + (b - 1) * np.log1p(-theta)
    return np.where((theta > 0) & (theta < 1), lp, -np.inf)   # zero density outside (0, 1)


rng = np.random.default_rng(np.random.SeedSequence([0, 0, 20261127]))
x = np.array([0.005, 0.03, 0.15, 0.40])                   # four chains, overdispersed starts
lp = log_post(x)
draws = np.empty((4, 6000))
for t in range(6000):
    prop = x + 0.04 * rng.standard_normal(4)              # symmetric random-walk proposal
    lp_prop = log_post(prop)
    accept = np.log(rng.random(4)) < lp_prop - lp          # accept with probability min(1, r)
    x, lp = np.where(accept, prop, x), np.where(accept, lp_prop, lp)
    draws[:, t] = x                                        # a rejection records the current state again
ve = 1 - draws[:, 1000:] / ((1 - draws[:, 1000:]) * r)    # drop 1,000 warmup draws; efficacy per draw
print("VE 2.5% and 97.5%:", np.quantile(ve, [0.025, 0.975]))
print("R-hat:", azs.rhat(ve), "| bulk ESS:", azs.ess(ve), "| tail ESS:", azs.ess(ve, method="tail", prob=(0.05, 0.95)))
print("MCSE of the 2.5% point:", azs.mcse(ve, method="quantile", prob=0.025))
```

It prints 0.90474 and 0.97519; R̂ 1.00082, bulk ESS 4,242 and tail ESS 4,458; and an MCSE of 0.0013. The line that is easiest to get wrong is the last one inside the loop: a sampler that records only accepted proposals over-represents the regions it leaves quickly, and its draws no longer have the posterior as their distribution. The lab's `mcmc.py` adds the accidents model, the diagnostics by hand, the measured guarantees and PyMC; see [Lab downloads](#lab-downloads).

### Reading the library's output

ArviZ and PyMC encode choices that change the numbers you read. <!-- L34 --> <!-- L31 -->

| Task | ArviZ 1.3 and PyMC 6.4 | Watch for |
|---|---|---|
| R̂ | `azs.rhat(x)`: rank-normalised split R̂, the larger of bulk and folded | `method="split"` is BDA3's; `"identity"` is unsplit |
| ESS | `azs.ess(x)`: bulk ESS; `method="mean"` for the MCSE of a mean | `method="tail"` on xarray input defaults to the 11% and 89% quantiles; pass `prob=(0.05, 0.95)` for Vehtari's tail ESS (on a NumPy array, omitting it raises a TypeError <!-- L35 -->) |
| summary | `azs.summary(idata)` | prints an 89% equal-tailed interval and the 11%/89% tail ESS by default |
| quantile MCSE | `azs.mcse(x, method="quantile", prob=0.025)` | the beta-quantile method; optimistic far in the tails |
| negative binomial | `pm.NegativeBinomial(mu=..., alpha=k)` | PyMC's `alpha` is the shape k, variance μ + μ²/k; statsmodels' `alpha` is 1/k |
| sampling | `pm.sample()`: NUTS, 1,000 tune, 1,000 draws, target_accept 0.8 | warns at R̂ above 1.01 and ESS below 100 per chain |

The tail-ESS default is the trap. On the NUTS run ArviZ's summary prints tail ESS 2,637 and 2,532 where the 5% and 95% definition, which R's `posterior` uses, <!-- L36 --> gives 2,945 and 2,957. The lab computes both and they match ArviZ's own functions to the last bit.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** reading R̂ below 1.1 as convergence. At 1.1, split R̂ passes a chain shifted by almost a whole posterior SD (0.99), and folded R̂ passes one only 0.36 times as wide as the others. On the trial's posterior, 10.6% of short runs with R̂ below 1.1 had the lower efficacy limit off by more than a point. Require R̂ below 1.01 and bulk and tail ESS above 400, and report the MCSE of every number you publish.

- **Dropping rejected iterations.** A rejection repeats the current state, and the repeat is a draw; the 1953 paper counted the old configuration again. <!-- L01 --> Keeping only accepted proposals samples the wrong distribution.
- **A missing Jacobian.** Sampling log k or logit θ without the Jacobian targets a different posterior, and every convergence diagnostic stays healthy because the chains agree on the wrong answer. Only a check against something known, a closed form, a grid or simulated data, finds it.
- **One chain.** A single chain cannot show a shifted or stuck chain, and its ESS can be far too high when modes are not mixed. <!-- L19 --> Run at least four from dispersed starts. <!-- L14 --> Geyer argued for one long run instead, <!-- L29 --> but the multi-chain diagnostics above need several.
- **Thinning to save ESS.** Keeping every tenth draw lowers the autocorrelation of what is kept but throws away information, so estimates get less efficient; <!-- L45 --> thin only to save storage.
- **Rare events.** P(VE ≤ 30%) is 2.46 × 10⁻²⁸ and the chain's estimate is 0. An MCMC estimate of a probability is reliable only far above one over the ESS.
- **Trusting a quantile's MCSE in the far tail.** It covered 86% to 91% where 95% was intended.
- **Defaults read as definitions.** ArviZ's summary prints an 89% interval and an 11%/89% tail ESS; PyMC's negative binomial `alpha` is the reciprocal of statsmodels'.

Newer diagnostics address the remaining gaps: nested R̂ for many short chains on parallel hardware, <!-- L37 --> R*, which trains classifiers to tell chains apart across all parameters, <!-- L38 --> and a local R̂ for individual quantiles. <!-- L39 --> All three still compare chains with each other, so none can see a mode that no chain reached.

## Key takeaways

- Random-walk Metropolis needs only the posterior up to a constant. On the trial's beta(8.700102, 163), 20,000 draws reproduced the 95% interval as 90.47% to 97.52% against the exact 90.32% to 97.62%, within 3 MCSEs at both ends.
- Dependent draws are worth S/τ independent ones. Here τ = 4.96 and 20,000 draws were worth 4,032; the naive standard error covered the truth in 65% of runs, the ESS-based one in 94.9%.
- Tune by acceptance, then freeze: efficiency peaked at 42% acceptance in one dimension and stayed within 20% of the peak between 27% and 51%.
- R̂ below 1.1 is not convergence. At 1.1 split R̂ passes a chain almost one SD off and folded R̂ a chain 0.36 times as wide; the current rule is R̂ below 1.01 with bulk and tail ESS above 400.
- No R̂ or ESS can see a mode no chain visited: chains in one mode of a bimodal posterior scored R̂ 1.0006 and ESS 4,295 while missing 30% of the probability.

## Try it yourself

**E1, reproduce.** Verify iteration 6 of Table 1: from θ = 0.0533 the proposal is θ* = 0.0319. Compute r from the beta(8.700102, 163) density without its normalising constant, and decide.

<details><summary>Answer</summary>

**Answer.** log r = 7.700102 × log(0.0319/0.0533) + 162 × log(0.9681/0.9467) = 7.700102 × (−0.5134) + 162 × 0.02235 = −3.953 + 3.621 = −0.332, so r ≈ 0.72 (the lab, with unrounded values, prints 0.717). The draw u = 0.897 exceeds r, so the proposal is rejected and the chain records 0.0533 again.

</details>

**E2, inspect.** The worked example's chains have τ = 4.961 over S = 20,000 kept draws. How many effective draws is that, and by what factor is the naive standard error SD/√S too small?

<details><summary>Answer</summary>

**Answer.** ESS = 20,000/4.961 = 4,032. The MCSE is SD/√ESS = SD/√S × √τ, so the naive standard error is too small by √4.961 = 2.23, which is why it covered the exact mean in only 65.1% of runs at this step.

</details>

**E3, predict.** The lab's `pfizer` stage runs the worked example; on its quick budget (four chains of 1,000 kept draws) step 0.04 accepts 43% of proposals with a bulk ESS of about 810. Before running `python mcmc.py pfizer --quick --step 0.01`, predict the acceptance rate, the bulk ESS and whether R̂ stays below 1.01.

<details><summary>Answer</summary>

**Answer.** A quarter of the step means smaller, more often accepted moves that travel less. The author's run accepts about 81% of proposals, gives a bulk ESS of 294 and an R̂ of 1.021, above 1.01, while every estimate still lies within 3 MCSEs of the closed form. The bulk ESS fell to about a third because each proposal is a quarter the size, so the chain needs more steps to cross the posterior.

</details>

The lab's README has these and two more: a diagnostic exercise in which a "faster" sampler on the log-odds scale passes every convergence check and misses the closed form by 13 MCSEs, and an extension that fits the same model to Clarke's flying-bomb counts, in which the fourth part found no evidence of extra variance, so the data barely constrain k.

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E5 exercises with answers, and cleanup.
- [`mcmc.py`](LAB_02) — the eight stages: pfizer, tuning, nb, diagnostics, mcse, rhat, bimodal and nuts.
- [`greenwood_yule1920_accidents.csv`](LAB_03) — Greenwood and Yule's 647 women by number of accidents, with provenance; put it in a `data` folder.
- [`clarke1946_flying_bombs.csv`](LAB_04) — Clarke's 576 squares of south London by number of flying-bomb hits, for the extension exercise; put it in a `data` folder.
- [`requirements.txt`](LAB_05) — the pinned NumPy, SciPy, PyMC and ArviZ versions.
- [`captures.json`](LAB_06) — the author's full run, machine-readable, with the private cross-check against R.
- [`captures-quick.json`](LAB_07) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_08) — the author's full run as printed.
- [`notebook.ipynb`](LAB_09) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-mcmc-diagnostics-metropolis-nuts.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. N. Metropolis, A. W. Rosenbluth, M. N. Rosenbluth, A. H. Teller and E. Teller. "Equation of state calculations by fast computing machines." *Journal of Chemical Physics* 21(6): 1087–1092, 1953. https://doi.org/10.1063/1.1699114
2. W. K. Hastings. "Monte Carlo sampling methods using Markov chains and their applications." *Biometrika* 57(1): 97–109, 1970. https://doi.org/10.1093/biomet/57.1.97
3. C. P. Robert and G. Casella. "A short history of Markov chain Monte Carlo: subjective recollections from incomplete data." *Statistical Science* 26(1): 102–115, 2011. https://doi.org/10.1214/10-STS351
4. J. E. Gubernatis. "Marshall Rosenbluth and the Metropolis algorithm." *Physics of Plasmas* 12(5): 057303, 2005. https://doi.org/10.1063/1.1887186
5. A. Gelman and D. B. Rubin. "Inference from iterative simulation using multiple sequences." *Statistical Science* 7(4): 457–472, 1992. https://doi.org/10.1214/ss/1177011136
6. C. J. Geyer. "Practical Markov chain Monte Carlo." *Statistical Science* 7(4): 473–483, 1992. https://doi.org/10.1214/ss/1177011137
7. S. P. Brooks and A. Gelman. "General methods for monitoring convergence of iterative simulations." *Journal of Computational and Graphical Statistics* 7(4): 434–455, 1998. https://doi.org/10.1080/10618600.1998.10474787
8. G. O. Roberts, A. Gelman and W. R. Gilks. "Weak convergence and optimal scaling of random walk Metropolis algorithms." *Annals of Applied Probability* 7(1): 110–120, 1997. https://doi.org/10.1214/aoap/1034625254
9. A. Gelman, J. B. Carlin, H. S. Stern, D. B. Dunson, A. Vehtari and D. B. Rubin. *Bayesian Data Analysis*, 3rd edition. CRC Press, 2013. https://doi.org/10.1201/b16018
10. A. Vehtari, A. Gelman, D. Simpson, B. Carpenter and P.-C. Bürkner. "Rank-normalization, folding, and localization: an improved R̂ for assessing convergence of MCMC." *Bayesian Analysis* 16(2): 667–718, 2021. https://doi.org/10.1214/20-BA1221
11. D. Vats and C. Knudson. "Revisiting the Gelman–Rubin diagnostic." *Statistical Science* 36(4): 518–529, 2021. https://doi.org/10.1214/20-STS812
12. V. Roy. "Convergence diagnostics for Markov chain Monte Carlo." *Annual Review of Statistics and Its Application* 7: 387–412, 2020. https://doi.org/10.1146/annurev-statistics-031219-041300
13. M. K. Cowles and B. P. Carlin. "Markov chain Monte Carlo convergence diagnostics: a comparative review." *Journal of the American Statistical Association* 91(434): 883–904, 1996. https://doi.org/10.1080/01621459.1996.10476956
14. J. M. Flegal, M. Haran and G. L. Jones. "Markov chain Monte Carlo: can we trust the third significant figure?" *Statistical Science* 23(2): 250–260, 2008. https://doi.org/10.1214/08-STS257
15. M. D. Hoffman and A. Gelman. "The No-U-Turn Sampler: adaptively setting path lengths in Hamiltonian Monte Carlo." *Journal of Machine Learning Research* 15(47): 1593–1623, 2014. https://jmlr.org/papers/v15/hoffman14a.html
16. C. C. Margossian, M. D. Hoffman, P. Sountsov, L. Riou-Durand, A. Vehtari and A. Gelman. "Nested R̂: assessing the convergence of Markov chain Monte Carlo when running many short chains." *Bayesian Analysis* 20(4): 1587–1614, 2025. https://doi.org/10.1214/24-BA1453
17. B. Lambert and A. Vehtari. "R*: a robust MCMC convergence diagnostic with uncertainty using decision tree classifiers." *Bayesian Analysis* 17(2): 353–379, 2022. https://doi.org/10.1214/20-BA1252
18. T. Moins, J. Arbel, A. Dutfoy and S. Girard. "On the use of a local R̂ to improve MCMC convergence diagnostic." *Bayesian Analysis* 20(1): 131–156, 2025. https://doi.org/10.1214/23-BA1399
19. Y. Yao, A. Vehtari and A. Gelman. "Stacking for non-mixing Bayesian computations: the curse and blessing of multimodal posteriors." *Journal of Machine Learning Research* 23(79): 1–45, 2022. https://jmlr.org/papers/v23/20-1426.html
20. M. Greenwood and G. U. Yule. "An inquiry into the nature of frequency distributions representative of multiple happenings with particular reference to the occurrence of multiple attacks of disease or of repeated accidents." *Journal of the Royal Statistical Society* 83(2): 255–279, 1920. https://doi.org/10.2307/2341080
21. F. P. Polack et al. "Safety and efficacy of the BNT162b2 mRNA Covid-19 vaccine." *New England Journal of Medicine* 383(27): 2603–2615, 2020. https://doi.org/10.1056/NEJMoa2034577
22. O. Abril-Pla et al. "PyMC: a modern, and comprehensive probabilistic programming framework in Python." *PeerJ Computer Science* 9: e1516, 2023. https://doi.org/10.7717/peerj-cs.1516
23. R. Kumar, C. Carroll, A. Hartikainen and O. Martin. "ArviZ a unified library for exploratory analysis of Bayesian models in Python." *Journal of Open Source Software* 4(33): 1143, 2019. https://doi.org/10.21105/joss.01143
24. arviz-stats 1.3.3 and arviz-base 1.3.1 source: `base/diagnostics.py`, `base/dataarray.py`, `summary.py`, `rcparams.py`. https://github.com/arviz-devs/arviz-stats (accessed 2026-11-27)
25. PyMC 6.4.0 source: `distributions/discrete.py`, `sampling/mcmc.py`, `stats/convergence.py`. https://github.com/pymc-devs/pymc (accessed 2026-11-27)
26. posterior 1.8.1 (R package), `ess_tail` and `rhat`. https://cran.r-project.org/package=posterior (accessed 2026-11-27)
