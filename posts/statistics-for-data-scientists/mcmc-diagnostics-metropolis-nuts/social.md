---
social_schema: 2
canonical_url: "https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts"
---

# Social publishing package — mcmc-diagnostics-metropolis-nuts

## LinkedIn post

A sampler always returns numbers. R-hat below 1.1 does not say they are right.

The twelfth part of Statistics for Data Scientists writes MCMC by hand and measures every diagnostic:

→ Random-walk Metropolis in twenty lines, run on a vaccine trial's posterior with a known answer: 20,000 draws give 90.47% to 97.52% against the exact 90.32% to 97.62%.
→ Dependence has a price: those 20,000 draws are worth 4,032 independent ones. The naive standard error covered the truth in 65% of repeated runs; SD/√ESS in 94.9%.
→ At R-hat 1.1, split R-hat still passes a chain shifted by almost a whole posterior SD; 1.01, the threshold since 2021, catches a third of one.
→ Chains started in one mode of a bimodal posterior scored R-hat 1.0006 and an ESS of 4,295, and missed 30% of the probability.
→ NUTS in PyMC, read line by line, including an ArviZ default that changes the tail ESS you see.

Every diagnostic is computed by hand, matched to ArviZ to the last bit, and reproduced by a lab you can rerun.

## LinkedIn first comment

Ask for R-hat below 1.01, bulk and tail ESS above 400, and an MCSE beside every number. Then remember none of them can see a mode no chain visited.

Read the full article on Canery: https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts

## Instagram caption

Can you trust your MCMC? Swipe through Metropolis written by hand, why a rejection is a draw, what tuning buys, why 20,000 draws can be worth 4,032, what R-hat 1.1 lets through, and a posterior that fools every diagnostic.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #bayesian #mcmc #python #pymc

## Shared feed order

1. `assets/social/feed-01-metropolis-by-hand.png` — The four steps of random-walk Metropolis, and its result on the trial's posterior: 20,000 draws give 90.47% to 97.52% against the exact 90.32% to 97.62%
2. `assets/social/feed-02-a-rejection-is-a-draw.png` — The first eight iterations of one chain from θ = 0.10 with step 0.04: two proposals accepted, six rejected, each rejection repeating the current value
3. `assets/social/feed-03-tune-the-step.png` — Three proposal steps on the trial posterior: 0.002 accepts 95.5% with ESS 46, 0.04 accepts 42.8% with ESS 3,638, and 1.0 accepts 2.2% with ESS 296, of 20,000 draws
4. `assets/social/feed-04-20000-draws-worth-4032.png` — Autocorrelation makes 20,000 draws worth 4,032 independent ones; the naive standard error covers the truth in 65.1% of runs, the ESS-based MCSE in 94.9%
5. `assets/social/feed-05-what-1-1-lets-through.png` — Split R-hat reaches 1.1 only when one chain is shifted by 0.99 SD (1.01 at 0.31); folded R-hat reaches 1.1 at an SD ratio of 0.36 (1.01 at 0.76); on 3,200 short runs, 10.6% passing 1.1 were off by more than a point
6. `assets/social/feed-06-the-mode-no-chain-visited.png` — Four chains started in one mode of 0.7 N(0, 1) + 0.3 N(16, 1) score R-hat 1.0006 and bulk ESS 4,295, yet report a mean of 0.006 against 4.8 and P(θ > 8) = 0 against 0.3
7. `assets/social/feed-07-reading-nuts-in-pymc.png` — PyMC's NUTS on the accidents model: R-hat 1.0005 and 1.0014, bulk ESS 3,769 and 3,943 of 4,000, 0 divergences, 2.68 leapfrog steps per draw; tail ESS of μ is 2,637 by ArviZ's default and 2,945 by Vehtari et al.'s definition
8. `assets/social/feed-08-read-the-article.png` — The article's five results in one list, and the call to read it

## Instagram Story

Not produced: this part ships feed cards only, at the owner's request (2026-10-30), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-metropolis-by-hand

