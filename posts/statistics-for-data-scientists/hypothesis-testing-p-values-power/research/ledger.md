# Source ledger — hypothesis-testing-p-values-power

Part 5 of *Statistics for Data Scientists*. Researched 2026-10-29, inline (no agents). Numbers the article
calls measured come from `lab/testing.py` and need no key; every published number, date, attribution and
named result carries one below. Several central papers are paywalled: those are cited for what their
abstracts state, no further, and each row says so. Every published number quoted in the article was
recomputed by the lab before it was used (Gelman & Carlin's retrodesign values, Ioannidis's Table 4,
Colquhoun's likelihood ratios, Cumming's p interval), and the article says where a printed value does not
reproduce.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Wasserstein, R. L. & Lazar, N. A., "The ASA statement on p-values: context, process, and purpose" (the six principles read in the ASA's release of the statement; the journal PDF served a bot page) | The American Statistician 70(2):129–133 | 2016 | 10.1080/00031305.2016.1154108 | standard | https://www.amstat.org/asa/files/pdfs/P-ValueStatement.pdf | 2026-10-29 |
| S2 | T1 | Wasserstein, R. L., Schirm, A. L. & Lazar, N. A., "Moving to a world beyond p below 0.05" (editorial; abstract record only) | The American Statistician 73(sup1):1–19 | 2019 | 10.1080/00031305.2019.1583913 | source | https://doi.org/10.1080/00031305.2019.1583913 | 2026-10-29 |
| S3 | T1 | Benjamini, Y., De Veaux, R. D., Efron, B., Evans, S., Glickman, M., Graubard, B. I. et al., "The ASA president's task force statement on statistical significance and replicability" (abstract) | The Annals of Applied Statistics 15(3):1084–1085 | 2021 | 10.1214/21-AOAS1501 | standard | https://doi.org/10.1214/21-AOAS1501 | 2026-10-29 |
| S4 | T1 | Fisher, R. A., *Statistical Methods for Research Workers*, 1st ed., ch. III (public domain; the Classics in the History of Psychology transcription) | Oliver and Boyd, Edinburgh | 1925 | — | standard | https://psychclassics.yorku.ca/Fisher/Methods/chap3.htm | 2026-10-29 |
| S5 | T1 | Neyman, J. & Pearson, E. S., "On the problem of the most efficient tests of statistical hypotheses" (abstract; the publisher's PDF served a bot page) | Philosophical Transactions of the Royal Society A 231:289–337 | 1933 | 10.1098/rsta.1933.0009 | peer-reviewed | https://doi.org/10.1098/rsta.1933.0009 | 2026-10-29 |
| S6 | T1 | Lehmann, E. L., "The Fisher, Neyman-Pearson theories of testing hypotheses: one theory or two?" (abstract) | Journal of the American Statistical Association 88(424):1242–1249 | 1993 | 10.1080/01621459.1993.10476404 | peer-reviewed | https://doi.org/10.1080/01621459.1993.10476404 | 2026-10-29 |
| S7 | T1 | Hubbard, R. & Bayarri, M. J., "Confusion over measures of evidence (p's) versus errors (α's) in classical statistical testing" (abstract) | The American Statistician 57(3):171–178 | 2003 | 10.1198/0003130031856 | peer-reviewed | https://doi.org/10.1198/0003130031856 | 2026-10-29 |
| S8 | T1 | Goodman, S. N., "Toward evidence-based medical statistics. 1: The P value fallacy" (abstract) | Annals of Internal Medicine 130(12):995–1004 | 1999 | 10.7326/0003-4819-130-12-199906150-00008 | peer-reviewed | https://doi.org/10.7326/0003-4819-130-12-199906150-00008 | 2026-10-29 |
| S9 | T1 | Greenland, S., Senn, S. J., Rothman, K. J., Carlin, J. B., Poole, C., Goodman, S. N. & Altman, D. G., "Statistical tests, P values, confidence intervals, and power: a guide to misinterpretations" (full text, CC BY 4.0, Europe PMC PMC4877414) | European Journal of Epidemiology 31(4):337–350 | 2016 | 10.1007/s10654-016-0149-3 | peer-reviewed | https://europepmc.org/article/PMC/PMC4877414 | 2026-10-29 |
| S10 | T1 | Nickerson, R. S., "Null hypothesis significance testing: a review of an old and continuing controversy" (the review the sweep started from; abstract) | Psychological Methods 5(2):241–301 | 2000 | 10.1037/1082-989X.5.2.241 | peer-reviewed | https://doi.org/10.1037/1082-989X.5.2.241 | 2026-10-29 |
| S11 | T1 | Hung, H. M. J., O'Neill, R. T., Bauer, P. & Köhne, K., "The behavior of the p-value when the alternative hypothesis is true" (abstract) | Biometrics 53(1):11–22 | 1997 | 10.2307/2533093 | peer-reviewed | https://doi.org/10.2307/2533093 | 2026-10-29 |
| S12 | T1 | Murdoch, D. J., Tsai, Y.-L. & Adcock, J., "P-values are random variables" (abstract) | The American Statistician 62(3):242–245 | 2008 | 10.1198/000313008X332421 | peer-reviewed | https://doi.org/10.1198/000313008X332421 | 2026-10-29 |
| S13 | T1 | Cumming, G., "Replication and p intervals: p values predict the future only vaguely, but confidence intervals do much better" (abstract) | Perspectives on Psychological Science 3(4):286–300 | 2008 | 10.1111/j.1745-6924.2008.00079.x | peer-reviewed | https://doi.org/10.1111/j.1745-6924.2008.00079.x | 2026-10-29 |
| S14 | T1 | Hoenig, J. M. & Heisey, D. M., "The abuse of power: the pervasive fallacy of power calculations for data analysis" (abstract) | The American Statistician 55(1):19–24 | 2001 | 10.1198/000313001300339897 | peer-reviewed | https://doi.org/10.1198/000313001300339897 | 2026-10-29 |
| S15 | T1 | Gelman, A. & Carlin, J., "Beyond power calculations: assessing type S (sign) and type M (magnitude) errors" (full text, the author's copy; © the authors, SAGE) | Perspectives on Psychological Science 9(6):641–651 | 2014 | 10.1177/1745691614551642 | peer-reviewed | http://www.stat.columbia.edu/~gelman/research/published/retropower_final.pdf | 2026-10-29 |
| S16 | T1 | Lu, J., Qiu, Y. & Deng, A., "A note on Type S/M errors in hypothesis testing" (read as the PsyArXiv preprint 10.31234/osf.io/n53zs) | British Journal of Mathematical and Statistical Psychology 72(1):1–17 | 2019 | 10.1111/bmsp.12132 | peer-reviewed | https://osf.io/n53zs/ | 2026-10-29 |
| S17 | T1 | Lakens, D., Mesquida, C., Xavier-Quintais, G., Rasti, S., Toffalini, E. & Altoè, G., "Rethinking type S and type M errors" (abstract) | Advances in Methods and Practices in Psychological Science 9(2) | 2026 | 10.1177/25152459261432530 | peer-reviewed | https://doi.org/10.1177/25152459261432530 | 2026-10-29 |
| S18 | T1 | van Zwet, E. W. & Cator, E. A., "The significance filter, the winner's curse and the need to shrink" (abstract; CC BY-NC-ND) | Statistica Neerlandica 75(4):437–452 | 2021 | 10.1111/stan.12241 | peer-reviewed | https://doi.org/10.1111/stan.12241 | 2026-10-29 |
| S19 | T1 | Ioannidis, J. P. A., "Why most discovered true associations are inflated" (abstract) | Epidemiology 19(5):640–648 | 2008 | 10.1097/EDE.0b013e31818131e7 | peer-reviewed | https://doi.org/10.1097/EDE.0b013e31818131e7 | 2026-10-29 |
| S20 | T1 | Durante, K. M., Rae, A. & Griskevicius, V., "The fluctuating female vote: politics, religion, and the ovulatory cycle" (abstract; its estimate and p-value as Gelman & Carlin report them) | Psychological Science 24(6):1007–1016 | 2013 | 10.1177/0956797612466416 | peer-reviewed | https://doi.org/10.1177/0956797612466416 | 2026-10-29 |
| S21 | T1 | Kanazawa, S., "Beautiful parents have more daughters: a further implication of the generalized Trivers–Willard hypothesis" (not read; as Gelman & Carlin report it) | Journal of Theoretical Biology 244(1):133–140 | 2007 | 10.1016/j.jtbi.2006.07.017 | peer-reviewed | https://doi.org/10.1016/j.jtbi.2006.07.017 | 2026-10-29 |
| S22 | T1 | Open Science Collaboration, "Estimating the reproducibility of psychological science" (abstract; the Tilburg postprint sits behind a Cloudflare check) | Science 349(6251):aac4716 | 2015 | 10.1126/science.aac4716 | peer-reviewed | https://doi.org/10.1126/science.aac4716 | 2026-10-29 |
| S23 | T3 | Reproducibility Project: Psychology, `rpp_data.csv`, OSF project ezcuj, component ytpuq, CC0 1.0 (file modified 2015-09-11, sha256 4d87a2636181…) | Open Science Framework | 2015 | osf.io/fgjvw | source | https://osf.io/fgjvw/ | 2026-10-29 |
| S24 | T3 | Hartgerink, C. H. J., van Aert, R. C. M. & van Assen, M. A. L. M., `masterscript.R`, the project's analysis script (no licence file in the repository; read, not shipped) | GitHub CenterForOpenScience/rpp | 2015 | — | source | https://raw.githubusercontent.com/CenterForOpenScience/rpp/master/masterscript.R | 2026-10-29 |
| S25 | T1 | Gilbert, D. T., King, G., Pettigrew, S. & Wilson, T. D., "Comment on 'Estimating the reproducibility of psychological science'" (abstract) | Science 351(6277):1037 | 2016 | 10.1126/science.aad7243 | peer-reviewed | https://doi.org/10.1126/science.aad7243 | 2026-10-29 |
| S26 | T1 | Anderson, C. J., Bahník, Š., Barnett-Cowan, M. et al., "Response to comment on 'Estimating the reproducibility of psychological science'" (abstract) | Science 351(6277):1037 | 2016 | 10.1126/science.aad9163 | peer-reviewed | https://doi.org/10.1126/science.aad9163 | 2026-10-29 |
| S27 | T1 | Ioannidis, J. P. A., "Why most published research findings are false" (full text, CC BY) | PLoS Medicine 2(8):e124 | 2005 | 10.1371/journal.pmed.0020124 | peer-reviewed | https://doi.org/10.1371/journal.pmed.0020124 | 2026-10-29 |
| S28 | T1 | Goodman, S. & Greenland, S., "Why most published research findings are false: problems in the analysis" (full text, CC BY, Europe PMC PMC1855693) | PLoS Medicine 4(4):e168 | 2007 | 10.1371/journal.pmed.0040168 | peer-reviewed | https://doi.org/10.1371/journal.pmed.0040168 | 2026-10-29 |
| S29 | T1 | Jager, L. R. & Leek, J. T., "An estimate of the science-wise false discovery rate and application to the top medical literature" (abstract) | Biostatistics 15(1):1–12 | 2014 | 10.1093/biostatistics/kxt007 | peer-reviewed | https://doi.org/10.1093/biostatistics/kxt007 | 2026-10-29 |
| S30 | T1 | Colquhoun, D., "An investigation of the false discovery rate and the misinterpretation of p-values" (full text, CC BY 4.0, Europe PMC PMC4448847) | Royal Society Open Science 1(3):140216 | 2014 | 10.1098/rsos.140216 | peer-reviewed | https://europepmc.org/article/PMC/PMC4448847 | 2026-10-29 |
| S31 | T1 | Colquhoun, D., "The reproducibility of research and the misinterpretation of p-values" (full text, CC BY 4.0, Europe PMC PMC5750014) | Royal Society Open Science 4(12):171085 | 2017 | 10.1098/rsos.171085 | peer-reviewed | https://europepmc.org/article/PMC/PMC5750014 | 2026-10-29 |
| S32 | T1 | Benjamin, D. J., Berger, J. O., Johannesson, M., Nosek, B. A., Wagenmakers, E.-J. et al., "Redefine statistical significance" (read as the PsyArXiv preprint 10.31234/osf.io/mky9j) | Nature Human Behaviour 2(1):6–10 | 2018 | 10.1038/s41562-017-0189-z | peer-reviewed | https://osf.io/mky9j/ | 2026-10-29 |
| S33 | T1 | Lakens, D., Adolfi, F. G., Albers, C. J., Anvari, F., Apps, M. A. J. et al., "Justify your alpha" (abstract) | Nature Human Behaviour 2(3):168–171 | 2018 | 10.1038/s41562-018-0311-x | peer-reviewed | https://doi.org/10.1038/s41562-018-0311-x | 2026-10-29 |
| S34 | T1 | Lakens, D., "Equivalence tests: a practical primer for t tests, correlations, and meta-analyses" (full text, Europe PMC PMC5502906) | Social Psychological and Personality Science 8(4):355–362 | 2017 | 10.1177/1948550617697177 | peer-reviewed | https://europepmc.org/article/PMC/PMC5502906 | 2026-10-29 |
| S35 | T1 | Schuirmann, D. J., "A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability" (not read; as Lakens 2017 cites it) | Journal of Pharmacokinetics and Biopharmaceutics 15(6):657–680 | 1987 | 10.1007/BF01068419 | peer-reviewed | https://doi.org/10.1007/BF01068419 | 2026-10-29 |
| S36 | T1 | Lakens, D., Scheel, A. M. & Isager, P. M., "Equivalence testing for psychological research: a tutorial" (abstract, CC BY) | Advances in Methods and Practices in Psychological Science 1(2):259–269 | 2018 | 10.1177/2515245918770963 | peer-reviewed | https://doi.org/10.1177/2515245918770963 | 2026-10-29 |
| S37 | T1 | Armitage, P., McPherson, C. K. & Rowe, B. C., "Repeated significance tests on accumulating data" (abstract) | Journal of the Royal Statistical Society A 132(2):235–244 | 1969 | 10.2307/2343787 | peer-reviewed | https://doi.org/10.2307/2343787 | 2026-10-29 |
| S38 | T1 | Simmons, J. P., Nelson, L. D. & Simonsohn, U., "False-positive psychology: undisclosed flexibility in data collection and analysis allows presenting anything as significant" (abstract) | Psychological Science 22(11):1359–1366 | 2011 | 10.1177/0956797611417632 | peer-reviewed | https://doi.org/10.1177/0956797611417632 | 2026-10-29 |
| S39 | T1 | Pocock, S. J., "Group sequential methods in the design and analysis of clinical trials" (abstract) | Biometrika 64(2):191–199 | 1977 | 10.1093/biomet/64.2.191 | peer-reviewed | https://doi.org/10.1093/biomet/64.2.191 | 2026-10-29 |
| S40 | T2 | statsmodels 0.15.0 documentation: `statsmodels.stats.weightstats.ttost_ind`, `statsmodels.stats.power.TTestIndPower` (also read as the installed docstrings) | statsmodels | 2026 | — | official-docs | https://www.statsmodels.org/stable/generated/statsmodels.stats.weightstats.ttost_ind.html | 2026-10-29 |
| S41 | T2 | SciPy 1.18.1 documentation: `scipy.stats.nct`, `scipy.stats.ttest_ind` | SciPy | 2026 | — | official-docs | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nct.html | 2026-10-29 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | title.search for 45 candidates from the plan, Fisher 1925 to van Zwet & Cator 2021 | venue, year, DOI, citation count and open copy for 40; Gelman & Carlin, Sellke et al. and Durante et al. missed on punctuation and were looked up by DOI |
| 2 | 1 | Crossref | works/{doi} for 20 central sources | authors, volume, issue and pages; Lu et al. is 2019 in print (online 2018); Durante's co-author is listed as Ashley Rae |
| 3 | 1 | Crossref | works/{doi} for 19 more | volume and pages for the rest; Benjamin et al. is 2(1):6–10, online 2017; Lakens et al. 2026 is AMPPS 9(2) |
| 4 | 1 | OpenAlex | abstracts (inverted index) for 36 paywalled or bot-walled sources | abstracts for 31; none for Goodman 2008, Button 2013, Camerer 2018, Kanazawa 2007 or Gelman & Tuerlinckx 2000 |
| 5 | 1 | OpenAlex | works?filter=cites:W2119303750 (Gelman & Carlin 2014), sorted by citations | 1,342 citing works; Benjamin et al. 2018, McShane et al. 2019, Loken & Gelman 2017 (measurement error) |
| 6 | 4 | Semantic Scholar | DOI:10.1177/1745691614551642/citations, influential only | six influential citers; Lakens et al. 2026, "Rethinking type S and type M errors", a critique of the method |
| 7 | 4 | OpenAlex | title.search: Rethinking Type S and Type M Errors | AMPPS 2026 version and two PsyArXiv versions; abstract: minimum-effect tests and the critical effect size are preferred |
| 8 | 1 | OpenAlex | works?filter=cites:W2040032582 (Colquhoun 2014), sorted by citations | 792 citers; Colquhoun 2017, Mayo 2018 (a critic of the screening model of tests) |
| 9 | 1 | OpenAlex | works?filter=cites:W2610765860 (Lakens 2017), sorted by citations | 2,246 citers; Lakens, Scheel & Isager 2018, the tutorial on smallest effects of interest |
| 10 | 1 | Europe PMC | REST fullTextXML for PMC4448847, PMC5750014, PMC4877414, PMC5502906, PMC1855693 | open full texts of Colquhoun 2014 and 2017, Greenland et al. 2016, Lakens 2017, Goodman & Greenland 2007; none for Senn 2002 |
| 11 | 2 | OSF | api.osf.io nodes/ezcuj and files/fgjvw | the RPP project and its Analysis component are CC0 1.0; rpp_data.csv 259,220 bytes, sha256 matches the download |
| 12 | 3 | OSF | download of rpp_data.csv; masterscript.R from the project's GitHub repository | 167 rows; 97 pairs with both effect sizes; significance codes reproduce 97 of 100 originals and 36 of 100 replications |
| 13 | 1 | OSF | preprints n53zs and mky9j, primary files | Lu, Qiu & Deng's preprint (Theorem 1, the closed-form exaggeration ratio) and Benjamin et al.'s preprint |
| 14 | 1 | arXiv | all:"type M error" OR all:"significance filter" | van Zwet & Cator (arXiv version), Vasishth et al. 2018 on the significance filter, Altoè et al. 2020 on design analysis |
| 15 | 1 | Europe PMC | search: "two one-sided tests" equivalence, open access, by citations | Lakens 2017 first (1,102 citations); no competing primer |
| 16 | 4 | Europe PMC | search: "false positive risk" "p-value", by citations | Colquhoun's line of work, one review in a psychiatry journal; nothing that overturns it |
| 17 | 1 | OpenAlex | search: p-value misinterpretation review | noise (PRISMA, clinical guidelines): OpenAlex's full-text search is unusable for this; title.search was used instead |
| 18 | 1 | OpenAlex | search: statistical significance replication crisis review | Ioannidis 2005, OSC 2015 and the ASA statement as the most cited; the field's map confirmed |
| 19 | 4 | OpenAlex | search: optional stopping type I error inflation sequential testing | noise; Armitage, McPherson & Rowe 1969 and Pocock 1977 were reached by title instead |
| 20 | 1 | Crossref | works/10.1198/000313001300339950 (Sellke, Bayarri & Berger) | The American Statistician 55(1):62–71; full text not reachable, so its calibration formula is not quoted |
| 21 | 4 | Semantic Scholar | paper/batch for 12 DOIs, openAccessPdf | HTTP 429 for the whole batch; logged, not retried |
| 22 | 2 | OpenAlex | works/doi for Wasserstein et al. 2019 and Benjamini et al. 2021 | the 2019 editorial's own note that it is not an endorsed ASA position, and the task force's reason for existing |
| 23 | 3 | Crossref | works/10.1111/stan.12241, 10.1177/25152459261432530 | van Zwet & Cator 75(4):437–452; Lakens et al. 2026 9(2), article number only |

Blocked, not worked around: tandfonline.com PDFs and royalsocietypublishing.org PDFs (bot pages),
research.tilburguniversity.edu files (Cloudflare challenge, HTTP 403), nature.com PDF (an HTML page), the
Semantic Scholar batch endpoint (HTTP 429).

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Durante et al. reported that ovulation moved single women toward Obama and women in relationships toward Romney; Gelman and Carlin report the comparison as a 17-percentage-point difference with two-sided p = .035 | S20 abstract; S15 p. 646 | the estimate and p as Gelman and Carlin report them; the paper's tables were not read |
| L02 | Gelman and Carlin convert p = .035 to z = 2.1 and SE = 17/2.1 = 8.1 points; they take 2 points as the upper end of plausible true differences because Obama's support varied by only 7 points over the 2012 campaign; their retrodesign() gives power 0.06, type S 24% and exaggeration 9.7 | S15 p. 646 | z rounded to 2.1; the exaggeration ratio is simulated |
| L03 | Fisher: the deviation with P = .05, or 1 in 20, is 1.96, nearly 2 standard deviations, and it is convenient to take this point as a limit in judging significance | S4 ch. III, p. 47 | normal deviations |
| L04 | Classical testing as taught is a hybrid of Fisher's evidential p and Neyman–Pearson's error rate α, which Hubbard and Bayarri call incompatible; Lehmann argues the two theories are complementary in their main practical aspects | S7 abstract; S6 abstract; S5 | abstracts only |
| L05 | ASA principles: a p-value can indicate how incompatible data are with a specified model; it does not measure the probability that the hypothesis is true or that the data were produced by chance alone; it does not measure the size of an effect | S1, principles 1, 2 and 5 | — |
| L06 | Greenland et al. list as misinterpretations that p is the probability the test hypothesis is true, that it is the probability chance alone produced the association, and that rejecting at P ≤ 0.05 means a 5% chance of being in error | S9, misinterpretations 1, 2 and 10 | — |
| L07 | Gelman and Carlin's design analysis imagines replications of the same design under an externally plausible true effect: power is the chance a replication is significant, the type S rate the chance a significant replication has the wrong sign, the exaggeration ratio the expected absolute value of a significant estimate over the true effect | S15 p. 643 and Figure 1 | unbiased estimate with known SE |
| L08 | Under a true null a p-value from a continuous statistic is uniform on 0 to 1 regardless of sample size; under an alternative its distribution depends on the sample size and the true parameter value | S11 abstract | continuous test statistic |
| L09 | Murdoch et al. argue that p-values should be taught through simulation, as random variables | S12 abstract | — |
| L10 | Cumming: in 25 simulated repetitions of a typical experiment p ranged from below .001 to .76; after an initial two-tailed p = .05 a replication's one-tailed p has an 80% chance of falling between .00008 and .44, however large the sample | S13 abstract | — |
| L11 | If the alternative is correct and two studies each have 80% power, both show P ≤ 0.05 at best 64% of the time, and one does while the other does not 32% of the time | S9, section on power | ideal conditions |
| L12 | Repeated significance tests at the same nominal level raise the chance of a significant result on a true null; by the law of the iterated logarithm a standardised cumulative sum eventually reaches any preassigned value with probability one; the paper gives results for binomial, normal and exponential data | S37 abstract | tests repeated as data accumulate |
| L13 | Simmons et al. show that flexibility in data collection, analysis and reporting dramatically increases actual false-positive rates above the nominal .05 | S38 abstract | — |
| L14 | Group sequential designs test the accumulated data after each group of patients at adjusted significance levels; Pocock gives exact results for a normal response with known variance | S39 abstract | two treatments |
| L15 | statsmodels' TTestIndPower.power takes the effect size, nobs1, alpha, ratio and alternative; SciPy's nct is the noncentral t distribution | S40; S41 | statsmodels 0.15.0, SciPy 1.18.1 |
| L16 | Hoenig and Heisey document a large literature that uses post-experiment power calculations to interpret non-significant results, and argue the approach is fundamentally flawed | S14 abstract | — |
| L17 | Gelman and Carlin distinguish their retrospective design analysis from deplored post hoc power: it focuses on sign and magnitude, and its effect size comes from information external to the data | S15 p. 642 | — |
| L18 | Gelman and Carlin: 80% power when the effect is 2.8 SE, with type S 1.2 × 10⁻⁶ and exaggeration 1.12; exaggeration problems start below 50% power and type S problems below 10% | S15 pp. 643–644 and Figure 2 | unbiased normal estimates |
| L19 | Kanazawa: 56% girls among first-born children of the most attractive parents against 48% for others, 8 points with p = .015, SE 3.3 (3.28 in their code); for true differences of 0.1, 0.3 and 1 point Gelman and Carlin give type S 46%, about 40% and 19% and exaggeration 77, 25 and 8 | S15 pp. 645–646; S21 | as Gelman and Carlin report it |
| L20 | Gelman and Carlin's retrodesign() computes power and the type S rate from the t or normal distribution and simulates the exaggeration ratio from n.sims = 10,000 draws | S15 appendix and note 2 | df = Inf in their examples |
| L21 | Lu, Qiu and Deng derive the closed-form expected type M error, the exaggeration ratio, as a function of the signal-to-noise ratio and the threshold | S16 Theorem 1 | normal test statistic |
| L22 | Lakens et al. argue type S and M errors help design and interpretation less than claimed, that tests against a minimum effect and the critical or bias-adjusted effect size are preferable, and that type S and M are valuable in teaching and in discussing studies that skipped good practice | S17 abstract | abstract only |
| L23 | van Zwet and Cator prove that the relative bias of the magnitude after the significance filter decreases with power, and that the usual confidence interval undercovers when power is below 50% | S18 abstract | conditioning on significance |
| L24 | OSC replicated 100 studies from three psychology journals with high-powered designs and original materials where available: 97% of originals and 36% of replications were significant, replication effects were half the originals, and replication success was better predicted by the strength of original evidence than by team characteristics | S22 abstract | abstract only |
| L25 | The RPP data file and its Analysis component are released under CC0 1.0; the project's script reads rows 1–167 and analyses effect sizes on the pairs with both r values present | S23; S24 lines 21–22 and 191–203 | file modified 2015-09-11 |
| L26 | Gilbert et al. argue the OSC article contains statistical errors and that its data are consistent with high reproducibility; Anderson et al. reply that both optimistic and pessimistic conclusions are possible and neither is yet warranted | S25 abstract; S26 abstract | abstracts only |
| L27 | Ioannidis: when a true discovery is claimed by crossing a significance threshold and the discovery study is underpowered, the observed effects are expected to be inflated | S19 abstract | — |
| L28 | Colquhoun's tree: 1,000 tests, 10% real effects, power 0.8, threshold 0.05: 80 true and 45 false positives, so 45/125 = 36% of positives are false | S30, Figure 2 and text | — |
| L29 | Ioannidis: PPV = (1 − β)R/(R − βR + α), so a finding is more likely true than false when (1 − β)R exceeds α; a bias term u extends the formula; Table 4 lists PPVs from 0.85 to 0.0010 for nine settings | S27, sections on the 2 × 2 table and bias, Table 4 | α = 0.05 |
| L30 | Benjamin et al. propose 0.005 for claims of new discoveries; p = 0.05 corresponds to Bayes factors of about 2.5 to 3.4; at prior odds of 1:10 the false positive rate exceeds 33% whatever the power; prediction markets and replication analyses suggest prior odds near 1:10 for psychology experiments | S32 | the preprint text |
| L31 | Colquhoun 2017 renames his 2014 false discovery rate the false positive risk, to avoid the multiple-comparison sense of FDR; for 16 per group (power 0.78) and an observed p = 0.05 the likelihood ratio is 2.76 and the risk 26% at prior 0.5 and 76% at prior 0.1; at p = 0.001 the ratio is about 100 and the risks 1% and 8% | S31, sections 1 and 3–5, Table 3 | t-test, true effect 1 SD |
| L32 | Colquhoun 2014: of 100,000 simulated tests with a real effect and 100,000 without, 1,424 and 511 gave p between 0.045 and 0.05, so 26% of those were false positives | S30, section on p-equals | n = 16 per group, prior 0.5 |
| L33 | Goodman and Greenland argue that Ioannidis's model counts only verdicts of significance instead of the observed p and adds a bias term that sharply diminishes studies' evidential value, so its proof of the title claim is unfounded | S28 | — |
| L34 | Jager and Leek estimate a 14% (SD 1%) rate of false discoveries among 5,322 p-values reported in abstracts of five medical journals from 2000 to 2010 | S29 abstract | their mixture model |
| L35 | Lakens et al. answer the 0.005 proposal by asking researchers to report and justify every design choice, including the alpha level | S33 abstract | — |
| L36 | The 2019 editorial recommended dropping "statistically significant"; the ASA president's task force, formed so that the editorial would not be read as ASA policy, states in 2021 that p-values and significance tests, properly applied and interpreted, should not be abandoned | S2; S3 abstract | — |
| L37 | Lakens: "no effect" appeared in 108 SPPS articles, almost all resting on non-significance; TOST runs two one-sided tests against lower and upper bounds from the smallest effect of interest, which matches a 90% CI inside the bounds | S34, introduction and the TOST section | α = 0.05 per test |
| L38 | Schuirmann's two one-sided tests procedure for assessing the equivalence of average bioavailability | S35, as S34 cites it | not read |
| L39 | statsmodels' ttost_ind tests whether m1 − m2 lies between low and upp, pooled or Welch, and returns the larger p-value and each one-sided test's statistic, p-value and degrees of freedom | S40, and the installed docstring | statsmodels 0.15.0 |
| L40 | Lakens, Scheel and Isager explain approaches to choosing a smallest effect size of interest and how to perform and report equivalence tests | S36 abstract | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S15 | Figure 2 | type S and M against power | the method's own summary curves | © the authors, SAGE; no reuse licence | http://www.stat.columbia.edu/~gelman/research/published/retropower_final.pdf | do not reuse; the lab computes the curves in closed form and marks both published studies and Gelman & Carlin's simulated values on them |
| F2 | S30 | Figure 2 (tree diagram) | the false positive risk | 1,000 tests split into 45 false and 80 true positives | CC BY 4.0 | https://doi.org/10.1098/rsos.140216 | do not reuse: the prose carries its two numbers, and an original figure carries the whole family over prior and power, which the tree shows at one point |
| F3 | S34 | Figure 1 | the four outcomes of a test and an equivalence test | means with 90% and 95% intervals against bounds | © the author, SAGE | https://doi.org/10.1177/1948550617697177 | do not reuse; the article draws the 63 non-significant replications of S23 against the same kind of bounds |
| F4 | S22 | Figure 3 | original against replication effect sizes | the project's scatter | © AAAS | https://doi.org/10.1126/science.aac4716 | do not reuse; the scatter is redrawn from the CC0 data with the article's own split by original p-value |

## Literature note

Not needed: the sweep found more than the L4 floor of peer-reviewed sources with identifiers.

## Open questions

- Neyman & Pearson 1933, Lehmann 1993, Hubbard & Bayarri 2003, Goodman 1999, Hung et al. 1997, Murdoch et
  al. 2008, Cumming 2008, Hoenig & Heisey 2001, Armitage et al. 1969, Simmons et al. 2011, Pocock 1977, OSC
  2015, Gilbert et al. 2016, Anderson et al. 2016, Jager & Leek 2014, van Zwet & Cator 2021, Lakens et al.
  2026 and the 2018 and 2021 statements are cited for what their abstracts state, no further.
- Durante et al.'s and Kanazawa's estimates are taken as Gelman & Carlin report them (17 points with
  p = .035; 8 points with p = .015); neither paper's tables were read. Gelman & Carlin round z to 2.1, so
  the standard error is 8.1 rather than the 8.06 that p = .035 implies; the article follows their 8.1.
- The OSC paper's own descriptive numbers (means and SDs of r) could not be read; the article quotes only
  its abstract, and computes everything else from the CC0 file with the project's own subset rule.
- Sellke, Bayarri & Berger's calibration is not quoted: its full text was not reachable, and the class of
  alternatives its bound assumes could not be checked.
