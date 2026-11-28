# Source ledger — bayesian-inference-conjugate-priors

Part 11 of *Statistics for Data Scientists*. Researched 2026-11-25, inline (no agents). Numbers the article calls computed
or measured come from `lab/bayes.py` and need no key; every published number, date, attribution, named result and library
convention carries one below. Read in full: Laplace's 1781 memoir (article XIX and XXVI), his 1783 memoir on Paris births
and the 1820 edition of the *Théorie analytique*, Book II chapter VI, all in R. J. Pulskamp's English translations; Polack
et al. 2020 (Europe PMC full text); the trial protocol's section 9.5 (Amendment 9, in the paper's supplementary appendix);
the FDA briefing document's section 5.2.5; Senn 2022 (Europe PMC, CC BY-NC-ND 4.0); BDA3 sections 2.1 to 2.8, 4.4 and
7.4; Wagenmakers and Ly (arXiv 2111.10191, the accepted version); Robert 2014 (arXiv 1303.5973). Cited for what their
abstracts state: Stigler 1986, Jeffreys 1946, Kass and Wasserman 1996, Kass and Raftery 1995, Edwards, Lindman and Savage
1963, Berger and Sellke 1987, Hyndman 1996, Brown, Cai and DasGupta 2001, Cook, Gelman and Rubin 2006, Diaconis and
Ylvisaker 1979, Gelman, Simpson and Betancourt 2017, Tuyl, Gerlach and Mengersen 2008. Not read, cited for what a read
source quotes: Lindley 1957 and Bartlett 1957 (as Wagenmakers and Ly quote them), Bayes 1763 (as BDA3 describes it). The
Royal Society, Taylor & Francis and Project Euclid PDFs were not attempted (they refuse scripts, per earlier parts).

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Laplace, P.-S., "Mémoire sur les probabilités" (read: articles I, XIX, XX and XXVI in R. J. Pulskamp's English translation, 2010) | Mémoires de l'Académie royale des sciences de Paris, année 1778 | 1781 | — | source | https://gtfp.cs.rhul.ac.uk/pulskamp/Laplace/memoir_probabilities.pdf | 2026-11-25 |
| S2 | T1 | Laplace, P.-S., "Sur les naissances, les mariages et les morts à Paris, depuis 1771 jusqu'en 1784; et dans toute l'étendue de la France, pendant les années 1781 et 1782" (read in full in Pulskamp's translation, 2010, including Table 1) | Mémoires de l'Académie royale des sciences de Paris 1783: 693–702 | 1783 | — | source | https://gtfp.cs.rhul.ac.uk/pulskamp/Laplace/naissances.pdf | 2026-11-25 |
| S3 | T1 | Laplace, P.-S., *Théorie analytique des probabilités*, 3rd edition, Book II, chapter VI, §§26–33 (read in Pulskamp's translation; first edition 1812) | Courcier, Paris (book) | 1820 | — | source | https://gtfp.cs.rhul.ac.uk/pulskamp/Laplace/TAP/TAP_book2_chap6.pdf | 2026-11-25 |
| S4 | T1 | Stigler, S. M., "Laplace's 1774 memoir on inverse probability" (abstract via OpenAlex) | Statistical Science 1(3):359–363 | 1986 | 10.1214/ss/1177013620 | peer-reviewed | https://doi.org/10.1214/ss/1177013620 | 2026-11-25 |
| S5 | T1 | Bayes, T., "An essay towards solving a problem in the doctrine of chances" (not read; its uniform prior as S10 §2.1 describes it) | Philosophical Transactions of the Royal Society 53:370–418 | 1763 | 10.1098/rstl.1763.0053 | peer-reviewed | https://doi.org/10.1098/rstl.1763.0053 | 2026-11-25 |
| S6 | T1 | Polack, F. P. et al., "Safety and efficacy of the BNT162b2 mRNA Covid-19 vaccine" (read via Europe PMC, PMC7745181: abstract, Statistical Analysis, Discussion, Table 2 and its notes) | New England Journal of Medicine 383(27):2603–2615 | 2020 | 10.1056/NEJMoa2034577 | peer-reviewed | https://europepmc.org/article/PMC/PMC7745181 | 2026-11-25 |
| S7 | T2 | Pfizer and BioNTech, Protocol C4591001, Amendment 9 (29 October 2020), §9.5 Interim Analyses with Tables 6–8 (pp. 119–121), from the supplementary appendix of S6 | Pfizer (NEJM supplementary material) | 2020 | — | official-docs | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7745181/supplementaryFiles | 2026-11-25 |
| S8 | T2 | U.S. Food and Drug Administration, "FDA Briefing Document: Pfizer-BioNTech COVID-19 Vaccine", VRBPAC meeting of 10 December 2020 (read: §5.2.5 with Tables 6, 7 and 11 and their notes; a U.S. government work) | FDA | 2020 | — | official-docs | https://www.fda.gov/media/144245/download | 2026-11-25 |
| S9 | T1 | Senn, S., "The design and analysis of vaccine trials for COVID-19 for the purpose of estimating efficacy" (read in full, PMC9350415; CC BY-NC-ND 4.0; found by the Crossref search, row 15) | Pharmaceutical Statistics 21(4):790–807 | 2022 | 10.1002/pst.2226 | peer-reviewed | https://europepmc.org/article/PMC/PMC9350415 | 2026-11-25 |
| S10 | T1 | Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A. & Rubin, D. B., *Bayesian Data Analysis*, 3rd ed. (authors' electronic edition): §§2.1–2.6, 2.8, 4.4, 7.4 | CRC Press (book) | 2013 | 10.1201/b16018 | peer-reviewed | http://www.stat.columbia.edu/~gelman/book/BDA3.pdf | 2026-11-25 |
| S11 | T1 | Jeffreys, H., "An invariant form for the prior probability in estimation problems" (abstract via OpenAlex) | Proceedings of the Royal Society of London A 186(1007):453–461 | 1946 | 10.1098/rspa.1946.0056 | peer-reviewed | https://doi.org/10.1098/rspa.1946.0056 | 2026-11-25 |
| S12 | T1 | Kass, R. E. & Wasserman, L., "The selection of prior distributions by formal rules" (abstract via OpenAlex; the review for the prior rung) | Journal of the American Statistical Association 91(435):1343–1370 | 1996 | 10.1080/01621459.1996.10477003 | peer-reviewed | https://doi.org/10.1080/01621459.1996.10477003 | 2026-11-25 |
| S13 | T1 | Tuyl, F., Gerlach, R. & Mengersen, K., "A comparison of Bayes–Laplace, Jeffreys, and other priors: the case of zero events" (abstract via OpenAlex; author order checked on Crossref) | The American Statistician 62(1):40–44 | 2008 | 10.1198/000313008X267839 | peer-reviewed | https://doi.org/10.1198/000313008X267839 | 2026-11-25 |
| S14 | T1 | Gelman, A., Simpson, D. & Betancourt, M., "The prior can often only be understood in the context of the likelihood" (abstract via OpenAlex; open access) | Entropy 19(10):555 | 2017 | 10.3390/e19100555 | peer-reviewed | https://doi.org/10.3390/e19100555 | 2026-11-25 |
| S15 | T1 | Diaconis, P. & Ylvisaker, D., "Conjugate priors for exponential families" (abstract via OpenAlex) | The Annals of Statistics 7(2):269–281 | 1979 | 10.1214/aos/1176344611 | peer-reviewed | https://doi.org/10.1214/aos/1176344611 | 2026-11-25 |
| S16 | T1 | Hyndman, R. J., "Computing and graphing highest density regions" (abstract via OpenAlex) | The American Statistician 50(2):120–126 | 1996 | 10.1080/00031305.1996.10474359 | peer-reviewed | https://doi.org/10.1080/00031305.1996.10474359 | 2026-11-25 |
| S17 | T1 | Brown, L. D., Cai, T. T. & DasGupta, A., "Interval estimation for a binomial proportion" (abstract via OpenAlex, as in Part 6) | Statistical Science 16(2):101–133 | 2001 | 10.1214/ss/1009213286 | peer-reviewed | https://doi.org/10.1214/ss/1009213286 | 2026-11-25 |
| S18 | T1 | Cook, S. R., Gelman, A. & Rubin, D. B., "Validation of software for Bayesian models using posterior quantiles" (abstract via OpenAlex) | Journal of Computational and Graphical Statistics 15(3):675–692 | 2006 | 10.1198/106186006X136976 | peer-reviewed | https://doi.org/10.1198/106186006X136976 | 2026-11-25 |
| S19 | T1 | Lindley, D. V., "A statistical paradox" (not read; its summary and p. 189 as quoted in S21) | Biometrika 44(1–2):187–192 | 1957 | 10.1093/biomet/44.1-2.187 | peer-reviewed | https://doi.org/10.1093/biomet/44.1-2.187 | 2026-11-25 |
| S20 | T1 | Bartlett, M. S., "A comment on D. V. Lindley's statistical paradox" (not read; as quoted in S21) | Biometrika 44(3–4):533–534 | 1957 | 10.1093/biomet/44.3-4.533 | peer-reviewed | https://doi.org/10.1093/biomet/44.3-4.533 | 2026-11-25 |
| S21 | T1 | Wagenmakers, E.-J. & Ly, A., "History and nature of the Jeffreys–Lindley paradox" (read in full, arXiv 2111.10191; open access; online 2022) | Archive for History of Exact Sciences 77(1):25–72 | 2023 | 10.1007/s00407-022-00298-3 | peer-reviewed | https://arxiv.org/abs/2111.10191 | 2026-11-25 |
| S22 | T1 | Kass, R. E. & Raftery, A. E., "Bayes factors" (abstract via OpenAlex; the review for the testing rung) | Journal of the American Statistical Association 90(430):773–795 | 1995 | 10.1080/01621459.1995.10476572 | peer-reviewed | https://doi.org/10.1080/01621459.1995.10476572 | 2026-11-25 |
| S23 | T1 | Edwards, W., Lindman, H. & Savage, L. J., "Bayesian statistical inference for psychological research" (abstract via OpenAlex) | Psychological Review 70(3):193–242 | 1963 | 10.1037/h0044139 | peer-reviewed | https://doi.org/10.1037/h0044139 | 2026-11-25 |
| S24 | T1 | Berger, J. O. & Sellke, T., "Testing a point null hypothesis: the irreconcilability of P values and evidence" (abstract via OpenAlex) | Journal of the American Statistical Association 82(397):112–122 | 1987 | 10.1080/01621459.1987.10478397 | peer-reviewed | https://doi.org/10.1080/01621459.1987.10478397 | 2026-11-25 |
| S25 | T1 | Robert, C. P., "On the Jeffreys–Lindley paradox" (read, arXiv 1303.5973; found by the forward chase from S19) | Philosophy of Science 81(2):216–232 | 2014 | 10.1086/675729 | peer-reviewed | https://arxiv.org/abs/1303.5973 | 2026-11-25 |
| S26 | T3 | SciPy 1.18.1 source, read in the lab's environment: `stats/_continuous_distns.py` (`gamma_gen`, `beta_gen`), `stats/_discrete_distns.py` (`betabinom_gen`) | SciPy | 2026 | — | source | https://github.com/scipy/scipy/blob/main/scipy/stats/_continuous_distns.py | 2026-11-25 |
| S27 | T2 | R 4.5.2 documentation read on the build machine: `Beta` (`pbeta` by TOMS 708, `qbeta` after AS 109), `GammaDist` (`dgamma(x, shape, rate = 1, scale = 1/rate)`) | R Core Team | 2025 | — | official-docs | https://stat.ethz.ch/R-manual/R-patched/library/stats/html/Beta.html | 2026-11-25 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Web search (standard) | Laplace "Mémoire sur les probabilités" 1781 Paris baptisms boys girls 251527 241945 | Pulskamp's translations at RHUL (the *Théorie analytique* chapter and the 1783 births memoir) and the York history-of-statistics pages; no snippet carried the counts |
| 2 | 1 | Web search (standard) | C4591001 protocol "0.700102" beta prior vaccine efficacy posterior probability 98.6% | secondary write-ups (a Senn guest post, two blogs) quoting the prior and the 98.6% boundary; not the protocol itself |
| 3 | 1 | Web search (standard) | Lindley's paradox "49,581" boys "48,870" girls example source | the widely copied birth example is an invented Wikipedia illustration reused by textbooks and blogs, not data; a real example had to come from elsewhere |
| 4 | 1 | Pulskamp's Laplace index (RHUL) | index page and the 1781 memoir | the 1781 memoir (S1): 251,527 and 241,945 for 1745–1770, Laplace's series and his 1.1521 over the seventh power of a million; London 1664–1757 |
| 5 | 2 | Pulskamp's Laplace index (RHUL) | the 1783 births memoir and *Théorie analytique* II.VI | S2's Table 1, Paris 1771–1784 by year and sex; S3's 393,386 and 377,555 for 1745–1784 and Laplace's 10^-72.2511780 |
| 6 | 1 | Pfizer CDN | C4591001_Clinical_Protocol_Nov2020.pdf | HTTP 403 |
| 7 | 1 | Europe PMC | supplementary files of PMC7745181 | the protocol (Amendment 9, 376 pages) and appendix: §9.5 with the prior, the 0.995 and 0.986 thresholds, Tables 6–8 |
| 8 | 1 | Europe PMC | full-text XML of PMC7745181 | Table 2's notes (prior beta(0.700102, 1) adjusted for surveillance time; posterior probability >0.9999), the 98.6% boundary and 2.5% type I error, the "95% confidence interval" wording in the Results on efficacy |
| 9 | 1 | Gelman's book page | BDA3 electronic edition | §2.1 (Laplace's 1.15 × 10^-42, the law of succession), §2.3 (central against highest-density intervals), §§2.4–2.6, §2.8 (Jeffreys, Beta(0, 0)), §4.4 |
| 10 | 1 | OpenAlex | DOI lookups, 19: Jeffreys 1946, Lindley 1957, Kass–Wasserman, Kass–Raftery, Stigler 1986, Hyndman, Brown–Cai–DasGupta, Edwards–Lindman–Savage, Berger–Sellke, Robert, Wagenmakers–Ly, Bayes 1763, Diaconis–Ylvisaker, Rubin 1984, Gelman–Simpson–Betancourt, Cousins 2017, Sprenger 2013, Shafer 1982, Polack | venues and abstracts for all but Lindley, Shafer and Cousins; open copies flagged for Wagenmakers–Ly, Robert and Cousins (arXiv) |
| 11 | 1 | arXiv | 2111.10191, 1303.5973, 1310.3791 | Wagenmakers and Ly read in full (Lindley's summary and p. 189, Bartlett's correction, Jeffreys' √n and t² = ln(2n/π)); Robert read; Cousins skimmed, not cited |
| 12 | 1 | Internet Archive | advanced search, title "Œuvres complètes de Laplace" | volumes 1, 2, 3, 10 and 13 only; neither volume 9 nor 11 (the 1781 and 1783 memoirs), so the 1783 table rests on the translation, checked against the 1812 totals |
| 13 | 4 | FDA | briefing document of 10 December 2020 | §5.2.5: the 97.5% reading of the interval; Table 11's severe-case credible interval −124.8 to 96.3; the final-analysis threshold printed as 99.5% in the notes of Tables 6 and 7 and as 98.6% in Table 11's |
| 14 | 4 | OpenAlex | forward chase: works citing Polack 2020 with "bayesian" in the title, by citations | regulatory tutorials (BMC Medical Research Methodology 2024, Therapeutic Innovation & Regulatory Science 2023); none analyses the trial's prior |
| 15 | 4 | Crossref | bibliographic: "Senn design and analysis of vaccine trials COVID-19 estimating efficacy" | Senn 2022 (S9), which analyses the prior in detail |
| 16 | 4 | OpenAlex | forward chase: works citing Lindley 1957, by citations | Kass–Raftery 1995, Edwards–Lindman–Savage 1963, Ioannidis 2005 and Bayes-factor methods papers |
| 17 | 1 | Crossref | bibliographic: "Bartlett comment Lindley statistical paradox Biometrika 1957" | Bartlett 1957 (S20) and Lindley 1957, both with Biometrika DOIs |
| 18 | 4 | Crossref | bibliographic: "Bayesian analysis BNT162b2 vaccine efficacy beta-binomial prior" | Gerlach, Mengersen and Tuyl 2009 on the Bayes–Laplace prior; nothing on the trial |
| 19 | 4 | Crossref | bibliographic: "comparison of Bayes-Laplace Jeffreys and other priors the case of zero events" | Tuyl, Gerlach and Mengersen 2008 (S13), first author confirmed by Crossref's sequence field |
| 20 | 4 | Wiley | Senn 2022 pdfdirect | HTTP 403; the Europe PMC search (DOI) found PMC9350415, whose full-text XML was read |
| 21 | 1 | OpenAlex | DOI lookups, 4: Senn 2022, Gerlach et al. 2009, Bartlett 1957, Tuyl et al. 2008 | abstracts for Senn and both prior papers; none for Bartlett |
| 22 | 5 | SciPy 1.18.1 source | `gamma_gen`, `beta_gen`, `betabinom_gen` docstrings | SciPy's gamma takes `scale = 1/rate`; beta uses Boost; the beta-binomial pmf |
| 23 | 5 | R 4.5.2 | help pages for `Beta` and `GammaDist` | `pbeta` is TOMS 708, `qbeta` follows AS 109; `dgamma` takes shape and rate, with scale = 1/rate |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Laplace pooled the Paris baptisms of the 26 years 1745–1770 from the Academy's list (Mémoires for 1771): 251,527 boys and 241,945 girls, a ratio of about 105 to 101 | S1 art. XIX | baptisms, Paris |
| L02 | Laplace took the boy probability x as uniform a priori, so the probability that x is at most ½ is the integral of x^p(1 − x)^q from 0 to ½ over that from 0 to 1; the first term of his series gave a numerator of 1.1521 over the seventh power of a million, which he called a little too great, with a second term of about 1/200; he regarded the boy excess as certain as any moral truth | S1 art. XIX | his approximation |
| L03 | Laplace's 1783 memoir prints Paris births by sex for each year 1771–1784 (1782: 9,851 boys, 9,536 girls), and a Total row of 151,859 boys and 145,159 girls | S2 Table 1 | the translation's table |
| L04 | The *Théorie analytique* gives 393,386 boys and 377,555 girls baptised in Paris from the start of 1745 to the end of 1784, foundlings included, and Laplace's value 10^-72.2511780 × (1 − 0.0030761) for the probability that x is at most ½ | S3 §28 | 3rd edition |
| L05 | BDA3 credits Laplace's first serious application of the binomial model with a uniform prior to these births, with P(ω ≥ 0.5) ≈ 1.15 × 10^-42 for the girl probability ω, and calls the predictive (y + 1)/(n + 2) Laplace's law of succession | S10 §2.1 | — |
| L06 | Laplace's 1774 memoir was the first widely read presentation of inverse probability, applied to binomial and location estimation | S4 abstract | — |
| L07 | Bayes's 1763 essay placed a uniform prior on the binomial probability (a ball thrown on a table) and obtained the posterior probability of an interval | S10 §2.1; S5 | — |
| L08 | Among participants without prior infection, 8 Covid-19 cases occurred at least 7 days after dose 2 in the vaccine group and 162 in the placebo group, over 2.214 and 2.222 thousand person-years; efficacy 95.0% with a 95% credible interval of 90.3% to 97.6%; posterior probability above 0.9999 that efficacy exceeds 30%; with or without prior infection, 9 and 169 cases over 2.332 and 2.345, 94.6% (89.9 to 97.3) | S6 abstract, Table 2 | the evaluable efficacy population |
| L09 | The credible interval and the posterior probability came from a beta-binomial model with prior beta(0.700102, 1) adjusted for surveillance time; efficacy is 100 × (1 − IRR), IRR the ratio of case rates per 1,000 person-years | S6 Table 2 notes, Statistical Analysis | — |
| L10 | The final analysis used a success boundary of 98.6% for P(VE > 30%) to compensate for the interim analysis and hold the overall type I error at 2.5% | S6 Statistical Analysis; S7 §9.5 | — |
| L11 | The paper's Results text on efficacy calls the same 90.3–97.6 interval a 95% confidence interval; Senn reads this as a typographical error | S6 Results, Efficacy (checked in the full text); S9 | — |
| L12 | The protocol proposes a minimally informative beta(0.700102, 1) prior for θ = (1 − VE)/(2 − VE), centred at θ = 0.4118 (VE 30%), which it calls pessimistic; its 95% intervals are 0.005 to 0.964 for θ and −26.2 to 0.995 for VE | S7 §9.5, pp. 119–120 | — |
| L13 | The protocol declares success at an interim analysis if P(VE > 30% given the data) exceeds 0.995 and at the final if it exceeds 0.986; Table 6 lists the boundaries 6:26 at 32 cases, 15:47 at 62, 25:67 at 92, 35:85 at 120 and 53:111 at 164, and futility 15:17, 26:36 and 35:57; the first interim analysis was not performed | S7 §9.5, Table 6 | 1:1 randomisation |
| L14 | The study stops for futility if the predicted probability of success at the final analysis falls below 5%, a posterior predictive probability computed from a beta-binomial model; both boundaries are nonbinding | S7 §9.5 | — |
| L15 | The thresholds were calibrated so that the overall probability of success when the true VE is 30% stays at 0.025; Tables 7 and 8 list operating characteristics at VE 30% to 80%, overall 0.021 at 30% and above 0.999 at 70% | S7 §9.5, Tables 7–8 | as printed |
| L16 | The FDA briefing reads the 90.3–97.6 interval as a 97.5% probability that the true efficacy is at least 90.3%; its Table 11 gives first severe Covid-19 from 7 days after dose 2 as 1 against 3 cases over 2.215 and 2.232 thousand person-years, VE 66.4% with credible interval −124.8 to 96.3 from the same prior, criterion not met | S8 §5.2.5, Table 11 | — |
| L17 | The FDA briefing states the final-analysis success criterion as a posterior probability above 99.5% in its text and the notes of Tables 6 and 7, and as above 98.6% in the note of Table 11 | S8 §5.2.5 | an inconsistency in S8 |
| L18 | Senn notes that the prior's first parameter is given to six significant figures and the second to one; the mean 0.4118 maps to VE 30%, but a mean does not carry through a nonlinear transformation as a median does; many betas share that mean, among them beta(1, 1.428363) | S9 §§ on the prior, Figures 4–5 | — |
| L19 | A referee's justification reported by Senn: the minimally informative unimodal beta with a given mean p of at most ½ is beta(p/(1 − p), 1), after Neuenschwander and colleagues | S9, equation (10) | the mean, not the median, matched |
| L20 | Senn argues that 30% is a target for the posterior, not a prior belief, so a prior centred there is not pessimistic | S9 | — |
| L21 | Central posterior intervals take the α/2 and 1 − α/2 quantiles; a highest posterior density region contains the stated probability with no point outside denser than any inside; the two coincide for symmetric unimodal posteriors and differ for skewed ones; central intervals are common because they are quantiles and come directly from simulation | S10 §2.3 | — |
| L22 | Hyndman defines highest density regions as regions of the given probability with the highest density, possibly several disjoint intervals for a multimodal density, and gives a method to compute them | S16 abstract | bounded, continuous density |
| L23 | A prior family is conjugate when the posterior stays in the family; the beta is conjugate to the binomial | S10 §2.4 | — |
| L24 | For a normal mean with known variance and a normal prior, the posterior mean is a precision-weighted average of the prior mean and the sample mean | S10 §2.5 | known variance |
| L25 | For Poisson counts with exposures x_i and a Gamma(α, β) prior on the rate, the posterior is Gamma(α + Σy, β + Σx) | S10 §2.6 | shape and rate |
| L26 | Conjugate priors for exponential families are characterised by a posterior mean of the mean parameter that is linear in the observation | S15 abstract | exponential families |
| L27 | Jeffreys' principle sets p(θ) ∝ J(θ)^{1/2}, J the Fisher information, so that the rule gives the same answer in any parameterisation; for the binomial this is Beta(½, ½), against Bayes–Laplace's Beta(1, 1); uniform on the logit is the improper Beta(0, 0), whose posterior is improper when y = 0 or n; a density flat in one parameterisation is not flat in another, the difficulty with Laplace's principle of insufficient reason | S10 §2.8 | — |
| L28 | Jeffreys showed that a certain differential form built from a law of chance is invariant under any transformation of its parameters, and proposed it as a general rule for the prior in estimation problems | S11 abstract | differentiable laws |
| L29 | Kass and Wasserman review formal-rule priors, describe Jeffreys' shift from priors as representations of ignorance to priors chosen by convention, and warn that with small samples relative to the number of parameters no default prior can be trusted | S12 abstract | — |
| L30 | Tuyl, Gerlach and Mengersen show that beta parameters below 1 concentrate mass near 0 or 1 and can suppress the data, so the Jeffreys prior is informative when there are no successes, and argue for the Bayes–Laplace prior as the reference for sensitivity analysis | S13 abstract | zero events |
| L31 | Gelman, Simpson and Betancourt argue that almost every way of building a prior is implicitly tied to a reference likelihood, so a prior is understood in the context of the whole analysis | S14 abstract | — |
| L32 | Asymptotically, a 95% central posterior interval covers the true value 95% of the time in repeated sampling at any fixed true value; a confidence region covers the true value at least 95% of the time at every value | S10 §4.4 | large samples, correct model |
| L33 | Brown, Cai and DasGupta recommend the Wilson interval or the equal-tailed Jeffreys interval for a binomial proportion in small samples | S17 abstract | n of 40 or less |
| L34 | Cook, Gelman and Rubin validate Bayesian software by simulating parameters from the prior and data from the model and checking the posterior quantiles of the true parameters | S18 abstract | — |
| L35 | Lindley's example: a result significant at 5% while the posterior probability of the null, for quite small prior probabilities of it, is as high as 95%; 5% in today's small sample does not mean the same as 5% in tomorrow's large one; his alternative was uniform over an interval I | S19 as quoted in S21 | normal mean, point null |
| L36 | Bartlett corrected a slip in Lindley's Bayes factor, a missing factor 1/I from the uniform density | S20 as quoted in S21 | — |
| L37 | Jeffreys derived the conflict from 1935 on, before Lindley; the evidence for a point null scales with √n, so an evidence threshold cannot be a fixed multiple of the standard error; for even odds and large n Jeffreys gave t² = ln(2n/π), t = 3.32 at n = 100,000 | S21 (Jeffreys 1937, 1938 as quoted) | Jeffreys' default priors |
| L38 | Kass and Raftery describe the Bayes factor as Jeffreys' measure of evidence, equal to the posterior odds of the null when its prior probability is one half | S22 abstract | — |
| L39 | Edwards, Lindman and Savage note that classical tests compare a sharp null with a diffuse alternative, and that evidence strongly supporting the null for a Bayesian can lead to rejection | S23 abstract | — |
| L40 | Berger and Sellke show that evidence against a point null can differ from the p-value by an order of magnitude: p = 0.05 for a normal mean gives a posterior probability of the null of at least 0.30 for any objective prior | S24 abstract | equal prior weights; normal mean |
| L41 | Robert reads the paradox both as a split between frequentist and Bayesian testing and as a warning against improper priors in tests | S25 abstract | — |
| L42 | SciPy's `gamma` takes a shape and `scale`, with scale equal to 1/rate; `beta` uses Boost; `betabinom(n, a, b)` has pmf C(n, k) B(k + a, n − k + b)/B(a, b) | S26 | SciPy 1.18.1 |
| L43 | R's `pbeta` implements TOMS 708 and `qbeta` follows AS 109; `dgamma` takes shape and rate, rate 1 by default, with scale = 1/rate | S27 | R 4.5.2 |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S9 | Figure 4 (the trial's prior on θ with alternatives) | How much does the prior matter? / L18 | the prior beside alternatives with the same mean | CC BY-NC-ND 4.0, which forbids adaptation and commercial use | https://europepmc.org/article/PMC/PMC9350415 | do not reuse; Figure 9 draws our own priors on two scales |
| F2 | S10 | Figure 2.2 (central interval against HPD region, bimodal) | Credible intervals / L21 | the two summaries side by side | the electronic edition is for non-commercial use only | http://www.stat.columbia.edu/~gelman/book/BDA3.pdf | do not reuse; Figure 5 computes both intervals for the trial's severe-case posterior |

## Open questions

- The 1783 table's printed Total row (151,859 boys, 145,159 girls) does not equal its own year rows (141,859; 135,610),
  which do reproduce the 1812 totals; whether the misprint is in the Academy's printing or the translation was not checked,
  since no scan of the *Œuvres complètes* volume 11 was found. The article uses the year rows.
- Laplace's first term recomputes to 1.15215 × 10^-42, which he printed as 1.1521; the exact integral is 1.14606 × 10^-42.
- The protocol's Table 8 prints the overall probability of success at VE 70% as above 0.999, but its own success columns
  sum to 0.994, the exact sequential value with binding futility (0.998 without). The other 44 printed operating
  characteristics reproduce.
- The FDA briefing's 99.5% (text, Tables 6–7 notes) against the protocol's and the paper's 98.6% for the final analysis:
  the article follows the protocol.
