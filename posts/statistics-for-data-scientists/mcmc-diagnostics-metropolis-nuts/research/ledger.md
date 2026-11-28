# Source ledger — mcmc-diagnostics-metropolis-nuts

Part 12 of *Statistics for Data Scientists*. Researched 2026-11-27, inline (no agents). Numbers the article calls computed
or measured come from `lab/mcmc.py` and need no key; every published number, date, attribution, named result and library
convention carries one below. Read in full or at the cited sections: Vehtari et al. 2021 (arXiv 1903.08008v5, the
accepted version), Roy 2020 (arXiv 1909.11827, the survey), Vats and Knudson 2021 (arXiv 1812.09384v3), Flegal, Haran
and Jones 2008 (arXiv math/0703746), Robert and Casella 2011 (arXiv 0808.2902), Brooks and Gelman 1998 (the authors'
copy), Gubernatis 2005 (Zenodo copy), Hoffman and Gelman 2014 (arXiv 1111.4246, abstract and section 3.2), BDA3
sections 11.2, 11.4–11.5, 12.2–12.3. Read as source code in the lab's environment: arviz-stats 1.3.3, arviz-base 1.3.1,
PyMC 6.4.0; R's posterior 1.8.1 in an isolated library. Cited for what their abstracts state: Metropolis et al. 1953,
Hastings 1970, Gelman and Rubin 1992 (the authors' copy is a scan with no text layer), Geyer 1992, Roberts, Gelman and
Gilks 1997, Cowles and Carlin 1996, Margossian et al. 2025, Lambert and Vehtari 2022, Moins et al. 2025, Yao, Vehtari and
Gelman 2022. The 1953 algorithm's details are cited as Robert and Casella describe them.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Metropolis, N., Rosenbluth, A. W., Rosenbluth, M. N., Teller, A. H. & Teller, E., "Equation of state calculations by fast computing machines" (abstract via OpenAlex; algorithm as S12 describes it) | Journal of Chemical Physics 21(6):1087–1092 | 1953 | 10.1063/1.1699114 | peer-reviewed | https://doi.org/10.1063/1.1699114 | 2026-11-27 |
| S2 | T1 | Hastings, W. K., "Monte Carlo sampling methods using Markov chains and their applications" (abstract via OpenAlex; acceptance rule as S12 describes it) | Biometrika 57(1):97–109 | 1970 | 10.1093/biomet/57.1.97 | peer-reviewed | https://doi.org/10.1093/biomet/57.1.97 | 2026-11-27 |
| S3 | T1 | Gelman, A. & Rubin, D. B., "Inference from iterative simulation using multiple sequences" (abstract via OpenAlex) | Statistical Science 7(4):457–472 | 1992 | 10.1214/ss/1177011136 | peer-reviewed | https://doi.org/10.1214/ss/1177011136 | 2026-11-27 |
| S4 | T1 | Geyer, C. J., "Practical Markov chain Monte Carlo" (abstract via OpenAlex; its initial-sequence estimators as S7 section 3.2 describes them) | Statistical Science 7(4):473–483 | 1992 | 10.1214/ss/1177011137 | peer-reviewed | https://doi.org/10.1214/ss/1177011137 | 2026-11-27 |
| S5 | T1 | Roberts, G. O., Gelman, A. & Gilks, W. R., "Weak convergence and optimal scaling of random walk Metropolis algorithms" (abstract via OpenAlex) | Annals of Applied Probability 7(1):110–120 | 1997 | 10.1214/aoap/1034625254 | peer-reviewed | https://doi.org/10.1214/aoap/1034625254 | 2026-11-27 |
| S6 | T1 | Brooks, S. P. & Gelman, A., "General methods for monitoring convergence of iterative simulations" (read, the authors' copy: sections 1–3 and the Weibull example) | Journal of Computational and Graphical Statistics 7(4):434–455 | 1998 | 10.1080/10618600.1998.10474787 | peer-reviewed | http://www.stat.columbia.edu/~gelman/research/published/brooksgelman2.pdf | 2026-11-27 |
| S7 | T1 | Vehtari, A., Gelman, A., Simpson, D., Carpenter, B. & Bürkner, P.-C., "Rank-normalization, folding, and localization: an improved R̂ for assessing convergence of MCMC" (read in full, arXiv 1903.08008v5, sections 1–4 and appendix A) | Bayesian Analysis 16(2):667–718 | 2021 | 10.1214/20-BA1221 | peer-reviewed | https://arxiv.org/abs/1903.08008 | 2026-11-27 |
| S8 | T1 | Hoffman, M. D. & Gelman, A., "The No-U-Turn Sampler: adaptively setting path lengths in Hamiltonian Monte Carlo" (read: abstract and section 3.2, dual averaging; JMLR volume 15, issue 47) | Journal of Machine Learning Research 15(47):1593–1623 | 2014 | arXiv:1111.4246 | peer-reviewed | https://jmlr.org/papers/v15/hoffman14a.html | 2026-11-27 |
| S9 | T1 | Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A. & Rubin, D. B., *Bayesian Data Analysis*, 3rd ed. (authors' electronic edition): sections 11.2, 11.4, 11.5, 12.2, 12.3 | CRC Press (book) | 2013 | 10.1201/b16018 | peer-reviewed | http://www.stat.columbia.edu/~gelman/book/BDA3.pdf | 2026-11-27 |
| S10 | T1 | Roy, V., "Convergence diagnostics for Markov chain Monte Carlo" (read, arXiv 1909.11827: sections 2.3–2.8 and the six-modal example 3.2; the survey for rung 1) | Annual Review of Statistics and Its Application 7:387–412 | 2020 | 10.1146/annurev-statistics-031219-041300 | peer-reviewed | https://arxiv.org/abs/1909.11827 | 2026-11-27 |
| S11 | T1 | Cowles, M. K. & Carlin, B. P., "Markov chain Monte Carlo convergence diagnostics: a comparative review" (abstract via OpenAlex) | Journal of the American Statistical Association 91(434):883–904 | 1996 | 10.1080/01621459.1996.10476956 | peer-reviewed | https://doi.org/10.1080/01621459.1996.10476956 | 2026-11-27 |
| S12 | T1 | Robert, C. P. & Casella, G., "A short history of Markov chain Monte Carlo: subjective recollections from incomplete data" (read, arXiv 0808.2902: sections 2.1 and 2.2) | Statistical Science 26(1):102–115 | 2011 | 10.1214/10-STS351 | peer-reviewed | https://arxiv.org/abs/0808.2902 | 2026-11-27 |
| S13 | T1 | Gubernatis, J. E., "Marshall Rosenbluth and the Metropolis algorithm" (read, Zenodo copy) | Physics of Plasmas 12(5):057303 | 2005 | 10.1063/1.1887186 | peer-reviewed | https://zenodo.org/records/1231899 | 2026-11-27 |
| S14 | T1 | Flegal, J. M., Haran, M. & Jones, G. L., "Markov chain Monte Carlo: can we trust the third significant figure?" (read, arXiv math/0703746: section 1) | Statistical Science 23(2):250–260 | 2008 | 10.1214/08-STS257 | peer-reviewed | https://arxiv.org/abs/math/0703746 | 2026-11-27 |
| S15 | T1 | Vats, D. & Knudson, C., "Revisiting the Gelman–Rubin diagnostic" (read, arXiv 1812.09384v3: sections 1 and 5; found by the forward chase from S3 and cited in S7) | Statistical Science 36(4):518–529 | 2021 | 10.1214/20-STS812 | peer-reviewed | https://arxiv.org/abs/1812.09384 | 2026-11-27 |
| S16 | T1 | Margossian, C. C., Hoffman, M. D., Sountsov, P., Riou-Durand, L., Vehtari, A. & Gelman, A., "Nested R̂: assessing the convergence of Markov chain Monte Carlo when running many short chains" (abstract, arXiv 2110.13017; forward chase from S7) | Bayesian Analysis 20(4):1587–1614 | 2025 | 10.1214/24-BA1453 | peer-reviewed | https://doi.org/10.1214/24-BA1453 | 2026-11-27 |
| S17 | T1 | Lambert, B. & Vehtari, A., "R*: a robust MCMC convergence diagnostic with uncertainty using decision tree classifiers" (abstract, arXiv 2003.07900; forward chase from S7) | Bayesian Analysis 17(2):353–379 | 2022 | 10.1214/20-BA1252 | peer-reviewed | https://doi.org/10.1214/20-BA1252 | 2026-11-27 |
| S18 | T1 | Moins, T., Arbel, J., Dutfoy, A. & Girard, S., "On the use of a local R̂ to improve MCMC convergence diagnostic" (abstract, arXiv 2205.06694; forward chase from S7) | Bayesian Analysis 20(1):131–156 | 2025 | 10.1214/23-BA1399 | peer-reviewed | https://doi.org/10.1214/23-BA1399 | 2026-11-27 |
| S19 | T1 | Yao, Y., Vehtari, A. & Gelman, A., "Stacking for non-mixing Bayesian computations: the curse and blessing of multimodal posteriors" (abstract, arXiv 2006.12335; forward chase from S7) | Journal of Machine Learning Research 23(79):1–45 | 2022 | arXiv:2006.12335 | peer-reviewed | https://jmlr.org/papers/v23/20-1426.html | 2026-11-27 |
| S20 | T1 | Greenwood, M. & Yule, G. U., "An inquiry into the nature of frequency distributions representative of multiple happenings…" (counts as printed in two reproductions, as in Parts 1 and 4) | Journal of the Royal Statistical Society 83(2):255–279 | 1920 | 10.2307/2341080 | peer-reviewed | https://doi.org/10.2307/2341080 | 2026-11-27 |
| S21 | T1 | Polack, F. P. et al., "Safety and efficacy of the BNT162b2 mRNA Covid-19 vaccine" (as read for Part 11: Table 2 and its notes) | New England Journal of Medicine 383(27):2603–2615 | 2020 | 10.1056/NEJMoa2034577 | peer-reviewed | https://doi.org/10.1056/NEJMoa2034577 | 2026-11-27 |
| S22 | T1 | Abril-Pla, O. et al., "PyMC: a modern, and comprehensive probabilistic programming framework in Python" (CC BY 4.0) | PeerJ Computer Science 9:e1516 | 2023 | 10.7717/peerj-cs.1516 | peer-reviewed | https://doi.org/10.7717/peerj-cs.1516 | 2026-11-27 |
| S23 | T1 | Kumar, R., Carroll, C., Hartikainen, A. & Martin, O., "ArviZ a unified library for exploratory analysis of Bayesian models in Python" (CC BY 4.0) | Journal of Open Source Software 4(33):1143 | 2019 | 10.21105/joss.01143 | peer-reviewed | https://doi.org/10.21105/joss.01143 | 2026-11-27 |
| S24 | T3 | arviz-stats 1.3.3 and arviz-base 1.3.1 source, read in the lab's environment: `base/diagnostics.py` (`_rhat`, `_rhat_rank`, `_ess`, `_ess_tail`, `_mcse_quantile`), `base/core.py` (`autocov`), `base/dataarray.py` (`ess`), `validate.py`, `sampling_diagnostics.py` (`rhat`, `ess`, `diagnose`), `summary.py`; arviz-base `rcparams.py` | ArviZ | 2026 | — | source | https://github.com/arviz-devs/arviz-stats/blob/main/src/arviz_stats/base/diagnostics.py | 2026-11-27 |
| S25 | T3 | PyMC 6.4.0 source, read in the lab's environment: `distributions/discrete.py` (`NegativeBinomial`), `sampling/mcmc.py` (`sample`), `stats/convergence.py`, `step_methods/hmc/nuts.py` | PyMC | 2026 | — | source | https://github.com/pymc-devs/pymc/blob/main/pymc/distributions/discrete.py | 2026-11-27 |
| S26 | T3 | posterior 1.8.1 (R), installed from CRAN into an isolated library: `ess_tail.default`, `rhat.default`, `mcse_quantile.default` | CRAN | 2026 | — | source | https://cran.r-project.org/package=posterior | 2026-11-27 |
| S27 | T3 | statsmodels 0.15.0 negative binomial convention, as read for Part 4 (`NegativeBinomial`, variance mu + alpha mu²) | statsmodels | 2026 | — | source | https://github.com/statsmodels/statsmodels/blob/main/statsmodels/discrete/discrete_model.py | 2026-11-27 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | full-text search "Markov chain Monte Carlo convergence diagnostics review", sorted by citations | noise (MrBayes, deep learning, mice); full-text search unusable, as in earlier parts |
| 2 | 1 | OpenAlex | full-text search "convergence assessment Markov chain Monte Carlo survey" | noise again |
| 3 | 1 | OpenAlex | title.search "convergence diagnostics markov chain monte carlo", by citations | Cowles and Carlin 1996 (2,449 citations), Roy 2020 (431): the two surveys |
| 4 | 1 | OpenAlex | title.search "convergence assessment techniques markov chain monte carlo" | Brooks and Roberts 1998 (Statistics and Computing), a third review; not cited |
| 5 | 1 | OpenAlex | title.search "monitoring convergence of iterative simulations" | Brooks and Gelman 1998 (7,860 citations) |
| 6 | 1 | arXiv | full texts 1909.11827, 1903.08008, 1812.09384, math/0703746, 0808.2902, 1111.4246, 2110.13017, 2003.07900, 2006.12335, 2205.06694 | all ten downloaded with text layers; Roy's taxonomy read first |
| 7 | 2 | Gelman's book page | BDA3 electronic edition | 11.2 (the Metropolis algorithm), 11.4–11.5 (split R̂, the 1.1 threshold, n_eff), 12.2–12.3 (2.4/√d, 0.44 to 0.23, two-phase adaptation); exercises 12.2 and 13.1 use a Cauchy location posterior for multimodality |
| 8 | 1 | OpenAlex | DOI lookups: Metropolis 1953, Hastings 1970, Gelman and Rubin 1992, Geyer 1992, Roberts, Gelman and Gilks 1997, Brooks and Gelman 1998 | metadata and abstracts; Roberts et al.'s 0.234 stated in the abstract |
| 9 | 1 | OpenAlex | DOI lookups: Cowles and Carlin, Roy, Vats and Knudson, Flegal et al., Robert and Casella, Roberts and Rosenthal 2001, Gubernatis, Vehtari et al. | metadata and abstracts; Gubernatis open at Zenodo; Roberts and Rosenthal's abstract states no rate, so not cited |
| 10 | 4 | Zenodo | record 1231899 | Gubernatis 2005 in full: Rosenbluth's recollection of who did the work |
| 11 | 2 | MCMC Handbook site | HandbookChapter1.pdf, HandbookChapter6.pdf | empty responses (0 bytes); Geyer's and Gelman and Shirley's chapters not read |
| 12 | 4 | Gelman's site | published/brooksgelman2.pdf, published/itsim.pdf | Brooks and Gelman 1998 with a text layer (read); Gelman and Rubin 1992 as a 16-page scan with no text (abstract used) |
| 13 | 1 | Semantic Scholar | graph API, DOI of Vehtari et al. 2021 | answered (200) |
| 14 | 1 | DBLP | publication search "Rhat rank-normalization" | HTTP 202 bot wall; not used |
| 15 | 4 | OpenAlex | forward chase: works citing Vehtari et al. 2021, title "convergence", "multimodal", "rhat", "effective sample size" | nested R̂ (2025), R* (2022), local R̂ (2025), stacking (2022), a 2026 arXiv preprint on multimodal diagnostics (not cited) |
| 16 | 4 | OpenAlex and arXiv | forward chase from Gelman and Rubin 1992 via S7's references | Vats and Knudson 2021: the R̂–ESS relation and the 1.1 survey |
| 17 | 1 | Crossref | DOI lookups: nested R̂, R*, local R̂, PyMC, ArviZ, Stan, Barnett 1966, Brooks and Roberts, Greenwood and Yule, BDA3, Handbook of MCMC | volumes and pages; a guessed DOI for Reeds 1985 resolved to Yatracos 1985, so it was searched instead |
| 18 | 1 | Crossref | bibliographic search "Asymptotic number of roots of Cauchy location likelihood equations" | Reeds 1985, 10.1214/aos/1176349554; Cauchy example later dropped (heavy tails let chains cross; see Open questions) |
| 19 | 2 | JMLR | papers v15/hoffman14a, v23/20-1426 | volume, issue and pages for NUTS and stacking |
| 20 | 2 | Crossref and arXiv | licence fields for 10.1214/20-BA1221, 10.1214/20-STS812, 10.7717/peerj-cs.1516, 10.21105/joss.01143; arXiv abs 1903.08008 | Vehtari et al.: no licence on Crossref, arXiv non-exclusive distribution licence, so its figures are not reusable; PyMC and ArviZ papers CC BY 4.0 |
| 21 | 5 | lab venv | arviz-stats 1.3.3 and arviz-base 1.3.1 source | R̂, ESS and MCSE as Vehtari et al. define them; tail ESS on xarray input at 0.11 and 0.89; summary at 89%; `diagnose` at 1.01 and 100 per chain |
| 22 | 5 | lab venv | PyMC 6.4.0 source | `alpha` is the shape k; `sample` defaults; warnings at R̂ above 1.01 and ESS below 100 per chain; NUTS `target_accept` 0.8 |
| 23 | 5 | CRAN | posterior 1.8.1, installed into an isolated library | tail ESS at 0.05 and 0.95; R̂ folds then splits |
| 24 | 5 | uv resolver | pymc and arviz with NumPy 2.5.4 and SciPy 1.18.1, Python 3.12 | PyMC 6.4.0, PyTensor 3.3.8, ArviZ 1.3.0 (arviz-stats 1.3.3, arviz-base 1.3.1), xarray 2026.9.0 |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Metropolis et al. moved each particle by a uniform random displacement and accepted the move with probability min(1, exp(−ΔE/kT)); a rejected move counted the previous configuration again in the average | S12 §2.1, describing S1 | 1953, a two-dimensional rigid-sphere system on MANIAC |
| L02 | The 1953 runs used 16 steps of burn-in and 48 to 64 further iterations, four to five hours on the Los Alamos computer | S12 §2.1 | as Robert and Casella report it |
| L03 | Marshall Rosenbluth recalled that Teller suggested ensemble averaging and that he and Arianna Rosenbluth did the work; Arianna wrote the code used | S13 §III | recollection at the 2003 50th-anniversary conference |
| L04 | Hastings 1970 generalised the 1953 method to proposals that need not be symmetric, as a statistical tool, with an account of the error in Monte Carlo estimates | S2 abstract; S12 §2.2 | — |
| L05 | Gelman and Rubin recommended several independent sequences from overdispersed starting points, comparing between- and within-sequence variation to estimate how much sharper inference could become | S3 abstract | normal-theory approximations |
| L06 | Gelman and Rubin's reading: a potential scale reduction of 1.1 meant little to gain from longer runs; Brooks and Gelman showed the between-chain variance can fall before it rises | S7 §2 | as Vehtari et al. recount it |
| L07 | Brooks and Gelman described 1.2 as sometimes used for approximate convergence; in their Weibull example the PSRF fell below 1.1 at iterations 800 to 1,300, before one chain found the rest of the space | S6 §2 (Figure 1, the Weibull example) and §3 (the 1.2 guideline) | five sequences |
| L08 | BDA3 computes R̂ on split chains (since its third edition) and says its authors have generally been satisfied with 1.1 as a threshold | S9 §11.4 footnote 2, §11.5 | — |
| L09 | BDA3's jumping rule: random-walk scale about 2.4/√d times the posterior SD, efficiency about 0.3/d, acceptance about 0.44 in one dimension falling to about 0.23 beyond five | S9 §12.2 | multivariate normal target, proposal shaped like it |
| L10 | BDA3 adapts in a first phase and then runs a fixed phase, using only the fixed phase's draws, because adaptation that depends on the past breaks the target | S9 §12.3 | — |
| L11 | Roberts, Gelman and Gilks: the asymptotically optimal acceptance rate of random-walk Metropolis is 0.234 under quite general conditions | S5 abstract | dimension to infinity; product-form targets |
| L12 | Vehtari et al.: traditional R̂ fails with heavy tails and with chains of equal location but different variance; they propose rank-normalised, folded R̂, local efficiency and quantile MCSE, and rank plots | S7 abstract, §1.2 | — |
| L13 | Vehtari et al. use the sample only if R̂ is below 1.01, much tighter than Gelman and Rubin's level, having seen R̂ dip below 1.1 well before convergence | S7 §2 | rank-normalised, folded split R̂ |
| L14 | Vehtari et al. recommend at least four chains, and rank-normalised (bulk) ESS above 400, an average of 50 per split chain with four chains | S7 §2, §3.2 | as a first-level check |
| L15 | ESS in Vehtari et al.: the multi-chain autocorrelation of their equation 10, biased autocovariances (divisor n) by FFT, Geyer's initial positive and initial monotone sequences, and an upper bound of S log10 S | S7 §3.2 | — |
| L16 | Rank normalisation replaces draws by Φ⁻¹((r − 3/8)/(S + 1/4)) with pooled ranks (Blom 1958); folding takes absolute deviations from the median; the reported R̂ is the larger of bulk and folded | S7 §4.1, §4.2 | — |
| L17 | Tail ESS is the smaller of the ESS of the indicators at the 5% and 95% quantiles | S7 §4.3 | — |
| L18 | The quantile MCSE propagates the 16% and 84% quantiles of beta(S_eff α + 1, S_eff (1 − α) + 1) through the sorted draws and halves the distance; it can have high variance in extreme tails | S7 §4.4 | — |
| L19 | With well-separated modes and chains stuck in them, the multi-chain ESS approaches the number of modes found; a single chain's ESS can be drastically too high | S7 §2, §3.2 | — |
| L20 | Vehtari et al.'s appendix A: at 1.01 split R̂ detects a chain shifted by a third of an SD or more, at 1.1 only by about one SD | S7 appendix A | four chains of independent normal draws |
| L21 | Appendix A: at 1.01 folded split R̂ detects a chain with SD below three quarters of the others', and at 1.1 with SD below a quarter | S7 appendix A | the same construction |
| L22 | Dynamic HMC can give an ESS above the number of draws for near-normal parameters, because successive draws can be negatively correlated | S7 §3.2 | — |
| L23 | R̂ is recommended as the primary diagnostic in Stan, JAGS, WinBUGS, OpenBUGS, PyMC3 and NIMBLE | S7 §1 | as of 2021 |
| L24 | Vats and Knudson: R̂ ≈ √(1 + m/ESS) for m chains, so 1.1 corresponds to an ESS of about 5m | S15 §1, §5 | their R̂ with batch-means variance |
| L25 | Of 100 papers from 2017 citing Gelman and Rubin, 43 used 1.1 as the cutoff and 12 used 1.01 | S15 §1 Table 1 | a random sample |
| L26 | Roy's survey: 1.1 is the cutoff generally used, as BDA recommends; chains stuck at one local mode of a six-modal target led R̂ and its multivariate version to declare convergence | S10 §2.4, §3.2 | — |
| L27 | Cowles and Carlin compared 13 diagnostics and found that all can fail to detect the failures they were designed for; no finite MCMC sample can be certified representative | S11 abstract | — |
| L28 | In 2006 issues of JASA, Biometrika and JRSS B, 39 papers used MCMC and only 3 addressed the Monte Carlo error of their estimates | S14 §1 | — |
| L29 | Geyer argued for one long run, with Monte Carlo error estimated by time-series methods, and introduced new variance estimators | S4 abstract | — |
| L30 | HMC takes steps informed by first-order gradient information; NUTS removes its number-of-steps setting by stopping a trajectory when it starts to double back, and adapts the step size by dual averaging, so it needs no hand tuning | S8 abstract, §3.2 | — |
| L31 | PyMC's `NegativeBinomial(mu, alpha)` has variance mu + mu²/alpha, so its alpha is the shape k; statsmodels' alpha is 1/k | S25 `discrete.py`; S27 | PyMC 6.4.0; statsmodels 0.15.0 |
| L32 | `pm.sample` defaults: 1,000 draws after 1,000 tuning steps, chains = max(2, cores), NUTS with target_accept 0.8, jitter+adapt_diag initialisation | S25 `mcmc.py`, `nuts.py` | PyMC 6.4.0 |
| L33 | PyMC warns when any R̂ exceeds 1.01, when ESS per chain falls below 100, and when there are divergences | S25 `stats/convergence.py` | PyMC 6.4.0 |
| L34 | ArviZ 1.3 reports R̂ by the rank method by default; its summary prints an 89% equal-tailed interval; on xarray input its tail ESS takes prob from that 0.89, so the 11% and 89% quantiles; its `diagnose` flags R̂ above 1.01 and ESS below 100 per chain | S24 | arviz-stats 1.3.3, arviz-base 1.3.1 |
| L35 | ArviZ 1.3.3's array interface raises TypeError for tail ESS unless prob is given | S24 `base/diagnostics.py` `_ess_tail` | NumPy array input |
| L36 | R's posterior takes tail ESS at the 5% and 95% quantiles and folds the draws before splitting them | S26 | posterior 1.8.1 |
| L37 | Nested R̂ extends R̂ to many short chains run in parallel, as on GPUs | S16 abstract | — |
| L38 | R* trains classifiers to tell chains apart, giving one statistic across all parameters with its uncertainty | S17 abstract | — |
| L39 | Local R̂ localises the diagnostic to quantiles of the target and catches issues other versions miss | S18 abstract | — |
| L40 | Stacking combines parallel non-mixing runs with weights chosen by cross-validation; it is not full Bayesian inference, and can predict better under misspecification | S19 abstract | — |
| L41 | Greenwood and Yule's 647 women had 447, 132, 42, 21, 3 and 2 accidents for 0 to 5 over five weeks | S20 | counts from two reproductions, as in Parts 1 and 4 |
| L42 | The trial's primary analysis: 8 and 162 cases over 2.214 and 2.222 thousand person-years, prior beta(0.700102, 1) on the vaccine group's share | S21 Table 2 notes | as reproduced in Part 11 |
| L43 | PyMC and ArviZ are documented in Abril-Pla et al. 2023 and Kumar et al. 2019 | S22, S23 | — |
| L44 | PyMC's model log density includes the Jacobian terms of its parameter transformations by default | S25 `model/core.py` (`Model.logp`, `jacobian=True`) | PyMC 6.4.0 |
| L45 | Vehtari et al. do not recommend thinning, which throws away information and gives less efficient estimates | S7 appendix C | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S7 | Figure 2 (R̂ histograms under four scenarios) | What R̂ compares / L12 | shows traditional R̂ below 1.1 for chains that are not mixed | not verified: no licence on Crossref; arXiv non-exclusive distribution licence | https://arxiv.org/abs/1903.08008 | do not reuse; Figure 10 shows our own cases |
| F2 | S7 | Figures 21 and 25 (split R̂ against shift, folded R̂ against scale) | Is 1.1 close enough / L20, L21 | the detection limits at 1.01 and 1.1 | not verified, as F1 | https://arxiv.org/abs/1903.08008 | do not reuse; Figure 11 recomputes the curves and adds the crossings |
| F3 | S10 | Figure 12 (iterative R̂ for the six-modal target) | The mode no chain visited / L26 | R̂ near 1 with chains stuck in one mode | not verified (arXiv non-exclusive licence) | https://arxiv.org/abs/1909.11827 | do not reuse; Figure 12 is our own |

## Open questions

- Vehtari et al.'s appendix puts folded R̂'s 1.1 limit at an SD ratio of a quarter; the lab finds the median crossing
  1.1 at 0.36 for 250, 1,000 and 4,000 draws per chain. A grid in quarters (1, 0.75, 0.5, 0.25) gives their statement,
  since 0.5 scores 1.054 and 0.25 scores 1.16; the article reports both.
- Their single realisations (split R̂ 1.05 for a 0.5 shift, folded 1.06 for SD 0.75, 250 draws) sit above the lab's
  medians (1.026 and 1.010); single runs vary, so the article quotes only the detection statements.
- A Cauchy location posterior (BDA3 exercises 12.2 and 13.1) was tried for the bimodal case and dropped: its heavy
  tails let a well-tuned random walk cross between modes in most runs, even with five points per cluster. The article
  uses a constructed two-normal mixture, labelled as constructed.
- Gelman and Rubin 1992 was not read beyond its abstract (the open copy is a scan); its threshold is cited through
  Vehtari et al. and BDA3.
