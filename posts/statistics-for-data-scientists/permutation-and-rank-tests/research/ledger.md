# Source ledger — permutation-and-rank-tests

Part 10 of *Statistics for Data Scientists*. Researched 2026-11-23, inline (no agents). Numbers the article calls
measured or computed come from `lab/permutation.py` and need no key; every published number, date, attribution,
named result and library convention carries one below. Read in full: Fisher's *The Design of Experiments*, chapter
III (§§14–21), in the second edition of 1937 (a scan; the first edition is 1935); Darwin 1876 (Darwin Online's
transcription, with the page scans of pp. 16 and 234 read as images); Chung and Romano 2013 (arXiv 1304.5939, the
author version); Phipson and Smyth 2010 (arXiv 1603.05766, the authors' corrected version); Fay and Proschan 2010
(PubMed Central PMC2857732). Cited for what their abstracts state: Hodges and Lehmann 1956 and 1963, Romano 1990,
Mann and Whitney 1947, Divine et al. 2018, Brunner and Munzel 2000, Fagerland and Sandvik 2009, Karch 2021,
Hemerik and Goeman 2018, Ernst 2004, David 2008, Kruskal and Wallis 1952, DiCiccio and Romano 2017 and Bauer 1972.
Not read, cited for attribution only as a read source states it: Wilcoxon 1945, Janssen 1997, Spearman 1904,
Kendall 1938, Best and Roberts 1975. Project Euclid served a bot page for the Hodges–Lehmann and Fay–Proschan PDFs;
no challenge was attempted.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Darwin, C., *The Effects of Cross and Self Fertilisation in the Vegetable Kingdom* (read: chapter I pp. 14–17 with Galton's report and table, chapter VI Table XCVII p. 234; page scans 033 and 251 read as images) | John Murray, London | 1876 | — | source | https://darwin-online.org.uk/content/frameset?itemID=F1249&viewtype=text&pageseq=1 | 2026-11-23 |
| S2 | T1 | Fisher, R. A., *The Design of Experiments*, 2nd edition (read: chapter III, §§14–21, Tables 3–5; the first edition is 1935, per S3) | Oliver and Boyd, Edinburgh | 1937 | — | source | https://www.gwern.net/doc/statistics/decision/1937-fisher-thedesignofexperiments.pdf | 2026-11-23 |
| S3 | T1 | David, H. A., "The beginnings of randomization tests" (abstract via OpenAlex) | The American Statistician 62(1):70–72 | 2008 | 10.1198/000313008X269576 | peer-reviewed | https://doi.org/10.1198/000313008X269576 | 2026-11-23 |
| S4 | T1 | Phipson, B. & Smyth, G. K., "Permutation p-values should never be zero: calculating exact p-values when permutations are randomly drawn" (read in full, the authors' corrected version on arXiv) | Statistical Applications in Genetics and Molecular Biology 9(1): Article 39 | 2010 | 10.2202/1544-6115.1585 | peer-reviewed | https://arxiv.org/abs/1603.05766 | 2026-11-23 |
| S5 | T1 | Hemerik, J. & Goeman, J. J., "Exact testing with random permutations" (abstract via OpenAlex; found by the forward chase from S4; online 2017) | TEST 27(4):811–825 | 2018 | 10.1007/s11749-017-0571-1 | peer-reviewed | https://doi.org/10.1007/s11749-017-0571-1 | 2026-11-23 |
| S6 | T1 | Ernst, M. D., "Permutation methods: a basis for exact inference" (abstract via OpenAlex; the review this rung looked for) | Statistical Science 19(4):676–685 | 2004 | 10.1214/088342304000000396 | peer-reviewed | https://doi.org/10.1214/088342304000000396 | 2026-11-23 |
| S7 | T1 | Romano, J. P., "On the behavior of randomization tests without a group invariance assumption" (abstract via OpenAlex) | Journal of the American Statistical Association 85(411):686–692 | 1990 | 10.1080/01621459.1990.10474928 | peer-reviewed | https://doi.org/10.1080/01621459.1990.10474928 | 2026-11-23 |
| S8 | T1 | Chung, E. & Romano, J. P., "Exact and asymptotically robust permutation tests" (read in full, arXiv 1304.5939v1) | The Annals of Statistics 41(2):484–507 | 2013 | 10.1214/13-AOS1090 | peer-reviewed | https://arxiv.org/abs/1304.5939 | 2026-11-23 |
| S9 | T1 | Janssen, A., "Studentized permutation tests for non-i.i.d. hypotheses and the generalized Behrens–Fisher problem" (not read; its result as S8, Example 2.1, states it) | Statistics & Probability Letters 36(1):9–21 | 1997 | 10.1016/S0167-7152(97)00043-6 | peer-reviewed | https://doi.org/10.1016/S0167-7152(97)00043-6 | 2026-11-23 |
| S10 | T1 | Mann, H. B. & Whitney, D. R., "On a test of whether one of two random variables is stochastically larger than the other" (abstract via OpenAlex) | The Annals of Mathematical Statistics 18(1):50–60 | 1947 | 10.1214/aoms/1177730491 | peer-reviewed | https://doi.org/10.1214/aoms/1177730491 | 2026-11-23 |
| S11 | T1 | Wilcoxon, F., "Individual comparisons by ranking methods" (not read; the attribution S10's abstract makes) | Biometrics Bulletin 1(6):80–83 | 1945 | 10.2307/3001968 | peer-reviewed | https://doi.org/10.2307/3001968 | 2026-11-23 |
| S12 | T1 | Fay, M. P. & Proschan, M. A., "Wilcoxon–Mann–Whitney or t-test? On assumptions for hypothesis tests and multiple interpretations of decision rules" (read in full, PMC2857732; the survey for the rank-test rung) | Statistics Surveys 4:1–39 | 2010 | 10.1214/09-SS051 | peer-reviewed | https://pmc.ncbi.nlm.nih.gov/articles/PMC2857732/ | 2026-11-23 |
| S13 | T1 | Divine, G. W., Norton, H. J., Barón, A. E. & Juarez-Colunga, E., "The Wilcoxon–Mann–Whitney procedure fails as a test of medians" (abstract via OpenAlex) | The American Statistician 72(3):278–286 | 2018 | 10.1080/00031305.2017.1305291 | peer-reviewed | https://doi.org/10.1080/00031305.2017.1305291 | 2026-11-23 |
| S14 | T1 | Brunner, E. & Munzel, U., "The nonparametric Behrens–Fisher problem: asymptotic theory and a small-sample approximation" (abstract via OpenAlex) | Biometrical Journal 42(1):17–25 | 2000 | 10.1002/(SICI)1521-4036(200001)42:1<17::AID-BIMJ17>3.0.CO;2-U | peer-reviewed | https://doi.org/10.1002/(SICI)1521-4036(200001)42:1%3C17::AID-BIMJ17%3E3.0.CO;2-U | 2026-11-23 |
| S15 | T1 | Fagerland, M. W. & Sandvik, L., "The Wilcoxon–Mann–Whitney test under scrutiny" (abstract via OpenAlex) | Statistics in Medicine 28(10):1487–1497 | 2009 | 10.1002/sim.3561 | peer-reviewed | https://doi.org/10.1002/sim.3561 | 2026-11-23 |
| S16 | T1 | Karch, J. D., "Psychologists should use Brunner–Munzel's instead of Mann–Whitney's U test as the default nonparametric procedure" (abstract via OpenAlex; found by the forward chase from S13; open access) | Advances in Methods and Practices in Psychological Science 4(2) | 2021 | 10.1177/2515245921999602 | peer-reviewed | https://doi.org/10.1177/2515245921999602 | 2026-11-23 |
| S17 | T1 | Hodges, J. L. & Lehmann, E. L., "The efficiency of some nonparametric competitors of the t-test" (abstract via OpenAlex) | The Annals of Mathematical Statistics 27(2):324–335 | 1956 | 10.1214/aoms/1177728261 | peer-reviewed | https://doi.org/10.1214/aoms/1177728261 | 2026-11-23 |
| S18 | T1 | Hodges, J. L. & Lehmann, E. L., "Estimates of location based on rank tests" (abstract via OpenAlex) | The Annals of Mathematical Statistics 34(2):598–611 | 1963 | 10.1214/aoms/1177704172 | peer-reviewed | https://doi.org/10.1214/aoms/1177704172 | 2026-11-23 |
| S19 | T1 | Bauer, D. F., "Constructing confidence sets using rank statistics" (abstract via OpenAlex; named by S27's `wilcox.test` page) | Journal of the American Statistical Association 67(339):687–690 | 1972 | 10.1080/01621459.1972.10481279 | peer-reviewed | https://doi.org/10.1080/01621459.1972.10481279 | 2026-11-23 |
| S20 | T1 | Spearman, C., "The proof and measurement of association between two things" (not read; attribution) | The American Journal of Psychology 15(1):72–101 | 1904 | 10.2307/1412159 | peer-reviewed | https://doi.org/10.2307/1412159 | 2026-11-23 |
| S21 | T1 | Kendall, M. G., "A new measure of rank correlation" (not read; attribution) | Biometrika 30(1–2):81–93 | 1938 | 10.1093/biomet/30.1-2.81 | peer-reviewed | https://doi.org/10.1093/biomet/30.1-2.81 | 2026-11-23 |
| S22 | T1 | Kruskal, W. H. & Wallis, W. A., "Use of ranks in one-criterion variance analysis" (abstract via OpenAlex) | Journal of the American Statistical Association 47(260):583–621 | 1952 | 10.1080/01621459.1952.10483441 | peer-reviewed | https://doi.org/10.1080/01621459.1952.10483441 | 2026-11-23 |
| S23 | T1 | DiCiccio, C. J. & Romano, J. P., "Robust permutation tests for correlation and regression coefficients" (abstract via OpenAlex; found by the forward chase from S8) | Journal of the American Statistical Association 112(519):1211–1220 | 2017 | 10.1080/01621459.2016.1202117 | peer-reviewed | https://doi.org/10.1080/01621459.2016.1202117 | 2026-11-23 |
| S24 | T1 | Best, D. J. & Roberts, D. E., "Algorithm AS 89: the upper tail probabilities of Spearman's rho" (not read; as S27's `cor.test` page describes it) | Applied Statistics 24(3):377–379 | 1975 | 10.2307/2347111 | peer-reviewed | https://doi.org/10.2307/2347111 | 2026-11-23 |
| S25 | T3 | SciPy 1.18.1 source, read in the lab's environment: `stats/_resampling.py` (`permutation_test`), `_mannwhitneyu.py`, `_wilcoxon.py`, `_morestats.py` (`wilcoxon`), `_stats_py.py` (`brunnermunzel`, `kendalltau`, `spearmanr`), `_correlation.py` (`spearmanrho`) | SciPy | 2026 | — | source | https://github.com/scipy/scipy/blob/main/scipy/stats/_resampling.py | 2026-11-23 |
| S26 | T2 | SciPy 1.18.1 documentation, `scipy.stats` | SciPy | 2026 | — | official-docs | https://docs.scipy.org/doc/scipy/reference/stats.html | 2026-11-23 |
| S27 | T2 | R 4.5.2 documentation and source, read on the build machine: help pages `wilcox.test`, `cor.test`; the source of `wilcox.test.default`, `cor.test.default`, `kruskal.test.default` | R Core Team | 2025 | — | official-docs | https://stat.ethz.ch/R-manual/R-patched/library/stats/html/wilcox.test.html | 2026-11-23 |
| S28 | T1 | Efron, B. & Tibshirani, R. J., *An Introduction to the Bootstrap*: the law-school sample of 15, as exported from CRAN `bootstrap` 2019.6 (BSD 3-clause) by Part 7's lab | Chapman & Hall | 1993 | 10.1201/9780429246593 | source | https://cran.r-project.org/package=bootstrap | 2026-11-23 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Darwin Online | item F1249, text view, and page scans 033 (p. 16) and 251 (p. 234) | the 15 Zea mays pairs in Galton's table and Table XCVII; the site's transcription misreads two fractions that the scans and the printed totals settle |
| 2 | 1 | Web search (standard) | Fisher 1935 Design of Experiments Darwin Zea mays randomization test 1,726 32,768 | a scan of the 1937 second edition (gwern.net) and lecture slides; no source for the count 1,726 except Fisher himself |
| 3 | 1 | Web search (standard) | David 2008 "The beginnings of randomization tests" American Statistician Fisher Darwin | Jacquez and Jacquez 2002 (Mathematical Biosciences) on Darwin's data; two arXiv reviews citing David 2008 |
| 4 | 2 | gwern.net | Fisher, The Design of Experiments, 2nd ed., chapter III | read §§14–21: t = 2.148 against 2.145; Table 4 (835, 28, 863 of 32,768; 5.267%); the absence of randomisation as Darwin's one flaw; Galton's re-arranged columns, t = 5.171 |
| 5 | 1 | OpenAlex | DOI lookups, 9: Hodges–Lehmann 1956 and 1963, Romano 1990, Chung–Romano 2013, Divine et al. 2018, Phipson–Smyth 2010, Wilcoxon 1945, Mann–Whitney 1947, Fay–Proschan 2010 | venues and abstracts for all but Wilcoxon 1945; open copies flagged for Chung–Romano (Project Euclid), Phipson–Smyth (arXiv), Fay–Proschan |
| 6 | 1 | OpenAlex | DOI lookups, 12: Brunner–Munzel 2000, Janssen 1997, Pitman 1937, Spearman 1904, Kendall 1938, Kruskal–Wallis 1952, Ernst 2004, Fligner–Policello 1981, Fagerland–Sandvik 2009, DiCiccio–Romano 2017, Neubert–Brunner 2007, Bauer 1972 | abstracts for Brunner–Munzel, Kruskal–Wallis, Ernst, Fligner–Policello, Fagerland–Sandvik, DiCiccio–Romano and Bauer; none for Janssen, Pitman, Spearman, Kendall, Neubert–Brunner (Elsevier and older JRSS records carry none) |
| 7 | 1 | OpenAlex | title search, 5 queries (Jacquez 2002, David 2008, others) | HTTP 429, too many requests; moved to Crossref |
| 8 | 1 | Crossref | bibliographic search, 5: Jacquez and Jacquez 2002; David 2008; Pitman's 1948 efficiency notes; Lehmann's *Nonparametrics*; Hollander, Wolfe and Chicken | DOIs for Jacquez 2002 and David 2008; Pitman's notes have no record (only a 2018 reprint chapter); book reviews for Lehmann; the 2015 Wiley third edition of Hollander et al. |
| 9 | 1 | arXiv | ti:"Exact and asymptotically robust permutation tests" | 1304.5939v1, read: the permutation and sampling variances of the mean difference agree only with equal sizes or equal variances; Janssen's studentised test; Table 1 for medians |
| 10 | 1 | arXiv | 1603.05766 (Phipson and Smyth, the corrected author version) | read: b/m is uniform under the null, its size (floor(m alpha) + 1)/(m + 1); the exact (b + 1)/(m + 1); about 30 zero p-values in 30,000 genes at m = 1,000; the with-replacement formula |
| 11 | 1 | Europe PMC | DOI:"10.1214/09-SS051"; full-text XML for PMC2857732 | PMC2857732 found; the XML endpoint returned 503, the PMC article page was read in full |
| 12 | 1 | Project Euclid | the open PDFs of Fay–Proschan 2010 and Hodges–Lehmann 1956 | an HTML bot page for both; not attempted further |
| 13 | 1 | OpenAlex | search "permutation tests review", sorted by citations | full-text noise (limma, gradient boosting); the review used, Ernst 2004, came from its DOI and S4's reference list |
| 14 | 1 | OpenAlex | search "Wilcoxon Mann-Whitney test assumptions medians", sorted by citations | noise; Fay–Proschan 2010 is the survey, found by DOI |
| 15 | 4 | OpenAlex | forward chase: works citing Chung–Romano 2013, by citations | Young 2019 (QJE, randomisation inference in economics), the WRS2 package, knockoffs; DiCiccio–Romano 2017 on correlation found by DOI from the same line |
| 16 | 4 | OpenAlex | forward chase: works citing Divine et al. 2018, by citations | Karch 2021 (AMPPS): Mann–Whitney assumes exchangeability; Brunner–Munzel by default |
| 17 | 4 | OpenAlex | forward chase: works citing Phipson–Smyth 2010 with "permutation" in the title | Winkler et al. 2014 (NeuroImage); Hemerik and Goeman 2018 (TEST), random permutations with the identity are exact |
| 18 | 1 | OpenAlex | DOI lookups, 4: Karch 2021, Hemerik–Goeman 2018, Jacquez 2002, David 2008 | abstracts for Karch, Hemerik–Goeman and David; Jacquez 2002 has none, so it is not cited |
| 19 | 4 | Semantic Scholar | paper API, citations of DOI 10.1214/aoms/1177728261 | 404, paper not found |
| 20 | 5 | SciPy 1.18.1 source | `permutation_test`, `mannwhitneyu`, `wilcoxon`, `brunnermunzel`, `kendalltau`, `spearmanr`, `spearmanrho` | the defaults and conventions recorded in L36–L39 |
| 21 | 5 | R 4.5.2 | `wilcox.test.default`, `cor.test.default` and `kruskal.test.default` source; `wilcox.test` and `cor.test` help | the defaults recorded in L28 and L40 |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Darwin raised crossed and self-fertilised *Zea mays* in the greenhouse; seeds germinated in pairs of equal age were planted on opposite sides of four large pots and measured to the tips of the leaves when 1 to 2 feet tall; Table XCVII lists 15 pairs, in inches and eighths | S1 pp. 14, 233–234 | the young plants; later measurements dropped pot I |
| L02 | Darwin asked Galton to judge how trustworthy the averages were; Galton took the Zea mays table as his worked example | S1 pp. 15–16 | — |
| L03 | Fisher re-analysed Darwin's 15 Zea mays differences in *The Design of Experiments* (1935); its 1935 demonstration made randomisation tests known | S2 ch. III; S3 abstract | first edition 1935, read in the 1937 edition |
| L04 | Fisher's t for the 15 differences is 2.148 on 14 degrees of freedom, against a 5% point of 2.145: significant, though barely | S2 §17 | normal model |
| L05 | Fisher counted the 2^15 = 32,768 sign assignments: 835 totals exceed 314 eighths, 28 equal it, 863 are at least as great; with the mirror image, 5.267% of the possibilities | S2 §21, Table 4 | sign assignments equally likely |
| L06 | Fisher put part of the small gap between the two tests down to the t distribution's continuity, which counts only half of the 28 tied totals | S2 §21 | — |
| L07 | Fisher: assigning the two sites of each pair at random, as by a coin, makes each pair's error enter the average with a positive or negative sign at equal and independent chances; the one flaw in Darwin's procedure was the absence of randomisation | S2 §20 | — |
| L08 | Fisher framed the general test as one of the wider hypothesis that the two series come from the same population, with no normality, made available by the physical act of randomisation | S2 §21 | — |
| L09 | Galton paired the tallest crossed plant with the tallest self-fertilised plant and so on; Fisher computed t = 5.171 for those differences, a value chance would exceed once or twice in 10,000 trials, and called the procedure a falsification | S2 §19; S1 p. 16 | — |
| L10 | Darwin Online's text transcription of Table XCVII prints 18 3/8 and 21 3/8 where the 1876 scans print 18 5/8 and 21 5/8; only the scans' values reproduce the printed totals 302.88 and 263.63 | S1 page scans 033 and 251 | transcription read 2026-11-23 |
| L11 | Permutation methods for exact inference date to Fisher in 1935 and are exact and distribution-free in situations the review describes | S6 abstract; S3 abstract | — |
| L12 | With m random permutations and B the count at least as extreme, B/m is uniform on 0, 1/m, ..., 1 under a continuous null, so a test at level alpha rejects with probability (floor(m alpha) + 1)/(m + 1), never below 1/(m + 1); the exact Monte Carlo p-value is (b + 1)/(m + 1) | S4 §§2, 4–5 | continuous statistic, distinct values |
| L13 | Genomic permutation p-values are often understated by about 1/m; with m = 1,000 permutations for each of 30,000 null genes about 30 p-values are exactly zero, and they survive any multiple-testing correction | S4 abstract, §3 | — |
| L14 | When permutations are drawn with replacement the exact p-value is slightly less than (b + 1)/(m + 1) | S4 §6 | — |
| L15 | A test using random permutations together with the identity is exact; earlier theory treated random permutations as approximate | S5 abstract | — |
| L16 | The randomisation construction rests on the data's distribution being invariant under a group of transformations; the two-sample permutation test of the mean difference is generally asymptotically valid as a test of equal means only with equal sample sizes; for medians it is generally invalid even with equal sizes | S7 abstract | asymptotic |
| L17 | The permutation distribution of the mean difference and its true sampling distribution have the same asymptotic variance only if the sample sizes are equal or the variances are equal | S8 §1, Example 2.1 | — |
| L18 | Janssen showed that a permutation test on the studentised difference of means attains asymptotic rejection probability alpha under unequal variances and sizes while keeping exact level alpha when the distributions are identical; Chung and Romano generalise it | S8 Example 2.1 (continued), abstract; S9 | asymptotic |
| L19 | In Chung and Romano's simulation (10,000 sets, 999 random permutations each), the permutation test of medians for N(0, 1) against N(0, 5) rejected 23.1% one-sided at 101 and 101 (nominal 5%); studentised, 6.2% | S8 §4, Table 1 | one-sided, alpha 0.05 |
| L20 | Mann and Whitney proposed U, from the relative ranks of x's and y's, to test the hypothesis that the two distributions are equal; Wilcoxon had proposed an equivalent test in 1945; the test is consistent against alternatives in which one variable is stochastically larger | S10 abstract; S11 | continuous distributions |
| L21 | The Mann–Whitney functional is P(X > Y) + ½P(X = Y); the WMW rule is consistent against alternatives where it differs from ½, but invalid under the nonparametric Behrens–Fisher hypothesis that it equals ½ with unequal distributions; Brunner and Munzel's studentised statistic is asymptotically valid there, and Neubert and Brunner's permutation version is exact when the distributions are equal | S12 §5.1 | — |
| L22 | The WMW procedure fails as a test of medians; what it tests is P(X1 < X2) + P(X1 = X2)/2, shown with real and constructed counterexamples | S13 abstract | — |
| L23 | Brunner and Munzel estimate the rank statistic's variance from overall and within-sample ranks, use a t distribution with Satterthwaite–Welch degrees of freedom for small samples, and find the WMW test conservative or liberal depending on the ratio of sample sizes and variances | S14 abstract | groups of 10 or more |
| L24 | Small differences in variances and moderate skewness move the WMW test's true significance level far from nominal; Brunner–Munzel's test is generally better | S15 abstract | — |
| L25 | Mann–Whitney's test assumes exchangeability; when it fails the test can mislead even in large samples; Brunner–Munzel controls type I error with similar power and is recommended as the default | S16 abstract | — |
| L26 | Hodges and Lehmann define point estimates of location and shift from rank test statistics such as Wilcoxon's; for a symmetric distribution the estimate is symmetric about, and so unbiased for, the parameter | S18 abstract | symmetric distribution for unbiasedness |
| L27 | With exact p-values, `wilcox.test(conf.int = TRUE)` returns the Hodges–Lehmann estimate and an exact interval by Bauer's algorithm; the one-sample estimate targets the pseudomedian, the median of (u + v)/2, which equals the median for a symmetric distribution; the two-sample estimate is the median of the difference between a draw from x and a draw from y, not the difference in medians | S27 `wilcox.test` help; S19 | exact case: n under 50, no ties |
| L28 | R's `wilcox.test` computes an exact p-value when the samples have fewer than 50 finite values and no ties, otherwise a normal approximation with continuity correction; its one-sample V is the sum of the positive ranks | S27 `wilcox.test` help and source | R 4.5.2 |
| L29 | The asymptotic Pitman efficiency of the two-sample Wilcoxon test relative to the t-test never falls below 0.864 for shifts of a continuous distribution; the same holds for Kruskal–Wallis against F and for the one-sample test of a symmetric distribution's centre | S17 abstract | location shift; local alternatives |
| L30 | The ARE of WMW to t is 12 sigma^2 (integral of f^2)^2; it is 3/pi = 0.955 for the normal; the density 3(5 − y^2)/(20 sqrt 5) on abs(y) below sqrt 5 attains the minimum 108/125 = 0.864; for t with d degrees of freedom WMW is more efficient when d is at most 18 and the ARE grows without bound as d approaches 2 | S12 §5.3 | location shift |
| L31 | Spearman's rank correlation is due to Spearman (1904) and Kendall's tau to Kendall (1938) | S20; S21 | attribution |
| L32 | Kruskal and Wallis rank all observations together and compare the C rank sums; H is approximately chi-squared on C − 1 degrees of freedom when the samples come from one population | S22 abstract | not too small samples |
| L33 | A permutation test on the sample correlation is exact for independence, but as a test of zero correlation its rejection probability can be far from nominal; studentising the correlation fixes that asymptotically | S23 abstract | — |
| L34 | R's `cor.test` computes Spearman's p by AS 89, exact for n below 10 and an Edgeworth series above; Kendall's p is exact for n below 50 without ties | S27 `cor.test` help and source; S24 | R 4.5.2 |
| L35 | Kruskal–Wallis in R and SciPy refers H to the chi-squared distribution | S27 `kruskal.test.default`; S25 | — |
| L36 | SciPy's `permutation_test` defaults to 9,999 resamples; it enumerates exactly when the distinct permutations number no more than `n_resamples`, otherwise samples randomly and adds one to the count and the denominator (citing Phipson and Smyth); two-sided p is twice the smaller one-sided p; ties within a relative tolerance of 100 machine epsilons count as equal; with one sample and `permutation_type='samples'` it flips signs | S25 `_resampling.py` | SciPy 1.18.1 |
| L37 | SciPy's `mannwhitneyu` uses its exact method only when one sample has 8 or fewer values and there are no ties; otherwise the normal approximation with continuity correction; its statistic is U for the first sample | S25 `_mannwhitneyu.py`; S26 | SciPy 1.18.1 |
| L38 | SciPy's `wilcoxon` reports, for a two-sided test, the smaller of the two rank sums; `method='auto'` uses the asymptotic method above 50 differences | S25 `_wilcoxon.py`, `_morestats.py` | SciPy 1.18.1 |
| L39 | SciPy's `spearmanr` p-value comes from a t approximation; `kendalltau` is exact when there are no ties and n is 33 or less; `brunnermunzel` refers its statistic to a t distribution by default | S25 `_stats_py.py`, `_correlation.py` | SciPy 1.18.1 |
| L40 | The law-school sample: 15 American law schools' average LSAT and undergraduate GPA, Efron and Tibshirani's example, BSD 3-clause via CRAN `bootstrap` | S28; Part 7's lab CSV | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S1 | Table XCVII, page 234 (scan) | Worked example / L01 | shows Darwin's own numbers | the 1876 text is public domain, but the scan carries Darwin Online's notice and its reuse terms were not verified | https://darwin-online.org.uk/ | do not reuse; Figure 1 plots the same numbers with the pairs and differences drawn |
| F2 | S4 | Figure A (size of B/m against nominal alpha, m = 20) | When is a permutation test exact? / L12 | the staircase above the diagonal | arXiv non-exclusive licence, not a reuse licence | https://arxiv.org/abs/1603.05766 | do not reuse; our Figure 4 computes the family-wise consequence instead |
| F3 | S12 | Figure 4 (normal, scaled t with 18 df, the minimum-ARE density) | What do ranks cost? / L30 | the three shapes beside each other | licence not verified on the PMC page | https://pmc.ncbi.nlm.nih.gov/articles/PMC2857732/ | do not reuse; our Figure 9 measures power instead |

## Open questions

- Fisher's continuity-adjusted t: he prints 2.139 (one-sided 2.529%); rescaling t by 313/314 gives 2.1412 (2.517%). The
  article does not quote the adjusted value.
- Jacquez and Jacquez 2002 argue about whether Darwin's pairs were true paired comparisons; only its title was seen, so
  it is not cited.
- Pitman's 1948 lecture notes, where 3/pi first appears, have no bibliographic record; the article attributes the
  value through Fay and Proschan and Hodges and Lehmann.
