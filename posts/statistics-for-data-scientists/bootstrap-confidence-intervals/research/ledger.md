# Source ledger — bootstrap-confidence-intervals

Part 7 of *Statistics for Data Scientists*. Researched 2026-11-01, inline (no agents). Numbers the article calls
measured or computed come from `lab/bootstrap.py` (and the optional `lab/crosscheck.R`) and need no key; every
published number, date, attribution, named result and library convention carries one below. Project Euclid served
an Incapsula page to scripts again, so the *Annals* papers are cited for what their abstracts state, or for what an
open paper that discusses them reports, and each row says which. Efron and Hastie's *Computer Age Statistical
Inference* (the authors' free copy, read in full for chapters 10 and 11) carries the definitions of the bootstrap
standard error, the percentile, BC and BCa methods, the jackknife acceleration, second-order accuracy and the
bootstrap-t; Hesterberg 2015 (arXiv version, read in full) carries the practical comparison; Horowitz 2019 (arXiv
version, read in full) carries the counterexample of the maximum and the orders of coverage error. Efron and
Tibshirani's 1993 book was not read; the law-school data come from its companion R package, whose documentation and
source were read.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Efron, B., "Bootstrap methods: another look at the jackknife" (abstract via OpenAlex; Project Euclid served an Incapsula page) | The Annals of Statistics 7(1):1–26 | 1979 | 10.1214/aos/1176344552 | peer-reviewed | https://doi.org/10.1214/aos/1176344552 | 2026-11-01 |
| S2 | T1 | Efron, B., "Better bootstrap confidence intervals" (abstract via OpenAlex; the BCa construction as given in S6) | Journal of the American Statistical Association 82(397):171–185 | 1987 | 10.1080/01621459.1987.10478410 | peer-reviewed | https://doi.org/10.1080/01621459.1987.10478410 | 2026-11-01 |
| S3 | T1 | Efron, B. & Tibshirani, R. J., *An Introduction to the Bootstrap* (not read; cited as the origin of the law-school data, as the package documentation in S5 states) | Chapman & Hall/CRC | 1993 | 10.1201/9780429246593 | peer-reviewed | https://doi.org/10.1201/9780429246593 | 2026-11-01 |
| S4 | T1 | DiCiccio, T. J. & Efron, B., "Bootstrap confidence intervals" (the survey the sweep started from; abstract via OpenAlex, Project Euclid blocked) | Statistical Science 11(3):189–228 | 1996 | 10.1214/ss/1032280214 | peer-reviewed | https://doi.org/10.1214/ss/1032280214 | 2026-11-01 |
| S5 | T3 | `bootstrap` 2019.6, R package for the book in S3 (S original by R. Tibshirani, R port by F. Leisch): DESCRIPTION, LICENSE, `man/law.Rd`, `man/law82.Rd`, `R/bcanon.R` and the data files read from the CRAN source tarball | CRAN | 2019 | — | source | https://cran.r-project.org/package=bootstrap | 2026-11-01 |
| S6 | T1 | Efron, B. & Hastie, T., *Computer Age Statistical Inference* (the authors' copy, corrected 2017; chapters 10 and 11 read in full) | Cambridge University Press | 2016 | 10.1017/CBO9781316576533 | peer-reviewed | https://hastie.su.domains/CASI/ | 2026-11-01 |
| S7 | T1 | Bickel, P. J. & Freedman, D. A., "Some asymptotic theory for the bootstrap" (abstract via OpenAlex; the counterexample of the maximum as stated in S8) | The Annals of Statistics 9(6):1196–1217 | 1981 | 10.1214/aos/1176345637 | peer-reviewed | https://doi.org/10.1214/aos/1176345637 | 2026-11-01 |
| S8 | T1 | Horowitz, J. L., "Bootstrap methods in econometrics" (read in full, arXiv:1809.04016v1; the published version's venue, volume and pages confirmed with Crossref) | Annual Review of Economics 11:193–224 | 2019 | 10.1146/annurev-economics-080218-025651 | peer-reviewed | https://arxiv.org/abs/1809.04016 | 2026-11-01 |
| S9 | T1 | Athreya, K. B., "Bootstrap of the mean in the infinite variance case" (abstract via OpenAlex) | The Annals of Statistics 15(2):724–731 | 1987 | 10.1214/aos/1176350371 | peer-reviewed | https://doi.org/10.1214/aos/1176350371 | 2026-11-01 |
| S10 | T1 | Hall, P., "Theoretical comparison of bootstrap confidence intervals" (abstract via OpenAlex) | The Annals of Statistics 16(3):927–953 | 1988 | 10.1214/aos/1176350933 | peer-reviewed | https://doi.org/10.1214/aos/1176350933 | 2026-11-01 |
| S11 | T1 | Hesterberg, T. C., "What teachers should know about the bootstrap: resampling in the undergraduate statistics curriculum" (read in full, arXiv:1411.5279v1) | The American Statistician 69(4):371–386 | 2015 | 10.1080/00031305.2015.1089789 | peer-reviewed | https://arxiv.org/abs/1411.5279 | 2026-11-01 |
| S12 | T1 | Giné, E. & Zinn, J., "Necessary conditions for the bootstrap of the mean" (abstract via OpenAlex) | The Annals of Statistics 17(2):684–691 | 1989 | 10.1214/aos/1176347134 | peer-reviewed | https://doi.org/10.1214/aos/1176347134 | 2026-11-01 |
| S13 | T1 | Knight, K., "On the bootstrap of the sample mean in the infinite variance case" (abstract via OpenAlex) | The Annals of Statistics 17(3):1168–1175 | 1989 | 10.1214/aos/1176347262 | peer-reviewed | https://doi.org/10.1214/aos/1176347262 | 2026-11-01 |
| S14 | T1 | Hall, P., "Asymptotic properties of the bootstrap for heavy-tailed distributions" (abstract via OpenAlex) | The Annals of Probability 18(3):1342–1360 | 1990 | 10.1214/aop/1176990748 | peer-reviewed | https://doi.org/10.1214/aop/1176990748 | 2026-11-01 |
| S15 | T1 | Künsch, H. R., "The jackknife and the bootstrap for general stationary observations" (abstract via OpenAlex) | The Annals of Statistics 17(3):1217–1241 | 1989 | 10.1214/aos/1176347265 | peer-reviewed | https://doi.org/10.1214/aos/1176347265 | 2026-11-01 |
| S16 | T1 | Swanepoel, J. W. H., "A note on proving that the (modified) bootstrap works" (abstract via OpenAlex) | Communications in Statistics — Theory and Methods 15(11):3193–3203 | 1986 | 10.1080/03610928608829303 | peer-reviewed | https://doi.org/10.1080/03610928608829303 | 2026-11-01 |
| S17 | T1 | Bickel, P. J., Götze, F. & van Zwet, W. R., "Resampling fewer than n observations: gains, losses, and remedies for losses" (abstract and introduction read in the journal's open PDF; no DOI was assigned, so the identifier is its Mathematical Reviews number) | Statistica Sinica 7(1):1–31 | 1997 | MR1441142 | peer-reviewed | https://www3.stat.sinica.edu.tw/statistica/oldpdf/A7n11.pdf | 2026-11-01 |
| S18 | T1 | Schenker, N., "Qualms about bootstrap confidence intervals" (abstract via OpenAlex) | Journal of the American Statistical Association 80(390):360–361 | 1985 | 10.1080/01621459.1985.10478123 | peer-reviewed | https://doi.org/10.1080/01621459.1985.10478123 | 2026-11-01 |
| S19 | T1 | Hall, P., "On the number of bootstrap simulations required to construct a confidence interval" (abstract via OpenAlex) | The Annals of Statistics 14(4):1453–1462 | 1986 | 10.1214/aos/1176350169 | peer-reviewed | https://doi.org/10.1214/aos/1176350169 | 2026-11-01 |
| S20 | T1 | Polansky, A. M., "Upper bounds on the true coverage of bootstrap percentile type confidence intervals" (abstract via OpenAlex) | The American Statistician 53(4):362–369 | 1999 | 10.1080/00031305.1999.10474491 | peer-reviewed | https://doi.org/10.1080/00031305.1999.10474491 | 2026-11-01 |
| S21 | T1 | Andrews, D. W. K., "Inconsistency of the bootstrap when a parameter is on the boundary of the parameter space" (not read; its example and result as stated in S8) | Econometrica 68(2):399–405 | 2000 | 10.1111/1468-0262.00114 | peer-reviewed | https://doi.org/10.1111/1468-0262.00114 | 2026-11-01 |
| S22 | T1 | Carpenter, J. & Bithell, J., "Bootstrap confidence intervals: when, which, what? A practical guide for medical statisticians" (abstract via OpenAlex; used to check the sweep's coverage of methods, not cited for a fact) | Statistics in Medicine 19(9):1141–1164 | 2000 | 10.1002/(SICI)1097-0258(20000515)19:9%3C1141::AID-SIM479%3E3.0.CO;2-F | peer-reviewed | https://doi.org/10.1002/(SICI)1097-0258(20000515)19:9%3C1141::AID-SIM479%3E3.0.CO;2-F | 2026-11-01 |
| S23 | T1 | Davison, A. C., Hinkley, D. V. & Young, G. A., "Recent developments in bootstrap methodology" (abstract via OpenAlex: subsampling, m out of n, bootstrap failures) | Statistical Science 18(2):141–157 | 2003 | 10.1214/ss/1063994969 | peer-reviewed | https://doi.org/10.1214/ss/1063994969 | 2026-11-01 |
| S24 | T3 | SciPy 1.18.1, `scipy.stats.bootstrap` and `scipy.stats.quantile` (source read in the installed package: `_resampling.py`, `_bca_interval`, `_percentile_of_score`) | SciPy | 2026 | — | source | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html | 2026-11-01 |
| S25 | T3 | R `boot` 1.3.32 (Canty and Ripley; the companion of Davison and Hinkley's 1997 book): `boot.ci`, `bca.ci`, `perc.ci`, `basic.ci`, `stud.ci`, `norm.ci`, `norm.inter`, `empinf`, `empinf.reg`, `usual.jack` (source printed from the installed package) | CRAN | 2025 | — | source | https://cran.r-project.org/package=boot | 2026-11-01 |
| S26 | T1 | Fisher, R. A., "Frequency distribution of the values of the correlation coefficient in samples from an indefinitely large population" (not read; cited for attribution of the exact distribution, as S6 §11.1 states; Crossref gives pages 507–521 under the publisher's DOI) | Biometrika 10(4):507–521 | 1915 | 10.1093/biomet/10.4.507 | peer-reviewed | https://doi.org/10.1093/biomet/10.4.507 | 2026-11-01 |
| S27 | T1 | Logan, B. F., Mallows, C. L., Rice, S. O. & Shepp, L. A., "Limit distributions of self-normalized sums" (abstract via OpenAlex) | The Annals of Probability 1(5):788–809 | 1973 | 10.1214/aop/1176996846 | peer-reviewed | https://doi.org/10.1214/aop/1176996846 | 2026-11-01 |
| S28 | T2 | Chen, D., "Online Retail" [dataset], UCI Machine Learning Repository (as recorded in Part 2's ledger: CC BY 4.0; the per-customer spend file copied from Part 6's lab) | UCI Machine Learning Repository | 2015 | 10.24432/C5BW33 | source | https://archive.ics.uci.edu/dataset/352/online+retail | 2026-11-01 |
| S29 | T1 | Canty, A. J., Davison, A. C., Hinkley, D. V. & Ventura, V., "Bootstrap diagnostics and remedies" (abstract via OpenAlex) | Canadian Journal of Statistics 34(1):5–27 | 2006 | 10.1002/cjs.5550340103 | peer-reviewed | https://doi.org/10.1002/cjs.5550340103 | 2026-11-01 |
| S30 | T1 | Politis, D. N. & Romano, J. P., "The stationary bootstrap" (abstract via OpenAlex) | Journal of the American Statistical Association 89(428):1303–1313 | 1994 | 10.1080/01621459.1994.10476870 | peer-reviewed | https://doi.org/10.1080/01621459.1994.10476870 | 2026-11-01 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | title.search for 36 candidates: the plan's six key sources (Efron 1979, Efron 1987, Efron–Tibshirani, DiCiccio–Efron, Bickel–Freedman, Athreya) and the sweep's others (Hall 1986, 1988, 1992; Singh; Künsch; Giné–Zinn; Knight; Arcones–Giné; Bickel–Götze–van Zwet; Swanepoel; Efron 1981 ×2, 1982, 1985, 2003; Efron–Gong; Diaconis–Efron; Schenker; Carpenter–Bithell; Hesterberg; Davison–Hinkley(–Young); Andrews; Politis–Romano; Fisher 1915; Efron–Hastie; Canty et al.; DiCiccio–Romano; Beran; Lahiri) | venue, year, DOI and citation count for all 36; abstracts for 28; open copies only on Project Euclid (Annals, Statistical Science) and Taylor & Francis (Hesterberg) |
| 2 | 1 | Web search | DiCiccio Efron 1996 "Bootstrap confidence intervals" Statistical Science pdf | only the Project Euclid record and a discussion record on EPFL Infoscience |
| 3 | 1 | Project Euclid | the DiCiccio–Efron PDF by curl | an Incapsula page; the paper is cited for its abstract |
| 4 | 1 | Web search | Efron Hastie "Computer Age Statistical Inference" pdf | the authors' Stanford page; its download page points to the authors' Google Drive copy, which was read (chapters 10–11) |
| 5 | 2 | CRAN | the `bootstrap` package page and source tarball 2019.6 | BSD 3-clause; datasets `law` (15) and `law82` (82); `bcanon`: z0 from the strict share, centred jackknife acceleration, `quantile(type = 1)` |
| 6 | 5 | SciPy source | `scipy/stats/_resampling.py` and `scipy.stats.quantile` in the installed 1.18.1 | default `method='BCa'`, `n_resamples=9999`; z0 from the mid-rank share; jackknife acceleration; type 7 quantiles; `paired=True` resamples index rows |
| 7 | 5 | R source | `boot` 1.3.32 functions printed in R 4.5.2 | `bca.ci`: z0 from the strict share; acceleration from `empinf`, which picks a regression on the resampling frequencies when R ≥ n; `norm.inter` interpolation; `basic`, `stud`, `norm` definitions |
| 8 | 4 | arXiv | API and PDF, "What teachers should know about the bootstrap" | 1411.5279v1, read: the reverse percentile (basic) interval is wrong-way for skewness; narrowness bias; bootstrap-t best for skewed populations; first- and second-order accuracy defined |
| 9 | 1 | EPFL Infoscience | records 84918 (Canty et al. 2006), 84830 (Davison–Hinkley), 84828 (a DiCiccio–Efron discussion) | JavaScript application pages, no PDF reached |
| 10 | 4 | Web search | "Bickel and Freedman (1981)" bootstrap fails sample maximum uniform 1 − 1/e | Horowitz's review states the counterexample with the 1 − 1/e limit; Statistica Sinica and Springer copies of Bickel–Götze–van Zwet |
| 11 | 4 | Web search | "Singh (1981)" bootstrap m-dependent fails | the independence failure is attributed to Singh 1981 only in secondary sources that do not state it precisely; the article attributes no dependence result to Singh |
| 12 | 1 | arXiv | API and PDF, 1809.04016 (Horowitz) | read: the maximum (due to Bickel and Freedman), the boundary (Andrews 2000), m out of n for the maximum (Swanepoel 1986), error orders for one-sided and symmetrical intervals, block bootstraps |
| 13 | 1 | OpenAlex | title.search for 10 more: Horowitz 2019, Fisher 1921, Liu–Singh 1992, Hall 1990, Logan et al. 1973, Efron 1992, Polansky 1999, Chernick–LaBudde, Efron 1981 (censored), Hinkley 1988 | Hall 1990's abstract (a few extreme values determine the bootstrap distribution); Polansky's coverage bounds; Logan et al.'s non-normal limit; Liu–Singh without a venue; Hinkley 1988 not matched |
| 14 | 1 | OpenAlex | forward: cites:W2126728600 (Efron 1987) with "coverage", then with "BCa" | Polansky 1999; Martin 1990 on bootstrap iteration; a 1992 "Qualms about BCa" note |
| 15 | 1 | OpenAlex | forward: cites:W1507985183 (DiCiccio–Efron 1996) with "confidence interval", by citations | Carpenter and Bithell 2000 and applied interval comparisons; no correction of the BCa theory |
| 16 | 4 | OpenAlex | forward: cites:W2067707835 (Bickel–Freedman 1981) with inconsistency, fails or failure | Andrews 2000 (boundary), Abadie and Imbens 2008 (matching estimators), Sen et al. 2010 (Grenander estimator), a 2024 *Biometrika* paper on Chatterjee's rank correlation: bootstrap failures remain an active topic |
| 17 | 1 | OpenAlex | title.search: "Computers and the theory of statistics: thinking the unthinkable" | Efron 1979, SIAM Review 21(4):460–480; not open, not cited |
| 18 | 1 | OpenAlex | backward: the 55 referenced works of DiCiccio–Efron 1996 | Efron 1979, 1981, 1987; Hall 1986, 1988, 1992; Beran 1987; Hall and Martin 1988; Efron 1992: the map of the interval literature |
| 19 | 1 | Semantic Scholar | paper DOI:10.1214/ss/1032280214 | 2,526 citations, 119 influential; no new source |
| 20 | 1 | Google Scholar | bootstrap confidence intervals review (curl) | Carpenter and Bithell 2000, DiCiccio and Romano 1988, Wehrens et al. 2000, Hesterberg 2011: surveys already logged or practitioner tutorials |
| 21 | 1 | Crossref | works for 10.1146/annurev-economics-080218-025651 and 10.1137/1021092 | Horowitz: Annual Review of Economics 11, 193–224, 2019; Efron 1979: SIAM Review 21(4), 460–480 |
| 22 | 1 | Statistica Sinica | the open PDF of Bickel–Götze–van Zwet 1997 | abstract and introduction read: m = o(n) resampling and when it repairs bootstrap failure |
| 23 | 2 | CASI (S6) | chapter 11 searched for Fisher's transformation and the bootstrap-t on the correlation | Fisher's φ = ½ log((1 + ρ)/(1 − ρ)) with SD 1/√(n − 3); bootstrap-t intervals for a correlation agree with exact ones on Fisher's scale and look out of place on the raw scale |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | `scipy.stats.bootstrap` returns a BCa interval unless told otherwise, from 9,999 resamples | S24 signature | SciPy 1.18.1 |
| L02 | R's `boot.ci` returns up to five intervals from one bootstrap object: normal, basic, studentized, percentile and BCa | S25 `boot.ci` | boot 1.3.32 |
| L03 | Efron introduced the bootstrap in 1979 as a general way to estimate the sampling distribution of a statistic from one sample, and showed the jackknife to be a linear approximation to it | S1 abstract | — |
| L04 | The bootstrap standard error is the SD of B replicates, each the statistic on a sample of n drawn with replacement from the data; it is the plug-in estimate of the true SE, with F replaced by the empirical distribution that puts 1/n on each point (the nonparametric MLE of F) | S6 §10.2, eqs. 10.13–10.20 | iid sample |
| L05 | About 200 replicates usually suffice for a standard error; intervals need on the order of 1,000 to 2,000 | S6 §10.2 and §11.4 | the authors' rule of thumb |
| L06 | Bickel and Freedman proved the bootstrap asymptotically valid in many situations (t statistics, empirical and quantile processes, von Mises functionals) and gave counterexamples where it fails | S7 abstract | asymptotic |
| L07 | The law-school data: a random sample of 15 from a universe of 82 American law schools, with LSAT (average score on a national law test) and GPA (average undergraduate grade-point average); used in Efron and Tibshirani's book to bootstrap the correlation | S5 `man/law.Rd`, `man/law82.Rd`; S3 | — |
| L08 | The BC and BCa constructions: p0 the share of replicates less than θ̂, z0 = Φ⁻¹(p0); BCa takes the replicates' percentile at Φ(z0 + (z0 + z_α)/(1 − a(z0 + z_α))); a can be estimated from the jackknife as Σd³/(6(Σd²)^1.5) with d the jackknife mean minus each leave-one-out estimate | S6 eqs. 11.31–11.33, 11.39, 11.40 | one-sample nonparametric problems |
| L09 | Fisher derived the exact distribution of the normal-sample correlation in 1915 and proposed working with φ = ½ log((1 + ρ)/(1 − ρ)), nearly normal with SD 1/√(n − 3) | S6 §11.1, eqs. 11.11–11.12; S26 | bivariate normal data |
| L10 | The percentile method is transformation invariant: if some monotone transformation makes the estimate normal with constant variance and no bias, the percentile interval is correct without the transformation being known | S6 §11.2, eqs. 11.20–11.26 | the transformation exists |
| L11 | A first-order accurate interval has one-sided coverage errors of order 1/√n, needing four times the sample to halve them; a second-order one has errors of order 1/n; BCa is second-order accurate, while the percentile and BC methods are not | S6 §11.4, eqs. 11.36–11.38; S11 §5 | asymptotic, smooth problems |
| L12 | BCa makes three corrections to the standard interval: for non-normality (the percentiles), for bias (z0) and for a standard error that changes with θ (a); it reduces to BC when a = 0, to the percentile interval when z0 = 0 | S6 §11.4 | — |
| L13 | BC and BCa work most dependably when abs(z0) and abs(a) are small, say at most 0.2; a large z0 warns of bias | S6 §11.4, the high-dimensional example | the authors' rule of thumb |
| L14 | Hall compared seven bootstrap methods and found percentile-t and BCa the most promising, confirming that BCa is second-order correct; other methods made serious errors in coverage | S10 abstract | asymptotic |
| L15 | The basic interval (Davison and Hinkley's name; Hesterberg's reverse percentile) mirrors the percentile interval about θ̂, is asymmetric in the wrong direction for skewed data, and its coverage was the worst in Hesterberg's simulations | S11 §5.4, §5.6 | — |
| L16 | Bootstrap-t intervals are not transformation invariant; for a correlation they agree well with exact intervals on Fisher's scale, and need a formula for the SE | S6 §11.5 | — |
| L17 | Hall showed that the bootstrap-t's coverage improvement holds for any B when the nominal level is a multiple of 1/(B + 1), and that small B gives longer intervals | S19 abstract | continuous data |
| L18 | Schenker showed that the percentile and BC intervals for the variance of a normal distribution cover substantially below nominal in small and moderate samples | S18 abstract | — |
| L19 | Percentile intervals are too narrow in small samples (narrowness bias: the bootstrap SE of a mean is √((n − 1)/n) times s/√n); for skewed populations t procedures converge to their nominal coverage slowly, at rate 1/√n, and the bootstrap-t was the best of the intervals Hesterberg compared | S11 §3.2, §4.5, §5.2, §5.6 | — |
| L20 | Intervals built from percentiles of the bootstrap distribution have upper bounds on their finite-sample coverage, which can be low, even for methods that are second-order accurate | S20 abstract | finite samples |
| L21 | The counterexample of the sample maximum is due to Bickel and Freedman: for a uniform sample the bootstrap maximum equals the sample maximum with probability 1 − (1 − 1/n)^n, which tends to 1 − 1/e, so the bootstrap does not estimate the maximum's distribution consistently | S8 §2.1, example 3; S7 | uniform population |
| L22 | Resampling m observations, with m growing more slowly than n, repairs the bootstrap for the sample maximum (Swanepoel) and for other counterexamples of Bickel and Freedman | S16 abstract; S8 §3; S17 abstract | m → ∞, m/n → 0 |
| L23 | When the variance is infinite but the data are in a stable law's domain of attraction, the bootstrap distribution of the normalized mean converges to a random distribution, so the naive bootstrap can fail | S9 abstract; S13 abstract | heavy tails |
| L24 | Finite variance is necessary for the bootstrap of the mean to work almost surely | S12 abstract | — |
| L25 | Between light and extremely heavy tails, the bootstrap distribution of the mean does not converge in probability to a fixed limit, and a small number of extreme sample values determine its behaviour | S14 abstract | — |
| L26 | With infinite variance, the self-normalized sum (the t statistic's core) still converges, but to a non-normal limit that depends on the tail index | S27 abstract | tail index below 2 |
| L27 | Künsch extended the bootstrap to stationary dependent observations by resampling blocks of consecutive observations | S15 abstract; S8 §8 | block length growing slower than n |
| L28 | The stationary bootstrap resamples blocks of random length, for weakly dependent stationary data | S30 abstract | — |
| L29 | When a parameter can lie on the boundary of its space, the nonparametric bootstrap is inconsistent there (Andrews 2000) | S8 §2.1, example 2; S21 | parameter on the boundary |
| L30 | Bootstrap failures and the m out of n bootstrap are reviewed in a 2003 survey of bootstrap methodology | S23 abstract | — |
| L31 | SciPy's BCa: z0 from the mid-rank share ((#<) + (#≤))/2B; acceleration from the jackknife; limits from type 7 ('linear') quantiles; `paired=True` resamples rows of indices; the basic interval is 2θ̂ minus the percentile limits | S24 `_bca_interval`, `_percentile_of_score`, `bootstrap` | SciPy 1.18.1 |
| L32 | R's `bca.ci`: z0 from the strict share; acceleration Σl³/(6(Σl²)^1.5) from `empinf`, which with no `L` given and R ≥ n regresses the replicates on the resampling frequencies; `norm.inter` takes the (B + 1)α-th order statistic and interpolates on the normal quantile scale; `usual.jack` uses (n − 1)(θ̂ − θ̂₍ᵢ₎) uncentred | S25 `bca.ci`, `empinf`, `empinf.reg`, `norm.inter`, `usual.jack` | boot 1.3.32 |
| L33 | R's `norm.ci` subtracts the bootstrap bias estimate before adding ±z·SE; `stud.ci` reads the variance as the statistic's second element; `h`, `hdot` and `hinv` compute any interval on a transformed scale | S25 `norm.ci`, `stud.ci`, `boot.ci` | boot 1.3.32 |
| L34 | `bootstrap::bcanon` takes BCa limits with `quantile(type = 1)`, z0 from the strict share, and the centred jackknife acceleration | S5 `R/bcanon.R` | bootstrap 2019.6 |
| L35 | Customer spend: UCI Online Retail, CC BY 4.0; 4,317 customers with positive net spend | S28; Part 2's ledger | — |
| L36 | For the asymptotic normal approximation, coverage errors are of order 1/n for symmetrical intervals and 1/√n for one-sided ones | S8 §3, the summary after eq. (3.6) | smooth, asymptotically pivotal statistics |
| L37 | An accurate 95% interval misses 2.5% of the time on each side; a miss on one side is not compensated by fewer misses on the other, because findings are read with their direction | S11 §5, "Accurate Confidence Intervals" | — |
| L38 | Bootstrap diagnostics address data peculiarities, a wrong resampling model, misuse of simulation output and the method's own inaccuracy, including inconsistency and the order of correctness | S29 abstract | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S6 | Figures 11.3–11.5 (bootstrap correlations for the student score data) | worked example | shows a bootstrap distribution of a correlation and its percentile interval | Cambridge University Press; the free copy is for personal use only, no reuse licence | https://hastie.su.domains/CASI/ | do not reuse: our own law-school figure (Figure 2) carries the same idea on this post's data, with the true sampling distribution beside it |
| F2 | S11 | Figures 20–21 (one-sided non-coverage of seven intervals) | how each interval works | compares intervals' coverage | Taylor & Francis; arXiv licence is the default, which grants no reuse | https://arxiv.org/abs/1411.5279 | do not reuse: Figure 7 measures coverage on this post's population |
| F3 | S8 | none | — | the review has no figures for these examples | — | — | none |

## Open questions

- Whether the 15-school sample was drawn as the package says ("a random sample"), and by what mechanism, is not
  documented in the sources read; the article states only what the package documentation says.
- Whether the percentile and BCa coverage for Pareto data with tail index 1.5 converges to a limit below 95% is not
  settled by the sources read; the article reports the measured rise to n = 1,000 and the theorems that say the
  bootstrap distribution does not settle, and claims no limit.
- The dependence failure is not attributed to a paper: the measured SE ratio and its large-n value √((1 − φ)/(1 + φ))
  are derived in the article.
