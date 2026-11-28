# Outline — bayesian-inference-conjugate-priors

Series `statistics-for-data-scientists`, Part 11 of 18 (Bayesian inference arc; parent: Part 4). Private build file.

## Brief

- **Title:** Bayesian Inference by Hand: Conjugacy and Credible Intervals (60 characters). The plan's title, *Bayesian
  Inference by Hand: Priors, Conjugacy and Credible Intervals*, is 68 characters, over the 60 the validator allows;
  dropping "Priors," is the smallest change that fits, and the summary and tags carry "conjugate prior".
- **Answers:** how do a prior and a likelihood become a posterior, what does a credible interval say that a confidence
  interval cannot, and how did a vaccine trial use one?
- **Tier:** L3 (plan). Six things to learn: Bayes' rule on a binomial by hand (Laplace); a real prior-to-posterior
  analysis and its transformation to the reported scale (the trial); the three conjugate pairs from their kernels;
  equal-tailed against highest-density intervals and what a credible interval guarantees; the posterior predictive;
  prior sensitivity, non-invariance of flatness and Jeffreys' prior; the Bayes factor against the posterior, with
  Lindley's paradox. The worked example fits on one screen (one beta integral, one beta update). **Adjacent option:** L4
  would add the trial's sequential design in full (Tables 7–8 derived, nonbinding futility) and reference priors.
- **Difficulty:** advanced. Assumes Part 4's likelihood and Fisher information, Part 5's p-values, Part 6's
  confidence-interval coverage. **Adjacent option:** intermediate would drop Lindley's paradox and Jeffreys' rule.
- **Lab:** G1 · runs anywhere · E1–E4 · access none. Probe 2026-11-25 matches `access.md` (Python 3.12.16, NumPy 2.5.4,
  SciPy 1.18.1; RAM available 4–5 GiB); the lab peaks at 0.14 GB, `all` 10 s, `all --quick` 7 s. Venv reused
  unchanged; R 4.5.2 base is the private check (`author_crosscheck` in `captures.json`); no R file ships.
- **Corrects:** "With a flat prior the Bayesian answer is objective."
- **Four-point angle:** reconcile (Laplace's tail by exact integers, Boost and TOMS 708, and against his own series; the
  trial's three published credible intervals, the protocol's prior intervals, its Table 6 boundaries and 44 of 45
  printed operating characteristics); condition (the prior, the scale it is flat on, the surveillance-time map; a
  credible interval's 95% holds averaged over its prior, not at a fixed truth); measure (exact frequentist coverage of
  the trial's credible interval; a prior sweep; the Bayes factor against n); read the output (SciPy's gamma takes a
  scale, R's a rate; `betabinom`; the paper's "confidence interval" typo; the FDA's 99.5%; the protocol's ">0.999").

## Settled at research and in the lab

- Laplace, 1745–1770: 251,527 boys, 241,945 girls; Beta(251,528, 241,946), mean 0.509709, SD 0.000712, ½ 13.64 SDs
  below. P(x ≤ ½) = 1.14606 × 10^-42 (exact integers; SciPy's Boost and R's TOMS 708 agree to 9 digits). Laplace's
  first term recomputes to 1.15215 × 10^-42 (he printed 1.1521), 0.53% high, as his "a little too great" said; his
  second term is 1/186 (he wrote about 1/200). Law of succession 0.509709. The 1783 table's year rows sum to 141,859 and
  135,610 and reproduce the 1812 totals 393,386 and 377,555; its printed Total row (151,859; 145,159) does not.
- Trial prior: 0.4118/0.5882 = 0.700102006 (mean matched, rounded to four digits); θ at VE 30% = 0.7/1.7 = 0.411765;
  prior median θ 0.37155 = VE 40.9%; prior 95% θ 0.00515–0.96448 = VE −2,616% to 99.48% (protocol: −26.2 to 0.995 as
  fractions); prior P(VE < 0) 0.3845, P(VE > 30%) 0.5373.
- Posterior 8:162: Beta(8.700102, 163); VE 90.317–97.617 → 90.3–97.6 (adjusted, r = 0.996400); unadjusted 90.352 → 90.4.
  Median 94.84%, MLE 95.04%; P(VE ≤ 30%) = 2.46 × 10^-28. Prior weight 0.009902. 9:169 → 89.9–97.3. Severe 1:3 →
  −124.808 to 96.299 (unadjusted −123.1); P(VE > 30%) 0.743, criterion not met; prior weight 0.298.