- File: `assets/social/feed-01-metropolis-by-hand.png`
- Title: Metropolis, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: The four steps of random-walk Metropolis, and its result on the trial's posterior: 20,000 draws give 90.47% to 97.52% against the exact 90.32% to 97.62%
- Technical source: Worked example; Table 2; Figure 2; ledger L01, L42
- Visual structure: lockup and counter; serif title; deck; a panel with the four-step algorithm, a rule, then the exact interval in tangerine and the chain's interval in blue with its z-scores; takeaway; footer
- Visible-text transcript: Canery.in · random-walk Metropolis, one step: · 1  propose θ* = θ + s·z,  z ~ N(0, 1) · 2  r = p(θ*) / p(θ): the constant cancels · 3  accept if u < r,  u ~ Uniform(0, 1) · 4  record the state, moved or not · Part 11's trial posterior, beta(8.700102, 163) · exact 95% interval · 90.32% – 97.62% · 20,000 draws · 90.47% – 97.52% · z = +1.20 and −2.61 Monte Carlo standard errors · 01 / 08 · Metropolis, · by hand. · Twenty lines of NumPy, run on a vaccine · trial's posterior whose answer is known. · Both ends land within 3 Monte Carlo · standard errors of the closed form. · MCMC YOU CAN TRUST · CANERY.IN
- Alt text: Card: the four steps of random-walk Metropolis; on the trial posterior 20,000 draws give 90.47%–97.52% against the exact 90.32%–97.62%.
- Long description: Random-walk Metropolis in four steps: propose a nearby value, compute the ratio of posterior densities (the normalising constant cancels), accept if a uniform draw is below the ratio, and record the state whether it moved or not. Run on Part 11's trial posterior, beta(8.700102, 163), 20,000 kept draws from four chains give a 95% credible interval for vaccine efficacy of 90.47% to 97.52%, against the exact 90.32% to 97.62%; the two ends are +1.20 and −2.61 Monte Carlo standard errors from the closed form. Takeaway: both ends land within 3 Monte Carlo standard errors.
- Keywords: Metropolis algorithm, MCMC, random walk, Bayesian posterior, credible interval, Monte Carlo standard error
- Canonical URL: https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts

### feed-02-a-rejection-is-a-draw

- File: `assets/social/feed-02-a-rejection-is-a-draw.png`
- Title: A rejection is a draw
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The first eight iterations of one chain from θ = 0.10 with step 0.04: two proposals accepted, six rejected, each rejection repeating the current value
- Technical source: Worked example; Table 1; Figure 1; ledger L01
- Visual structure: lockup and counter; serif title; deck; a table with columns t, θ, θ*, r, u and decision, accepted rows in blue; takeaway; footer
- Visible-text transcript: Canery.in · t · θ · θ* · r · u · decision · 1 · 0.1000 · 0.1166 · 0.159 · 0.426 · stay at θ · 2 · 0.1000 · 0.0684 · 14.4 · 0.741 · accept · 3 · 0.0684 · 0.0533 · 1.98 · 0.633 · accept · 4 · 0.0533 · 0.0890 · 0.102 · 0.511 · stay at θ · 5 · 0.0533 · 0.0174 · 0.075 · 0.138 · stay at θ · 6 · 0.0533 · 0.0319 · 0.717 · 0.897 · stay at θ · 7 · 0.0533 · 0.1700 · 4.2e-6 · 0.506 · stay at θ · 8 · 0.0533 · 0.0328 · 0.765 · 0.829 · stay at θ · 02 / 08 · A rejection · is a draw. · Eight iterations from θ = 0.10 with step 0.04: · two proposals accepted, six rejected. · Five rejections leave five copies of 0.0533 · in the record, and they belong there. · MCMC YOU CAN TRUST · CANERY.IN
- Alt text: Card: eight Metropolis iterations with proposal, density ratio r, uniform u and decision; two accepted, six rejected.
- Long description: A table of the first eight iterations of random-walk Metropolis on the trial posterior, from θ = 0.10 with step 0.04. Iterations 2 and 3 are accepted (r = 14.4 and 1.98, both at least 1). Iterations 1 and 4 to 8 are rejected, including iteration 6, where r = 0.717 but the uniform draw is 0.897; each rejection keeps θ, so 0.0533 is recorded five times. Takeaway: five rejections leave five copies of 0.0533 in the record, and they belong there.
- Keywords: Metropolis algorithm, acceptance ratio, rejection, Markov chain, MCMC by hand
- Canonical URL: https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts

### feed-03-tune-the-step

