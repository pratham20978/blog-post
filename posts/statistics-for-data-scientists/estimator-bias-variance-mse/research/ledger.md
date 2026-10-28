# Source ledger — estimator-bias-variance-mse

Series `statistics-for-data-scientists`, Part 3. Research run 2026-10-28, inline (no agents). Every row was
read at the URL given unless the Source cell says otherwise. Numbers the post calls **measured** come from
the lab (`lab/estimators.py`, `captures.json`) and carry no key here; every quoted fact, date, published
number and named result does. Pages behind bot checks were logged as blocked, not worked around.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Efron, B. & Morris, C., "Data analysis using Stein's estimator and its generalizations" (read in full: the JSTOR copy a McGill course page hosts, retrieved from its 2025 Wayback snapshot because the live page now returns 404) | Journal of the American Statistical Association 70(350):311–319 | 1975 | 10.1080/01621459.1975.10479864 | peer-reviewed | https://web.archive.org/web/20250819192305/http://www.medicine.mcgill.ca/epidemiology/hanley/bios602/MultiLevelData/EfronMorrisJASA1975.pdf | 2026-10-28 |
| S2 | T1 | Efron, B. & Morris, C., "Stein's paradox in statistics" (pp. 119–123 read as page images of the scan on Efron's Stanford page, via its 2021 Wayback snapshot; a magazine article by S1's authors, not peer-reviewed: every number the post quotes from it is recomputed by the lab or checked against S1) | Scientific American 236(5):119–127 | 1977 | 10.1038/scientificamerican0577-119 | practitioner | https://web.archive.org/web/20210507182709/https://statweb.stanford.edu/~ckirby/brad/other/Article1977.pdf | 2026-10-28 |
| S3 | T1 | James, W. & Stein, C., "Estimation with quadratic loss" (§1–2 read, UC Berkeley's digital archive of the symposium; Project Euclid served a bot check) | Proceedings of the Fourth Berkeley Symposium on Mathematical Statistics and Probability 1:361–379 | 1961 | Project Euclid euclid.bsmsp/1200512173 | peer-reviewed | https://digitalassets.lib.berkeley.edu/math/ucb/text/math_s4_v1_article-19.pdf | 2026-10-28 |
| S4 | T1 | Stein, C., "Inadmissibility of the usual estimator for the mean of a multivariate normal distribution" (§1 read, UC Berkeley's digital archive) | Proceedings of the Third Berkeley Symposium on Mathematical Statistics and Probability 1:197–206 | 1956 | 10.1525/9780520313880-018 | peer-reviewed | https://digitalassets.lib.berkeley.edu/math/ucb/text/math_s3_v1_article-15.pdf | 2026-10-28 |
| S5 | T1 | Ruggles, R. & Brodie, H., "An empirical approach to economic intelligence in World War II" (not read: Taylor & Francis and JSTOR only, no open copy; its table and method are taken from S6 and S7, which reproduce it and agree) | Journal of the American Statistical Association 42(237):72–91 | 1947 | 10.1080/01621459.1947.10501915 | peer-reviewed | https://doi.org/10.1080/01621459.1947.10501915 | 2026-10-28 |
| S6 | T1 | Simon, C. M., "A Bayesian treatment of the German tank problem" (read as arXiv v2, §1; published open access) | The Mathematical Intelligencer 46(2):117–127 | 2024 | 10.1007/s00283-023-10274-6 | peer-reviewed | https://arxiv.org/abs/2301.00046 | 2026-10-28 |
| S7 | T1 | Miller, S. J., Sharma, K. & Yang, A., "The German tank problem with multiple factories" (§1–2.1 read, the published PDF on NSF's public-access repository) | The PUMP Journal of Undergraduate Research 7:231–257 | 2024 | 10.46787/pump.v7i0.4249 | peer-reviewed | https://par.nsf.gov/servlets/purl/10580624 | 2026-10-28 |
| S8 | T1 | Clark, G., Gonye, A. & Miller, S. J., "Lessons from the German tank problem" (read as arXiv v2; its comparison table is reproduced from a wiki, so it is not used for the numbers) | The Mathematical Intelligencer 43(4):19–28 | 2021 | 10.1007/s00283-021-10082-w | peer-reviewed | https://arxiv.org/abs/2101.08162 | 2026-10-28 |
| S9 | T1 | Goodman, L. A., "Serial number analysis" (not read: Taylor & Francis only; cited for attribution through S6 and S7) | Journal of the American Statistical Association 47(260):622–634 | 1952 | 10.1080/01621459.1952.10483442 | peer-reviewed | https://doi.org/10.1080/01621459.1952.10483442 | 2026-10-28 |
| S10 | T1 | Robert, C. P. & Roberts, G. O., "Rao–Blackwellisation in the Markov chain Monte Carlo era" (§1 read as arXiv v1) | International Statistical Review 89(2):237–249 | 2021 | 10.1111/insr.12463 | peer-reviewed | https://arxiv.org/abs/2101.01011 | 2026-10-28 |
| S11 | T1 | Blackwell, D., "Conditional expectation and unbiased sequential estimation" (not read: Project Euclid served an Incapsula bot check to curl and nothing to WebFetch; cited for attribution through S10) | The Annals of Mathematical Statistics 18(1):105–110 | 1947 | 10.1214/aoms/1177730497 | peer-reviewed | https://doi.org/10.1214/aoms/1177730497 | 2026-10-28 |
| S12 | T1 | Brown, L. D., "In-season prediction of batting averages: a field test of empirical Bayes and Bayes methodologies" (§1 read as arXiv v1, which carries the published pagination note) | The Annals of Applied Statistics 2(1):113–152 | 2008 | 10.1214/07-AOAS138 | peer-reviewed | https://arxiv.org/abs/0803.3697 | 2026-10-28 |
| S13 | T1 | Morris, C. N. & Lysy, M., "Shrinkage estimation in multilevel normal models" (abstract and §1 read as arXiv v1) | Statistical Science 27(1):115–134 | 2012 | 10.1214/11-STS363 | peer-reviewed | https://arxiv.org/abs/1203.5610 | 2026-10-28 |
| S14 | T1 | Stigler, S. M., "The 1988 Neyman Memorial Lecture: a Galtonian perspective on shrinkage estimators" (abstract only, via OpenAlex; Project Euclid blocked) | Statistical Science 5(1):147–155 | 1990 | 10.1214/ss/1177012274 | peer-reviewed | https://doi.org/10.1214/ss/1177012274 | 2026-10-28 |
| S15 | T1 | Benhamou, E., "A few properties of sample variance" (§2 read, eq. 10) | arXiv | 2018 | arXiv:1809.03774v1 | preprint | https://arxiv.org/abs/1809.03774 | 2026-10-28 |
| S16 | T1 | Student, "The probable error of a mean" (§I read, the University of York's transcription; already read in full for Part 2) | Biometrika 6(1):1–25 | 1908 | 10.1093/biomet/6.1.1 | peer-reviewed | https://www.york.ac.uk/depts/maths/histstat/student.pdf | 2026-10-28 |
| S17 | T2 | Arel-Bundock, V., Rdatasets: `pscl::EfronMorris` CSV and its documentation (an independent transcription of S1's Table 1, used to cross-check ours) | Rdatasets | 2026 | — | source | https://vincentarelbundock.github.io/Rdatasets/doc/pscl/EfronMorris.html | 2026-10-28 |
| S18 | T2 | NumPy 2.5 documentation, "Parallel random number generation" (`SeedSequence`) | NumPy | 2026 | — | official-docs | https://numpy.org/doc/stable/reference/random/parallel.html | 2026-10-28 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | title.search for the plan's key sources: "empirical approach to economic intelligence", "serial number analysis", "some practical techniques in serial number analysis", "estimation with quadratic loss", "inadmissibility of the usual estimator for the mean of a multivariate normal", "data analysis using Stein's estimator", "Stein's paradox in statistics", "Stein's estimation rule and its competitors" | DOIs and venues for Ruggles and Brodie 1947 (52 citations), Goodman 1952 and 1954, Stein 1956 (UC Press DOI), Efron and Morris 1973, 1975 (843 citations) and 1977; James and Stein 1961 only as its Springer reprint; no open copy flagged for any |
| 2 | 1 | OpenAlex | title.search: "conditional expectation and unbiased sequential estimation", "simple method for improving some estimators", "inadmissibility of the usual estimator for the variance", "simple approximation for unbiased estimation of the standard deviation", "Galtonian perspective on shrinkage estimators", "in-season prediction of batting averages", "lessons from the german tank problem", "estimating the size of a population" | Blackwell 1947 and Goodman 1953 (Project Euclid links), Stein 1964 (Springer, no open copy), Gurland and Tripathi 1971, Stigler 1990, Brown 2008 (open), Clark et al. 2021 (open on arXiv), Johnson 1994 |
| 3 | 1 | Google Scholar | "empirical approach to economic intelligence in world war II" | HTTP 403 for the session; logged as blocked |
| 4 | 1 | Project Euclid | PDF and article pages for Goodman 1953, Blackwell 1947 and James and Stein 1961, by curl and by WebFetch | an Incapsula bot check to curl, an empty page to WebFetch; logged as blocked, not worked around |
| 5 | 1 | Web search | Ruggles Brodie 1947 economic intelligence pdf tanks serial numbers | no open copy of the paper (one unauthorised upload, not used); pointed to Simon 2023 and Miller, Sharma and Yang 2024, which reproduce its table |
| 6 | 1 | Web search | Efron Morris "Stein's paradox in statistics" 1977 pdf; Efron Morris 1975 "data analysis using Stein's estimator" pdf | the scan on Efron's Stanford page (404 live, 2021 Wayback snapshot read) and a McGill course copy of the 1975 paper (404 live, 2025 Wayback snapshot read) |
| 7 | 1 | Web search | digitalassets.lib.berkeley.edu James Stein "Estimation with quadratic loss" | only the Project Euclid link; scanning the archive's article numbers then found James and Stein 1961 (Fourth Symposium, article 19) and Stein 1956 (Third Symposium, article 15) |
| 8 | 2 | OpenAlex | abstracts of Guglielmo 2008, Stigler 1990, Gurland and Tripathi 1971, Johnson 1994 | Stigler's abstract (Stein's paradox as Galton's regression); Guglielmo's abstract does not mention serial numbers; the other two carry no usable abstract |
| 9 | 1 | OpenAlex | forward chase: works citing Ruggles and Brodie 1947 | 53 citing works: Goodman 1952, Guglielmo 2008 (economists in WWII intelligence), and applications in ecology, networks and auctions; no correction of the 1947 comparison |
| 10 | 1 | OpenAlex | forward chase: works citing Efron and Morris 1975 with "batting" or "shrinkage" in the title | Brown 2008 (a field test on the 2005 season), later batting models, and 71 shrinkage papers led by Morris and Lysy 2012, a review of shrinkage in multilevel normal models |
| 11 | 1 | arXiv | ti:"german tank"; all:"Stein paradox"; ti:"James-Stein" AND ti:review; ti:shrinkage AND ti:review AND ti:estimation | six German-tank papers (Clark et al. 2021, Simon 2022, Miller et al. 2024, a 2022 generalisation, a 2019 order-statistics case study, a 2026 note); Stein-paradox papers on PCA, covariance and RL baselines; no review titled for James–Stein |
| 12 | 1 | Crossref | Ruggles Brodie 1947; Goodman serial number analysis 1952; Efron Morris Stein's paradox | confirmed JASA 42(237):72–91 and its 1999 reprint chapter, JASA 47(260):622–634, and Scientific American 236(5):119–127 |
| 13 | 1 | Semantic Scholar | citations of Efron and Morris 1975 and of Ruggles and Brodie 1947 (graph API) | answered this session: 2026 batting and shrinkage applications for the first; for the second Simon 2022, Miller et al. 2024, a 2023 study of conflict-loss estimation and a 2024 note on Leo Goodman |
| 14 | 4 | Web search | Stein 1964 inadmissibility of the usual variance estimator, ism.ac.jp | no open copy; Kubokawa's 1998 review abstract (CIRJE) states the inadmissibility result loosely; ISM's archive returned 404 and DTIC 403; the post does not claim it |
| 15 | 3 | Web search | variance of the sample variance in terms of excess kurtosis | Benhamou 2018 (arXiv) eq. 10 for i.i.d. data; O'Neill 2014 (TAS) paywalled |
| 16 | 2 | Rdatasets | `pscl::EfronMorris` CSV and documentation | the 18 players with hits in 45 at-bats, remaining at-bats and rest-of-season averages; every value equals our transcription of S1's Table 1 |
| 17 | 4 | Web search | CASI (Efron and Hastie 2016) PDF, chapter 7 on James–Stein and baseball | the book's site no longer links the PDF (404 at both known paths); not used |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | From 1943, Allied economic intelligence read serial numbers on the chassis, engines, gearboxes and bogie wheels of captured German tanks, and from captured records, to estimate tank production | S6 §1.1 (citing S5) | S5 not read; two reproductions agree |
| L02 | Conventional production estimates (extrapolating prewar capacity, secret reports, prisoner interrogation) were unreliable or contradictory | S6 §1.1 | as summarised by S6 from S5 |
| L03 | Monthly German tank production: June 1940, intelligence 1,000, serial-number analysis 169, German records 122; June 1941, 1,550, 244 and 271; August 1942, 1,550, 327 and 342 | S6 Table 1; S7 Fig. 1 (both from S5) | S5 not read; the two reproductions print identical numbers |
| L04 | Gearbox serial numbers ran in one unbroken sequence; chassis numbers came in blocks per model, leaving gaps | S6 §1.1 note 2 | as summarised by S6 |
| L05 | The textbook German tank problem: serial numbers 1 to N, k tanks captured without replacement, every tank equally likely to be captured; its maximum likelihood estimator is the largest serial number seen, which can never exceed N and so is biased low | S6 §1.2–1.3; S7 §1 | the three assumptions as stated |
| L06 | Goodman (1952) derived the minimum-variance unbiased estimator m + m/k − 1, and a confidence interval for N | S6 §1.3; S7 §1 (citing S9) | S9 not read |
| L07 | The sample maximum is a complete sufficient statistic: given it, the other k − 1 serial numbers are a uniformly random subset of 1 to m − 1, whatever N is; so m(1 + 1/k) − 1 is the unique minimum-variance unbiased estimator (Lehmann–Scheffé) | S7 §2.1, eqs. 2.7–2.8, Theorem 2.3 | sampling without replacement from 1 to N |
| L08 | The variance of m(1 + 1/k) − 1 is (N + 1)(N − k)/(k(k + 2)) | S7 Remark 2.2 | same model |
| L09 | The Rao–Blackwell theorem (Rao 1945, Blackwell 1947): replacing an estimator by its conditional expectation given a sufficient statistic improves it under any convex loss | S10 §1 (attribution to S11) | S11 not read |
| L10 | For independent normal observations with known unit variance, estimating each mean by its own observation is admissible under total squared error when there are one or two means, and inadmissible from three | S4 §1 | known variance; loss is the sum of squared errors |
| L11 | James and Stein's estimator (1 − (p − 2)/‖X‖²)X has smaller total risk than X for every mean vector when p ≥ 3; its risk is p − (p − 2)² E[1/(p − 2 + 2K)] with K Poisson with mean ‖ξ‖²/2, equal to 2 at ξ = 0 and rising toward p | S3 §2, eqs. (5)–(6) | X normal with identity covariance |
| L12 | Among unbiased estimators, and among translation-invariant ones, X has the smallest risk at every mean | S3 §2 | same setting |
| L13 | Efron and Morris took the 18 players with exactly 45 official at-bats in the New York Times of 26 April or 3 May 1970, so that all had equal variances, and chose the sample to include an unusually good hitter, Clemente; the task was to predict each player's average over the rest of the season | S1 §2 | 1970 season |
| L14 | Their method: transform each average by √45 · arcsin(2y − 1) to stabilise its variance near 1, then shrink toward the grand mean with constant k − 3; their shrinkage estimate (k − 3)/V was 0.791 | S1 §2, eqs. 2.1, 2.3, 2.5 | arcsine scale; equal at-bats |
| L15 | On the transformed scale the total squared prediction error was 17.56 for the separate averages and 5.01 for Stein's rule, an efficiency of 3.50; Stein's rule was closer for 15 players and worse for Clemente, Swoboda and Rodriguez | S1 §2 | against rest-of-season averages treated as the truth |
| L16 | The 1975 text prints the grand mean of the transformed averages as −3.275 and the rule as 0.209 X − 2.59; its Table 2 estimates match the column mean, −3.317 | S1 eq. 2.5 and Table 2 (checked by the lab) | a printing slip in the text; the tables are consistent |
| L17 | John Tukey said at the 1972 American Statistical Association meeting that the savings from such estimators would not exceed ten percent in practice | S1 §1 | as reported by Efron and Morris |
| L18 | The 1977 article's raw-scale rule: z = ȳ + c(y − ȳ) with grand average ȳ = 0.265 and shrinking factor c = 0.212; Clemente's 0.400 becomes 0.294 and Munson's 0.178 becomes 0.247 | S2 p. 119 | raw batting averages, equal at-bats |
| L19 | The 1977 article prints total squared errors of 0.077 for the averages and 0.022 for the James–Stein estimates, 3.5 times as accurate, with the James–Stein estimate closer for 16 of 18 players | S2 p. 121 | recomputed by the lab as 0.0753 and 0.0213 from S1's table |
| L20 | The shrinking factor is c = 1 − (k − 3)σ²/Σ(y − ȳ)², with σ² the variance of one average | S2 p. 123 | equal variances |
| L21 | Stein proved in 1955 that the average is inadmissible for very many means; James and Stein's 1961 paper extended it to every k above 2 with an explicit estimator; for one mean, admissibility of the average was proved in 1950 | S2 p. 122 | as narrated by the authors |
| L22 | Lumping an unrelated proportion (9 imported cars among 45, 0.200) with the 18 players gives it a James–Stein estimate of 0.251 | S2 p. 121 | an illustration of the theorem's indifference to meaning |
| L23 | Brown's field test on the 2005 season: the naive predictor, each player's current average, was the poorest of the methods in every situation; separating pitchers from other players mattered, and one heteroscedastic variant of Efron and Morris's rule did worst among the shrinkage methods | S12 §1, A1–A4 | 2005 MLB data; players with more than 10 first-stage at-bats |
| L24 | The improvement holds when shrinking toward any fixed point, and unequal variances complicate the picture | S13 abstract | k ≥ 3 normal means |
| L25 | Seen as Galton's regression toward the mean, Stein's paradox is transparent | S14 abstract | abstract only |
| L26 | For i.i.d. data the sample variance (divisor n − 1) has variance μ₄/n − (n − 3)σ⁴/(n(n − 1)), which is 2σ⁴/(n − 1) for normal data | S15 eq. 10 | i.i.d., finite fourth moment; a preprint |
| L27 | For normal samples Student found the distribution of s² (a Pearson Type III curve, today a scaled chi-squared) and from it the distribution of s | S16 §I | normal data |
| L28 | NumPy builds independent streams from a list of integers through SeedSequence | S18 | NumPy 2.5 |
| L29 | The rest-of-season averages are themselves estimates; accounting for their error would favour Stein's rule further | S1 note 3 | Efron and Morris's argument |
| L30 | The 1977 article states that 3.5 is close to the expected ratio of the two total squared errors for these data, so the result was not luck | S2 p. 121 | the authors' calculation, not shown |
| L31 | When the first serial number is unknown, (max − min)(1 + 2/(k − 1)) − 1 is an unbiased estimator of N | S8 §3 | serials consecutive from an unknown start; k ≥ 2 |
| L32 | If the true means are themselves normal around a common mean with variance τ², the Bayes estimate shrinks each observation toward that mean by the noise share 1/(1 + τ²); estimating that share from the spread of the observations gives the James–Stein rule, an empirical Bayes estimator | S1 §1, eqs. 1.7–1.10 | unit-variance noise; equal variances |
| L33 | Efron and Morris's limited-translation rule caps how far any one estimate may move; for k = 18 it reduces the maximum component risk from 4.60 (Stein's rule) to 1.52, in units of the separate estimate's risk, while keeping 80% of Stein's saving over the separate estimates | S1 §2 | unit-variance normal means, k = 18, s = 0.8; a worst case over θ, not the batting data's realised errors |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S2 | the bar chart on p. 120 (each player's initial average, season average and James–Stein estimate, with squared errors) | Stein's paradox / L19 | it shows the 16-of-18 result per player | Scientific American copyright; no licence or permission | https://doi.org/10.1038/scientificamerican0577-119 | do not reuse; our Figure 9 plots the same data as a regression, which adds the truth line and the slope |
| F2 | S2 | the shrinkage diagram on p. 121 (lines from observed averages to James–Stein estimates) | Stein's paradox / L18 | it shows every average pulled 79% toward 0.265 | Scientific American copyright; no licence | same | do not reuse; not redrawn either, to avoid a lookalike |
| F3 | S6 | Table 1 (Ruggles and Brodie's three months) | Worked example / L03 | the numbers, not a picture | the article is open access, but it is a table of facts | https://doi.org/10.1007/s00283-023-10274-6 | draw our own chart from the numbers (Figure 4) |
| F4 | S8 | Figure 2 (the same comparison) | Worked example / L03 | — | reproduced from a wiki, provenance unclear | https://arxiv.org/abs/2101.08162 | do not reuse |

## Open questions

- Ruggles and Brodie 1947 was not read. Its table rests on two reproductions (S6, S7) that print identical
  numbers; what exactly was counted (all tank types, or one) is not stated in either.
- The 1977 article prints total squared errors of 0.077 and 0.022. Recomputed from the 1975 table they are
  0.0753 and 0.0213 (0.0754 from the printed averages, 0.0591 and 0.0179 against full-season averages).
  No variant tried reproduces 0.077; the ratio, 3.5, agrees either way. The post quotes both.
- The 1975 table prints "Williams (Chi, AL)" while the 1977 figure names Billy Williams. It does not change
  any number; the lab keeps the 1975 table's labels.
- Stein's 1964 result that even the best divisor can be beaten when the mean is unknown was not read (no
  open copy); the post does not claim it.