- Table 6: success at ≤ 6, 15, 25, 35, 53 (posterior probabilities 0.9965 and 0.9892 around the first; 0.9904 and
  0.9853 around 53 against 0.986). Futility from POS < 5%: 15 (POS 7.19% at 14, 3.11% at 15), 26, 35. Tables 7–8: 44 of
  45 printed values; overall success at VE 30% 0.0210; at VE 70% exact 0.994 where the table prints >0.999 and its own
  columns sum to 0.994.
- Conjugate: beta-binomial marginal 0.01013023 both ways; vaccine rate Gamma(8.5, 2.214), 3.84 (1.71–6.82) per 1,000
  person-years; placebo Gamma(162.5, 2.222), 73.13 (62.32–84.80); their share is Beta(8.5, 162.5), VE 90.46–97.69%.
  Normal–normal: 1782 (0.50812 ± 0.00359) after N(0.509709, 0.000712²): prior weight 0.9622, posterior 0.509649 ±
  0.000698 = the exact beta update.
- Intervals, 8:162: equal-tailed 90.32–97.62, HDI on VE 90.86–97.94, HDI on θ mapped 90.81–97.89; P(VE ≥ lower) 97.50%,
  96.11%, 96.27%. Severe: −124.81 to 96.30; HDI on VE −69.71 to 99.95; on θ mapped −73.55 to 99.08.
- Coverage of the trial's 95% credible interval, exact: 170 cases, VE 0–95%: 92.9% to 96.5% (Clopper–Pearson 95.1% to
  98.0%); 4 cases: 91.7% to 100% (86.6% at VE 96.3%); averaged over the prior 95.000000% by quadrature, 95.01% ± 0.03 and
  95.03% ± 0.03 by simulation (S 400,000).