- File: `assets/social/feed-03-tune-the-step.png`
- Title: Tune the step, not the answer
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Three proposal steps on the trial posterior: 0.002 accepts 95.5% with ESS 46, 0.04 accepts 42.8% with ESS 3,638, and 1.0 accepts 2.2% with ESS 296, of 20,000 draws
- Technical source: How big should the step be?; Figures 4 and 5; ledger L09, L11
- Visual structure: lockup and counter; serif title; deck; a panel with three rows, each a step size with its acceptance rate and a bar proportional to its effective sample size, the good step in tangerine; takeaway; footer
- Visible-text transcript: Canery.in · four chains × 5,000 draws, the trial's posterior · step 0.002: crawls · accepts 95.5% · ESS 46 · step 0.04: mixes · accepts 42.8% · ESS 3,638 · step 1.0: sticks · accepts 2.2% · ESS 296 · 03 / 08 · Tune the step, · not the answer. · Too small and almost every move is accepted · but goes nowhere; too large and almost every · move is refused. · Efficiency peaked at 42% acceptance and stayed · within 20% of it from 27% to 51%. · MCMC YOU CAN TRUST · CANERY.IN
- Alt text: Card: step 0.002 gives ESS 46, step 0.04 ESS 3,638, step 1.0 ESS 296 from 20,000 draws; acceptance 95.5%, 42.8%, 2.2%.
- Long description: Four chains of 5,000 draws on the trial's posterior at three proposal steps. Step 0.002 accepts 95.5% of proposals but crawls, with an effective sample size of 46; step 1.0 accepts 2.2% and sticks, with 296; step 0.04, about 2.4 posterior standard deviations, accepts 42.8% and mixes, with 3,638. Takeaway: efficiency peaked at 42% acceptance and stayed within 20% of the peak for acceptance between 27% and 51%.
- Keywords: proposal scale, acceptance rate, effective sample size, Metropolis tuning, optimal scaling
- Canonical URL: https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts

### feed-04-20000-draws-worth-4032

- File: `assets/social/feed-04-20000-draws-worth-4032.png`
- Title: 20,000 draws, worth 4,032
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Autocorrelation makes 20,000 draws worth 4,032 independent ones; the naive standard error covers the truth in 65.1% of runs, the ESS-based MCSE in 94.9%
- Technical source: How many independent draws is a chain worth?; Figures 7 and 8; ledger L14, L15
- Visual structure: lockup and counter; serif title; deck; a panel with the ESS formula and values, then coverage results for two step sizes, naive in ink and ESS-based in tangerine; takeaway; footer
- Visible-text transcript: Canery.in · τ = 1 + 2 Σ ρ_t = 4.961;  ESS = 20,000 / 4.961 = 4,032 · 2,000 runs: how often estimate ± 1.96 SE covers the truth · step 0.04 · naive SE = SD/√S · 65.1% · MCSE = SD/√ESS · 94.9% · step 0.008, slow · naive SE = SD/√S · 29.8% · MCSE = SD/√ESS · 93.2% · 04 / 08 · 20,000 draws, · worth 4,032. · Consecutive draws are correlated, so they carry · less information than independent ones. · The naive standard error was 2.2 times too · small. Report SD/√ESS beside every estimate. · MCMC YOU CAN TRUST · CANERY.IN
- Alt text: Card: τ = 4.961 so 20,000 draws are worth 4,032; naive SE covers 65.1% and 29.8%, SD/√ESS covers 94.9% and 93.2%.
- Long description: Consecutive Metropolis draws are correlated. The integrated autocorrelation time τ = 1 + 2Σρ_t is 4.961 for the worked example, so the effective sample size is 20,000/4.961 = 4,032. Over 2,000 independent runs per step size, estimate ± 1.96 standard errors covered the exact posterior mean in 65.1% of runs with the naive SD/√S and 94.9% with SD/√ESS at step 0.04, and in 29.8% and 93.2% at the slow step 0.008. Takeaway: the naive standard error was about 2.2 times too small; report SD/√ESS beside every estimate.
- Keywords: effective sample size, autocorrelation, Monte Carlo standard error, MCMC, coverage
- Canonical URL: https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts

### feed-05-what-1-1-lets-through