- Priors, 8:162: 90.1 to 90.9 at the lower limit across trial, Senn's beta(1, 1.428363), uniform, Jeffreys, Haldane.
  Severe: lower −154.6 (uniform) to −116.6 (Senn's). Prior worth 170 cases at VE 0%: 52.3–70.4%. Uniform on θ: P(VE < 0)
  ½, P(VE > 90%) 0.0909; logistic on the log-odds. E3 (0:5): trial 29.9–99.9, uniform 11.7–99.6, Jeffreys 36.5–100,
  Haldane improper.
- Lindley, 1782: 9,851 of 19,387, z 2.262, exact p 0.0241; BF01 8.597 (uniform), P(H0) 0.896; informed prior BF10
  11.54; ceiling BF10 12.93; estimation P(θ ≤ ½) 0.0118, 95% 0.5011–0.5152. Years with p < 0.05 and BF01 > 1: 1772, 1778,
  1779, 1782. Break-even z ≈ 3.07 (Jeffreys' formula 3.069). At z 2.262: BF01 = 1 at n 260, 19 at 94,708.

## Sections and budget

Validator words (decimals count twice; References add about 1,100). Target about 7,300 in all, under the 7,500 cap.

| Section | Words | Reader can now | Figures | Keys |
|---|---|---|---|---|
| Insights, level line, jump list, lab notice | 260 | state the answer | — | — |
| Why this matters | 150 | see what the trial's interval licenses | — | L16 |
| The problem | 300 | name prior, likelihood, posterior; state the claim | — | L06, L07 |
| Worked example | 720 | compute Laplace's tail and the trial's interval | FIG_01, FIG_02 | L01–L05, L08–L13 |
| Intuition | 300 | read a beta prior as pseudo-counts; see the compromise | FIG_03 | L16 |
| Conjugate priors from the likelihood kernel | 500 | derive beta, gamma and normal updates | FIG_04 | L23–L26 |
| Credible intervals: equal tails or highest density? | 380 | compute both; know which transforms | FIG_05 | L16, L21, L22 |
| What does a credible interval promise? | 400 | state its guarantee; measure its coverage | FIG_06 | L32–L34 |
| The posterior predictive distribution | 360 | predict counts; rebuild the futility rule | FIG_07 | L05, L13–L15 |
| How much does the prior matter? | 520 | run a sensitivity sweep; see flatness change with scale | FIG_08, FIG_09 | L18–L20, L27–L31 |
| Bayes factors and Lindley's paradox | 600 | compute a Bayes factor; explain the paradox | FIG_10, FIG_11 | L35–L41 |
| The math | 420 | the formulas, each with the worked numbers | — | L25, L27 |
| Implementation | 380 | run the analysis; read library parameterisations | — | L42, L43 |
| Limitations and common mistakes | 300 | avoid six mistakes | — | L11, L17 |
| Key takeaways | 200 | carry five claims | — | — |
| Try it yourself | 230 | E1 and E3 from the article | — | — |
| References | ~1,100 | — | — | — |

## Figure plan

| # | Section | One thing it communicates | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| 1 | Worked example | Laplace's posterior for the boy probability, and the 10^-42 tail at ½ on a log scale | plot | Q4: a closed-form density | Half lies 13.6 SDs into the tail |
| 2 | Worked example | the trial's prior and posterior on θ, and the posterior of VE with the published interval | plot | Q4: densities and a transformation | Prior to posterior to efficacy |
| 3 | Intuition | prior, likelihood and posterior for 1:3 and 8:162: a compromise weighted by counts | plot | Q4: densities to scale | Four cases leave the prior 30% of the weight; 170 leave it 1% |
| 4 | Conjugate | gamma–Poisson for the two arms; normal–normal for one year after 26 | plot | Q4: closed-form densities | Rates per 1,000 person-years; precision weights |
| 5 | Credible intervals | equal-tailed against highest-density intervals for 1:3 and 8:162 | plot | Q4: one density, three intervals | The published interval is the equal-tailed one |
| 6 | What a credible interval promises | exact coverage against true VE for 170 and 4 cases, beside Clopper–Pearson | plot | Q1: computed curves | 95% on average over the prior, not at each VE |
| 7 | Predictive | the beta-binomial predictive at 14 and 15 of 32; POS against the split at three interims | plot | Q1: computed distributions | The futility rule is a predictive probability |
| 8 | Prior matter | VE interval against prior strength, two centres, two splits | plot | Q1: computed sweep | 170 cases outvote a light prior; 4 do not |
| 9 | Prior matter | uniform, Jeffreys and the trial's prior on θ and on the log-odds | plot | Q4: densities on two scales | Flat on θ is a hill on the log-odds |
| 10 | Lindley | p-value against BF01 for the 14 years | plot | Q1: computed values | Four years reject at 5% while the data favour ½ |
| 11 | Lindley | 1782's BF01 against the prior's concentration and against n | plot | Q1: computed curves | The Bayes factor depends on H1's prior and on n |
| cover | — | the trial's posterior for VE with its interval in tangerine | placed | template cover in the series house layout | — |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| prior, likelihood, posterior, Bayes' theorem | The problem | beliefs before the data; probability of the data given θ; beliefs after; posterior ∝ prior × likelihood | the inference itself | every Bayesian analysis |
| beta distribution, uniform prior | Worked example | the distribution on [0, 1] with shapes a and b; Beta(1, 1) | the natural prior for a proportion | binomial data |
| vaccine efficacy, incidence rate ratio, surveillance time | Worked example | 1 − IRR; ratio of case rates; follow-up in person-years | the trial's estimand and exposure | rate comparisons |
| credible interval | Worked example | an interval holding 95% of the posterior | a probability statement about θ given the data | reporting |
| pseudo-counts, prior weight | Intuition | a + b as prior cases; the weight (a + b)/(a + b + n) | how strong a beta prior is | sensitivity |
| conjugate prior, kernel, marginal likelihood | Conjugate | a family closed under updating; the θ-dependent factor; the normaliser | closed-form posteriors | binomial, Poisson, normal |
| precision | Conjugate | the reciprocal of a variance | the weight in normal–normal updating | — |
| equal-tailed interval, highest-density interval (HDI) | Credible intervals | quantile interval; shortest interval | two summaries that disagree under skew | skewed posteriors |
| coverage of a credible interval, calibration | What a credible interval promises | frequency the interval contains a fixed true value; average over the prior | what 95% guarantees | regulatory use |
| posterior predictive distribution, beta-binomial, law of succession, probability of success | Predictive | the distribution of future data given past data | predictions and futility rules | interim analyses |
| prior sensitivity, sceptical prior | Prior matter | how the answer moves with the prior; a prior centred on no effect | checking the prior | small counts |
| Jeffreys prior, improper prior, Haldane prior | Prior matter | ∝ √I(θ); infinite mass; Beta(0, 0) | invariance; flat on the log-odds | default analyses |
| Bayes factor, point null, Lindley's paradox | Lindley | ratio of marginal likelihoods; H0: θ = ½ exactly; p small while P(H0) is large | testing against estimation | large samples |
| operating characteristics | Predictive | a Bayesian rule's frequentist error rates | how the trial set its thresholds | confirmatory trials |