- File: `assets/social/feed-05-what-1-1-lets-through.png`
- Title: What R-hat 1.1 lets through
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Split R-hat reaches 1.1 only when one chain is shifted by 0.99 SD (1.01 at 0.31); folded R-hat reaches 1.1 at an SD ratio of 0.36 (1.01 at 0.76); on 3,200 short runs, 10.6% passing 1.1 were off by more than a point
- Technical source: Is 1.1 close enough to 1?; Figure 11; ledger L13, L20, L21
- Visual structure: lockup and counter; serif title; deck; a panel with two threshold results from constructed chains, a rule, then two rates from short runs on the trial posterior, the 1.01 rule in tangerine; takeaway; footer
- Visible-text transcript: Canery.in · 4 chains of normal draws, one altered; median of 400 runs · one chain shifted: split R-hat · 0.99 SD · needed to reach 1.1; 1.01 is reached at 0.31 SD · one chain narrow: folded R-hat · 0.36 × SD · needed to reach 1.1; 1.01 is reached at 0.76 · 3,200 short runs on the trial's posterior: · R-hat < 1.1: lower limit off > 1 point · 10.6% · R-hat < 1.01, ESS > 400 · 0.0% · 05 / 08 · What R-hat 1.1 · lets through. · The old cutoff passes a chain shifted by · almost a whole posterior standard deviation. · Use R-hat below 1.01, with bulk and · tail ESS above 400. · MCMC YOU CAN TRUST · CANERY.IN
- Alt text: Card: split R-hat reaches 1.1 at a 0.99 SD shift and folded R-hat at 0.36 SD; 10.6% of runs passing 1.1 were off by over a point.
- Long description: Four chains of independent normal draws with one altered, median of 400 runs per point: split R-hat reaches 1.1 only when one chain is shifted by 0.99 posterior standard deviations, and 1.01 at 0.31; folded R-hat reaches 1.1 only when one chain's spread falls to 0.36 of the others', and 1.01 at 0.76. On 3,200 short runs of the trial sampler, 10.6% of runs with R-hat below 1.1 had the lower efficacy limit off by more than one point, against none of the runs with R-hat below 1.01 and both ESS values above 400. Takeaway: use R-hat below 1.01, with bulk and tail ESS above 400.
- Keywords: R-hat, Gelman-Rubin, convergence diagnostics, split R-hat, rank normalization, MCMC thresholds
- Canonical URL: https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts

### feed-06-the-mode-no-chain-visited

- File: `assets/social/feed-06-the-mode-no-chain-visited.png`
- Title: Perfect diagnostics, 30% missing
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Four chains started in one mode of 0.7 N(0, 1) + 0.3 N(16, 1) score R-hat 1.0006 and bulk ESS 4,295, yet report a mean of 0.006 against 4.8 and P(θ > 8) = 0 against 0.3
- Technical source: The mode no chain visited; Figure 12; ledger L26, L27
- Visual structure: lockup and counter; serif title; deck; a panel with R-hat and bulk ESS marked as passing, a rule, then the chain's mean and probability in blue against the exact values; takeaway; footer
- Visible-text transcript: Canery.in · 0.7 N(0, 1) + 0.3 N(16, 1); four chains started near 0 · R-hat · 1.0006 · below 1.01: passes · bulk ESS · 4,295 · above 400: passes · mean · 0.006 · exact 4.8 · P(θ > 8) · 0.0 · exact 0.3 · 06 / 08 · Perfect diagnostics, · 30% missing. · A posterior with two modes; none of 24,000 · iterations crossed the valley. · No within- or between-chain statistic can · see a mode that no chain visited. · MCMC YOU CAN TRUST · CANERY.IN
- Alt text: Card: chains in one mode of a bimodal posterior score R-hat 1.0006 and ESS 4,295 but miss 30% of the probability.
- Long description: A constructed bimodal posterior, 0.7 N(0, 1) + 0.3 N(16, 1), with four well-tuned chains all started near 0. None of 24,000 iterations crossed the valley. R-hat is 1.0006 and bulk ESS 4,295, both passing, yet the chains' mean is 0.006 against the exact 4.8 and their probability above 8 is 0 against 0.3. Takeaway: no within- or between-chain statistic can see a mode that no chain visited.
- Keywords: multimodal posterior, MCMC failure, R-hat limitation, convergence diagnostics, mixing
- Canonical URL: https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts

### feed-07-reading-nuts-in-pymc

- File: `assets/social/feed-07-reading-nuts-in-pymc.png`
- Title: Reading NUTS in PyMC
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: PyMC's NUTS on the accidents model: R-hat 1.0005 and 1.0014, bulk ESS 3,769 and 3,943 of 4,000, 0 divergences, 2.68 leapfrog steps per draw; tail ESS of μ is 2,637 by ArviZ's default and 2,945 by Vehtari et al.'s definition
- Technical source: NUTS in PyMC: reading the production diagnostics; Reading the library's output; Figure 13; ledger L30, L33, L34
- Visual structure: lockup and counter; serif title; deck; a panel with three diagnostic rows, a rule, then the two tail ESS definitions, Vehtari et al.'s in tangerine; takeaway; footer
- Visible-text transcript: Canery.in · PyMC, NUTS: Greenwood and Yule's accidents, 4 × 1,000 draws · R-hat, mu and k · 1.0005 / 1.0014 · bulk ESS of 4,000 · 3,769 / 3,943 · divergences · 0 · 2.68 leapfrog steps per draw · tail ESS of mu, two definitions: · ArviZ summary: 11% / 89% · 2,637 · Vehtari et al.: 5% / 95% · 2,945 · 07 / 08 · Reading NUTS · in PyMC. · The production sampler, read through its · diagnostics and checked against a grid. · ArviZ's summary defaults to an 89% interval · and an 11%/89% tail ESS. Know the defaults. · MCMC YOU CAN TRUST · CANERY.IN
- Alt text: Card: PyMC NUTS on the accidents model, R-hat 1.0005/1.0014, ESS 3,769/3,943 of 4,000, 0 divergences; tail ESS 2,637 versus 2,945.
- Long description: The Greenwood and Yule negative binomial model in PyMC 6.4 with NUTS, four chains of 1,000 draws. R-hat is 1.0005 for μ and 1.0014 for k; bulk ESS is 3,769 and 3,943 of 4,000 draws; there are 0 divergences; NUTS takes 2.68 leapfrog steps per draw. The tail ESS of μ is 2,637 in ArviZ's summary, which uses the 11% and 89% quantiles by default, and 2,945 under Vehtari et al.'s 5% and 95% definition. Takeaway: ArviZ's summary defaults to an 89% interval and an 11%/89% tail ESS.
- Keywords: NUTS, PyMC, ArviZ, Hamiltonian Monte Carlo, effective sample size, divergences
- Canonical URL: https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: MCMC you can trust
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The article's five results in one list, and the call to read it
- Technical source: Insights; Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel with five headed results; takeaway; the call to read in tangerine
- Visible-text transcript: Canery.in · by hand · 20,000 draws: VE 90.47% to 97.52% · dependence · τ = 4.961: 20,000 draws worth 4,032 · standard errors · naive covers 65.1%, SD/√ESS 94.9% · thresholds · 1.1 passes shifts up to 0.99 SD; use 1.01, ESS > 400 · blind spot · one mode: R-hat 1.0006, 30% of the posterior missing · 08 / 08 · MCMC you · can trust. · A sampler by hand, every diagnostic by hand, · matched to ArviZ, and every guarantee measured. · The full walk-through, with the lab, the · notebook and PyMC's output read line by line. · READ IT AT CANERY.IN/BLOGS/MCMC-DIAGNOSTICS-METROPOLIS-NUTS
- Alt text: Card: a summary of five results: Metropolis by hand, ESS, standard errors, R-hat thresholds and the unvisited mode.
- Long description: A closing card with five results: 20,000 hand-written Metropolis draws give VE 90.47% to 97.52%; τ = 4.961 makes them worth 4,032 independent draws; the naive standard error covers 65.1% against 94.9% for SD/√ESS; R-hat 1.1 passes shifts up to 0.99 SD, so use 1.01 with ESS above 400; and chains in one mode score R-hat 1.0006 with 30% of the posterior missing. The call to read the article on canery.in.
- Keywords: MCMC, Metropolis, R-hat, effective sample size, Bayesian computation
- Canonical URL: https://canery.in/blogs/mcmc-diagnostics-metropolis-nuts

